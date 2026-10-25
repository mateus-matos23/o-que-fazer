from typing import TYPE_CHECKING

from django.contrib import admin
from django.db.models import Model
from django.http import HttpRequest

from .models import Agency, Source, SourceImport, SourceSnapshot

# ModelAdmin só é genérico nos stubs; em runtime a classe não aceita subscrição.
if TYPE_CHECKING:
    _ModelAdmin = admin.ModelAdmin[Model]
else:
    _ModelAdmin = admin.ModelAdmin


class ReadOnlyAdmin(_ModelAdmin):
    """Conteúdo entra por `load_content`/`fetch_sources`; o admin serve só para consulta."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return False


@admin.register(Agency)
class AgencyAdmin(ReadOnlyAdmin):
    list_display = ("slug", "name", "jurisdiction")


@admin.register(Source)
class SourceAdmin(ReadOnlyAdmin):
    list_display = ("slug", "agency", "format", "jurisdiction", "url")
    list_filter = ("format", "jurisdiction")


@admin.register(SourceSnapshot)
class SourceSnapshotAdmin(ReadOnlyAdmin):
    list_display = ("source", "content_sha256", "declared_updated_at")


@admin.register(SourceImport)
class SourceImportAdmin(ReadOnlyAdmin):
    list_display = ("source", "fetched_at", "outcome", "http_status")
    list_filter = ("outcome",)
