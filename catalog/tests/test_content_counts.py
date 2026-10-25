"""Contagens globais do conteúdo real carregado de content/ (uma linha por jornada somada)."""

import pytest

pytestmark = pytest.mark.django_db


def test_global_counts(loaded: dict[str, int]) -> None:
    # CPF irregular + desligamento do trabalho + perda de documentos.
    assert loaded == {
        "Situation": 3,
        "Question": 4,
        "AnswerOption": 17,
        "Procedure": 11,
        "ProcedureDetail": 8,
        "Requirement": 27,
        "ServiceChannel": 26,
        "Rule": 7,
        "Condition": 9,
        "Dependency": 0,
    }
