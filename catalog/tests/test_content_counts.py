"""Contagens globais do conteúdo real carregado de content/ (uma linha por jornada somada)."""

import pytest

from catalog.loader import validate
from conftest import ROOT

pytestmark = pytest.mark.django_db


def test_global_counts(loaded: dict[str, int]) -> None:
    # CPF irregular + desligamento do trabalho + perda de documentos + transferência de veículo.
    assert loaded == {
        "Situation": 4,
        "Question": 8,
        "AnswerOption": 32,
        "Procedure": 18,
        "ProcedureDetail": 12,
        "Requirement": 43,
        "ServiceChannel": 37,
        "Rule": 17,
        "Condition": 21,
        "Dependency": 4,
        "TriageNode": 4,
        "TriageChoice": 14,
    }


def test_real_content_passes_validation_with_triage(loaded: dict[str, int]) -> None:
    content, _ = validate(ROOT / "content")
    assert {n.slug for n in content.triage} == {"inicio", "documentos", "trabalho", "veiculo"}
