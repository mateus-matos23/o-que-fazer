from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Tri, Unknown
from guidance.engine.questions import next_question
from guidance.tests.factories import catalog, cond, procedure, question, rule

UNKNOWN = Unknown.UNKNOWN


def ask(cat: Catalog, facts: Facts) -> str | None:
    chosen = next_question(cat, facts, evaluate(cat, facts))
    return chosen.slug if chosen else None


def test_picks_question_that_affects_most_procedures() -> None:
    cat = catalog(
        (question("q1"), question("q2")),
        (
            procedure("p1", rule("r1", cond("q1", "ANY_OF", "a"))),
            procedure("p2", rule("r2", cond("q2", "ANY_OF", "a"))),
            procedure("p3", rule("r3", cond("q2", "NONE_OF", "b"))),
        ),
    )
    assert ask(cat, {}) == "q2"


def test_tie_breaks_by_order_then_slug() -> None:
    procs = (procedure("p", rule("r", cond("qa", "ANY_OF", "a"), cond("qb", "ANY_OF", "a"))),)
    by_order = catalog((question("qa", order=2), question("qb", order=1)), procs)
    assert ask(by_order, {}) == "qb"
    by_slug = catalog((question("qb", order=1), question("qa", order=1)), procs)
    assert ask(by_slug, {}) == "qa"


def test_never_repeats_answered_or_unknown() -> None:
    cat = catalog(
        (question("q1"), question("q2")),
        (procedure("p", rule("r", cond("q1", "ANY_OF", "a"), cond("q2", "ANY_OF", "a"))),),
    )
    assert ask(cat, {"q1": UNKNOWN}) == "q2"
    assert ask(cat, {"q1": UNKNOWN, "q2": UNKNOWN}) is None


def test_stops_when_nothing_is_undetermined() -> None:
    cat = catalog((question("q"),), (procedure("p", rule("r", cond("q", "ANY_OF", "a"))),))
    assert ask(cat, {"q": frozenset({"a"})}) is None


def test_ignores_question_absent_from_conditions() -> None:
    cat = catalog(
        (question("usada"), question("solta", order=-1)),
        (procedure("p", rule("r", cond("usada", "ANY_OF", "a"))),),
    )
    assert ask(cat, {}) == "usada"
    assert ask(cat, {"usada": UNKNOWN}) is None  # "solta" tem pontuação 0 (RN02)


def test_ignores_not_applicable_procedures() -> None:
    cat = catalog(
        (question("q1"), question("q2")),
        (
            procedure("p1", rule("r1", cond("q1", "ANY_OF", "a"), cond("q2", "ANY_OF", "a"))),
            procedure("p2", rule("r2", cond("q1", "ANY_OF", "a"))),
        ),
    )
    # q1=b elimina ambos; nada a perguntar
    assert ask(cat, {"q1": frozenset({"b"})}) is None


def test_cpf_irregular_in_miniature() -> None:
    q = question("situacao", ("suspenso", "pendente", "cancelado", "nulo", "falecido"))
    cat = catalog(
        (q,),
        (
            procedure("regularizar", rule("r1", cond("situacao", "ANY_OF", "suspenso"))),
            procedure("dirpf", rule("r2", cond("situacao", "ANY_OF", "pendente"))),
            procedure(
                "atendimento",
                rule("r3", cond("situacao", "ANY_OF", "falecido", "cancelado", "nulo")),
            ),
            procedure("consultar", clarifies="situacao"),
        ),
        candidates=("regularizar", "dirpf", "atendimento"),
    )
    assert ask(cat, {}) == "situacao"

    facts: Facts = {"situacao": frozenset({"suspenso"})}
    result = evaluate(cat, facts)
    assert {s: e.status for s, e in result.items()} == {
        "regularizar": Tri.APPLICABLE,
        "dirpf": Tri.NOT_APPLICABLE,
        "atendimento": Tri.NOT_APPLICABLE,
    }
    assert ask(cat, facts) is None

    unknown: Facts = {"situacao": UNKNOWN}
    assert {e.status for e in evaluate(cat, unknown).values()} == {Tri.UNDETERMINED}
    assert ask(cat, unknown) is None
