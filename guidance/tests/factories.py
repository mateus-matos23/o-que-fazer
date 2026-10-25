from datetime import UTC, datetime
from typing import Literal

from guidance.engine.model import (
    Catalog,
    Citation,
    ConditionDef,
    DependencyDef,
    OptionDef,
    ProcedureDef,
    QuestionDef,
    RuleDef,
)

CITATION = Citation("fonte", "trecho", datetime(2026, 1, 1, tzinfo=UTC), None)


def question(
    slug: str,
    options: tuple[str, ...] = ("a", "b", "c"),
    *,
    kind: Literal["SINGLE", "MULTIPLE"] = "SINGLE",
    allows_unknown: bool = True,
    order: int = 0,
) -> QuestionDef:
    return QuestionDef(
        slug, slug, kind, allows_unknown, order, tuple(OptionDef(o, o) for o in options)
    )


def cond(q: str, operator: Literal["ANY_OF", "NONE_OF"], *options: str) -> ConditionDef:
    return ConditionDef(q, operator, frozenset(options))


def rule(slug: str, *conditions: ConditionDef) -> RuleDef:
    return RuleDef(slug, slug, conditions, CITATION)


def procedure(slug: str, *rules: RuleDef, clarifies: str | None = None) -> ProcedureDef:
    return ProcedureDef(slug, slug, "", "orgao", "FEDERAL", clarifies, rules, (), (), (), CITATION)


def catalog(
    questions: tuple[QuestionDef, ...],
    procedures: tuple[ProcedureDef, ...],
    candidates: tuple[str, ...] | None = None,
    dependencies: tuple[DependencyDef, ...] = (),
) -> Catalog:
    return Catalog(
        "situacao",
        "Situação",
        frozenset(candidates if candidates is not None else (p.slug for p in procedures)),
        {q.slug: q for q in questions},
        {p.slug: p for p in procedures},
        dependencies,
    )


def dep(
    before: str,
    after: str,
    kind: Literal["MANDATORY", "CONDITIONAL", "RECOMMENDED"] = "MANDATORY",
    when: RuleDef | None = None,
) -> DependencyDef:
    return DependencyDef(before, after, kind, when, CITATION)
