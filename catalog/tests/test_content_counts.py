"""Contagens globais do conteúdo real carregado de content/ (uma linha por jornada somada)."""

import pytest

from catalog.loader import validate
from conftest import ROOT

pytestmark = pytest.mark.django_db


def test_global_counts(loaded: dict[str, int]) -> None:
    # CPF irregular + desligamento do trabalho + perda de documentos + transferência de veículo
    # + falecimento na família.
    assert loaded == {
        "Situation": 5,
        "Question": 10,
        "AnswerOption": 39,
        "Procedure": 21,
        "ProcedureDetail": 12,
        "Requirement": 55,
        "ServiceChannel": 48,
        "Rule": 19,
        "Condition": 25,
        "Dependency": 4,
        "TriageNode": 5,
        "TriageChoice": 17,
    }


def test_real_content_passes_validation_with_triage(loaded: dict[str, int]) -> None:
    content, _ = validate(ROOT / "content")
    assert {n.slug for n in content.triage} == {
        "inicio",
        "documentos",
        "trabalho",
        "veiculo",
        "familia",
    }
