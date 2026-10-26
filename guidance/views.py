import logging
from dataclasses import dataclass
from typing import Literal

from django.db.models import Prefetch, Q
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from catalog.models import (
    START_NODE,
    Procedure,
    ServiceChannel,
    Situation,
    TriageChoice,
    TriageNode,
)
from guidance.engine.channels import ChannelPreference, lacks_preferred, order_channels
from guidance.engine.effect import answer_effect
from guidance.engine.evaluation import evaluate, visible_items
from guidance.engine.model import (
    Answer,
    Catalog,
    ChannelDef,
    DependencyDef,
    Facts,
    ProcedureDef,
    RequirementDef,
    Tri,
    Unknown,
)
from guidance.engine.ordering import DependencyCycleError
from guidance.engine.plan import Plan, PlanStep, build_plan
from guidance.engine.questions import next_question
from guidance.forms import AnswerForm, ChannelPreferenceForm, SearchForm
from guidance.repository import (
    ProcedureNotFound,
    SituationNotFound,
    load_catalog,
    load_procedure,
)
from guidance.session import (
    clear_situation,
    pop_effect,
    read_channel_preference,
    read_facts,
    write_answer,
    write_channel_preference,
    write_effect,
)

logger = logging.getLogger(__name__)


def _load(slug: str) -> Catalog:
    try:
        return load_catalog(slug)
    except SituationNotFound:
        raise Http404("Situação não encontrada") from None


def _see_other(url: str) -> HttpResponseRedirect:
    response = HttpResponseRedirect(url)
    response.status_code = 303  # PRG: o navegador refaz a requisição como GET
    return response


@dataclass(frozen=True, slots=True)
class EffectView:
    entered: tuple[str, ...]
    left: tuple[str, ...]
    in_play: int


def _effect_view(request: HttpRequest, catalog: Catalog) -> EffectView | None:
    """Consome o aviso de uso único; sem mudança a mostrar, não há bloco."""
    effect = pop_effect(request.session, catalog)
    if effect is None or not (effect.entered or effect.left or effect.in_play):
        return None
    return EffectView(
        tuple(catalog.procedures[s].title for s in effect.entered),
        tuple(catalog.procedures[s].title for s in effect.left),
        effect.in_play,
    )


def _answer_and_record_effect(
    request: HttpRequest, catalog: Catalog, before: Facts, question_slug: str, answer: Answer
) -> None:
    write_answer(request.session, catalog.situation_slug, question_slug, answer)
    after = {**before, question_slug: answer}
    try:
        effect = answer_effect(catalog, before, after)
    except DependencyCycleError:
        return  # a view do plano já registra e mostra o erro
    write_effect(request.session, catalog.situation_slug, effect)


@require_GET
def situation_list(request: HttpRequest) -> HttpResponse:
    situations = Situation.objects.order_by("title")
    return render(request, "guidance/situation_list.html", {"situations": situations})


def _triage_node(slug: str) -> TriageNode | None:
    return (
        TriageNode.objects.filter(slug=slug)
        .prefetch_related(
            Prefetch("choices", TriageChoice.objects.select_related("next_node", "situation"))
        )
        .first()
    )


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    node = _triage_node(START_NODE)
    if node is None:  # conteúdo sem funil: a lista de situações é a entrada
        return situation_list(request)
    return render(request, "guidance/triage.html", {"node": node, "is_start": True})


@require_GET
def triage(request: HttpRequest, slug: str) -> HttpResponse:
    if slug == START_NODE:
        return redirect("guidance:home")  # o início tem uma só URL
    node = _triage_node(slug)
    if node is None:
        raise Http404("Pergunta não encontrada")
    return render(request, "guidance/triage.html", {"node": node, "is_start": False})


@require_GET
def uncovered(request: HttpRequest) -> HttpResponse:
    situations = Situation.objects.order_by("title")
    return render(request, "guidance/uncovered.html", {"situations": situations})


