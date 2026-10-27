"""Valida o conteúdo real da jornada "aposentadoria" (fixture `loaded` do conftest)."""

import pytest

from catalog.models import (
    AnswerOption,
    Dependency,
    Procedure,
    ProcedureDetail,
    Question,
    Requirement,
    Rule,
    Situation,
)

pytestmark = pytest.mark.django_db

SITUATION = "aposentadoria"
BY_AGE = "aposentadoria-por-idade-urbana"
BY_TIME = "aposentadoria-por-tempo-de-contribuicao"
CNIS = "extrato-cnis"
SIMULATOR = "simular-aposentadoria"
TYPE = "tipo-de-aposentadoria"
WORK = "meio-de-trabalho-aposentadoria"


def test_situation_candidates(loaded: dict[str, int]) -> None:
    situation = Situation.objects.get(slug=SITUATION)
    assert set(situation.candidates.values_list("slug", flat=True)) == {BY_AGE, BY_TIME, CNIS}


def test_only_type_accepts_unknown(loaded: dict[str, int]) -> None:
    kinds = {
        q.slug: (q.kind, q.allows_unknown)
        for q in Question.objects.filter(situations__slug=SITUATION)
    }
    assert kinds == {
        TYPE: (Question.Kind.SINGLE, True),
        WORK: (Question.Kind.SINGLE, False),
    }


def test_rural_work_is_out_of_coverage(loaded: dict[str, int]) -> None:
    assert AnswerOption.objects.get(question__slug=WORK, slug="rural").out_of_coverage
    assert not AnswerOption.objects.get(question__slug=WORK, slug="urbano").out_of_coverage


def test_no_dependencies_between_procedures(loaded: dict[str, int]) -> None:
    assert not Dependency.objects.filter(after__situations__slug=SITUATION).exists()  # RN08


def test_extract_applies_to_anyone_without_rule(loaded: dict[str, int]) -> None:
    assert not Rule.objects.filter(procedure__slug=CNIS).exists()


def test_simulator_is_the_only_clarification_for_type(loaded: dict[str, int]) -> None:
    clarifiers = set(Procedure.objects.filter(clarifies__slug=TYPE).values_list("slug", flat=True))
    assert clarifiers == {SIMULATOR}
    assert not Situation.objects.get(slug=SITUATION).candidates.filter(slug=SIMULATOR).exists()


def test_all_procedures_are_inss_federal(loaded: dict[str, int]) -> None:
    procedures = Procedure.objects.filter(situations__slug=SITUATION)
    assert procedures.count() == 3
    assert all(p.agency.slug == "inss" and p.jurisdiction == "FEDERAL" for p in procedures)
    simulator = Procedure.objects.get(slug=SIMULATOR)
    assert simulator.agency.slug == "inss" and simulator.jurisdiction == "FEDERAL"


def test_no_deadline_or_cost_from_waiting_times(loaded: dict[str, int]) -> None:
    # Tempos de espera e de etapa das páginas não são prazo de resposta (evidência).
    assert not ProcedureDetail.objects.filter(
        procedure__slug__in=[BY_AGE, BY_TIME, CNIS, SIMULATOR]
    ).exists()  # RN11: sem custo ou prazo documentado nas amostras


@pytest.mark.parametrize(
    ("procedure", "count"), [(BY_AGE, 6), (BY_TIME, 6), (CNIS, 6), (SIMULATOR, 2)]
)
def test_requirements_follow_each_documentation_block(
    loaded: dict[str, int], procedure: str, count: int
) -> None:
    requirements = Requirement.objects.filter(procedure__slug=procedure)
    assert requirements.count() == count
    assert requirements.filter(description__contains="CPF").exists()
