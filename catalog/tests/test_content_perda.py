"""Valida o conteúdo real da jornada "perda de documentos" (fixture `loaded` do conftest)."""

import pytest

from catalog.models import AnswerOption, Dependency, Procedure, Question, Rule, Situation

pytestmark = pytest.mark.django_db

SITUATION = "perda-de-documentos"
QUESTION = "documentos-perdidos"


def test_situation_candidates(loaded: dict[str, int]) -> None:
    situation = Situation.objects.get(slug=SITUATION)
    assert set(situation.candidates.values_list("slug", flat=True)) == {
        "segunda-via-cpf",
        "registrar-ocorrencia-extravio",
        "segunda-via-cin",
        "segunda-via-cnh",
    }


def test_question_is_multiple_without_unknown(loaded: dict[str, int]) -> None:
    question = Question.objects.get(slug=QUESTION)
    assert question.kind == Question.Kind.MULTIPLE
    assert not question.allows_unknown
    assert list(question.situations.values_list("slug", flat=True)) == [SITUATION]


def test_out_of_coverage_options(loaded: dict[str, int]) -> None:
    options = AnswerOption.objects.filter(question__slug=QUESTION)
    assert {o.slug for o in options} == {"cpf", "cin", "cnh", "titulo-de-eleitor"}
    assert {o.slug for o in options if o.out_of_coverage} == {"titulo-de-eleitor"}


def test_each_second_copy_has_rule_and_police_has_none(loaded: dict[str, int]) -> None:
    rules = Rule.objects.filter(procedure__situations__slug=SITUATION)
    assert {(r.slug, r.procedure.slug) for r in rules if r.procedure} == {
        ("regra-cpf-perdido", "segunda-via-cpf"),
        ("regra-cin-perdida", "segunda-via-cin"),
        ("regra-cnh-perdida", "segunda-via-cnh"),
    }


def test_police_procedure_is_maranhao_and_cost_is_not_informed(loaded: dict[str, int]) -> None:
    procedure = Procedure.objects.get(slug="registrar-ocorrencia-extravio")
    assert procedure.agency.slug == "policia-civil-ma"
    assert procedure.jurisdiction == "MARANHAO"
    assert not procedure.details.exists()  # custo e prazo: "não informado" (RN11)
    assert procedure.requirements.count() == 1  # e-mail para receber o boletim
    assert [c.url for c in procedure.channels.all()] == [
        "https://www.policiacivil.ma.gov.br/delegacia-online/"
    ]


def test_cpf_procedure_reuses_receita_and_states_channel_condition(loaded: dict[str, int]) -> None:
    procedure = Procedure.objects.get(slug="segunda-via-cpf")
    assert procedure.agency.slug == "receita-federal"
    assert {d.kind for d in procedure.details.all()} == {"COST", "DEADLINE"}
    # A condição do canal "sem gov.br" consta do texto da página e vai na descrição do canal.
    without_govbr = procedure.channels.get(description__contains="sem gov.br")
    assert "nos últimos dois anos" in without_govbr.description
    assert "gov.br" not in " ".join(r.description for r in procedure.requirements.all())


def test_cnh_procedure_is_detran_with_documented_cost(loaded: dict[str, int]) -> None:
    procedure = Procedure.objects.get(slug="segunda-via-cnh")
    assert procedure.agency.slug == "detran-ma"
    assert procedure.jurisdiction == "MARANHAO"
    cost = procedure.details.get()
    assert cost.kind == "COST" and "R$ 90,00" in cost.text


def test_cin_procedure_cost_is_not_informed(loaded: dict[str, int]) -> None:
    procedure = Procedure.objects.get(slug="segunda-via-cin")
    assert procedure.agency.slug == "ident-ma"
    assert not procedure.details.exists()  # custo da 2ª via não consta das fontes lidas (RN11)
    assert any("Certidão" in r.description for r in procedure.requirements.all())


def test_only_dependency_is_police_report_before_cnh(loaded: dict[str, int]) -> None:
    dependencies = Dependency.objects.filter(after__situations__slug=SITUATION)
    assert [(d.before.slug, d.after.slug, d.kind) for d in dependencies] == [
        ("registrar-ocorrencia-extravio", "segunda-via-cnh", "MANDATORY")
    ]


def test_only_income_tax_clarification_step(loaded: dict[str, int]) -> None:
    steps = Procedure.objects.filter(clarifies__situations__slug=SITUATION)
    assert list(steps.values_list("slug", "clarifies__slug")) == [
        ("consultar-declaracoes-ir", "declarou-imposto-de-renda")
    ]
