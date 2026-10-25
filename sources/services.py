from django.db import transaction
from django.utils import timezone

from .adapters import CollectError, collect
from .models import Source, SourceImport, SourceSnapshot


def import_source(source: Source) -> SourceImport:
    """Coleta a fonte e registra a importação; falha vira registro FAILED, nunca snapshot."""
    fetched_at = timezone.now()
    try:
        collected = collect(source)
    except CollectError as exc:
        return SourceImport.objects.create(
            source=source,
            fetched_at=fetched_at,
            http_status=exc.http_status,
            outcome=SourceImport.Outcome.FAILED,
            error=str(exc),
        )
    with transaction.atomic():
        # Mesmo hash = mesmo conteúdo bruto: reaproveita o snapshot e só registra a nova coleta.
        snapshot, _ = SourceSnapshot.objects.get_or_create(
            source=source,
            content_sha256=collected.content_sha256,
            defaults={
                "raw_text": collected.raw_text,
                "raw_json": collected.raw_json,
                "declared_updated_at": collected.declared_updated_at,
            },
        )
        return SourceImport.objects.create(
            source=source,
            fetched_at=fetched_at,
            http_status=collected.http_status,
            outcome=SourceImport.Outcome.OK,
            snapshot=snapshot,
        )
