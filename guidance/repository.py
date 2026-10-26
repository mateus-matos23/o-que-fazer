"""Monta o `Catalog` do motor a partir do ORM, com número fixo de consultas e cache por processo."""

from collections.abc import Iterable
from datetime import datetime
from typing import Literal

from django.db.models import Max, Prefetch, Q, QuerySet, Subquery

from catalog.models import (
    AnswerOption,
    Dependency,
    Procedure,
    Requirement,
    Rule,
    ServiceChannel,
    Situation,
)
from catalog.models import ProcedureDetail as Detail
from guidance.engine.model import (
    Catalog,
    ChannelDef,
    Citation,
    ConditionDef,
    DependencyDef,
    DetailDef,
    OptionDef,
    ProcedureDef,
    QuestionDef,
    RequirementDef,
    RuleDef,
)
from sources.models import SourceImport

QuestionKind = Literal["SINGLE", "MULTIPLE"]
Operator = Literal["ANY_OF", "NONE_OF"]
ChannelKind = Literal["ONLINE", "IN_PERSON", "PHONE", "APP", "EMAIL"]
DetailKind = Literal["COST", "DEADLINE"]
DependencyKind = Literal["MANDATORY", "CONDITIONAL", "RECOMMENDED"]

QUESTION_KINDS: tuple[QuestionKind, ...] = ("SINGLE", "MULTIPLE")
OPERATORS: tuple[Operator, ...] = ("ANY_OF", "NONE_OF")
CHANNEL_KINDS: tuple[ChannelKind, ...] = ("ONLINE", "IN_PERSON", "PHONE", "APP", "EMAIL")
DETAIL_KINDS: tuple[DetailKind, ...] = ("COST", "DEADLINE")
DEPENDENCY_KINDS: tuple[DependencyKind, ...] = ("MANDATORY", "CONDITIONAL", "RECOMMENDED")


type CitedRow = Rule | Procedure | Requirement | ServiceChannel | Detail | Dependency


class SituationNotFound(Exception):
    pass


class ProcedureNotFound(Exception):
    pass


def _choice[T: str](value: str, allowed: tuple[T, ...]) -> T:
    for option in allowed:
        if option == value:
            return option
    raise ValueError(f"valor inesperado {value!r}; esperado um de {allowed}")


def _closure_of_prerequisites(seeds: set[int]) -> set[int]:
    """Fecho para trás por QUALQUER Dependency (o motor decide quais ativar).

    Carrega todas as arestas numa única consulta (o catálogo é pequeno) em vez de uma por nível.
    """
    parents: dict[int, list[int]] = {}
    for before_id, after_id in Dependency.objects.values_list("before_id", "after_id"):
        parents.setdefault(after_id, []).append(before_id)
    relevant = set(seeds)
    pending = list(seeds)
    while pending:
        for before_id in parents.get(pending.pop(), ()):
            if before_id not in relevant:
                relevant.add(before_id)
                pending.append(before_id)
    return relevant


def _rule_def(rule: Rule, cite: CitationFactory) -> RuleDef:
    return RuleDef(
        slug=rule.slug,
        explanation=rule.explanation,
        conditions=tuple(
            ConditionDef(
                question=c.question.slug,
                operator=_choice(c.operator, OPERATORS),
                options=frozenset(o.slug for o in c.options.all()),
            )
            for c in rule.conditions.all()
        ),
        citation=cite(rule),
    )


class CitationFactory:
    def __init__(self, fetched_at: dict[int, datetime]) -> None:
        self._fetched_at = fetched_at

    def __call__(self, cited: CitedRow) -> Citation:
        snapshot = cited.snapshot
        fetched_at = self._fetched_at.get(snapshot.pk)
        if fetched_at is None:
            raise ValueError(f"snapshot {snapshot} sem importação OK")
        return Citation(
            source_slug=snapshot.source.slug,
            source_url=snapshot.source.url,
            excerpt=cited.excerpt,
            fetched_at=fetched_at,
            declared_updated_at=snapshot.declared_updated_at,
        )


CITED_SELECT = ("snapshot__source",)
# Regra opcional de requisito e canal (RF25): condições e citação, sem consulta por item.
ITEM_RULE_SELECT = (*CITED_SELECT, "rule__snapshot__source")
ITEM_RULE_PREFETCH = ("rule__conditions__question", "rule__conditions__options")


def _procedures() -> QuerySet[Procedure]:
    return (
        Procedure.objects.select_related("agency", "clarifies", *CITED_SELECT)
        .prefetch_related(
            Prefetch(
                "requirements",
                Requirement.objects.select_related(*ITEM_RULE_SELECT)
                .prefetch_related(*ITEM_RULE_PREFETCH)
                .order_by("id"),
            ),
            Prefetch(
                "channels",
                ServiceChannel.objects.select_related(*ITEM_RULE_SELECT)
                .prefetch_related(*ITEM_RULE_PREFETCH)
                .order_by("id"),
            ),
            Prefetch("details", Detail.objects.select_related(*CITED_SELECT).order_by("id")),
            Prefetch(
                "rules",
                Rule.objects.select_related(*CITED_SELECT)
                .prefetch_related("conditions__question", "conditions__options")
                .order_by("id"),
            ),
        )
        .order_by("id")
    )


def _procedure_snapshot_ids(procedures: list[Procedure]) -> set[int]:
    return _snapshot_ids(
        procedures,
        (r for p in procedures for r in p.requirements.all()),
        (c for p in procedures for c in p.channels.all()),
        (i.rule for p in procedures for i in p.requirements.all() if i.rule),
        (i.rule for p in procedures for i in p.channels.all() if i.rule),
        (d for p in procedures for d in p.details.all()),
        (r for p in procedures for r in p.rules.all()),
    )


