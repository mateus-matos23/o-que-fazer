"""Valida o conteúdo real de `content/` (carregado pela fixture `loaded` do conftest raiz)."""

import pytest

from catalog.models import AnswerOption, Procedure, Question, Rule, Situation

pytestmark = pytest.mark.django_db

_PROCEDURES = [
    "consultar-situacao-cpf",
    "regularizar-cpf-suspenso",
    "entregar-dirpf-pendente",
    "atendimento-receita-cpf",
]


def test_journey_counts(loaded: dict[str, int]) -> None:
    # Contagens globais (todas as jornadas) ficam em test_content_desligamento.py.
    slugs = ["cpf-situacao-cadastral"]
    assert AnswerOption.objects.filter(question__slug__in=slugs).count() == 5
    assert Rule.objects.filter(procedure__slug__in=_PROCEDURES).count() == 3
    assert Procedure.objects.filter(slug__in=_PROCEDURES).count() == 4


def test_situation_candidates(loaded: dict[str, int]) -> None:
    situation = Situation.objects.get(slug="cpf-irregular")
    # O esclarecimento não é candidato: entra no plano só pelo "não sei" (clarifies).
    assert set(situation.candidates.values_list("slug", flat=True)) == {
        "regularizar-cpf-suspenso",
        "entregar-dirpf-pendente",
        "atendimento-receita-cpf",
    }


def test_clarification_points_to_unknown_question(loaded: dict[str, int]) -> None:
    clarifier = Procedure.objects.get(slug="consultar-situacao-cpf")
    assert clarifier.clarifies == Question.objects.get(slug="cpf-situacao-cadastral")
    assert clarifier.clarifies.allows_unknown
