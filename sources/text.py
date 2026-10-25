"""Texto pesquisável de uma versão de fonte, usado para verificar trechos literais."""

from html.parser import HTMLParser

from .models import SourceSnapshot


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self.chunks.append(data)


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _json_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _json_strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _json_strings(item)]
    return []


def snapshot_text(snapshot: SourceSnapshot) -> str:
    if snapshot.raw_json is not None:
        return normalize_whitespace(" ".join(_json_strings(snapshot.raw_json)))
    extractor = TextExtractor()
    extractor.feed(snapshot.raw_text)
    return normalize_whitespace(" ".join(extractor.chunks))


def contains_excerpt(text: str, excerpt: str) -> bool:
    normalized = normalize_whitespace(excerpt)
    return bool(normalized) and normalized in text
