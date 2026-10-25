"""Monta o `Catalog` do motor a partir do ORM, com número fixo de consultas."""

from collections.abc import Iterable
from datetime import datetime
from typing import Literal

from django.db.models import Max, Prefetch, Q

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


def _snapshot_ids(*groups: Iterable[CitedRow]) -> set[int]:
    return {c.snapshot_id for group in groups for c in group}


def load_catalog(situation_slug: str) -> Catalog:
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

    cited_select = ("snapshot__source",)
    procedures = list(
        Procedure.objects.filter(id__in=relevant)
        .select_related("agency", "clarifies", *cited_select)
        .prefetch_related(
            Prefetch(
                "requirements", Requirement.objects.select_related(*cited_select).order_by("id")
            ),
            Prefetch(
                "channels", ServiceChannel.objects.select_related(*cited_select).order_by("id")
            ),
            Prefetch("details", Detail.objects.select_related(*cited_select).order_by("id")),
            Prefetch(
                "rules",
                Rule.objects.select_related(*cited_select)
                .prefetch_related("conditions__question", "conditions__options")
                .order_by("id"),
            ),
        )
        .order_by("id")
    )
    dependencies = list(
        Dependency.objects.filter(before_id__in=relevant, after_id__in=relevant)
        .select_related("before", "after", "rule__snapshot__source", *cited_select)
        .prefetch_related("rule__conditions__question", "rule__conditions__options")
        .order_by("id")
    )

    snapshot_ids = _snapshot_ids(
        procedures,
        (r for p in procedures for r in p.requirements.all()),
        (c for p in procedures for c in p.channels.all()),
        (d for p in procedures for d in p.details.all()),
        (r for p in procedures for r in p.rules.all()),
        dependencies,
        (d.rule for d in dependencies if d.rule is not None),
    )
    fetched_at = dict(
        SourceImport.objects.filter(outcome=SourceImport.Outcome.OK, snapshot_id__in=snapshot_ids)
        .values_list("snapshot_id")
        .annotate(last=Max("fetched_at"))
    )
    cite = CitationFactory(fetched_at)

    return Catalog(
        situation_slug=situation.slug,
        situation_title=situation.title,
        candidates=candidate_slugs,
        questions={
            q.slug: QuestionDef(
                slug=q.slug,
                text=q.text,
                kind=_choice(q.kind, QUESTION_KINDS),
                allows_unknown=q.allows_unknown,
                order=q.order,
                options=tuple(
                    OptionDef(o.slug, o.label, o.out_of_coverage) for o in q.options.all()
                ),
            )
            for q in questions
        },
        procedures={
            p.slug: ProcedureDef(
                slug=p.slug,
                title=p.title,
                description=p.description,
                agency_name=p.agency.name,
                jurisdiction=p.jurisdiction,
                clarifies=p.clarifies.slug if p.clarifies else None,
                rules=tuple(_rule_def(r, cite) for r in p.rules.all()),
                requirements=tuple(
                    RequirementDef(r.description, cite(r)) for r in p.requirements.all()
                ),
                channels=tuple(
                    ChannelDef(_choice(c.kind, CHANNEL_KINDS), c.description, c.url, cite(c))
                    for c in p.channels.all()
                ),
                details=tuple(
                    DetailDef(_choice(d.kind, DETAIL_KINDS), d.text, cite(d))
                    for d in p.details.all()
                ),
                citation=cite(p),
            )
            for p in procedures
        },
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
