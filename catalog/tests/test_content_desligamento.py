"""Valida o conteúdo real da jornada "desligamento do trabalho" (fixture `loaded` do conftest)."""

import pytest

from catalog.models import AnswerOption, Procedure, ProcedureDetail, Question, Rule, Situation

pytestmark = pytest.mark.django_db

SITUATION = "desligamento-do-trabalho"


def test_situation_candidates(loaded: dict[str, int]) -> None:
    situation = Situation.objects.get(slug=SITUATION)
    assert set(situation.candidates.values_list("slug", flat=True)) == {
        "seguro-desemprego",
        "seguro-desemprego-domestico",
        "saque-fgts-dispensa",
        "conferir-vinculos-ctps",
        "extrato-vinculos-caged",
    }


def test_questions_allow_unknown(loaded: dict[str, int]) -> None:
    questions = Question.objects.filter(situations__slug=SITUATION)
    assert {q.slug: q.allows_unknown for q in questions} == {
        "forma-de-termino": True,
        "tipo-de-vinculo": True,
        "vezes-seguro-desemprego": True,
    }


def test_out_of_coverage_options(loaded: dict[str, int]) -> None:
    options = AnswerOption.objects.filter(question__slug="forma-de-termino")
    assert {o.slug for o in options} == {
        "sem-justa-causa",
        "pedido-de-demissao",
        "justa-causa",
        "acordo",
        "culpa-reciproca",
        "fim-de-contrato",
    }
    assert {o.slug for o in options if o.out_of_coverage} == {
        "acordo",
        "culpa-reciproca",
        "fim-de-contrato",
    }
    assert not AnswerOption.objects.filter(
        question__slug="tipo-de-vinculo", out_of_coverage=True
    ).exists()


def test_ctps_and_caged_have_no_rules(loaded: dict[str, int]) -> None:
    ruled = set(
        Rule.objects.filter(procedure__isnull=False).values_list("procedure__slug", flat=True)
    )
    assert {"seguro-desemprego", "seguro-desemprego-domestico", "saque-fgts-dispensa"} <= ruled
    assert not ruled & {"conferir-vinculos-ctps", "extrato-vinculos-caged"}


def test_no_clarification_step(loaded: dict[str, int]) -> None:
    assert not Procedure.objects.filter(clarifies__situations__slug=SITUATION).exists()


def test_cost_and_deadline_cite_the_official_pages(loaded: dict[str, int]) -> None:
    details = {
        (d.procedure.slug, d.kind): d.text
        for d in ProcedureDetail.objects.filter(procedure__situations__slug=SITUATION)
    }
    assert details[("seguro-desemprego", "COST")] == "Gratuito para o cidadão."
    assert details[("seguro-desemprego", "DEADLINE")].startswith("Entre 31 e 60 dias corridos")
    assert "não é o prazo para pedir" in details[("seguro-desemprego", "DEADLINE")]
    assert details[("seguro-desemprego-domestico", "COST")] == "Gratuito para o cidadão."
    assert details[("extrato-vinculos-caged", "COST")] == "Gratuito para o cidadão."
    assert details[("conferir-vinculos-ctps", "DEADLINE")] == "Atendimento imediato."
    assert ("saque-fgts-dispensa", "COST") not in details  # a página não declara custo (RN11)
