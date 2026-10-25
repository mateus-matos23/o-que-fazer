from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from sources.models import Source, SourceImport
from sources.services import import_source


class Command(BaseCommand):
    help = "Coleta as fontes oficiais cadastradas e registra importações e snapshots."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--source", action="append", dest="slugs", metavar="SLUG")

    def handle(self, *args: Any, slugs: list[str] | None, **options: Any) -> None:
        sources = Source.objects.order_by("slug")
        if slugs:
            sources = sources.filter(slug__in=slugs)
            missing = set(slugs) - {source.slug for source in sources}
            if missing:
                raise CommandError(f"Fontes inexistentes: {', '.join(sorted(missing))}")

        failures = 0
        for source in sources:
            result = import_source(source)
            if result.outcome == SourceImport.Outcome.OK:
                self.stdout.write(f"OK     {source.slug}")
            else:
                failures += 1
                self.stderr.write(f"FALHA  {source.slug}: {result.error}")
        if failures:
            raise CommandError(f"{failures} fonte(s) falharam; veja as importações registradas.")
