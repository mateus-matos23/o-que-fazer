"""Valida o conteúdo real da jornada "transferência de veículo" (fixture `loaded` do conftest)."""

import pytest

from catalog.models import Dependency, Procedure, ProcedureDetail, Question, Situation

pytestmark = pytest.mark.django_db

SITUATION = "transferencia-de-veiculo"


def test_situation_candidates(loaded: dict[str, int]) -> None:
    situation = Situation.objects.get(slug=SITUATION)
    assert set(situation.candidates.values_list("slug", flat=True)) == {
        "consultar-restricoes-veiculo",
        "vistoria-veicular-ecv",
        "transferencia-digital-veiculo",
        "transferencia-balcao-veiculo",
    }


def test_only_counter_cases_accept_unknown(loaded: dict[str, int]) -> None:
    kinds = {
        q.slug: (q.kind, q.allows_unknown)
        for q in Question.objects.filter(situations__slug=SITUATION)
    }
    assert kinds == {
        "forma-de-transferencia": (Question.Kind.SINGLE, False),
        "casos-de-balcao-veiculo": (Question.Kind.MULTIPLE, True),
    }


def test_dependencies_inspection_mandatory_restrictions_recommended(loaded: dict[str, int]) -> None:
    dependencies = Dependency.objects.filter(after__situations__slug=SITUATION)
    assert {(d.before.slug, d.after.slug, d.kind) for d in dependencies} == {
        ("vistoria-veicular-ecv", "transferencia-digital-veiculo", "MANDATORY"),
        ("consultar-restricoes-veiculo", "transferencia-digital-veiculo", "RECOMMENDED"),
        ("consultar-restricoes-veiculo", "transferencia-balcao-veiculo", "RECOMMENDED"),
    }


def test_restrictions_lookup_is_free(loaded: dict[str, int]) -> None:
    cost = ProcedureDetail.objects.get(procedure__slug="consultar-restricoes-veiculo", kind="COST")
    assert cost.text == "Gratuito para o cidadão."
    assert cost.excerpt == "Este serviço é gratuito para o cidadão."


def test_detran_procedures_have_no_documented_cost(loaded: dict[str, int]) -> None:
    procedures = Procedure.objects.filter(situations__slug=SITUATION, agency__slug="detran-ma")
    assert procedures.count() == 3
    assert not any(p.details.exists() for p in procedures)  # taxa não consta da página (RN11)
    assert all(p.jurisdiction == "MARANHAO" for p in procedures)
