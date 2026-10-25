"""Coleta e extração por formato de fonte. Não toca no banco: o command `fetch_sources` persiste."""

import hashlib
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Any

from .models import Source
from .text import TextExtractor

TIMEOUT_SECONDS = 60
MAX_BYTES = 5 * 1024 * 1024
# gov.br responde 403 a requisições sem User-Agent (docs/dados/amostras/README.md).
USER_AGENT = "Mozilla/5.0"
_DECLARED_UPDATE = re.compile(r"Última Modificação:\s*(\d{2})/(\d{2})/(\d{4})")


class CollectError(Exception):
    def __init__(self, message: str, http_status: int | None = None) -> None:
        super().__init__(message)
        self.http_status = http_status


@dataclass(frozen=True)
class Collected:
    http_status: int
    raw_text: str
    raw_json: dict[str, Any] | None
    declared_updated_at: date | None
    content_sha256: str


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body: bytes = response.read(MAX_BYTES + 1)
            status: int = response.status
    except urllib.error.HTTPError as exc:
        raise CollectError(f"HTTP {exc.code}", http_status=exc.code) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise CollectError(f"falha de rede: {exc}") from exc
    if len(body) > MAX_BYTES:
        raise CollectError(f"resposta maior que {MAX_BYTES} bytes", http_status=status)
    return status, body


def parse_govbr_service(text: str) -> dict[str, Any]:
    """Valida a ficha de `servicos.gov.br/api/v1/servicos/{id}` e devolve o JSON completo."""
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CollectError(f"JSON inválido: {exc}") from exc
    if not isinstance(document, dict):
        raise CollectError("ficha não é um objeto JSON")
    if document.get("hasErro") is not False:
        raise CollectError(f"API sinalizou erro: {document.get('mensagem')!r}")
    service = document.get("resposta")
    if not isinstance(service, dict) or not service.get("nome"):
        raise CollectError("ficha sem 'resposta.nome'")
    return document


def extract_declared_update(html: str) -> date | None:
    """Data "Última Modificação" declarada na página; None quando não informada."""
    extractor = TextExtractor()
    extractor.feed(html)
    text = " ".join(" ".join(extractor.chunks).split())
    found: set[date] = set()
    for day, month, year in _DECLARED_UPDATE.findall(text):
        try:
            found.add(date(int(year), int(month), int(day)))
        except ValueError as exc:
            raise CollectError(f"data declarada inválida: {day}/{month}/{year}") from exc
    if len(found) > 1:
        raise CollectError(f"página declara datas divergentes: {sorted(found)}")
    return found.pop() if found else None


def collect(source: Source) -> Collected:
    status, body = fetch(source.url)
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CollectError("conteúdo não está em UTF-8", http_status=status) from exc
    sha256 = hashlib.sha256(body).hexdigest()
    try:
        match source.format:
            case Source.Format.GOVBR_API:
                # A ficha não traz data de atualização; ela vem da página HTML do serviço.
                return Collected(status, text, parse_govbr_service(text), None, sha256)
            case Source.Format.HTML:
                return Collected(status, text, None, extract_declared_update(text), sha256)
            case _:
                raise CollectError(f"formato sem adaptador: {source.format}")
    except CollectError as exc:
        exc.http_status = status
        raise
