"""Motor sobre o conteúdo real da jornada "desligamento do trabalho"."""

import pytest
from django.http import HttpResponse
from django.test import Client

from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Tri, Unknown
from guidance.engine.plan import Plan, build_plan
from guidance.engine.questions import next_question
from guidance.forms import UNKNOWN_VALUE
from guidance.repository import load_catalog

pytestmark = pytest.mark.django_db

SLUG = "desligamento-do-trabalho"
FORMA = "forma-de-termino"
VINCULO = "tipo-de-vinculo"
VEZES = "vezes-seguro-desemprego"
SEGURO = "seguro-desemprego"
DOMESTICO = "seguro-desemprego-domestico"
FGTS = "saque-fgts-dispensa"
CTPS = "conferir-vinculos-ctps"
CAGED = "extrato-vinculos-caged"
UNKNOWN = Unknown.UNKNOWN


def _facts(
    forma: str | Unknown | None,
    vinculo: str | Unknown | None = None,
    vezes: str | Unknown | None = None,
) -> Facts:
    raw = {FORMA: forma, VINCULO: vinculo, VEZES: vezes}
    return {q: v if isinstance(v, Unknown) else frozenset({v}) for q, v in raw.items() if v}


def _slugs(plan: Plan) -> set[str]:
    return {s.procedure.slug for s in plan.steps}


@pytest.fixture
def catalog(loaded: dict[str, int]) -> Catalog:
    return load_catalog(SLUG)


# (forma, vínculo, no plano, indeterminados fora do plano, próxima pergunta, fora de cobertura)
CASES = [
    ("sem-justa-causa", "empregado", {SEGURO, FGTS, CTPS, CAGED}, set(), VEZES, ()),
    ("sem-justa-causa", "domestico", {DOMESTICO, FGTS, CTPS, CAGED}, set(), None, ()),
    ("pedido-de-demissao", None, {CTPS, CAGED}, set(), None, ()),
    ("justa-causa", None, {CTPS, CAGED}, set(), None, ()),
    ("acordo", None, {CTPS, CAGED}, set(), None, ((FORMA, "acordo"),)),
    ("culpa-reciproca", None, {CTPS, CAGED}, set(), None, ((FORMA, "culpa-reciproca"),)),
    ("fim-de-contrato", None, {CTPS, CAGED}, set(), None, ((FORMA, "fim-de-contrato"),)),
    # "Não sei" mantém tudo indeterminado (RN03): nunca vira não aplicável.
    (UNKNOWN, None, {CTPS, CAGED}, {SEGURO, DOMESTICO, FGTS}, VINCULO, ()),
    ("sem-justa-causa", UNKNOWN, {FGTS, CTPS, CAGED}, {SEGURO, DOMESTICO}, None, ()),
]


@pytest.mark.parametrize(
    ("forma", "vinculo", "in_plan", "undetermined", "asks", "uncovered"), CASES
)
def test_plan_table(
    catalog: Catalog,
    forma: str | Unknown,
    vinculo: str | Unknown | None,
    in_plan: set[str],
    undetermined: set[str],
    asks: str | None,
    uncovered: tuple[tuple[str, str], ...],
) -> None:
    facts = _facts(forma, vinculo)
    plan = build_plan(catalog, facts)
    assert _slugs(plan) == in_plan
    assert set(plan.undetermined) == undetermined
    assert plan.uncovered == uncovered
    question = next_question(catalog, facts, evaluate(catalog, facts))
    assert (question.slug if question else None) == asks


def test_unknown_form_is_never_not_applicable(catalog: Catalog) -> None:
    evaluations = evaluate(catalog, _facts(UNKNOWN, UNKNOWN))
    for slug in (SEGURO, DOMESTICO, FGTS):
        assert evaluations[slug].status is Tri.UNDETERMINED


def test_unknown_form_asks_form_first(catalog: Catalog) -> None:
    question = next_question(catalog, {}, evaluate(catalog, {}))
    assert question is not None and question.slug == FORMA


def test_changing_answer_recomputes(catalog: Catalog) -> None:
    assert SEGURO in _slugs(build_plan(catalog, _facts("sem-justa-causa", "empregado")))
    assert SEGURO not in _slugs(build_plan(catalog, _facts("pedido-de-demissao", "empregado")))
    assert _slugs(build_plan(catalog, _facts("sem-justa-causa", "domestico"))) >= {DOMESTICO}


