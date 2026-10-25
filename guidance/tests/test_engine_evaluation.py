import pytest

from guidance.engine.evaluation import (
    evaluate,
    evaluate_condition,
    evaluate_procedure,
    evaluate_rule,
    validate_facts,
)
from guidance.engine.model import Answer, Facts, Tri, Unknown
from guidance.tests.factories import catalog, cond, procedure, question, rule

A, N, U = Tri.APPLICABLE, Tri.NOT_APPLICABLE, Tri.UNDETERMINED
UNKNOWN = Unknown.UNKNOWN


def fs(*slugs: str) -> frozenset[str]:
    return frozenset(slugs)


@pytest.mark.parametrize(
    ("operator", "answer", "expected"),
    [
        ("ANY_OF", None, U),
        ("NONE_OF", None, U),
        ("ANY_OF", UNKNOWN, U),
        ("NONE_OF", UNKNOWN, U),  # "não sei" não vira negativo
        ("ANY_OF", fs("a"), A),
        ("ANY_OF", fs("a", "c"), A),
        ("ANY_OF", fs("b"), N),
        ("ANY_OF", fs(), N),
        ("NONE_OF", fs("a"), N),
        ("NONE_OF", fs("b"), A),
        ("NONE_OF", fs(), A),
    ],
)
def test_evaluate_condition(operator: str, answer: Answer | None, expected: Tri) -> None:
    condition = cond("q", "ANY_OF" if operator == "ANY_OF" else "NONE_OF", "a")
    facts: Facts = {} if answer is None else {"q": answer}
    assert evaluate_condition(condition, facts) is expected


@pytest.mark.parametrize(
    ("results", "expected"),
    [
        ((A, A), A),
        ((A, U), U),
        ((A, N), N),
        ((U, N), N),
        ((U, U), U),
        ((N, N), N),
    ],
)
def test_evaluate_rule_kleene_and(results: tuple[Tri, Tri], expected: Tri) -> None:
    # A -> q=a casa; N -> q=b não casa; U -> pergunta ausente
    facts: Facts = {"q": fs("a")}
    by_status = {
        A: cond("q", "ANY_OF", "a"),
        N: cond("q", "ANY_OF", "b"),
        U: cond("x", "ANY_OF", "a"),
    }
    r = rule("r", *(by_status[s] for s in results))
    assert evaluate_rule(r, facts) is expected


@pytest.mark.parametrize(
    ("results", "expected"),
    [
        ((A, N), A),
        ((A, U), A),
        ((U, N), U),
        ((N, N), N),
        ((U, U), U),
    ],
)
def test_evaluate_procedure_kleene_or(results: tuple[Tri, Tri], expected: Tri) -> None:
    facts: Facts = {"q": fs("a")}
    by_status = {
        A: cond("q", "ANY_OF", "a"),
        N: cond("q", "ANY_OF", "b"),
        U: cond("x", "ANY_OF", "a"),
    }
    proc = procedure("p", *(rule(f"r{i}", by_status[s]) for i, s in enumerate(results)))
    evaluation = evaluate_procedure(proc, facts)
    assert evaluation.status is expected
    assert tuple(s for _, s in evaluation.rules) == results


def test_procedure_without_rules_is_applicable() -> None:
    assert evaluate_procedure(procedure("p"), {}).status is A


def test_changing_answer_recomputes() -> None:
    cat = catalog((question("q"),), (procedure("p", rule("r", cond("q", "ANY_OF", "a"))),))
    assert evaluate(cat, {"q": fs("a")})["p"].status is A
    assert evaluate(cat, {"q": fs("b")})["p"].status is N
    assert evaluate(cat, {})["p"].status is U


@pytest.mark.parametrize(
    ("facts", "message"),
    [
        ({"fora": fs("a")}, "fora"),
        ({"q": fs("zzz")}, "zzz"),
        ({"semsei": UNKNOWN}, "semsei"),
        ({"q": fs()}, "exatamente uma"),
        ({"q": fs("a", "b")}, "exatamente uma"),
    ],
)
def test_validate_facts_errors(facts: Facts, message: str) -> None:
    cat = catalog((question("q"), question("semsei", allows_unknown=False)), ())
    with pytest.raises(ValueError, match=message):
        validate_facts(cat, facts)


def test_validate_facts_accepts_valid_and_empty_multiple() -> None:
    cat = catalog((question("q"), question("m", kind="MULTIPLE")), ())
    validate_facts(cat, {"q": UNKNOWN, "m": fs()})
    validate_facts(cat, {"q": fs("a"), "m": fs("a", "b")})


def test_evaluate_validates_facts_first() -> None:
    with pytest.raises(ValueError, match="fora"):
        evaluate(catalog((), ()), {"fora": fs("a")})
