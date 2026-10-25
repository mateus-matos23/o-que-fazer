"""Contagens globais do conteúdo real carregado de content/ (uma linha por jornada somada)."""

import pytest

pytestmark = pytest.mark.django_db


def test_global_counts(loaded: dict[str, int]) -> None:
    # CPF irregular + desligamento do trabalho + perda de documentos.
    assert loaded == {
        "Situation": 3,
        "Question": 4,
        "AnswerOption": 17,
        "Procedure": 13,
        "ProcedureDetail": 9,
        "Requirement": 33,
        "ServiceChannel": 30,
        "Rule": 9,
        "Condition": 11,
        "Dependency": 1,
    }
