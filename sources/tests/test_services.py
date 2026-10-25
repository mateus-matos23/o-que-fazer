from datetime import date
from unittest import mock

import pytest
from django.core.management import CommandError, call_command

from sources.adapters import Collected, CollectError
from sources.models import Agency, Jurisdiction, Source, SourceImport, SourceSnapshot
from sources.services import import_source

pytestmark = pytest.mark.django_db


@pytest.fixture
def source() -> Source:
    agency = Agency.objects.create(slug="mte", name="MTE", jurisdiction=Jurisdiction.FEDERAL)
    return Source.objects.create(
        slug="pagina-seguro-desemprego",
        agency=agency,
        url="https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego",
        format=Source.Format.HTML,
        jurisdiction=Jurisdiction.FEDERAL,
    )


def _collected(sha: str = "a" * 64) -> Collected:
    return Collected(200, "<html/>", None, date(2026, 9, 25), sha)


def test_successful_import_creates_snapshot(source: Source) -> None:
    with mock.patch("sources.services.collect", return_value=_collected()):
        result = import_source(source)
    assert result.outcome == SourceImport.Outcome.OK
    assert result.snapshot is not None
    assert result.snapshot.declared_updated_at == date(2026, 9, 25)


def test_same_hash_reuses_snapshot(source: Source) -> None:
    with mock.patch("sources.services.collect", return_value=_collected()):
        first = import_source(source)
        second = import_source(source)
    assert first.snapshot_id == second.snapshot_id
    assert SourceSnapshot.objects.count() == 1
    assert SourceImport.objects.count() == 2


def test_changed_content_creates_new_snapshot(source: Source) -> None:
    with mock.patch("sources.services.collect", side_effect=[_collected(), _collected("b" * 64)]):
        import_source(source)
        import_source(source)
    assert SourceSnapshot.objects.count() == 2


def test_failure_is_recorded_without_snapshot(source: Source) -> None:
    error = CollectError("HTTP 404", http_status=404)
    with mock.patch("sources.services.collect", side_effect=error):
        result = import_source(source)
    assert result.outcome == SourceImport.Outcome.FAILED
    assert result.http_status == 404
    assert result.error == "HTTP 404"
    assert SourceSnapshot.objects.count() == 0


def test_command_fails_when_any_source_fails(source: Source) -> None:
    with (
        mock.patch("sources.services.collect", side_effect=CollectError("timeout")),
        pytest.raises(CommandError, match="1 fonte"),
    ):
        call_command("fetch_sources")
    assert SourceImport.objects.filter(outcome="FAILED").count() == 1


def test_command_rejects_unknown_slug(source: Source) -> None:
    with pytest.raises(CommandError, match="inexistentes: nao-existe"):
        call_command("fetch_sources", "--source", "nao-existe")
