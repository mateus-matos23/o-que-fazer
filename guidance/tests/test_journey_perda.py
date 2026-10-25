"""Motor sobre o conteúdo real da jornada "perda de documentos"."""

import pytest
from django.http import HttpResponse
from django.test import Client

from guidance.engine.model import Catalog, Facts
from guidance.engine.plan import Plan, build_plan
from guidance.repository import load_catalog

pytestmark = pytest.mark.django_db

SLUG = "perda-de-documentos"
QUESTION = "documentos-perdidos"
CPF = "segunda-via-cpf"
BO = "registrar-ocorrencia-extravio"
CIN = "segunda-via-cin"
CNH = "segunda-via-cnh"


def _facts(*options: str) -> Facts:
    return {QUESTION: frozenset(options)}


def _slugs(plan: Plan) -> set[str]:
    return {s.procedure.slug for s in plan.steps}


@pytest.fixture
def catalog(loaded: dict[str, int]) -> Catalog:
    return load_catalog(SLUG)


CASES = [
    (("cpf",), {CPF, BO}, ()),
    (("cnh",), {BO, CNH}, ()),
    (("cin",), {BO, CIN}, ()),
    (("titulo-de-eleitor",), {BO}, ((QUESTION, "titulo-de-eleitor"),)),
    (
        ("cpf", "cin", "cnh", "titulo-de-eleitor"),
        {CPF, BO, CIN, CNH},
        ((QUESTION, "titulo-de-eleitor"),),
    ),
    ((), {BO}, ()),
]


@pytest.mark.parametrize(("chosen", "in_plan", "uncovered"), CASES)
def test_plan_table(
    catalog: Catalog,
    chosen: tuple[str, ...],
    in_plan: set[str],
    uncovered: tuple[tuple[str, str], ...],
) -> None:
    plan = build_plan(catalog, _facts(*chosen))
    assert _slugs(plan) == in_plan
    assert plan.uncovered == uncovered
    assert not plan.undetermined


def test_police_report_comes_before_cnh(catalog: Catalog) -> None:
    layers = {s.procedure.slug: s.layer for s in build_plan(catalog, _facts("cnh", "cin")).steps}
    assert layers[BO] < layers[CNH]
    assert layers[CIN] == layers[BO]  # sem dependência documentada para a CIN


def test_changing_answer_recomputes(catalog: Catalog) -> None:
    assert CPF in _slugs(build_plan(catalog, _facts("cpf")))
    assert CPF not in _slugs(build_plan(catalog, _facts("cnh")))
    assert CPF in _slugs(build_plan(catalog, _facts("cnh", "cpf")))


def test_every_cited_step_has_sources(catalog: Catalog) -> None:
    for step in build_plan(catalog, _facts("cpf")).steps:
        assert step.procedure.citation.excerpt
        assert all(r.citation.excerpt for r in step.procedure.requirements)


def test_http_flow_shows_coverage_warning(loaded: dict[str, int], client: Client) -> None:
    answer = ["cpf", "cnh", "titulo-de-eleitor"]
    response = client.post(f"/s/{SLUG}/", {"question": QUESTION, "answer": answer})
    assert isinstance(response, HttpResponse) and response.status_code == 303
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert all(f'data-slug="{slug}"' in html for slug in (CPF, BO, CNH))
    assert "Limite de cobertura" in html
    assert "Título de eleitor" in html