def test_every_cited_step_has_sources(catalog: Catalog) -> None:
    for step in build_plan(catalog, _facts("sem-justa-causa", "empregado")).steps:
        assert step.procedure.citation.excerpt
        assert all(r.citation.excerpt for r in step.procedure.requirements)


def _post(client: Client, question: str, value: str) -> None:
    response = client.post(f"/s/{SLUG}/", {"question": question, "answer": value})
    assert isinstance(response, HttpResponse) and response.status_code == 303


def test_http_flow_to_plan(loaded: dict[str, int], client: Client) -> None:
    html = client.get(f"/s/{SLUG}/").content.decode()
    assert "Como você saiu do emprego?" in html
    _post(client, FORMA, "sem-justa-causa")
    assert "Que tipo de trabalho era?" in client.get(f"/s/{SLUG}/").content.decode()
    _post(client, VINCULO, "domestico")
    response = client.get(f"/s/{SLUG}/", follow=True)
    assert response.redirect_chain[-1] == (f"/s/{SLUG}/atendimento/", 302)
    response = client.post(f"/s/{SLUG}/atendimento/", {"preference": "tanto-faz"}, follow=True)
    assert response.redirect_chain[-1] == (f"/s/{SLUG}/plano/", 303)
    plan = response.content.decode()
    for slug in (DOMESTICO, FGTS, CTPS, CAGED):
        assert f'data-slug="{slug}"' in plan
    assert f'data-slug="{SEGURO}"' not in plan


def test_http_unknown_vinculo_keeps_seguros_out_of_plan(
    loaded: dict[str, int], client: Client
) -> None:
    _post(client, FORMA, "sem-justa-causa")
    _post(client, VINCULO, UNKNOWN_VALUE)
    plan = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert f'data-slug="{FGTS}"' in plan
    assert f'data-slug="{SEGURO}"' not in plan


PRIMEIRA = "Primeira solicitação"
SEGUNDA = "Segunda solicitação"
DEMAIS = "Demais solicitações"


def _carencia(catalog: Catalog, vezes: str | Unknown | None) -> dict[str, Tri]:
    step = next(
        s
        for s in build_plan(catalog, _facts("sem-justa-causa", "empregado", vezes)).steps
        if s.procedure.slug == SEGURO
    )
    return {
        label: tri
        for r, tri in step.requirements
        for label in (PRIMEIRA, SEGUNDA, DEMAIS)
        if r.description.startswith(label)
    }


@pytest.mark.parametrize(
    ("vezes", "shown"),
    [
        ("primeira", {PRIMEIRA: Tri.APPLICABLE}),
        ("segunda", {SEGUNDA: Tri.APPLICABLE}),
        ("terceira-ou-mais", {DEMAIS: Tri.APPLICABLE}),
        (UNKNOWN, dict.fromkeys((PRIMEIRA, SEGUNDA, DEMAIS), Tri.UNDETERMINED)),
        (None, dict.fromkeys((PRIMEIRA, SEGUNDA, DEMAIS), Tri.UNDETERMINED)),
    ],
)
def test_carencia_requirement_follows_number_of_requests(
    catalog: Catalog, vezes: str | Unknown | None, shown: dict[str, Tri]
) -> None:
    assert _carencia(catalog, vezes) == shown


def test_requests_question_only_when_seguro_is_applicable(catalog: Catalog) -> None:
    for facts in (
        _facts("pedido-de-demissao", "empregado"),
        _facts("sem-justa-causa", "domestico"),
        _facts("sem-justa-causa", UNKNOWN),
        _facts(UNKNOWN, "empregado"),
    ):
        question = next_question(catalog, facts, evaluate(catalog, facts))
        assert question is None or question.slug != VEZES


def test_requests_question_comes_after_form_and_vinculo(catalog: Catalog) -> None:
    order = []
    facts: Facts = {}
    for answer in ("sem-justa-causa", "empregado"):
        question = next_question(catalog, facts, evaluate(catalog, facts))
        assert question is not None
        order.append(question.slug)
        facts = {**facts, question.slug: frozenset({answer})}
    question = next_question(catalog, facts, evaluate(catalog, facts))
    assert order == [FORMA, VINCULO]
    assert question is not None and question.slug == VEZES


def test_changing_requests_answer_recomputes_requirements(catalog: Catalog) -> None:
    assert _carencia(catalog, "primeira") == {PRIMEIRA: Tri.APPLICABLE}
    assert _carencia(catalog, "segunda") == {SEGUNDA: Tri.APPLICABLE}
