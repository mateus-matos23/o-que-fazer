"""Contagens globais do conteúdo real carregado de content/ (uma linha por jornada somada)."""

import pytest

from catalog.loader import validate
from conftest import ROOT

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
        "TriageNode": 3,
        "TriageChoice": 12,
    }


def test_real_content_passes_validation_with_triage(loaded: dict[str, int]) -> None:
    content, _ = validate(ROOT / "content")
    assert {n.slug for n in content.triage} == {"inicio", "documentos", "trabalho"}