def _fetched_at(snapshot_ids: set[int]) -> dict[int, datetime]:
    return dict(
        SourceImport.objects.filter(outcome=SourceImport.Outcome.OK, snapshot_id__in=snapshot_ids)
        .values_list("snapshot_id")
        .annotate(last=Max("fetched_at"))
    )


def _item_rule(item: Requirement | ServiceChannel, cite: CitationFactory) -> RuleDef | None:
    return _rule_def(item.rule, cite) if item.rule else None


def _procedure_def(p: Procedure, cite: CitationFactory) -> ProcedureDef:
    return ProcedureDef(
        slug=p.slug,
        title=p.title,
        description=p.description,
        agency_name=p.agency.name,
        jurisdiction=p.jurisdiction,
        clarifies=p.clarifies.slug if p.clarifies else None,
        rules=tuple(_rule_def(r, cite) for r in p.rules.all()),
        requirements=tuple(
            RequirementDef(r.description, cite(r), _item_rule(r, cite))
            for r in p.requirements.all()
        ),
        channels=tuple(
            ChannelDef(
                _choice(c.kind, CHANNEL_KINDS), c.description, c.url, cite(c), _item_rule(c, cite)
            )
            for c in p.channels.all()
        ),
        details=tuple(
            DetailDef(_choice(d.kind, DETAIL_KINDS), d.text, cite(d)) for d in p.details.all()
        ),
        citation=cite(p),
    )


def load_procedure(slug: str) -> ProcedureDef:
    """Um procedimento isolado, para a busca direta (RF18): sem situação nem fatos."""
    procedure = _procedures().filter(slug=slug).first()
    if procedure is None:
        raise ProcedureNotFound(slug)
    cite = CitationFactory(_fetched_at(_procedure_snapshot_ids([procedure])))
    return _procedure_def(procedure, cite)


def _snapshot_ids(*groups: Iterable[CitedRow]) -> set[int]:
    return {c.snapshot_id for group in groups for c in group}


type CatalogVersion = tuple[int, int | None]

# Por slug, só a versão mais recente: o tamanho fica limitado ao número de situações.
_catalog_cache: dict[str, tuple[CatalogVersion, Catalog]] = {}


def _catalog_version(situation_slug: str) -> CatalogVersion | None:
    """Id da situação e da última importação OK, numa consulta.

    `load_content` recria o catálogo (ids novos) e `fetch_sources` cria importações; qualquer um
    dos dois muda a versão. shortcut: `load_sources` sozinho (nome de órgão, URL de fonte) não muda
    a versão; o fluxo documentado sempre termina em `load_content`; se isso mudar, versionar fontes.
    """
    last_ok_import = SourceImport.objects.filter(outcome=SourceImport.Outcome.OK).order_by("-id")
    return (
        Situation.objects.filter(slug=situation_slug)
        .annotate(last_import=Subquery(last_ok_import.values("id")[:1]))
        .values_list("id", "last_import")
        .first()
    )


def clear_catalog_cache() -> None:
    _catalog_cache.clear()


def load_catalog(situation_slug: str) -> Catalog:
    """O `Catalog` é imutável, então pode ser reusado entre requests enquanto a versão não mudar."""
    version = _catalog_version(situation_slug)
    if version is None:
        raise SituationNotFound(situation_slug)
    cached = _catalog_cache.get(situation_slug)
    if cached is not None and cached[0] == version:
        return cached[1]
    # Uma carga concorrente pode misturar versões; a próxima request vê a versão nova e refaz.
    catalog = _build_catalog(situation_slug)
    _catalog_cache[situation_slug] = (version, catalog)
    return catalog


def _build_catalog(situation_slug: str) -> Catalog:
    try:
        situation = Situation.objects.get(slug=situation_slug)
    except Situation.DoesNotExist:
        raise SituationNotFound(situation_slug) from None

    questions = list(
        situation.questions.order_by("order", "id").prefetch_related(
            Prefetch("options", AnswerOption.objects.order_by("id"))
        )
    )
    seeds = set(
        Procedure.objects.filter(
            Q(situations=situation) | Q(clarifies__situations=situation)
        ).values_list("id", flat=True)
    )
    candidate_slugs = frozenset(situation.candidates.values_list("slug", flat=True))
    relevant = _closure_of_prerequisites(seeds)

    procedures = list(_procedures().filter(id__in=relevant))
    dependencies = list(
        Dependency.objects.filter(before_id__in=relevant, after_id__in=relevant)
        .select_related("before", "after", "rule__snapshot__source", *CITED_SELECT)
        .prefetch_related("rule__conditions__question", "rule__conditions__options")
        .order_by("id")
    )

    snapshot_ids = _procedure_snapshot_ids(procedures) | _snapshot_ids(
        dependencies, (d.rule for d in dependencies if d.rule is not None)
    )
    cite = CitationFactory(_fetched_at(snapshot_ids))

    return Catalog(
        situation_slug=situation.slug,
        situation_title=situation.title,
        candidates=candidate_slugs,
        questions={
            q.slug: QuestionDef(
                slug=q.slug,
                text=q.text,
                help_text=q.help_text,
                kind=_choice(q.kind, QUESTION_KINDS),
                allows_unknown=q.allows_unknown,
                order=q.order,
                options=tuple(
                    OptionDef(o.slug, o.label, o.out_of_coverage) for o in q.options.all()
                ),
            )
            for q in questions
        },
        procedures={p.slug: _procedure_def(p, cite) for p in procedures},
        dependencies=tuple(
            DependencyDef(
                before=d.before.slug,
                after=d.after.slug,
                kind=_choice(d.kind, DEPENDENCY_KINDS),
                rule=_rule_def(d.rule, cite) if d.rule else None,
                citation=cite(d),
            )
            for d in dependencies
        ),
    )
