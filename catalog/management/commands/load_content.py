from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from catalog.loader import load_content
from sources.toml_schema import ContentError


class Command(BaseCommand):
    help = "Valida e substitui todo o conteúdo do catálogo a partir dos TOML de um diretório."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("directory", type=Path)

    def handle(self, *args: Any, directory: Path, **options: Any) -> None:
        try:
            counts = load_content(directory)
        except ContentError as exc:
            raise CommandError("\n".join(exc.lines)) from exc
        for model, count in counts.items():
            self.stdout.write(f"{model}: {count}")
