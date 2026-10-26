import http.client
import io
import urllib.error
from datetime import date
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from sources import adapters
from sources.adapters import CollectError, collect, extract_declared_update, parse_govbr_service
from sources.models import Source

SAMPLES = Path(__file__).resolve().parents[2] / "docs" / "dados" / "amostras"


@pytest.mark.parametrize("service_id", ["10416", "10420", "10424", "1045", "7839", "9815"])
def test_parses_real_govbr_samples(service_id: str) -> None:
    text = (SAMPLES / f"api-servicos-{service_id}.json").read_text(encoding="utf-8")
    document = parse_govbr_service(text)
    assert document["resposta"]["id"].endswith(f"/servicos/{service_id}")


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("{", "JSON inválido"),
        ("[]", "não é um objeto"),
        ('{"hasErro": true, "mensagem": "x"}', "API sinalizou erro"),
        ('{"hasErro": false, "resposta": {}}', "resposta.nome"),
    ],
)
def test_rejects_invalid_govbr_documents(text: str, message: str) -> None:
    with pytest.raises(CollectError, match=message):
        parse_govbr_service(text)


def test_extracts_declared_update_split_across_tags() -> None:
    html = "<p><span>Última Modificação:</span>\n <span>08/10/2026</span></p>"
    assert extract_declared_update(html) == date(2026, 10, 8)


def test_missing_declared_update_is_not_informed() -> None:
    html = "<p>Publicado em: quinta-feira, 1 de março de 2018</p>"
    assert extract_declared_update(html) is None


def test_repeated_same_date_is_accepted() -> None:
    html = "<p>Última Modificação: 24/09/2026</p><footer>Última Modificação: 24/09/2026</footer>"
    assert extract_declared_update(html) == date(2026, 9, 24)


def test_divergent_dates_fail_explicitly() -> None:
    html = "<p>Última Modificação: 24/09/2026</p><p>Última Modificação: 01/01/2025</p>"
    with pytest.raises(CollectError, match="divergentes"):
        extract_declared_update(html)


def test_impossible_date_fails() -> None:
    with pytest.raises(CollectError, match="inválida"):
        extract_declared_update("Última Modificação: 31/02/2026")


def _response(body: bytes, status: int = 200) -> Any:
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.status = status
    response.read.side_effect = lambda size: body[:size]
    return response


def _source(fmt: str) -> Source:
    return Source(slug="s", url="https://example.gov.br/x", format=fmt)


def test_collect_html_hashes_raw_bytes() -> None:
    body = "<p>Última Modificação: 25/09/2026</p>".encode()
    with mock.patch("urllib.request.urlopen", return_value=_response(body)):
        collected = collect(_source(Source.Format.HTML))
    assert collected.declared_updated_at == date(2026, 9, 25)
    assert collected.raw_json is None
    assert len(collected.content_sha256) == 64


def test_collect_http_error_keeps_status() -> None:
    error = urllib.error.HTTPError("u", 404, "Not Found", {}, io.BytesIO())  # type: ignore[arg-type]
    with (
        mock.patch("urllib.request.urlopen", side_effect=error),
        pytest.raises(CollectError) as info,
    ):
        collect(_source(Source.Format.HTML))
    assert info.value.http_status == 404


def test_collect_network_error_has_no_status() -> None:
    with (
        mock.patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")),
        pytest.raises(CollectError) as info,
    ):
        collect(_source(Source.Format.HTML))
    assert info.value.http_status is None


@pytest.mark.parametrize(
    "error", [ConnectionResetError("reset"), http.client.IncompleteRead(b"parcial")]
)
def test_collect_error_while_reading_body_is_a_network_error(error: Exception) -> None:
    response = _response(b"")
    response.read.side_effect = error
    with (
        mock.patch("urllib.request.urlopen", return_value=response),
        pytest.raises(CollectError, match="falha de rede") as info,
    ):
        collect(_source(Source.Format.HTML))
    assert info.value.http_status is None


def test_collect_parse_error_keeps_status() -> None:
    with (
        mock.patch("urllib.request.urlopen", return_value=_response(b"{")),
        pytest.raises(CollectError) as info,
    ):
        collect(_source(Source.Format.GOVBR_API))
    assert info.value.http_status == 200


def test_collect_rejects_oversized_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapters, "MAX_BYTES", 4)
    with (
        mock.patch("urllib.request.urlopen", return_value=_response(b"12345")),
        pytest.raises(CollectError, match="maior que"),
    ):
        collect(_source(Source.Format.HTML))
