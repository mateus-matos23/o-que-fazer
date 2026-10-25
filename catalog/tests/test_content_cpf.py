"""Valida o conteúdo real de `content/` (carregado pela fixture `loaded` do conftest raiz)."""

import pytest

from catalog.models import Procedure, Question, Situation

pytestmark = pytest.mark.django_db


def test_counts(loaded: dict[str, int]) -> None:
    assert loaded == {
        "Situation": 1,
        "Question": 1,
        "AnswerOption": 5,
        "Procedure": 4,
        "ProcedureDetail": 2,
        "Requirement": 4,
        "ServiceChannel": 8,
        "Rule": 3,
        "Condition": 3,
        "Dependency": 0,
    }


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
