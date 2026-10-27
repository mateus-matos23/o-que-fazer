"""Motor sobre o conteúdo real da jornada "falecimento na família"."""

import pytest
from django.test import Client

from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Unknown
from guidance.engine.plan import build_plan
from guidance.engine.questions import next_question
from guidance.repository import load_catalog

pytestmark = pytest.mark.django_db

SLUG = "falecimento-na-familia"
RELATION = "relacao-com-falecido"
WORK = "meio-de-trabalho-falecido"
URBAN = "pensao-por-morte-urbana"
RURAL = "pensao-por-morte-rural"
CERTIFICATE = "certidao-inexistencia-dependentes"


def _facts(relation: str, work: str | Unknown | None = "urbano") -> Facts:
    facts: dict[str, frozenset[str] | Unknown] = {RELATION: frozenset({relation})}
    if work is not None:
        facts[WORK] = work if isinstance(work, Unknown) else frozenset({work})
    return facts


@pytest.fixture
def catalog(loaded: dict[str, int]) -> Catalog:
    return load_catalog(SLUG)


@pytest.mark.parametrize(
    ("relation", "work", "in_plan"),
    [
        ("conjuge", "urbano", {URBAN, CERTIFICATE}),
        ("filho", "rural", {RURAL, CERTIFICATE}),
        ("pais", "urbano", {URBAN, CERTIFICATE}),
        ("irmao", "rural", {RURAL, CERTIFICATE}),
        ("outra", None, {CERTIFICATE}),
    ],
)
def test_plan_table(catalog: Catalog, relation: str, work: str | None, in_plan: set[str]) -> None:
    plan = build_plan(catalog, _facts(relation, work))
    assert {s.procedure.slug for s in plan.steps} == in_plan
    assert not plan.undetermined and not plan.uncovered


def test_unknown_work_keeps_both_pensions_undetermined(catalog: Catalog) -> None:
    statuses = {
        slug: e.status.name
        for slug, e in evaluate(catalog, _facts("conjuge", Unknown.UNKNOWN)).items()
    }
    assert statuses[URBAN] == statuses[RURAL] == "UNDETERMINED"  # "não sei" ≠ negativo (RN03)
    assert statuses[CERTIFICATE] == "APPLICABLE"


def test_changing_work_recomputes_plan(catalog: Catalog) -> None:
    facts = _facts("conjuge", "urbano")
    assert {s.procedure.slug for s in build_plan(catalog, facts).steps} == {URBAN, CERTIFICATE}
    facts = {**facts, WORK: frozenset({"rural"})}  # resposta editada de urbano para rural
    assert {s.procedure.slug for s in build_plan(catalog, facts).steps} == {RURAL, CERTIFICATE}


def test_work_question_only_matters_for_classes_of_dependents(catalog: Catalog) -> None:
    def asked(facts: Facts) -> str | None:
        question = next_question(catalog, facts, evaluate(catalog, facts))
        return question.slug if question else None

    assert asked({}) == RELATION
    assert asked(_facts("conjuge", None)) == WORK
    assert asked(_facts("outra", None)) is None  # "outra" afasta as duas pensões sem o meio


def test_http_flow_to_urban_plan_then_rural(loaded: dict[str, int], client: Client) -> None:
    client.post(f"/s/{SLUG}/", {"question": RELATION, "answer": "conjuge"})
    client.post(f"/s/{SLUG}/", {"question": WORK, "answer": "urbano"})
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert all(f'data-slug="{slug}"' in html for slug in (URBAN, CERTIFICATE))
    assert f'data-slug="{RURAL}"' not in html

    client.post(f"/s/{SLUG}/respostas/{WORK}/", {"answer": "rural"})
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert all(f'data-slug="{slug}"' in html for slug in (RURAL, CERTIFICATE))
    assert f'data-slug="{URBAN}"' not in html
