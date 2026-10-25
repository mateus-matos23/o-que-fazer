"""Repositório contra o content/ real (fixture `loaded` do conftest raiz) e dados mínimos extras."""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Condition, Dependency, Procedure, Rule, Situation
from guidance.engine.evaluation import evaluate
from guidance.engine.model import Facts, Unknown
from guidance.engine.plan import build_plan
from guidance.engine.questions import next_question
from guidance.repository import SituationNotFound, load_catalog

pytestmark = pytest.mark.django_db

QUESTION = "cpf-situacao-cadastral"
CLARIFIER = "consultar-situacao-cpf"


def _plan_slugs(facts: Facts) -> list[str]:
    plan = build_plan(load_catalog("cpf-irregular"), facts)
    return [step.procedure.slug for step in plan.steps]


def _extra_procedure(slug: str, *, candidate: bool = False) -> Procedure:
    template = Procedure.objects.get(slug="regularizar-cpf-suspenso")
    procedure = Procedure.objects.create(
        slug=slug,
        title=slug,
        description="",
        agency=template.agency,
        jurisdiction=template.jurisdiction,
        snapshot=template.snapshot,
        excerpt="x",
    )
    if candidate:
        Situation.objects.get(slug="cpf-irregular").candidates.add(procedure)
    return procedure


def _depends(before: Procedure, after: Procedure) -> Dependency:
    return Dependency.objects.create(
        before=before,
        after=after,
        kind=Dependency.Kind.MANDATORY,
        snapshot=before.snapshot,
        excerpt="x",
    )


def test_catalog_content(loaded: dict[str, int]) -> None:
    catalog = load_catalog("cpf-irregular")
    assert catalog.situation_title == "Meu CPF está irregular"
    assert catalog.candidates == {
        "regularizar-cpf-suspenso",
        "entregar-dirpf-pendente",
        "atendimento-receita-cpf",
    }
    assert [o.slug for o in catalog.questions[QUESTION].options] == [
        "suspenso",
        "pendente-de-regularizacao",
        "cancelado",
        "nulo",
        "falecido",
    ]
    assert catalog.procedures[CLARIFIER].clarifies == QUESTION
    citation = catalog.procedures["regularizar-cpf-suspenso"].citation
    assert citation.source_slug == "api-servicos-10416"
    assert citation.fetched_at.year == 2026
    assert catalog.dependencies == ()


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("suspenso", "regularizar-cpf-suspenso"),
        ("pendente-de-regularizacao", "entregar-dirpf-pendente"),
        ("cancelado", "atendimento-receita-cpf"),
        ("nulo", "atendimento-receita-cpf"),
        ("falecido", "atendimento-receita-cpf"),
    ],
)
def test_end_to_end_each_option(loaded: dict[str, int], answer: str, expected: str) -> None:
    assert _plan_slugs({QUESTION: frozenset({answer})}) == [expected]


def test_end_to_end_unknown_asks_clarification(loaded: dict[str, int]) -> None:
    plan = build_plan(load_catalog("cpf-irregular"), {QUESTION: Unknown.UNKNOWN})
    assert [s.procedure.slug for s in plan.steps] == [CLARIFIER]
    clarifies = plan.steps[0].clarifies
    assert clarifies is not None
    assert clarifies.slug == QUESTION


def test_end_to_end_no_facts_asks_question(loaded: dict[str, int]) -> None:
    catalog = load_catalog("cpf-irregular")
    plan = build_plan(catalog, {})
    assert plan.steps == ()
    assert len(plan.undetermined) == 3
    question = next_question(catalog, {}, evaluate(catalog, {}))
    assert question is not None
    assert question.slug == QUESTION


def test_prerequisite_outside_candidates_is_loaded_transitively(loaded: dict[str, int]) -> None:
    target = Procedure.objects.get(slug="regularizar-cpf-suspenso")
    middle = _extra_procedure("pre-intermediario")
    root = _extra_procedure("pre-raiz")
    _extra_procedure("sem-relacao")
    _depends(middle, target)
    _depends(root, middle)

    catalog = load_catalog("cpf-irregular")
    assert {"pre-intermediario", "pre-raiz"} <= set(catalog.procedures)
    assert "sem-relacao" not in catalog.procedures
    assert "pre-raiz" not in catalog.candidates
    assert {(d.before, d.after) for d in catalog.dependencies} == {
        ("pre-intermediario", "regularizar-cpf-suspenso"),
        ("pre-raiz", "pre-intermediario"),
    }


def test_query_count_is_independent_of_catalog_size(loaded: dict[str, int]) -> None:
    def count() -> int:
        with CaptureQueriesContext(connection) as ctx:
            load_catalog("cpf-irregular")
        return len(ctx)

    baseline = count()
    target = Procedure.objects.get(slug="regularizar-cpf-suspenso")
    template_condition = Condition.objects.first()
    assert template_condition is not None
    previous = target
    for i in range(5):
        extra = _extra_procedure(f"extra-{i}", candidate=True)
        rule = Rule.objects.create(
            slug=f"extra-rule-{i}",
            procedure=extra,
            explanation="x",
            snapshot=extra.snapshot,
            excerpt="x",
        )
        condition = Condition.objects.create(
            rule=rule, question=template_condition.question, operator="ANY_OF"
        )
        condition.options.set(template_condition.options.all())
        _depends(extra, previous)
        previous = extra

    assert count() == baseline
    assert baseline <= 16


def test_unknown_situation(loaded: dict[str, int]) -> None:
    with pytest.raises(SituationNotFound):
        load_catalog("nao-existe")
