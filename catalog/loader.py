"""Carga de conteúdo do catálogo: valida tudo sem escrever e depois substitui o catálogo inteiro."""

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.db import models, transaction

from guidance.engine.model import DependencyKind, Operator, QuestionKind
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
    START_NODE,
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
    TriageChoice,
    TriageNode,
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
        {"help": str, "allows_unknown": bool, "order": int_range_of(Question, "order")},
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
            "requirements": [Schema({"description": str, **_CITATION}, {"rule": str})],
            "channels": [
                Schema(
                    {
                        "kind": frozenset(ServiceChannel.Kind.values),
                        "description": str,
                        **_CITATION,
                    },
                    {"url": text_of(ServiceChannel, "url"), "rule": str},
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
    "triage": Schema(
        {
            "slug": _slug(TriageNode),
            "text": str,
            "options": [
                Schema(
                    {"label": text_of(TriageChoice, "label")},
                    {
                        "next": str,
                        "situation": str,
                        "uncovered": bool,
                        "icon": frozenset(TriageChoice.Icon.values),
                    },
                )
            ],
        },
        {"help": str},
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
    rule: str | None = None  # só requisitos e canais; slug da regra que condiciona o item


@dataclass(frozen=True)
class ProcedureRecord:
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
class ConditionRecord:
    question: str
    operator: Operator  # validado pelo schema antes de virar registro
    options: list[str]


@dataclass(frozen=True)
class RuleRecord:
    file: str
    slug: str
    procedure: str | None
    explanation: str
    cite: Cite
    conditions: list[ConditionRecord]


@dataclass(frozen=True)
class DependencyRecord:
    file: str
    before: str
    after: str
    kind: DependencyKind  # validado pelo schema antes de virar registro
    rule: str | None
    cite: Cite

    @property
    def label(self) -> str:
        return f"{self.before}->{self.after}"


@dataclass(frozen=True)
class QuestionRecord:
    file: str
    slug: str
    text: str
    help_text: str
    kind: QuestionKind  # validado pelo schema antes de virar registro
    allows_unknown: bool
    order: int
    situations: list[str]
    options: list[tuple[str, str]]
    out_of_coverage: frozenset[str]  # slugs das opções sem orientação oficial


@dataclass(frozen=True)
class SituationRecord:
    file: str
    slug: str
    title: str
    candidates: list[str]


@dataclass(frozen=True)
class TriageOptionRecord:
    label: str
    next_node: str | None
    situation: str | None
    uncovered: bool
    icon: str = ""


@dataclass(frozen=True)
class TriageNodeRecord:
    file: str
    slug: str
    text: str
    help_text: str
    options: list[TriageOptionRecord]


@dataclass
class Content:
    situations: list[SituationRecord] = field(default_factory=list)
    questions: list[QuestionRecord] = field(default_factory=list)
    procedures: list[ProcedureRecord] = field(default_factory=list)
    rules: list[RuleRecord] = field(default_factory=list)
    dependencies: list[DependencyRecord] = field(default_factory=list)
    triage: list[TriageNodeRecord] = field(default_factory=list)


def _cite(raw: dict[str, Any]) -> Cite:
    return Cite(raw["source"], raw["excerpt"])


def _parse(file: str, doc: dict[str, Any], content: Content) -> None:
    for r in doc.get("situations", []):
        content.situations.append(SituationRecord(file, r["slug"], r["title"], r["candidates"]))
    for r in doc.get("questions", []):
        options = [(o["slug"], o["label"]) for o in r["options"]]
        uncovered = frozenset(o["slug"] for o in r["options"] if o.get("out_of_coverage", False))
        content.questions.append(
            QuestionRecord(
                file,
                r["slug"],
                r["text"],
                r.get("help", ""),
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
            ProcedureRecord(
                file,
                r["slug"],
                r["title"],
                r["description"],
                r["agency"],
                r["jurisdiction"],
                _cite(r),
                r.get("clarifies"),
                [
                    Item("", i["description"], "", _cite(i), i.get("rule"))
                    for i in r.get("requirements", [])
                ],
                [
                    Item(i["kind"], i["description"], i.get("url", ""), _cite(i), i.get("rule"))
                    for i in r.get("channels", [])
                ],
                [Item(i["kind"], i["text"], "", _cite(i)) for i in r.get("details", [])],
            )
        )
    for r in doc.get("rules", []):
        conditions = [
            ConditionRecord(c["question"], c["operator"], c["options"]) for c in r["conditions"]
        ]
        content.rules.append(
            RuleRecord(file, r["slug"], r.get("procedure"), r["explanation"], _cite(r), conditions)
        )
    for r in doc.get("triage", []):
        choices = [
            TriageOptionRecord(
                o["label"],
                o.get("next"),
                o.get("situation"),
                o.get("uncovered", False),
                o.get("icon", ""),
            )
            for o in r["options"]
        ]
        content.triage.append(
            TriageNodeRecord(file, r["slug"], r["text"], r.get("help", ""), choices)
        )
    for r in doc.get("dependencies", []):
        content.dependencies.append(
            DependencyRecord(file, r["before"], r["after"], r["kind"], r.get("rule"), _cite(r))
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

    procedures = {p.slug for p in content.procedures}
    questions = {q.slug: q for q in content.questions}
    situations = {s.slug for s in content.situations}
    rules = {r.slug: r for r in content.rules}

    problems += _situation_problems(content, procedures)
    problems += _question_problems(content, situations)
    problems += _procedure_problems(content, questions, rules)
    problems += _rule_problems(content, procedures, questions)
    problems += _dependency_problems(content, procedures, rules)
    if content.triage:
        problems += _triage_problems(content, situations)
    problems += _situation_question_problems(content, rules, questions)
    return problems + _cycle_problems(content, procedures)


def _situation_problems(content: Content, procedures: set[str]) -> list[str]:
    """Candidatos apontam para procedimentos existentes."""
    problems: list[str] = []
    for s in content.situations:
        problems += [
            f"{s.file}: {s.slug}: procedimento inexistente em candidates: {c}"
            for c in s.candidates
            if c not in procedures
        ]
    return problems


def _question_problems(content: Content, situations: set[str]) -> list[str]:
    """Situações existentes e opções únicas, fora dos slugs reservados."""
    problems: list[str] = []
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
    return problems


def _procedure_problems(
    content: Content, questions: dict[str, QuestionRecord], rules: dict[str, RuleRecord]
) -> list[str]:
    """Órgão, `clarifies`, regras dos itens e detalhes sem repetição."""
    problems: list[str] = []
    agencies = set(Agency.objects.values_list("slug", flat=True))
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
        for name, items in (("requisito", p.requirements), ("canal", p.channels)):
            for i, item in enumerate(items):
                if item.rule is None:
                    continue
                problems += _rule_ref_problems(f"{p.file}: {p.slug}: {name}[{i}]", item.rule, rules)
        kinds = Counter(d.kind for d in p.details)
        problems += [
            f"{p.file}: {p.slug}: detalhe duplicado: {kind}" for kind, n in kinds.items() if n > 1
        ]
    return problems


def _rule_problems(
    content: Content, procedures: set[str], questions: dict[str, QuestionRecord]
) -> list[str]:
    """Procedimento, uso e condições de cada regra."""
    problems: list[str] = []
    options = {q.slug: {slug for slug, _ in q.options} for q in content.questions}
    used_by_dependency = {d.rule for d in content.dependencies if d.rule is not None}
    used_by_item = {
        i.rule for p in content.procedures for i in (*p.requirements, *p.channels) if i.rule
    }
    used_by_rule_ref = used_by_dependency | used_by_item
    for r in content.rules:
        if r.procedure is not None and r.procedure not in procedures:
            problems.append(f"{r.file}: {r.slug}: procedimento inexistente: {r.procedure}")
        if not r.conditions:
            problems.append(f"{r.file}: {r.slug}: regra sem condições")
        if r.procedure is None and r.slug not in used_by_rule_ref:
            problems.append(
                f"{r.file}: {r.slug}: regra órfã (sem procedure, dependência, requisito ou canal)"
            )
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
    return problems


def _dependency_problems(
    content: Content, procedures: set[str], rules: dict[str, RuleRecord]
) -> list[str]:
    """Extremos existentes, pares únicos e regra só em dependência CONDITIONAL."""
    problems: list[str] = []
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
            problems += _rule_ref_problems(f"{d.file}: {d.label}", d.rule, rules)
    return problems


def _rule_ref_problems(where: str, rule_slug: str, rules: dict[str, RuleRecord]) -> list[str]:
    """Regra citada por requisito, canal ou dependência: existe e não define aplicabilidade."""
    rule = rules.get(rule_slug)
    if rule is None:
        return [f"{where}: regra inexistente: {rule_slug}"]
    if rule.procedure is not None:
        return [f"{where}: regra {rule_slug} define aplicabilidade (tem procedure)"]
    return []


def _situation_question_problems(
    content: Content, rules: dict[str, RuleRecord], questions: dict[str, QuestionRecord]
) -> list[str]:
    """Toda pergunta citada por regra de um procedimento relevante precisa estar ligada à situação.

    Relevantes = como em `guidance.repository.load_catalog`: candidatos, esclarecimentos de
    perguntas da situação e o fecho para trás por qualquer dependência.
    """
    parents: dict[str, list[str]] = {}
    for d in content.dependencies:
        parents.setdefault(d.after, []).append(d.before)
    problems: list[str] = []
    for situation in content.situations:
        relevant = set(situation.candidates) | {
            p.slug
            for p in content.procedures
            if p.clarifies in questions and situation.slug in questions[p.clarifies].situations
        }
        pending = list(relevant)
        while pending:
            for before in parents.get(pending.pop(), ()):
                if before not in relevant:
                    relevant.add(before)
                    pending.append(before)
        used: list[str] = [r.slug for r in content.rules if r.procedure in relevant]
        for p in content.procedures:
            if p.slug in relevant:
                used += [i.rule for i in (*p.requirements, *p.channels) if i.rule]
        used += [
            d.rule
            for d in content.dependencies
            if d.rule and d.kind == Dependency.Kind.CONDITIONAL and d.after in relevant
        ]
        reported: set[tuple[str, str]] = set()
        for slug in used:
            rule = rules.get(slug)
            for c in rule.conditions if rule else ():
                question = questions.get(c.question)
                if (
                    rule
                    and question
                    and situation.slug not in question.situations
                    and (slug, c.question) not in reported
                ):
                    reported.add((slug, c.question))
                    problems.append(
                        f"{rule.file}: {slug}: pergunta {c.question} não está ligada à situação "
                        f"{situation.slug}"
                    )
    return problems


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


def _triage_problems(content: Content, situations: set[str]) -> list[str]:
    """Funil de triagem: destinos válidos, sem ciclo e com toda situação e todo nó alcançáveis."""
    problems = _duplicates([(n.file, n.slug) for n in content.triage], "triage")
    nodes = {n.slug: n for n in content.triage}
    if START_NODE not in nodes:
        problems.append(f"{content.triage[0].file}: {START_NODE}: nó inicial ausente")
    edges: set[tuple[str, str]] = set()
    for n in content.triage:
        if not n.text.strip():
            problems.append(f"{n.file}: {n.slug}: text vazio")
        if not n.options:
            problems.append(f"{n.file}: {n.slug}: nó sem opções")
        for i, o in enumerate(n.options):
            where = f"{n.file}: {n.slug}: options[{i}]"
            if not o.label.strip():
                problems.append(f"{where}: label vazio")
            destinations = [o.next_node is not None, o.situation is not None, o.uncovered]
            if sum(destinations) != 1:
                problems.append(f"{where}: informe exatamente um entre next, situation e uncovered")
            if o.next_node is not None:
                if o.next_node in nodes:
                    edges.add((n.slug, o.next_node))
                else:
                    problems.append(f"{where}: nó inexistente em next: {o.next_node}")
            if o.situation is not None and o.situation not in situations:
                problems.append(f"{where}: situação inexistente: {o.situation}")
    try:
        kahn_layers(nodes, edges)
    except DependencyCycleError as exc:
        first = exc.nodes[0]
        problems.append(
            f"{nodes[first].file}: {first}: ciclo no funil de triagem envolvendo: "
            + ", ".join(exc.nodes)
        )
    adjacency: dict[str, list[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, []).append(target)
    reached = {START_NODE} & nodes.keys()
    pending = list(reached)
    while pending:
        for target in adjacency.get(pending.pop(), ()):
            if target not in reached:
                reached.add(target)
                pending.append(target)
    problems += [
        f"{n.file}: {n.slug}: nó inalcançável a partir de {START_NODE}"
        for n in content.triage
        if n.slug not in reached
    ]
    covered = {
        o.situation for n in content.triage if n.slug in reached for o in n.options if o.situation
    }
    problems += [
        f"{s.file}: {s.slug}: situação não alcançável pelo funil de triagem"
        for s in content.situations
        if s.slug not in covered
    ]
    return problems


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
    """Apaga e recria o catálogo; `bulk_create` por tabela, na ordem das chaves estrangeiras."""
    for model in (
        TriageNode,
        Dependency,
        Requirement,
        ServiceChannel,
        Rule,
        Situation,
        Procedure,
        Question,
    ):
        model.objects.all().delete()

    question_by_slug, option_by_key = _create_questions(content.questions)
    procedure_by_slug = _create_procedures(content.procedures, question_by_slug, snapshots)
    situation_by_slug = _create_situations(content, procedure_by_slug, question_by_slug)
    _create_triage(content.triage, situation_by_slug)
    rule_by_slug = _create_rules(
        content.rules, procedure_by_slug, question_by_slug, option_by_key, snapshots
    )
    # Requisitos e canais referenciam regras, então só nascem depois delas.
    _create_items(content.procedures, procedure_by_slug, rule_by_slug, snapshots)
    Dependency.objects.bulk_create(
        Dependency(
            before=procedure_by_slug[d.before],
            after=procedure_by_slug[d.after],
            kind=d.kind,
            rule=rule_by_slug[d.rule] if d.rule else None,
            snapshot=snapshots[d.cite.source],
            excerpt=d.cite.excerpt,
        )
        for d in content.dependencies
    )


def _create_questions(
    records: list[QuestionRecord],
) -> tuple[dict[str, Question], dict[tuple[str, str], AnswerOption]]:
    created = Question.objects.bulk_create(
        Question(
            slug=q.slug,
            text=q.text,
            help_text=q.help_text,
            kind=q.kind,
            allows_unknown=q.allows_unknown,
            order=q.order,
        )
        for q in records
    )
    question_by_slug = {q.slug: q for q in created}
    options = AnswerOption.objects.bulk_create(
        AnswerOption(
            question=question_by_slug[q.slug],
            slug=slug,
            label=label,
            out_of_coverage=slug in q.out_of_coverage,
        )
        for q in records
        for slug, label in q.options
    )
    return question_by_slug, {(o.question.slug, o.slug): o for o in options}


def _create_procedures(
    records: list[ProcedureRecord],
    question_by_slug: dict[str, Question],
    snapshots: dict[str, SourceSnapshot],
) -> dict[str, Procedure]:
    agency_by_slug = {a.slug: a for a in Agency.objects.all()}
    created = Procedure.objects.bulk_create(
        Procedure(
            slug=p.slug,
            title=p.title,
            description=p.description,
            agency=agency_by_slug[p.agency],
            jurisdiction=p.jurisdiction,
            clarifies=question_by_slug[p.clarifies] if p.clarifies else None,
            snapshot=snapshots[p.cite.source],
            excerpt=p.cite.excerpt,
        )
        for p in records
    )
    procedure_by_slug = {p.slug: p for p in created}
    ProcedureDetail.objects.bulk_create(
        ProcedureDetail(
            procedure=procedure_by_slug[p.slug],
            kind=item.kind,
            text=item.text,
            snapshot=snapshots[item.cite.source],
            excerpt=item.cite.excerpt,
        )
        for p in records
        for item in p.details
    )
    return procedure_by_slug


def _create_situations(
    content: Content,
    procedure_by_slug: dict[str, Procedure],
    question_by_slug: dict[str, Question],
) -> dict[str, Situation]:
    created = Situation.objects.bulk_create(
        Situation(slug=s.slug, title=s.title) for s in content.situations
    )
    situation_by_slug = {s.slug: s for s in created}
    Situation.candidates.through._default_manager.bulk_create(
        Situation.candidates.through(
            situation_id=situation_by_slug[s.slug].pk, procedure_id=procedure_by_slug[c].pk
        )
        for s in content.situations
        for c in s.candidates
    )
    Question.situations.through._default_manager.bulk_create(
        Question.situations.through(
            question_id=question_by_slug[q.slug].pk, situation_id=situation_by_slug[slug].pk
        )
        for q in content.questions
        for slug in q.situations
    )
    return situation_by_slug


def _create_triage(nodes: list[TriageNodeRecord], situation_by_slug: dict[str, Situation]) -> None:
    created = TriageNode.objects.bulk_create(
        TriageNode(slug=n.slug, text=n.text, help_text=n.help_text) for n in nodes
    )
    node_by_slug = {n.slug: n for n in created}
    TriageChoice.objects.bulk_create(
        TriageChoice(
            node=node_by_slug[n.slug],
            label=o.label,
            icon=o.icon,
            order=order,
            next_node=node_by_slug[o.next_node] if o.next_node else None,
            situation=situation_by_slug[o.situation] if o.situation else None,
        )
        for n in nodes
        for order, o in enumerate(n.options, start=1)
    )


def _create_rules(
    records: list[RuleRecord],
    procedure_by_slug: dict[str, Procedure],
    question_by_slug: dict[str, Question],
    option_by_key: dict[tuple[str, str], AnswerOption],
    snapshots: dict[str, SourceSnapshot],
) -> dict[str, Rule]:
    created = Rule.objects.bulk_create(
        Rule(
            slug=r.slug,
            procedure=procedure_by_slug[r.procedure] if r.procedure else None,
            explanation=r.explanation,
            snapshot=snapshots[r.cite.source],
            excerpt=r.cite.excerpt,
        )
        for r in records
    )
    rule_by_slug = {r.slug: r for r in created}
    pairs = [(r, c) for r in records for c in r.conditions]
    conditions = Condition.objects.bulk_create(
        Condition(
            rule=rule_by_slug[r.slug], question=question_by_slug[c.question], operator=c.operator
        )
        for r, c in pairs
    )
    Condition.options.through._default_manager.bulk_create(
        Condition.options.through(
            condition_id=condition.pk, answeroption_id=option_by_key[(c.question, o)].pk
        )
        for condition, (_, c) in zip(conditions, pairs, strict=True)
        for o in c.options
    )
    return rule_by_slug


def _create_items(
    records: list[ProcedureRecord],
    procedure_by_slug: dict[str, Procedure],
    rule_by_slug: dict[str, Rule],
    snapshots: dict[str, SourceSnapshot],
) -> None:
    Requirement.objects.bulk_create(
        Requirement(
            procedure=procedure_by_slug[p.slug],
            description=item.text,
            rule=rule_by_slug[item.rule] if item.rule else None,
            snapshot=snapshots[item.cite.source],
            excerpt=item.cite.excerpt,
        )
        for p in records
        for item in p.requirements
    )
    ServiceChannel.objects.bulk_create(
        ServiceChannel(
            procedure=procedure_by_slug[p.slug],
            kind=item.kind,
            description=item.text,
            url=item.url,
            rule=rule_by_slug[item.rule] if item.rule else None,
            snapshot=snapshots[item.cite.source],
            excerpt=item.cite.excerpt,
        )
        for p in records
        for item in p.channels
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
    TriageNode,
    TriageChoice,
)


def load_content(directory: Path) -> dict[str, int]:
    content, snapshots = validate(directory)
    with transaction.atomic():
        _replace(content, snapshots)
    return {model.__name__: model._default_manager.count() for model in _COUNTED}
