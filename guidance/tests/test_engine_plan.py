import pytest

from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Tri, Unknown
from guidance.engine.ordering import DependencyCycleError
from guidance.engine.plan import Plan, build_plan
from guidance.engine.questions import next_question
from guidance.tests.factories import catalog, cond, dep, procedure, question, rule

UNKNOWN = Unknown.UNKNOWN
A = frozenset({"a"})
B = frozenset({"b"})
QS = (question("q"),)
ON = rule("on", cond("q", "ANY_OF", "a"))


def slugs(plan: Plan) -> list[str]:
    return [s.procedure.slug for s in plan.steps]


def layers(plan: Plan) -> dict[str, int]:
    return {s.procedure.slug: s.layer for s in plan.steps}


def test_only_applicable_enter_and_undetermined_is_reported() -> None:
    cat = catalog(
        (question("q"), question("z")),
        (
            procedure("ok", ON),
            procedure("no", rule("n", cond("q", "ANY_OF", "b"))),
            procedure("maybe", rule("m", cond("z", "ANY_OF", "a"))),
            procedure("free"),
        ),
    )
    plan = build_plan(cat, {"q": A})
    assert slugs(plan) == ["free", "ok"]
    assert plan.undetermined == ("maybe",)
    ok = plan.steps[1]
    assert ok.reasons == (ON,) and ok.status is Tri.APPLICABLE and ok.required_for == ()


def test_clarification_enters_only_on_unknown() -> None:
    cat = catalog(
        QS,
        (procedure("main", ON), procedure("check", clarifies="q")),
        candidates=("main",),
    )
    plan = build_plan(cat, {"q": UNKNOWN})
    step = plan.steps[0]
    assert slugs(plan) == ["check"] and plan.undetermined == ("main",)
    assert step.status is Tri.UNDETERMINED and step.clarifies == cat.questions["q"]
    assert slugs(build_plan(cat, {"q": A})) == ["main"]
    assert slugs(build_plan(cat, {})) == []


def test_mandatory_linear_and_diamond_layers() -> None:
    procs = tuple(procedure(s) for s in "abcd")
    linear = catalog((), procs, dependencies=(dep("a", "b"), dep("b", "c")))
    assert layers(build_plan(linear, {})) == {"a": 1, "b": 2, "c": 3, "d": 1}
    diamond = catalog(
        (),
        procs,
        dependencies=(dep("a", "b"), dep("a", "c"), dep("b", "d"), dep("c", "d")),
    )
    plan = build_plan(diamond, {})
    assert slugs(plan) == ["a", "b", "c", "d"]
    assert layers(plan) == {"a": 1, "b": 2, "c": 2, "d": 3}
    assert [d.before for d in plan.steps[3].after] == ["b", "c"]


@pytest.mark.parametrize(
    ("facts", "pulled", "status"),
    [({"q": A}, True, Tri.APPLICABLE), ({}, True, Tri.UNDETERMINED), ({"q": B}, False, None)],
)
def test_prerequisite_not_candidate(facts: Facts, pulled: bool, status: Tri | None) -> None:
    cat = catalog(
        QS,
        (procedure("main"), procedure("pre", ON)),
        candidates=("main",),
        dependencies=(dep("pre", "main"),),
    )
    plan = build_plan(cat, facts)
    if not pulled:
        assert slugs(plan) == ["main"]
        return
    assert slugs(plan) == ["pre", "main"]
    assert plan.steps[0].status is status and plan.steps[0].required_for == ("main",)


def test_prerequisite_is_transitive() -> None:
    cat = catalog(
        (),
        (procedure("a"), procedure("b"), procedure("c")),
        candidates=("c",),
        dependencies=(dep("a", "b"), dep("b", "c")),
    )
    plan = build_plan(cat, {})
    assert layers(plan) == {"a": 1, "b": 2, "c": 3}
    assert plan.steps[0].required_for == ("b",) and plan.steps[1].required_for == ("c",)


def test_prerequisite_required_by_many_is_sorted() -> None:
    cat = catalog(
        (),
        (procedure("p"), procedure("y"), procedure("x")),
        candidates=("x", "y"),
        dependencies=(dep("p", "y"), dep("p", "x")),
    )
    assert build_plan(cat, {}).steps[0].required_for == ("x", "y")


