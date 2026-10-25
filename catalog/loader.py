"""Carga de conteúdo do catálogo: valida tudo sem escrever e depois substitui o catálogo inteiro."""

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.db import models, transaction

from guidance.engine.ordering import DependencyCycleError, kahn_layers
from sources.models import Agency, Jurisdiction, Source, SourceImport, SourceSnapshot
from sources.text import contains_excerpt, snapshot_text
from sources.toml_schema import (
    ContentError,
    Schema,
    Text,
    check_document,
    int_range_of,
    read_toml,
    text_of,
)

from .models import (
    AnswerOption,
    Condition,
    Dependency,
    Procedure,
    ProcedureDetail,
    Question,
    Requirement,
    Rule,
    ServiceChannel,
    Situation,
)

RESERVED_OPTION_SLUGS = frozenset({"nao-sei", "unknown"})


def _slug(model: type[models.Model]) -> Text:
    return text_of(model, "slug", slug=True)


_CITATION = {"source": str, "excerpt": str}
_TABLES = {
    "situations": Schema(
        {
            "slug": _slug(Situation),
            "title": text_of(Situation, "title"),
            "candidates": [str],
        }
    ),
    "questions": Schema(
        {
            "slug": _slug(Question),
            "text": str,
            "kind": frozenset(Question.Kind.values),
            "situations": [str],
            "options": [
                Schema(
                    {
                        "slug": _slug(AnswerOption),
                        "label": text_of(AnswerOption, "label"),
                    },
                    {"out_of_coverage": bool},
                )
            ],
        },
        {"allows_unknown": bool, "order": int_range_of(Question, "order")},
    ),
    "procedures": Schema(
        {
            "slug": _slug(Procedure),
            "title": text_of(Procedure, "title"),
            "description": str,
            "agency": str,
            "jurisdiction": frozenset(Jurisdiction.values),
            **_CITATION,
        },
        {
            "clarifies": str,
            "requirements": [Schema({"description": str, **_CITATION})],
            "channels": [
                Schema(
                    {
                        "kind": frozenset(ServiceChannel.Kind.values),
                        "description": str,
                        **_CITATION,
                    },
                    {"url": text_of(ServiceChannel, "url")},
                )
            ],
            "details": [
                Schema({"kind": frozenset(ProcedureDetail.Kind.values), "text": str, **_CITATION})
            ],
        },
    ),
    "rules": Schema(
        {
            "slug": _slug(Rule),
            "explanation": str,
            "conditions": [
                Schema(
                    {
                        "question": str,
                        "operator": frozenset(Condition.Operator.values),
                        "options": [str],
                    }
                )
            ],
            **_CITATION,
        },
        {"procedure": str},
    ),
    "dependencies": Schema(
        {
            "before": str,
            "after": str,
            "kind": frozenset(Dependency.Kind.values),
            **_CITATION,
        },
        {"rule": str},
    ),
}


@dataclass(frozen=True)
class Cite:
    source: str
    excerpt: str


@dataclass(frozen=True)
class Item:
    """Requisito, canal ou detalhe de um procedimento."""

    kind: str
    text: str
    url: str
    cite: Cite


@dataclass(frozen=True)
class ProcedureDef:
    file: str
    slug: str
    title: str
    description: str
    agency: str
    jurisdiction: str
    cite: Cite
    clarifies: str | None
    requirements: list[Item]
    channels: list[Item]
    details: list[Item]


@dataclass(frozen=True)
class ConditionDef:
    question: str
    operator: str
    options: list[str]


@dataclass(frozen=True)
class RuleDef:
    file: str
    slug: str
    procedure: str | None
    explanation: str
    cite: Cite
    conditions: list[ConditionDef]


@dataclass(frozen=True)
class DependencyDef:
    file: str
    before: str
    after: str
    kind: str
    rule: str | None
    cite: Cite

    @property
    def label(self) -> str:
        return f"{self.before}->{self.after}"


@dataclass(frozen=True)
class QuestionDef:
    file: str
    slug: str
    text: str
    kind: str
    allows_unknown: bool
    order: int
    situations: list[str]
    options: list[tuple[str, str]]
    out_of_coverage: frozenset[str]  # slugs das opções sem orientação oficial


@dataclass(frozen=True)
class SituationDef:
    file: str
    slug: str
    title: str
    candidates: list[str]


@dataclass
class Content:
    situations: list[SituationDef] = field(default_factory=list)
    questions: list[QuestionDef] = field(default_factory=list)
    procedures: list[ProcedureDef] = field(default_factory=list)
    rules: list[RuleDef] = field(default_factory=list)
    dependencies: list[DependencyDef] = field(default_factory=list)


