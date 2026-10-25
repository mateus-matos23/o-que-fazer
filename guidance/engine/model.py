"""Tipos imutáveis do motor. Espelham catalog/models.py, mas sem Django: o motor é Python puro."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Literal


class Tri(Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNDETERMINED = "UNDETERMINED"


class Unknown(Enum):
    """O "não sei": mantém o fato desconhecido, nunca vira resposta negativa (RN03)."""

    UNKNOWN = "UNKNOWN"


Answer = frozenset[str] | Unknown
Facts = Mapping[str, Answer]  # chave = slug da pergunta; ausente = não respondida


@dataclass(frozen=True, slots=True)
class Citation:
    source_slug: str
    source_url: str
    excerpt: str
    fetched_at: datetime
    declared_updated_at: date | None


@dataclass(frozen=True, slots=True)
class OptionDef:
    slug: str
    label: str
    out_of_coverage: bool = False  # sem orientação oficial nesta versão


@dataclass(frozen=True, slots=True)
class QuestionDef:
    slug: str
    text: str
    help_text: str
    kind: Literal["SINGLE", "MULTIPLE"]
    allows_unknown: bool
    order: int
    options: tuple[OptionDef, ...]


@dataclass(frozen=True, slots=True)
class ConditionDef:
    question: str
    operator: Literal["ANY_OF", "NONE_OF"]
    options: frozenset[str]


@dataclass(frozen=True, slots=True)
class RuleDef:
    slug: str
    explanation: str
    conditions: tuple[ConditionDef, ...]
    citation: Citation


@dataclass(frozen=True, slots=True)
class RequirementDef:
    description: str
    citation: Citation
    rule: RuleDef | None = None  # sem regra = sempre vale


@dataclass(frozen=True, slots=True)
class ChannelDef:
    kind: Literal["ONLINE", "IN_PERSON", "PHONE", "APP", "EMAIL"]
    description: str
    url: str
    citation: Citation
    rule: RuleDef | None = None  # sem regra = sempre vale


@dataclass(frozen=True, slots=True)
class DetailDef:
    kind: Literal["COST", "DEADLINE"]
    text: str
    citation: Citation


@dataclass(frozen=True, slots=True)
class ProcedureDef:
    slug: str
    title: str
    description: str
    agency_name: str
    jurisdiction: str
    clarifies: str | None
    rules: tuple[RuleDef, ...]
    requirements: tuple[RequirementDef, ...]
    channels: tuple[ChannelDef, ...]
    details: tuple[DetailDef, ...]
    citation: Citation


@dataclass(frozen=True, slots=True)
class DependencyDef:
    before: str
    after: str
    kind: Literal["MANDATORY", "CONDITIONAL", "RECOMMENDED"]
    rule: RuleDef | None
    citation: Citation


@dataclass(frozen=True, slots=True)
class Catalog:
    situation_slug: str
    situation_title: str
    candidates: frozenset[str]
    questions: Mapping[str, QuestionDef]
    # Todos os relevantes: candidatos, esclarecimentos e pré-requisitos alcançáveis.
    procedures: Mapping[str, ProcedureDef]
    dependencies: tuple[DependencyDef, ...]
