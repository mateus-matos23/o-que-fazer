from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from sources.loader import load_sources
from sources.toml_schema import ContentError


class Command(BaseCommand):
    help = "Carrega órgãos e fontes de um arquivo TOML (upsert por slug; nunca apaga)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("path", type=Path)

    def handle(self, *args: Any, path: Path, **options: Any) -> None:
        try:
            counts = load_sources(path)
        except ContentError as exc:
            raise CommandError("\n".join(exc.lines)) from exc
        except OSError as exc:
            raise CommandError(f"não foi possível ler {path}: {exc.strerror}") from exc
        for model, count in counts.items():
            self.stdout.write(f"{model}: {count}")