def conditional(facts: Facts) -> tuple[Catalog, Plan]:
    cat = catalog(
        QS,
        (procedure("main"), procedure("pre")),
        candidates=("main",),
        dependencies=(dep("pre", "main", "CONDITIONAL", ON),),
    )
    return cat, build_plan(cat, facts)


def test_conditional_dependency_only_when_rule_applies() -> None:
    assert slugs(conditional({"q": A})[1]) == ["pre", "main"]
    assert slugs(conditional({"q": B})[1]) == ["main"]
    cat, plan = conditional({})
    assert slugs(plan) == ["main"]
    chosen = next_question(cat, {}, evaluate(cat, {}))
    assert chosen is not None and chosen.slug == "q"


def test_recommended_never_adds_and_reorders_within_layer() -> None:
    procs = (procedure("a"), procedure("b"), procedure("out"))
    alone = catalog((), procs, candidates=("a",), dependencies=(dep("out", "a", "RECOMMENDED"),))
    assert slugs(build_plan(alone, {})) == ["a"]

    cat = catalog((), procs, candidates=("a", "b"), dependencies=(dep("b", "a", "RECOMMENDED"),))
    plan = build_plan(cat, {})
    assert slugs(plan) == ["b", "a"] and layers(plan) == {"a": 1, "b": 1}
    assert [d.before for d in plan.steps[1].after] == ["b"]


def test_recommended_does_not_cross_layers() -> None:
    cat = catalog(
        (),
        (procedure("a"), procedure("b"), procedure("c")),
        dependencies=(dep("a", "b"), dep("c", "a", "RECOMMENDED")),
    )
    plan = build_plan(cat, {})
    assert layers(plan) == {"a": 1, "c": 1, "b": 2}  # c é recomendada antes de a: mesma camada
    cat = catalog(
        (),
        (procedure("a"), procedure("b"), procedure("c")),
        dependencies=(dep("a", "b"), dep("b", "c"), dep("c", "a", "RECOMMENDED")),
    )
    plan = build_plan(cat, {})
    assert slugs(plan) == ["a", "b", "c"]
    assert [d.before for d in plan.steps[0].after] == ["c"]


def test_cycle_raises() -> None:
    cat = catalog((), (procedure("a"), procedure("b")), dependencies=(dep("a", "b"), dep("b", "a")))
    with pytest.raises(DependencyCycleError):
        build_plan(cat, {})


def test_changing_answer_changes_plan() -> None:
    cat = catalog(QS, (procedure("x", ON), procedure("y", rule("n", cond("q", "ANY_OF", "b")))))
    assert slugs(build_plan(cat, {"q": A})) == ["x"]
    assert slugs(build_plan(cat, {"q": B})) == ["y"]


def test_deterministic() -> None:
    cat = catalog((), tuple(procedure(s) for s in "dcba"), dependencies=(dep("a", "d"),))
    assert build_plan(cat, {}) == build_plan(cat, {})
    assert slugs(build_plan(cat, {})) == ["a", "b", "c", "d"]


def test_uncovered_single_and_multiple_in_question_then_option_order() -> None:
    cat = catalog(
        (
            question("late", order=2, uncovered=("a",)),
            question("early", ("x", "y", "z"), kind="MULTIPLE", order=1, uncovered=("x", "z")),
            question("covered", order=0),
        ),
        (procedure("p"),),
    )
    facts: Facts = {
        "late": A,
        "early": frozenset({"z", "x", "y"}),
        "covered": A,
    }
    assert build_plan(cat, facts).uncovered == (("early", "x"), ("early", "z"), ("late", "a"))
    assert slugs(build_plan(cat, facts)) == ["p"]  # as demais etapas seguem normais


def test_uncovered_ignores_unknown_unanswered_and_covered_choice() -> None:
    cat = catalog((question("q", uncovered=("b",)),), (procedure("p"),))
    assert build_plan(cat, {"q": UNKNOWN}).uncovered == ()
    assert build_plan(cat, {}).uncovered == ()
    assert build_plan(cat, {"q": A}).uncovered == ()
    assert build_plan(cat, {"q": B}).uncovered == (("q", "b"),)
