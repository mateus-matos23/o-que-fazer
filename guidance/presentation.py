"""Apresentação: transforma o resultado do motor em linhas prontas para os templates, sem I/O."""

from dataclasses import dataclass

from catalog.models import ServiceChannel
from guidance.engine.channels import ChannelPreference, lacks_preferred, order_channels
from guidance.engine.effect import AnswerEffect
from guidance.engine.model import (
    Catalog,
    ChannelDef,
    DependencyDef,
    DetailKind,
    Facts,
    ProcedureDef,
    RequirementDef,
    Tri,
    Unknown,
)
from guidance.engine.plan import Plan, PlanStep


@dataclass(frozen=True, slots=True)
class EffectView:
    entered: tuple[str, ...]
    left: tuple[str, ...]
    in_play: int


def effect_view(catalog: Catalog, effect: AnswerEffect | None) -> EffectView | None:
    """Sem mudança a mostrar, não há bloco."""
    if effect is None or not (effect.entered or effect.left or effect.in_play):
        return None
    return EffectView(
        tuple(catalog.procedures[s].title for s in effect.entered),
        tuple(catalog.procedures[s].title for s in effect.left),
        effect.in_play,
    )


@dataclass(frozen=True, slots=True)
class DependencyLine:
    title: str
    suggestion: bool  # RECOMMENDED: sugestão de ordem, não exigência (RN08)


@dataclass(frozen=True, slots=True)
class ChannelLine:
    kind_label: str
    channel: ChannelDef
    maybe: str = ""  # explicação da regra quando o canal "pode valer" (RF25)


@dataclass(frozen=True, slots=True)
class RequirementLine:
    description: str
    maybe: str = ""


@dataclass(frozen=True, slots=True)
class StepView:
    step: PlanStep
    required_for: tuple[str, ...]
    after: tuple[DependencyLine, ...]
    requirements: tuple[RequirementLine, ...]
    channels: tuple[ChannelLine, ...]
    costs: tuple[str, ...]
    deadlines: tuple[str, ...]
    channel_notice: str = ""


def step_view(
    catalog: Catalog, step: PlanStep, preference: ChannelPreference | None = None
) -> StepView:
    def title(slug: str) -> str:
        return catalog.procedures[slug].title

    def line(dependency: DependencyDef) -> DependencyLine:
        return DependencyLine(title(dependency.before), dependency.kind == "RECOMMENDED")

    procedure = step.procedure
    return StepView(
        step=step,
        required_for=tuple(title(slug) for slug in step.required_for),
        after=tuple(line(d) for d in step.after),
        requirements=requirement_lines(step.requirements),
        channels=channel_lines(step.channels, preference),
        costs=detail_texts(procedure, "COST"),
        deadlines=detail_texts(procedure, "DEADLINE"),
        channel_notice=preference.missing_notice
        if preference and lacks_preferred([c for c, _ in step.channels], preference)
        else "",
    )


def _maybe(item: RequirementDef | ChannelDef, tri: Tri) -> str:
    return item.rule.explanation if item.rule and tri is Tri.UNDETERMINED else ""


def requirement_lines(
    pairs: tuple[tuple[RequirementDef, Tri], ...],
) -> tuple[RequirementLine, ...]:
    return tuple(RequirementLine(r.description, _maybe(r, t)) for r, t in pairs)


def channel_lines(
    pairs: tuple[tuple[ChannelDef, Tri], ...], preference: ChannelPreference | None = None
) -> tuple[ChannelLine, ...]:
    return tuple(
        ChannelLine(ServiceChannel.Kind(c.kind).label, c, _maybe(c, t))
        for c, t in order_channels(pairs, preference)
    )


def detail_texts(procedure: ProcedureDef, kind: DetailKind) -> tuple[str, ...]:
    return tuple(d.text for d in procedure.details if d.kind == kind)


@dataclass(frozen=True, slots=True)
class UncoveredLine:
    question_text: str
    option_label: str


def uncovered_lines(catalog: Catalog, pairs: tuple[tuple[str, str], ...]) -> list[UncoveredLine]:
    lines = []
    for question_slug, option_slug in pairs:
        question = catalog.questions[question_slug]
        label = next(o.label for o in question.options if o.slug == option_slug)
        lines.append(UncoveredLine(question.text, label))
    return lines


def plan_context(
    catalog: Catalog, result: Plan, preference: ChannelPreference | None
) -> dict[str, object]:
    steps = [step_view(catalog, step, preference) for step in result.steps]
    return {
        "steps": steps,
        "start_steps": [s for s in steps if s.step.layer == 1],
        "requirement_steps": [s for s in steps if s.requirements],
        "uncovered": uncovered_lines(catalog, result.uncovered),
        "undetermined": [catalog.procedures[s].title for s in result.undetermined],
    }


@dataclass(frozen=True, slots=True)
class AnswerLine:
    question_slug: str
    text: str
    labels: tuple[str, ...]
    unknown: bool


def answer_lines(catalog: Catalog, facts: Facts) -> list[AnswerLine]:
    lines = []
    for question in sorted(catalog.questions.values(), key=lambda q: q.order):
        answer = facts.get(question.slug)
        if answer is None:
            continue
        chosen = () if isinstance(answer, Unknown) else answer
        lines.append(
            AnswerLine(
                question.slug,
                question.text,
                tuple(o.label for o in question.options if o.slug in chosen),
                isinstance(answer, Unknown),
            )
        )
    return lines
