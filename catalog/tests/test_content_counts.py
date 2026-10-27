"""Contagens globais do conteúdo real carregado de content/ (uma linha por jornada somada)."""

import pytest

from catalog.loader import validate
from conftest import ROOT

pytestmark = pytest.mark.django_db


def test_global_counts(loaded: dict[str, int]) -> None:
    # CPF irregular + desligamento do trabalho + perda de documentos + transferência de veículo
    # + falecimento na família + aposentadoria.
    assert loaded == {
        "Situation": 6,
        "Question": 12,
        "AnswerOption": 43,
        "Procedure": 25,
        "ProcedureDetail": 25,
        "Requirement": 75,
        "ServiceChannel": 62,
        "Rule": 21,
        "Condition": 28,
        "Dependency": 4,
        "TriageNode": 1,
        "TriageChoice": 6,
    }


def test_real_content_passes_validation_with_triage(loaded: dict[str, int]) -> None:
    content, _ = validate(ROOT / "content")
    assert [n.slug for n in content.triage] == ["inicio"]
