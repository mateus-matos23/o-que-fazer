"""Fixture compartilhada: carrega sources + content/ reais com snapshots de amostras reais.

Limitação: as amostras HTML em docs/dados/amostras são trechos de texto (não o HTML bruto) e
`receita-consulta-situacao-cpf` não tem amostra; para ela o texto é sintético, copiado da evidência.
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from catalog.loader import load_content
from sources.loader import load_sources
from sources.models import Source, SourceImport, SourceSnapshot

ROOT = Path(__file__).resolve().parents[0]
SAMPLES = ROOT / "docs" / "dados" / "amostras"
SYNTHETIC = {
    "receita-consulta-situacao-cpf": (
        'Campos: "CPF:" e "Data de Nascimento:" "O comprovante gerado não fornece informações '
        "sobre a situação econômica, financeira ou fiscal do titular do CPF, limita-se tão "
        'somente a comprovar a situação cadastral no CPF."'
    ),
}
SAMPLE_FILES = {
    "api-servicos-10416": "api-servicos-10416.json",
    "api-servicos-10420": "api-servicos-10420.json",
    "govbr-atualizar-cpf": "html-atualizar-cadastro-de-pessoas-fisicas.md",
    "govbr-inscrever-cpf": "html-inscrever-no-cpf.md",
    "govbr-declarar-irpf": "html-declarar-meu-imposto-de-renda.md",
    "receita-meu-cpf": "html-receitafederal-meu-cpf.md",
}


def _snapshot(source: Source) -> SourceSnapshot:
    if source.slug in SYNTHETIC:
        text, raw_json = SYNTHETIC[source.slug], None
    else:
        raw = (SAMPLES / SAMPLE_FILES[source.slug]).read_text(encoding="utf-8")
        if source.format == Source.Format.GOVBR_API:
            text, raw_json = raw, json.loads(raw)
        else:
            block = re.search(r"```text\n(.*?)```", raw, re.DOTALL)
            assert block, source.slug
            text, raw_json = block.group(1), None
    return SourceSnapshot.objects.create(
        source=source,
        content_sha256=hashlib.sha256(text.encode()).hexdigest(),
        raw_text=text,
        raw_json=raw_json,
    )


@pytest.fixture
def loaded(db: None) -> dict[str, int]:
    load_sources(ROOT / "content" / "sources.toml")
    for source in Source.objects.all():
        SourceImport.objects.create(
            source=source,
            fetched_at=datetime(2026, 10, 10, tzinfo=UTC),
            outcome=SourceImport.Outcome.OK,
            snapshot=_snapshot(source),
        )
    return load_content(ROOT / "content")