def _cite(raw: dict[str, Any]) -> Cite:
    return Cite(raw["source"], raw["excerpt"])


def _parse(file: str, doc: dict[str, Any], content: Content) -> None:
    for r in doc.get("situations", []):
        content.situations.append(SituationDef(file, r["slug"], r["title"], r["candidates"]))
    for r in doc.get("questions", []):
        options = [(o["slug"], o["label"]) for o in r["options"]]
        uncovered = frozenset(o["slug"] for o in r["options"] if o.get("out_of_coverage", False))
        content.questions.append(
            QuestionDef(
                file,
                r["slug"],
                r["text"],
                r["kind"],
                r.get("allows_unknown", False),
                r.get("order", 0),
                r["situations"],
                options,
                uncovered,
            )
        )
    for r in doc.get("procedures", []):
        content.procedures.append(
            ProcedureDef(
                file,
                r["slug"],
                r["title"],
                r["description"],
                r["agency"],
                r["jurisdiction"],
                _cite(r),
                r.get("clarifies"),
                [Item("", i["description"], "", _cite(i)) for i in r.get("requirements", [])],
                [
                    Item(i["kind"], i["description"], i.get("url", ""), _cite(i))
                    for i in r.get("channels", [])
                ],
                [Item(i["kind"], i["text"], "", _cite(i)) for i in r.get("details", [])],
            )
        )
    for r in doc.get("rules", []):
        conditions = [
            ConditionDef(c["question"], c["operator"], c["options"]) for c in r["conditions"]
        ]
        content.rules.append(
            RuleDef(file, r["slug"], r.get("procedure"), r["explanation"], _cite(r), conditions)
        )
    for r in doc.get("dependencies", []):
        content.dependencies.append(
            DependencyDef(file, r["before"], r["after"], r["kind"], r.get("rule"), _cite(r))
        )


def _duplicates(file_slugs: list[tuple[str, str]], table: str) -> list[str]:
    counts = Counter(slug for _, slug in file_slugs)
    return [
        f"{file}: {slug}: slug duplicado em {table}"
        for file, slug in file_slugs
        if counts[slug] > 1
    ]


def _structure_problems(content: Content) -> list[str]:
    """Slugs únicos, referências por slug e coerência entre regras, perguntas e dependências."""
    problems: list[str] = []
    for table, records in (
        ("situations", content.situations),
        ("questions", content.questions),
        ("procedures", content.procedures),
        ("rules", content.rules),
    ):
        problems += _duplicates([(r.file, r.slug) for r in records], table)

    agencies = set(Agency.objects.values_list("slug", flat=True))
    procedures = {p.slug for p in content.procedures}
    questions = {q.slug: q for q in content.questions}
    situations = {s.slug for s in content.situations}
    rules = {r.slug: r for r in content.rules}
    options = {q.slug: {slug for slug, _ in q.options} for q in content.questions}

    for s in content.situations:
        problems += [
            f"{s.file}: {s.slug}: procedimento inexistente em candidates: {c}"
            for c in s.candidates
            if c not in procedures
        ]
    for q in content.questions:
        problems += [
            f"{q.file}: {q.slug}: situação inexistente: {s}"
            for s in q.situations
            if s not in situations
        ]
        slugs = [slug for slug, _ in q.options]
        problems += [
            f"{q.file}: {q.slug}: opção duplicada: {slug}"
            for slug, n in Counter(slugs).items()
            if n > 1
        ]
        problems += [
            f"{q.file}: {q.slug}: slug de opção reservado: {slug}"
            for slug in slugs
            if slug in RESERVED_OPTION_SLUGS
        ]
    for p in content.procedures:
        if p.agency not in agencies:
            problems.append(f"{p.file}: {p.slug}: órgão inexistente: {p.agency}")
        if p.clarifies is not None:
            clarified = questions.get(p.clarifies)
            if clarified is None:
                problems.append(
                    f"{p.file}: {p.slug}: pergunta inexistente em clarifies: {p.clarifies}"
                )
            elif not clarified.allows_unknown:
                problems.append(
                    f"{p.file}: {p.slug}: clarifies: {p.clarifies} não permite 'não sei'"
                )
        kinds = Counter(d.kind for d in p.details)
        problems += [
            f"{p.file}: {p.slug}: detalhe duplicado: {kind}" for kind, n in kinds.items() if n > 1
        ]

    used_by_dependency = {d.rule for d in content.dependencies if d.rule is not None}
    for r in content.rules:
        if r.procedure is not None and r.procedure not in procedures:
            problems.append(f"{r.file}: {r.slug}: procedimento inexistente: {r.procedure}")
        if not r.conditions:
            problems.append(f"{r.file}: {r.slug}: regra sem condições")
        if r.procedure is None and r.slug not in used_by_dependency:
            problems.append(f"{r.file}: {r.slug}: regra órfã (sem procedure e sem dependência)")
        for c in r.conditions:
            if c.question not in questions:
                problems.append(f"{r.file}: {r.slug}: pergunta inexistente: {c.question}")
                continue
            if not c.options:
                problems.append(f"{r.file}: {r.slug}: condição sem opções ({c.question})")
            problems += [
                f"{r.file}: {r.slug}: opção {o} não pertence à pergunta {c.question}"
                for o in c.options
                if o not in options[c.question]
            ]

    seen: set[tuple[str, str]] = set()
    for d in content.dependencies:
        for end in (d.before, d.after):
            if end not in procedures:
                problems.append(f"{d.file}: {d.label}: procedimento inexistente: {end}")
        if d.before == d.after:
            problems.append(f"{d.file}: {d.label}: dependência de um procedimento sobre ele mesmo")
        if (d.before, d.after) in seen:
            problems.append(f"{d.file}: {d.label}: par before/after duplicado")
        seen.add((d.before, d.after))
        if d.kind == Dependency.Kind.CONDITIONAL and d.rule is None:
            problems.append(f"{d.file}: {d.label}: dependência CONDITIONAL sem rule")
        if d.kind != Dependency.Kind.CONDITIONAL and d.rule is not None:
            problems.append(f"{d.file}: {d.label}: rule só é permitida em dependência CONDITIONAL")
        if d.rule is not None:
            used = rules.get(d.rule)
            if used is None:
                problems.append(f"{d.file}: {d.label}: regra inexistente: {d.rule}")
            elif used.procedure is not None:
                problems.append(
                    f"{d.file}: {d.label}: regra {d.rule} define aplicabilidade (tem procedure)"
                )
    return problems + _cycle_problems(content, procedures)


