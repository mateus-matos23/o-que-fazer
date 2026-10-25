import pytest

from guidance.engine.effect import AnswerEffect, answer_effect
from guidance.engine.model import Unknown
from guidance.engine.ordering import DependencyCycleError
from guidance.engine.plan import build_plan
from guidance.tests.factories import catalog, cond, dep, procedure, question, rule

UNKNOWN = Unknown.UNKNOWN
A = {"q1": frozenset({"a"})}
B = {"q1": frozenset({"b"})}

CAT = catalog(
    (question("q1"), question("q2")),
    (
        procedure("so-a", rule("r1", cond("q1", "ANY_OF", "a"))),
        procedure("so-b", rule("r2", cond("q1", "ANY_OF", "b"))),
        procedure("depende-de-q2", rule("r3", cond("q2", "ANY_OF", "a"))),
        procedure("consulta", clarifies="q1"),
    ),
    candidates=("so-a", "so-b", "depende-de-q2"),
)


def test_answer_puts_procedure_in_plan() -> None:
    assert answer_effect(CAT, {}, A) == AnswerEffect(("so-a",), (), 1)


def test_answer_takes_procedure_out_of_plan() -> None:
    assert answer_effect(CAT, A, {"q1": frozenset({"c"})}) == AnswerEffect((), ("so-a",), 1)


def test_undetermined_to_not_applicable_is_not_a_departure() -> None:
    # so-b nunca esteve nas etapas: estava em "faltam informações" e virou não aplicável
    assert "so-b" not in {s.procedure.slug for s in build_plan(CAT, {}).steps}
    assert answer_effect(CAT, {}, A).left == ()


def test_same_answer_rewritten_has_no_changes() -> None:
    effect = answer_effect(CAT, A, dict(A))
    assert (effect.entered, effect.left) == ((), ())


def test_swapping_option_enters_and_leaves() -> None:
    assert answer_effect(CAT, A, B) == AnswerEffect(("so-b",), ("so-a",), 1)


def test_unknown_brings_clarification_in_and_takes_answer_out() -> None:
    assert answer_effect(CAT, {}, {"q1": UNKNOWN}) == AnswerEffect(("consulta",), (), 3)
    assert answer_effect(CAT, A, {"q1": UNKNOWN}) == AnswerEffect(("consulta",), ("so-a",), 3)


def test_in_play_equals_plan_undetermined() -> None:
    facts = {"q1": UNKNOWN, "q2": UNKNOWN}
    assert answer_effect(CAT, A, facts).in_play == len(build_plan(CAT, facts).undetermined)


def test_in_play_ignores_pulled_prerequisites() -> None:
    cat = catalog(
        (question("q1"),),
        (
            procedure("alvo", rule("r1", cond("q1", "ANY_OF", "a"))),
            procedure("pre"),
        ),
        candidates=("alvo",),
        dependencies=(dep("pre", "alvo"),),
    )
    effect = answer_effect(cat, {}, A)
    assert effect.entered == ("pre", "alvo")  # ordem das etapas
    assert effect.in_play == len(build_plan(cat, A).undetermined) == 0


def test_multiple_choice_enters_several_in_plan_order() -> None:
    cat = catalog(
        (question("docs", ("cpf", "cin", "cnh"), kind="MULTIPLE"),),
        (
            procedure("via-cnh", rule("r1", cond("docs", "ANY_OF", "cnh"))),
            procedure("via-cpf", rule("r2", cond("docs", "ANY_OF", "cpf"))),
            procedure("via-cin", rule("r3", cond("docs", "ANY_OF", "cin"))),
        ),
    )
    effect = answer_effect(cat, {}, {"docs": frozenset({"cpf", "cnh"})})
    assert set(effect.entered) == {"via-cnh", "via-cpf"}
    assert effect.left == ()


def test_cycle_propagates() -> None:
    cat = catalog(
        (question("q1"),),
        (procedure("x"), procedure("y")),
        dependencies=(dep("x", "y"), dep("y", "x")),
    )
    with pytest.raises(DependencyCycleError):
        answer_effect(cat, {}, A)
