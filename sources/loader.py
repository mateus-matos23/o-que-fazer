"""Carga de órgãos e fontes (`content/sources.toml`): upsert por slug, nunca apaga."""

from collections import Counter
from pathlib import Path
from typing import Any

from django.db import transaction

from .models import Agency, Jurisdiction, Source
from .toml_schema import ContentError, Schema, check_document, read_toml, text_of

_JURISDICTIONS = frozenset(Jurisdiction.values)
_TABLES = {
    "agencies": Schema(
        {
            "slug": text_of(Agency, "slug", slug=True),
            "name": text_of(Agency, "name"),
            "jurisdiction": _JURISDICTIONS,
        }
    ),
    "sources": Schema(
        {
            "slug": text_of(Source, "slug", slug=True),
            "agency": str,
            "url": text_of(Source, "url"),
            "format": frozenset(Source.Format.values),
            "jurisdiction": _JURISDICTIONS,
        },
        {"access_notes": str},
    ),
}


def _semantic_problems(
    file: str, agencies: list[dict[str, Any]], sources: list[dict[str, Any]]
) -> list[str]:
    problems: list[str] = []
    for table, records in (("agencies", agencies), ("sources", sources)):
        counts = Counter(record["slug"] for record in records)
        problems += [
            f"{file}: {slug}: slug duplicado em {table}" for slug, n in counts.items() if n > 1
        ]
    for url, n in Counter(record["url"] for record in sources).items():
        if n > 1:
            problems.append(f"{file}: {url}: url duplicada em sources")
    known_agencies = {record["slug"] for record in agencies} | set(
        Agency.objects.values_list("slug", flat=True)
    )
    for record in sources:
        if record["agency"] not in known_agencies:
            problems.append(f"{file}: {record['slug']}: agência inexistente: {record['agency']}")
        # shortcut: troca de URL entre fontes existentes é rejeitada; tratar se surgir caso real
        clash = Source.objects.filter(url=record["url"]).exclude(slug=record["slug"]).first()
        if clash:
            problems.append(f"{file}: {record['slug']}: url já usada pela fonte {clash.slug}")
    return problems


def load_sources(path: Path) -> dict[str, int]:
    doc = read_toml(path)
    problems = check_document(doc, _TABLES, path.name)
    if problems:
        raise ContentError(problems)
    agencies: list[dict[str, Any]] = doc.get("agencies", [])
    sources: list[dict[str, Any]] = doc.get("sources", [])
    problems = _semantic_problems(path.name, agencies, sources)
    if problems:
        raise ContentError(problems)

    with transaction.atomic():
        for record in agencies:
            Agency.objects.update_or_create(
                slug=record["slug"],
                defaults={"name": record["name"], "jurisdiction": record["jurisdiction"]},
            )
        for record in sources:
            Source.objects.update_or_create(
                slug=record["slug"],
                defaults={
                    "agency": Agency.objects.get(slug=record["agency"]),
                    "url": record["url"],
                    "format": record["format"],
                    "jurisdiction": record["jurisdiction"],
                    "access_notes": record.get("access_notes", ""),
                },
            )
    return {"Agency": len(agencies), "Source": len(sources)}
