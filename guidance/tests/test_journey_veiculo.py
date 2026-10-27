"""Motor sobre o conteúdo real da jornada "transferência de veículo"."""

import pytest
from django.test import Client

from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, Facts, Unknown
from guidance.engine.plan import build_plan
from guidance.engine.questions import next_question
from guidance.repository import load_catalog

pytestmark = pytest.mark.django_db

SLUG = "transferencia-de-veiculo"
FORM = "forma-de-transferencia"
CASES_Q = "casos-de-balcao-veiculo"
RESTRICTIONS = "consultar-restricoes-veiculo"
INSPECTION = "vistoria-veicular-ecv"
DIGITAL = "transferencia-digital-veiculo"
COUNTER = "transferencia-balcao-veiculo"


def _facts(form: str, cases: tuple[str, ...] | Unknown | None = ()) -> Facts:
    facts: dict[str, frozenset[str] | Unknown] = {FORM: frozenset({form})}
    if cases is not None:
        facts[CASES_Q] = cases if isinstance(cases, Unknown) else frozenset(cases)
    return facts


@pytest.fixture
def catalog(loaded: dict[str, int]) -> Catalog:
    return load_catalog(SLUG)


@pytest.mark.parametrize(
    ("form", "cases", "in_plan"),
    [
        ("compra-e-venda", (), {RESTRICTIONS, INSPECTION, DIGITAL}),
        ("compra-e-venda", ("crv-nao-digital",), {RESTRICTIONS, COUNTER}),
        ("compra-e-venda", ("pessoa-juridica", "mudanca-de-estado"), {RESTRICTIONS, COUNTER}),
        ("heranca", (), {RESTRICTIONS, COUNTER}),
        ("doacao", None, {RESTRICTIONS, COUNTER}),
        ("leilao", ("categoria-especial",), {RESTRICTIONS, COUNTER}),
    ],
)
def test_plan_table(
    catalog: Catalog, form: str, cases: tuple[str, ...] | None, in_plan: set[str]
) -> None:
    plan = build_plan(catalog, _facts(form, cases))
    assert {s.procedure.slug for s in plan.steps} == in_plan
    assert not plan.undetermined and not plan.uncovered


def test_unknown_cases_keep_both_transfers_undetermined(catalog: Catalog) -> None:
    facts = _facts("compra-e-venda", Unknown.UNKNOWN)
    statuses = {slug: e.status.name for slug, e in evaluate(catalog, facts).items()}
    assert statuses[DIGITAL] == statuses[COUNTER] == "UNDETERMINED"  # "não sei" ≠ negativo (RN03)
    assert statuses[RESTRICTIONS] == "APPLICABLE"


def test_inspection_comes_before_digital_transfer(catalog: Catalog) -> None:
    layers = {
        s.procedure.slug: s.layer for s in build_plan(catalog, _facts("compra-e-venda")).steps
    }
    assert layers[INSPECTION] < layers[DIGITAL]


def test_cases_question_only_matters_for_purchase(catalog: Catalog) -> None:
    def asked(facts: Facts) -> str | None:
        question = next_question(catalog, facts, evaluate(catalog, facts))
        return question.slug if question else None

    assert asked({}) == FORM
    assert asked(_facts("compra-e-venda", None)) == CASES_Q
    assert asked(_facts("heranca", None)) is None  # o balcão já vale; a pergunta não muda o plano


def test_http_flow_to_digital_plan(loaded: dict[str, int], client: Client) -> None:
    client.post(f"/s/{SLUG}/", {"question": FORM, "answer": "compra-e-venda"})
    client.post(f"/s/{SLUG}/", {"question": CASES_Q})
    html = client.get(f"/s/{SLUG}/plano/").content.decode()
    assert all(f'data-slug="{slug}"' in html for slug in (RESTRICTIONS, INSPECTION, DIGITAL))
    assert f'data-slug="{COUNTER}"' not in html