@require_http_methods(["GET", "POST"])
def question(request: HttpRequest, slug: str) -> HttpResponse:
    catalog = _load(slug)
    facts = read_facts(request.session, catalog)
    if request.method == "POST":
        current = catalog.questions.get(request.POST.get("question", ""))
        if current is None:
            return HttpResponseBadRequest("Pergunta inválida para esta situação.")
        form = AnswerForm(current, request.POST, facts.get(current.slug))
        if form.is_valid():
            _answer_and_record_effect(request, catalog, facts, current.slug, form.cleaned_answer())
            return _see_other(reverse("guidance:question", args=[slug]))
    else:
        current = next_question(catalog, facts, evaluate(catalog, facts))
        if current is None:
            if read_channel_preference(request.session) is None:
                return redirect("guidance:channel_preference", slug=slug)
            return redirect("guidance:plan", slug=slug)  # o plano consome o aviso
        form = AnswerForm(current, initial_answer=facts.get(current.slug))
    context = {
        "catalog": catalog,
        "question": current,
        "form": form,
        "answer_count": len(facts),
        "effect": _effect_view(request, catalog) if request.method == "GET" else None,
    }
    return render(request, "guidance/question.html", context)


@require_http_methods(["GET", "POST"])
def channel_preference(request: HttpRequest, slug: str) -> HttpResponse:
    catalog = _load(slug)  # não toca no aviso de efeito: quem consome é o plano
    current = read_channel_preference(request.session)
    if request.method == "POST":
        form = ChannelPreferenceForm(request.POST)
        if form.is_valid():
            write_channel_preference(request.session, form.cleaned_data["preference"])
            return _see_other(reverse("guidance:plan", args=[slug]))
    else:
        form = ChannelPreferenceForm(initial={"preference": current.slug if current else None})
    return render(request, "guidance/channel_preference.html", {"catalog": catalog, "form": form})


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


def _step_view(
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
        requirements=_requirement_lines(step.requirements),
        channels=_channel_lines(step.channels, preference),
        costs=_detail_texts(procedure, "COST"),
        deadlines=_detail_texts(procedure, "DEADLINE"),
        channel_notice=preference.missing_notice
        if preference and lacks_preferred([c for c, _ in step.channels], preference)
        else "",
    )


def _maybe(item: RequirementDef | ChannelDef, tri: Tri) -> str:
    return item.rule.explanation if item.rule and tri is Tri.UNDETERMINED else ""


def _requirement_lines(
    pairs: tuple[tuple[RequirementDef, Tri], ...],
) -> tuple[RequirementLine, ...]:
    return tuple(RequirementLine(r.description, _maybe(r, t)) for r, t in pairs)


def _channel_lines(
    pairs: tuple[tuple[ChannelDef, Tri], ...], preference: ChannelPreference | None = None
) -> tuple[ChannelLine, ...]:
    return tuple(
        ChannelLine(ServiceChannel.Kind(c.kind).label, c, _maybe(c, t))
        for c, t in order_channels(pairs, preference)
    )


def _detail_texts(procedure: ProcedureDef, kind: Literal["COST", "DEADLINE"]) -> tuple[str, ...]:
    return tuple(d.text for d in procedure.details if d.kind == kind)


@dataclass(frozen=True, slots=True)
class UncoveredLine:
    question_text: str
    option_label: str


def _uncovered_lines(catalog: Catalog, pairs: tuple[tuple[str, str], ...]) -> list[UncoveredLine]:
    lines = []
    for question_slug, option_slug in pairs:
        question = catalog.questions[question_slug]
        label = next(o.label for o in question.options if o.slug == option_slug)
        lines.append(UncoveredLine(question.text, label))
    return lines


