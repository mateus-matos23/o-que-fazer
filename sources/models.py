from django.db import models


class Jurisdiction(models.TextChoices):
    FEDERAL = "FEDERAL", "Federal"
    MARANHAO = "MARANHAO", "Maranhão"
    SAO_LUIS = "SAO_LUIS", "São Luís"


class Agency(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=10, choices=Jurisdiction)

    def __str__(self) -> str:
        return self.name


class Source(models.Model):
    class Format(models.TextChoices):
        GOVBR_API = "GOVBR_API", "API de serviços do Gov.br (JSON)"
        HTML = "HTML", "Página HTML"

    slug = models.SlugField(unique=True)
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name="sources")
    url = models.URLField(max_length=500, unique=True)
    format = models.CharField(max_length=10, choices=Format)
    jurisdiction = models.CharField(max_length=10, choices=Jurisdiction)
    access_notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.slug


class SourceSnapshot(models.Model):
    """Conteúdo bruto preservado; várias importações com o mesmo hash reaproveitam o snapshot."""

    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="snapshots")
    content_sha256 = models.CharField(max_length=64)
    raw_text = models.TextField()
    raw_json = models.JSONField(null=True, blank=True)
    # Data de vigência declarada pelo órgão (RN12); nula = "não informado". Distinta da coleta.
    declared_updated_at = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "content_sha256"], name="unique_snapshot_per_source_hash"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.source.slug}@{self.content_sha256[:12]}"


class SourceImport(models.Model):
    class Outcome(models.TextChoices):
        OK = "OK", "Sucesso"
        FAILED = "FAILED", "Falha"

    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="imports")
    fetched_at = models.DateTimeField()
    http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    outcome = models.CharField(max_length=6, choices=Outcome)
    error = models.TextField(blank=True)
    snapshot = models.ForeignKey(
        SourceSnapshot, on_delete=models.PROTECT, null=True, blank=True, related_name="imports"
    )

    class Meta:
        constraints = [
            # Sucesso sempre preserva conteúdo; falha nunca produz snapshot e registra o erro.
            models.CheckConstraint(
                condition=(
                    models.Q(outcome="OK", snapshot__isnull=False, error="")
                    | models.Q(outcome="FAILED", snapshot__isnull=True) & ~models.Q(error="")
                ),
                name="import_outcome_matches_snapshot",
            ),
        ]
        indexes = [models.Index(fields=["source", "-fetched_at"])]

    def __str__(self) -> str:
        return f"{self.source.slug} {self.fetched_at:%Y-%m-%d %H:%M} {self.outcome}"
