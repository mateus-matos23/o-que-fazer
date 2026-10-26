"""Motor sobre o conteúdo real da jornada "perda de documentos"."""

import pytest
from django.http import HttpResponse
from django.test import Client

from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Tri, Unknown
from guidance.engine.plan import Plan, PlanStep, build_plan
from guidance.engine.questions import next_question
from guidance.repository import load_catalog

pytestmark = pytest.mark.django_db

SLUG = "perda-de-documentos"
QUESTION = "documentos-perdidos"
IR = "declarou-imposto-de-renda"
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
    client.post(f"/s/{SLUG}/", {"question": IR, "answer": "sim"})
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert all(f'data-slug="{slug}"' in html for slug in (CPF, BO, CNH))
    assert "Limite de cobertura" in html
    assert "Título de eleitor" in html


def _cpf_channels(catalog: Catalog, ir: str | Unknown | None) -> list[tuple[str, Tri]]:
    facts: dict[str, frozenset[str] | Unknown] = {QUESTION: frozenset({"cpf"})}
    if ir is not None:
        facts[IR] = ir if isinstance(ir, Unknown) else frozenset({ir})
    step = next(s for s in build_plan(catalog, facts).steps if s.procedure.slug == CPF)
    return [(c.description, tri) for c, tri in step.channels]


@pytest.mark.parametrize(
    ("ir", "without_govbr"),
    [("sim", None), ("nao", Tri.APPLICABLE), (Unknown.UNKNOWN, Tri.UNDETERMINED)],
)
def test_channel_without_govbr_follows_income_tax_answer(
    catalog: Catalog, ir: str | Unknown, without_govbr: Tri | None
) -> None:
    channels = _cpf_channels(catalog, ir)
    found = [tri for description, tri in channels if "sem gov.br" in description]
    assert found == ([] if without_govbr is None else [without_govbr])
    assert any(
        tri is Tri.APPLICABLE and "sem gov.br" not in d for d, tri in channels
    )  # gov.br fica


def test_income_tax_question_only_when_cpf_is_applicable(catalog: Catalog) -> None:
    def asked(*chosen: str) -> str | None:
        facts = _facts(*chosen)
        question = next_question(catalog, facts, evaluate(catalog, facts))
        return question.slug if question else None

    assert asked("cpf") == IR
    assert asked("cnh", "cin") is None
    assert asked() is None


def test_changing_income_tax_answer_recomputes_channels(catalog: Catalog) -> None:
    assert not any("sem gov.br" in d for d, _ in _cpf_channels(catalog, "sim"))
    assert any("sem gov.br" in d for d, _ in _cpf_channels(catalog, "nao"))


CLARIFICATION = "consultar-declaracoes-ir"


def _steps_with_ir(catalog: Catalog, ir: str | Unknown | None) -> dict[str, PlanStep]:
    facts: dict[str, frozenset[str] | Unknown] = {QUESTION: frozenset({"cpf"})}
    if ir is not None:
        facts[IR] = ir if isinstance(ir, Unknown) else frozenset({ir})
    return {s.procedure.slug: s for s in build_plan(catalog, facts).steps}


def test_unknown_income_tax_answer_brings_clarification(catalog: Catalog) -> None:
    steps = _steps_with_ir(catalog, Unknown.UNKNOWN)
    clarified = steps[CLARIFICATION].clarifies
    assert clarified is not None and clarified.slug == IR
    assert CPF in steps


@pytest.mark.parametrize("ir", ["sim", "nao", None])
def test_known_or_unasked_income_tax_has_no_clarification(catalog: Catalog, ir: str | None) -> None:
    assert CLARIFICATION not in _steps_with_ir(catalog, ir)


def test_clarification_disappears_when_cpf_is_removed(catalog: Catalog) -> None:
    facts: dict[str, frozenset[str] | Unknown] = {
        QUESTION: frozenset({"cnh"}),
        IR: Unknown.UNKNOWN,
    }
    assert CLARIFICATION not in _slugs(build_plan(catalog, facts))