def _cycle_problems(content: Content, procedures: set[str]) -> list[str]:
    edges = {
        (d.before, d.after)
        for d in content.dependencies
        if d.before != d.after and d.before in procedures and d.after in procedures
    }
    try:
        kahn_layers(procedures, edges)
    except DependencyCycleError as exc:
        in_cycle = set(exc.nodes)
        first = next(
            d
            for d in content.dependencies
            if d.before != d.after and d.before in in_cycle and d.after in in_cycle
        )
        return [f"{first.file}: {first.label}: {exc}"]
    return []


def _citations(content: Content) -> Iterator[tuple[str, str, str, Cite]]:
    """(arquivo, dono, onde, citação) de cada afirmação do conteúdo."""
    for p in content.procedures:
        yield p.file, p.slug, "procedimento", p.cite
        for name, items in (
            ("requisito", p.requirements),
            ("canal", p.channels),
            ("detalhe", p.details),
        ):
            for i, item in enumerate(items):
                yield p.file, p.slug, f"{name}[{i}]", item.cite
    for r in content.rules:
        yield r.file, r.slug, "regra", r.cite
    for d in content.dependencies:
        yield d.file, d.label, "dependência", d.cite


def _latest_snapshots(slugs: set[str]) -> dict[str, SourceSnapshot]:
    """Snapshot da importação OK mais recente de cada fonte que tem uma."""
    latest: dict[str, SourceSnapshot] = {}
    imports = (
        SourceImport.objects.filter(source__slug__in=slugs, outcome=SourceImport.Outcome.OK)
        .select_related("source", "snapshot")
        .order_by("source__slug", "-fetched_at", "-id")
    )
    for imported in imports:
        if imported.snapshot is not None:
            latest.setdefault(imported.source.slug, imported.snapshot)
    return latest


def _citation_problems(content: Content) -> tuple[list[str], dict[str, SourceSnapshot]]:
    citations = list(_citations(content))
    wanted = {cite.source for *_, cite in citations}
    existing = set(Source.objects.filter(slug__in=wanted).values_list("slug", flat=True))
    snapshots = _latest_snapshots(existing)
    texts = {slug: snapshot_text(snapshot) for slug, snapshot in snapshots.items()}
    problems: list[str] = []
    for file, owner, where, cite in citations:
        if cite.source not in existing:
            problems.append(f"{file}: {owner}: {where}: fonte inexistente: {cite.source}")
        elif cite.source not in texts:
            problems.append(
                f"{file}: {owner}: {where}: fonte {cite.source} sem importação bem-sucedida; "
                "rode fetch_sources"
            )
        elif not contains_excerpt(texts[cite.source], cite.excerpt):
            problems.append(
                f"{file}: {owner}: {where}: trecho não encontrado na fonte {cite.source}"
            )
    return problems, snapshots