def plan(request: HttpRequest, slug: str) -> HttpResponse:
    catalog = _load(slug)
    facts = read_facts(request.session, catalog)
    evaluations = evaluate(catalog, facts)
    if next_question(catalog, facts, evaluations) is not None:
        return redirect("guidance:question", slug=slug)  # plano só com perguntas encerradas
    try:
        result = build_plan(catalog, facts, evaluations)
    except DependencyCycleError as error:
        logger.error("ciclo entre dependências: situação=%s procedimentos=%s", slug, error.nodes)
        return render(
            request,
            "guidance/error.html",
            {"message": "Não foi possível montar o plano agora. Tente novamente mais tarde."},
            status=500,
        )
    preference = read_channel_preference(request.session)
    context = {
        "catalog": catalog,
        "preference": preference,
        **_plan_context(catalog, result, preference),
        "effect": _effect_view(request, catalog),
    }
    return render(request, "guidance/plan.html", context)


def _plan_context(
    catalog: Catalog, result: Plan, preference: ChannelPreference | None
) -> dict[str, object]:
    steps = [_step_view(catalog, step, preference) for step in result.steps]
    return {
        "steps": steps,
        "start_steps": [s for s in steps if s.step.layer == 1],
        "requirement_steps": [s for s in steps if s.requirements],
        "uncovered": _uncovered_lines(catalog, result.uncovered),
        "undetermined": [catalog.procedures[s].title for s in result.undetermined],
    }


@dataclass(frozen=True, slots=True)
class AnswerLine:
    question_slug: str
    text: str
    labels: tuple[str, ...]
    unknown: bool


def review(request: HttpRequest, slug: str) -> HttpResponse:
    catalog = _load(slug)
    facts = read_facts(request.session, catalog)
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
    return render(request, "guidance/review.html", {"catalog": catalog, "lines": lines})


@require_http_methods(["GET", "POST"])
def edit_answer(request: HttpRequest, slug: str, question_slug: str) -> HttpResponse:
    catalog = _load(slug)
    current = catalog.questions.get(question_slug)
    if current is None:
        raise Http404("Pergunta não encontrada")
    facts = read_facts(request.session, catalog)
    if request.method == "POST":
        form = AnswerForm(current, request.POST, facts.get(current.slug))
        if form.is_valid():
            _answer_and_record_effect(request, catalog, facts, current.slug, form.cleaned_answer())
            return _see_other(reverse("guidance:question", args=[slug]))  # recalcula (invariante 8)
    else:
        form = AnswerForm(current, initial_answer=facts.get(current.slug))
    context = {"catalog": catalog, "question": current, "form": form, "answer_count": len(facts)}
    return render(request, "guidance/question.html", context)


@require_POST
def restart(request: HttpRequest, slug: str) -> HttpResponse:
    _load(slug)
    clear_situation(request.session, slug)
    return _see_other(reverse("guidance:question", args=[slug]))


def search(request: HttpRequest) -> HttpResponse:
    form = SearchForm(request.GET if "q" in request.GET else None)
    results = None
    if form.is_valid():
        # shortcut: icontains não ignora acentos ("demissao" não acha "demissão");
        # trocar por unaccent ou pela busca textual do Postgres se o catálogo crescer.
        term = form.cleaned_data["q"]
        results = (
            Procedure.objects.filter(Q(title__icontains=term) | Q(description__icontains=term))
            .select_related("agency")
            .order_by("title")
        )
    return render(request, "guidance/search.html", {"form": form, "results": results})


def procedure_detail(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        procedure = load_procedure(slug)
    except ProcedureNotFound:
        raise Http404("Serviço não encontrado") from None
    context = {
        "procedure": procedure,
        # Sem fatos: itens com regra aparecem marcados como "pode valer".
        "requirements": _requirement_lines(visible_items(procedure.requirements, {})),
        "channels": _channel_lines(visible_items(procedure.channels, {})),
        "costs": _detail_texts(procedure, "COST"),
        "deadlines": _detail_texts(procedure, "DEADLINE"),
    }
    return render(request, "guidance/procedure.html", context)
