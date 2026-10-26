"""Montagem do plano: junta aplicabilidade (evaluation) e ordem (ordering) sem misturá-las."""

from collections import defaultdict, deque
from dataclasses import dataclass

from guidance.engine.evaluation import (
    evaluate,
    evaluate_procedure,
    evaluate_rule,
    pending_rule_questions,
    visible_items,
)
from guidance.engine.model import (
    Catalog,
    ChannelDef,
    DependencyDef,
    Facts,
    ProcedureDef,
    QuestionDef,
    RequirementDef,
    RuleDef,
    Tri,
    Unknown,
)
from guidance.engine.ordering import kahn_layers


@dataclass(frozen=True, slots=True)
class PlanStep:
    procedure: ProcedureDef
    layer: int  # 1-based; mesma camada = etapas independentes entre si
    status: Tri  # APPLICABLE, ou UNDETERMINED para pré-requisito puxado ou esclarecimento
    reasons: tuple[RuleDef, ...]  # regras APPLICABLE que justificam a etapa
    required_for: tuple[str, ...]  # etapas que exigem esta (quando entrou como pré-requisito)
    clarifies: QuestionDef | None  # pergunta respondida com "não sei"
    after: tuple[DependencyDef, ...]  # dependências ativas "depois de X" com X no plano (RF19)
    # Itens que valem para os fatos (RF25), na ordem original; UNDETERMINED = "pode valer".
    requirements: tuple[tuple[RequirementDef, Tri], ...]
    channels: tuple[tuple[ChannelDef, Tri], ...]


@dataclass(frozen=True, slots=True)
class Plan:
    steps: tuple[PlanStep, ...]
    undetermined: tuple[str, ...]  # candidatos indeterminados que não entraram
    # (pergunta, opção) escolhidas que estão fora da cobertura; UNKNOWN nunca entra
    uncovered: tuple[tuple[str, str], ...]


def build_plan(catalog: Catalog, facts: Facts) -> Plan:
    evaluations = evaluate(catalog, facts)

    status: dict[str, Tri] = {}
    reasons: dict[str, tuple[RuleDef, ...]] = {}
    clarifies: dict[str, QuestionDef] = {}
    required_for: dict[str, set[str]] = defaultdict(set)
    for slug, evaluation in evaluations.items():
        if evaluation.status is Tri.APPLICABLE:
            status[slug] = Tri.APPLICABLE
            reasons[slug] = tuple(r for r, s in evaluation.rules if s is Tri.APPLICABLE)
    pending = pending_rule_questions(catalog, facts, evaluations)
    for slug, procedure in catalog.procedures.items():
        if (
            procedure.clarifies is not None
            and facts.get(procedure.clarifies) is Unknown.UNKNOWN
            and procedure.clarifies in pending  # só enquanto a pergunta ainda importa
        ):
            clarifies[slug] = catalog.questions[procedure.clarifies]
            status.setdefault(slug, Tri.UNDETERMINED)
            reasons.setdefault(slug, ())

    active = [
        d
        for d in catalog.dependencies
        if d.kind == "MANDATORY"
        or (d.kind == "CONDITIONAL" and d.rule and evaluate_rule(d.rule, facts) is Tri.APPLICABLE)
    ]
    incoming: dict[str, list[str]] = defaultdict(list)
    for d in active:
        incoming[d.after].append(d.before)

    # Fecho de pré-requisitos: só entra o que não é NOT_APPLICABLE; nunca inventa exigência.
    pulled: set[str] = set()
    queue = deque(status)
    while queue:
        after = queue.popleft()
        for before in incoming[after]:
            if before not in status:
                evaluation = evaluate_procedure(catalog.procedures[before], facts)
                if evaluation.status is Tri.NOT_APPLICABLE:
                    continue
                status[before] = evaluation.status
                reasons[before] = tuple(r for r, s in evaluation.rules if s is Tri.APPLICABLE)
                pulled.add(before)
                queue.append(before)
            if before in pulled:
                required_for[before].add(after)

    edges = [(d.before, d.after) for d in active if d.before in status and d.after in status]
    layers = kahn_layers(status, edges)  # ciclo propaga: nunca plano parcial

    # RECOMMENDED (RN08) só desempata dentro da camada.
    recommended = [d for d in catalog.dependencies if d.kind == "RECOMMENDED"]
    layer_of = {slug: i for i, layer in enumerate(layers, 1) for slug in layer}
    ordered: list[str] = []
    for i, layer in enumerate(layers, 1):
        inner = [
            (d.before, d.after)
            for d in recommended
            if layer_of.get(d.before) == i and layer_of.get(d.after) == i
        ]
        ordered.extend(slug for sub in kahn_layers(layer, inner) for slug in sub)

    shown = [d for d in (*active, *recommended) if d.before in status and d.after in status]
    steps = tuple(
        PlanStep(
            procedure=catalog.procedures[slug],
            layer=layer_of[slug],
            status=status[slug],
            reasons=reasons[slug],
            required_for=tuple(sorted(required_for[slug])),
            clarifies=clarifies.get(slug),
            after=tuple(d for d in shown if d.after == slug),
            requirements=visible_items(catalog.procedures[slug].requirements, facts),
            channels=visible_items(catalog.procedures[slug].channels, facts),
        )
        for slug in ordered
    )
    undetermined = tuple(
        sorted(
            slug
            for slug, e in evaluations.items()
            if e.status is Tri.UNDETERMINED and slug not in status
        )
    )
    return Plan(steps, undetermined, _uncovered(catalog, facts))


def _uncovered(catalog: Catalog, facts: Facts) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for question in sorted(catalog.questions.values(), key=lambda q: (q.order, q.slug)):
        answer = facts.get(question.slug)
        if answer is None or isinstance(answer, Unknown):
            continue
        pairs.extend(
            (question.slug, o.slug)
            for o in question.options
            if o.out_of_coverage and o.slug in answer
        )
    return tuple(pairs)
