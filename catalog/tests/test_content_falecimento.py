"""Valida o conteúdo real da jornada "falecimento na família" (fixture `loaded` do conftest)."""

import pytest

from catalog.models import Dependency, Procedure, Question, Rule, Situation

pytestmark = pytest.mark.django_db

SITUATION = "falecimento-na-familia"
CERTIFICATE = "certidao-inexistencia-dependentes"


def test_situation_candidates(loaded: dict[str, int]) -> None:
    situation = Situation.objects.get(slug=SITUATION)
    assert set(situation.candidates.values_list("slug", flat=True)) == {
        "pensao-por-morte-urbana",
        "pensao-por-morte-rural",
        CERTIFICATE,
    }


def test_only_work_environment_accepts_unknown(loaded: dict[str, int]) -> None:
    kinds = {
        q.slug: (q.kind, q.allows_unknown)
        for q in Question.objects.filter(situations__slug=SITUATION)
    }
    assert kinds == {
        "relacao-com-falecido": (Question.Kind.SINGLE, False),
        "meio-de-trabalho-falecido": (Question.Kind.SINGLE, True),
    }


def test_no_dependencies_between_procedures(loaded: dict[str, int]) -> None:
    assert not Dependency.objects.filter(after__situations__slug=SITUATION).exists()  # RN08


def test_certificate_applies_to_anyone_without_rule(loaded: dict[str, int]) -> None:
    assert not Rule.objects.filter(procedure__slug=CERTIFICATE).exists()


def test_all_procedures_are_inss_federal(loaded: dict[str, int]) -> None:
    procedures = Procedure.objects.filter(situations__slug=SITUATION)
    assert procedures.count() == 3
    assert all(p.agency.slug == "inss" and p.jurisdiction == "FEDERAL" for p in procedures)
    assert not any(p.details.filter(kind="COST").exists() for p in procedures)  # RN11