def validate(directory: Path) -> tuple[Content, dict[str, SourceSnapshot]]:
    """Lê e valida todo o conteúdo sem escrever no banco; acumula os problemas."""
    if not directory.is_dir():
        raise ContentError([f"{directory}: -: diretório inexistente"])
    files = sorted(p for p in directory.glob("*.toml") if p.name != "sources.toml")
    if not files:
        raise ContentError([f"{directory}: -: nenhum arquivo de conteúdo (*.toml) encontrado"])
    content = Content()
    problems: list[str] = []
    for path in files:
        try:
            doc = read_toml(path)
        except ContentError as exc:
            problems += exc.lines
            continue
        found = check_document(doc, _TABLES, path.name)
        problems += found
        if not found:
            _parse(path.name, doc, content)
    if problems:
        raise ContentError(problems)
    problems = _structure_problems(content)
    citation_problems, snapshots = _citation_problems(content)
    problems += citation_problems
    if problems:
        raise ContentError(problems)
    return content, snapshots


def _replace(content: Content, snapshots: dict[str, SourceSnapshot]) -> None:
    for model in (Dependency, Rule, Situation, Procedure, Question):
        model.objects.all().delete()

    question_by_slug: dict[str, Question] = {}
    option_by_key: dict[tuple[str, str], AnswerOption] = {}
    for q in content.questions:
        question = Question.objects.create(
            slug=q.slug, text=q.text, kind=q.kind, allows_unknown=q.allows_unknown, order=q.order
        )
        question_by_slug[q.slug] = question
        for slug, label in q.options:
            option_by_key[(q.slug, slug)] = AnswerOption.objects.create(
                question=question,
                slug=slug,
                label=label,
                out_of_coverage=slug in q.out_of_coverage,
            )

    agency_by_slug = {a.slug: a for a in Agency.objects.all()}
    procedure_by_slug: dict[str, Procedure] = {}
    for p in content.procedures:
        procedure = Procedure.objects.create(
            slug=p.slug,
            title=p.title,
            description=p.description,
            agency=agency_by_slug[p.agency],
            jurisdiction=p.jurisdiction,
            clarifies=question_by_slug[p.clarifies] if p.clarifies else None,
            snapshot=snapshots[p.cite.source],
            excerpt=p.cite.excerpt,
        )
        procedure_by_slug[p.slug] = procedure
        for item in p.requirements:
            Requirement.objects.create(
                procedure=procedure,
                description=item.text,
                snapshot=snapshots[item.cite.source],
                excerpt=item.cite.excerpt,
            )
        for item in p.channels:
            ServiceChannel.objects.create(
                procedure=procedure,
                kind=item.kind,
                description=item.text,
                url=item.url,
                snapshot=snapshots[item.cite.source],
                excerpt=item.cite.excerpt,
            )
        for item in p.details:
            ProcedureDetail.objects.create(
                procedure=procedure,
                kind=item.kind,
                text=item.text,
                snapshot=snapshots[item.cite.source],
                excerpt=item.cite.excerpt,
            )

    for s in content.situations:
        situation = Situation.objects.create(slug=s.slug, title=s.title)
        situation.candidates.set([procedure_by_slug[c] for c in s.candidates])
    for q in content.questions:
        question_by_slug[q.slug].situations.set(Situation.objects.filter(slug__in=q.situations))

    rule_by_slug: dict[str, Rule] = {}
    for r in content.rules:
        rule = Rule.objects.create(
            slug=r.slug,
            procedure=procedure_by_slug[r.procedure] if r.procedure else None,
            explanation=r.explanation,
            snapshot=snapshots[r.cite.source],
            excerpt=r.cite.excerpt,
        )
        rule_by_slug[r.slug] = rule
        for c in r.conditions:
            condition = Condition.objects.create(
                rule=rule, question=question_by_slug[c.question], operator=c.operator
            )
            condition.options.set([option_by_key[(c.question, o)] for o in c.options])

    for d in content.dependencies:
        Dependency.objects.create(
            before=procedure_by_slug[d.before],
            after=procedure_by_slug[d.after],
            kind=d.kind,
            rule=rule_by_slug[d.rule] if d.rule else None,
            snapshot=snapshots[d.cite.source],
            excerpt=d.cite.excerpt,
        )


_COUNTED: tuple[type[models.Model], ...] = (
    Situation,
    Question,
    AnswerOption,
    Procedure,
    ProcedureDetail,
    Requirement,
    ServiceChannel,
    Rule,
    Condition,
    Dependency,
)


def load_content(directory: Path) -> dict[str, int]:
    content, snapshots = validate(directory)
    with transaction.atomic():
        _replace(content, snapshots)
    return {model.__name__: model._default_manager.count() for model in _COUNTED}
