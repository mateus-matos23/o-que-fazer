"""Validação estrita de documentos TOML de conteúdo (chaves e tipos), sem tocar no banco."""

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.db import connection, models

# Escalar (`str`, `bool`, `int`), conjunto de strings permitidas, tabela aninhada ou lista
# de um único tipo de elemento (`[str]`, `[Schema(...)]`).
type Kind = type | frozenset[str] | Schema | Text | IntRange | list[Kind]


class ContentError(Exception):
    """Um ou mais problemas de conteúdo, uma linha por problema."""

    def __init__(self, lines: list[str]) -> None:
        super().__init__("\n".join(lines))
        self.lines = lines


_SLUG = re.compile(r"[-a-zA-Z0-9_]+")


@dataclass(frozen=True)
class Text:
    """String limitada pela coluna do model; `slug` exige o formato de SlugField."""

    max_length: int
    slug: bool = False


@dataclass(frozen=True)
class IntRange:
    low: int | None
    high: int | None


def text_of(model: type[models.Model], name: str, *, slug: bool = False) -> Text:
    column = model._meta.get_field(name)
    if not isinstance(column, models.CharField) or column.max_length is None:
        raise TypeError(f"{model.__name__}.{name} não é um CharField com max_length")
    return Text(column.max_length, slug)


def int_range_of(model: type[models.Model], name: str) -> IntRange:
    low, high = connection.ops.integer_field_range(model._meta.get_field(name).get_internal_type())
    return IntRange(low, high)


@dataclass(frozen=True)
class Schema:
    required: Mapping[str, Kind]
    optional: Mapping[str, Kind] = field(default_factory=dict)


def _check_value(value: object, kind: Kind, where: str) -> list[str]:
    if isinstance(kind, Schema):
        return check_table(value, kind, where)
    if isinstance(kind, frozenset):
        if isinstance(value, str) and value in kind:
            return []
        return [f"{where}: valor {value!r} fora de {sorted(kind)}"]
    if isinstance(kind, Text):
        if not isinstance(value, str):
            return [f"{where}: esperado str"]
        if len(value) > kind.max_length:
            return [f"{where}: excede {kind.max_length} caracteres"]
        if kind.slug and not _SLUG.fullmatch(value):
            return [f"{where}: slug inválido (use letras, números, hífen e sublinhado)"]
        return []
    if isinstance(kind, IntRange):
        if type(value) is not int:
            return [f"{where}: esperado int"]
        if (kind.low is not None and value < kind.low) or (
            kind.high is not None and value > kind.high
        ):
            return [f"{where}: fora da faixa {kind.low}..{kind.high}"]
        return []
    if isinstance(kind, list):
        if not isinstance(value, list):
            return [f"{where}: esperado lista"]
        return [
            p for i, item in enumerate(value) for p in _check_value(item, kind[0], f"{where}[{i}]")
        ]
    if type(value) is not kind:
        return [f"{where}: esperado {kind.__name__}"]
    return []


def check_table(value: object, schema: Schema, where: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{where}: esperado tabela"]
    prefix = f"{where}." if where else ""
    problems = [
        f"{prefix}{key}: chave obrigatória ausente" for key in schema.required if key not in value
    ]
    for key, item in value.items():
        kind = schema.required.get(key, schema.optional.get(key))
        if kind is None:
            problems.append(f"{prefix}{key}: chave desconhecida")
        else:
            problems.extend(_check_value(item, kind, f"{prefix}{key}"))
    return problems


def read_toml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_bytes().decode("utf-8")
    except OSError as exc:
        raise ContentError(
            [f"{path.name}: -: não foi possível ler o arquivo: {exc.strerror}"]
        ) from exc
    except UnicodeDecodeError as exc:
        raise ContentError([f"{path.name}: -: arquivo não está em UTF-8"]) from exc
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ContentError([f"{path.name}: -: TOML inválido: {exc}"]) from exc


def check_document(doc: dict[str, Any], tables: Mapping[str, Schema], file: str) -> list[str]:
    """Linhas `<arquivo>: <slug>: <problema>`; registros sem slug usam `<tabela>[i]`."""
    problems = [f"{file}: -: {key}: chave desconhecida" for key in doc if key not in tables]
    for name, schema in tables.items():
        records = doc.get(name, [])
        if not isinstance(records, list):
            problems.append(f"{file}: -: {name}: esperado lista de tabelas")
            continue
        for i, record in enumerate(records):
            label = record.get("slug") if isinstance(record, dict) else None
            owner = label if isinstance(label, str) else f"{name}[{i}]"
            problems.extend(f"{file}: {owner}: {p}" for p in check_table(record, schema, ""))
    return problems
