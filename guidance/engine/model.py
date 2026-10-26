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


QuestionKind = Literal["SINGLE", "MULTIPLE"]
Operator = Literal["ANY_OF", "NONE_OF"]
ChannelKind = Literal["ONLINE", "IN_PERSON", "PHONE", "APP", "EMAIL"]
DetailKind = Literal["COST", "DEADLINE"]
DependencyKind = Literal["MANDATORY", "CONDITIONAL", "RECOMMENDED"]

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
    kind: QuestionKind
    allows_unknown: bool
    order: int
    options: tuple[OptionDef, ...]


@dataclass(frozen=True, slots=True)
class ConditionDef:
    question: str
    operator: Operator
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
    kind: ChannelKind
    description: str
    url: str
    citation: Citation
    rule: RuleDef | None = None  # sem regra = sempre vale


@dataclass(frozen=True, slots=True)
class DetailDef:
    kind: DetailKind
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
    kind: DependencyKind
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
