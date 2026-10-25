import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from sources.models import Agency, Jurisdiction, Source, SourceImport, SourceSnapshot

pytestmark = pytest.mark.django_db


@pytest.fixture
def source() -> Source:
    agency = Agency.objects.create(
        slug="receita-federal", name="Receita Federal", jurisdiction=Jurisdiction.FEDERAL
    )
    return Source.objects.create(
        slug="api-10416",
        agency=agency,
        url="https://servicos.gov.br/api/v1/servicos/10416",
        format=Source.Format.GOVBR_API,
        jurisdiction=Jurisdiction.FEDERAL,
    )


@pytest.fixture
def snapshot(source: Source) -> SourceSnapshot:
    return SourceSnapshot.objects.create(source=source, content_sha256="a" * 64, raw_text="{}")


def test_successful_import_requires_snapshot(source: Source) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        SourceImport.objects.create(
            source=source, fetched_at=timezone.now(), http_status=200, outcome="OK"
        )


def test_failed_import_requires_error_and_no_snapshot(
    source: Source, snapshot: SourceSnapshot
) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        SourceImport.objects.create(source=source, fetched_at=timezone.now(), outcome="FAILED")
    with pytest.raises(IntegrityError), transaction.atomic():
        SourceImport.objects.create(
            source=source,
            fetched_at=timezone.now(),
            outcome="FAILED",
            error="timeout",
            snapshot=snapshot,
        )


def test_valid_imports_are_accepted(source: Source, snapshot: SourceSnapshot) -> None:
    SourceImport.objects.create(
        source=source, fetched_at=timezone.now(), http_status=200, outcome="OK", snapshot=snapshot
    )
    SourceImport.objects.create(
        source=source, fetched_at=timezone.now(), outcome="FAILED", error="timeout"
    )
    assert source.imports.count() == 2


def test_snapshot_hash_is_unique_per_source(source: Source, snapshot: SourceSnapshot) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        SourceSnapshot.objects.create(source=source, content_sha256="a" * 64, raw_text="{}")
