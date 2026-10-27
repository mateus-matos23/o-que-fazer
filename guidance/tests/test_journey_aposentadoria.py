"""Motor sobre o conteúdo real da jornada "aposentadoria"."""

import pytest
from django.test import Client

from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Tri, Unknown
from guidance.engine.plan import Plan, PlanStep, build_plan
from guidance.engine.questions import next_question
from guidance.repository import load_catalog

pytestmark = pytest.mark.django_db

SLUG = "aposentadoria"
TYPE = "tipo-de-aposentadoria"
WORK = "meio-de-trabalho-aposentadoria"
BY_AGE = "aposentadoria-por-idade-urbana"
BY_TIME = "aposentadoria-por-tempo-de-contribuicao"
CNIS = "extrato-cnis"
SIMULATOR = "simular-aposentadoria"


def _facts(kind: str | Unknown | None, work: str | None = "urbano") -> Facts:
    facts: dict[str, frozenset[str] | Unknown] = {}
    if kind is not None:
        facts[TYPE] = kind if isinstance(kind, Unknown) else frozenset({kind})
    if work is not None:
        facts[WORK] = frozenset({work})
    return facts


def _slugs(plan: Plan) -> set[str]:
    return {s.procedure.slug for s in plan.steps}


def _step(plan: Plan, slug: str) -> PlanStep:
    return next(s for s in plan.steps if s.procedure.slug == slug)


@pytest.fixture
def catalog(loaded: dict[str, int]) -> Catalog:
    return load_catalog(SLUG)


@pytest.mark.parametrize(
    ("kind", "work", "in_plan", "uncovered"),
    [
        ("por-idade", "urbano", {BY_AGE, CNIS}, ()),
        ("por-tempo-de-contribuicao", None, {BY_TIME, CNIS}, ()),
        ("por-idade", "rural", {CNIS}, ((WORK, "rural"),)),
    ],
)
def test_plan_table(
    catalog: Catalog,
    kind: str,
    work: str | None,
    in_plan: set[str],
    uncovered: tuple[tuple[str, str], ...],
) -> None:
    plan = build_plan(catalog, _facts(kind, work))
    assert _slugs(plan) == in_plan
    assert plan.uncovered == uncovered
    assert not plan.undetermined


def test_time_based_plan_never_asks_work_environment(catalog: Catalog) -> None:
    facts = _facts("por-tempo-de-contribuicao", None)
    evaluations = evaluate(catalog, facts)
    question = next_question(catalog, facts, evaluations)
    assert question is None  # a regra de tempo não cita o meio de trabalho


def test_unknown_type_brings_simulator_and_keeps_retirements_undetermined(catalog: Catalog) -> None:
    facts = _facts(Unknown.UNKNOWN, None)
    plan = build_plan(catalog, facts)
    clarified = _step(plan, SIMULATOR).clarifies
    assert clarified is not None and clarified.slug == TYPE
    assert _step(plan, SIMULATOR).status is Tri.UNDETERMINED
    assert BY_AGE not in _slugs(plan) and BY_TIME not in _slugs(plan)
    assert set(plan.undetermined) == {BY_AGE, BY_TIME}  # "não sei" ≠ negativo (RN03)
    assert CNIS in _slugs(plan)


def test_changing_type_recomputes_plan(catalog: Catalog) -> None:
    facts = _facts("por-idade", "urbano")
    assert _slugs(build_plan(catalog, facts)) == {BY_AGE, CNIS}
    facts = {**facts, TYPE: frozenset({"por-tempo-de-contribuicao"})}  # resposta editada
    plan = build_plan(catalog, facts)
    assert _slugs(plan) == {BY_TIME, CNIS}
    assert SIMULATOR not in _slugs(plan)


def test_http_flow_recomputes_after_editing_type(loaded: dict[str, int], client: Client) -> None:
    client.post(f"/s/{SLUG}/", {"question": TYPE, "answer": "por-idade"})
    client.post(f"/s/{SLUG}/", {"question": WORK, "answer": "urbano"})
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert all(f'data-slug="{slug}"' in html for slug in (BY_AGE, CNIS))
    assert f'data-slug="{BY_TIME}"' not in html

    client.post(f"/s/{SLUG}/respostas/{TYPE}/", {"answer": "por-tempo-de-contribuicao"})
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert f'data-slug="{BY_TIME}"' in html and f'data-slug="{CNIS}"' in html
    assert f'data-slug="{BY_AGE}"' not in html
