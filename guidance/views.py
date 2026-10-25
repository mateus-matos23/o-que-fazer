import logging
from dataclasses import dataclass

from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from catalog.models import ServiceChannel, Situation
from guidance.engine.evaluation import evaluate
from guidance.engine.model import Catalog, ChannelDef, DependencyDef, Unknown
from guidance.engine.ordering import DependencyCycleError
from guidance.engine.plan import PlanStep, build_plan
from guidance.engine.questions import next_question
from guidance.forms import AnswerForm
from guidance.repository import SituationNotFound, load_catalog
from guidance.session import clear_situation, read_facts, write_answer

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


def situation_list(request: HttpRequest) -> HttpResponse:
    situations = Situation.objects.order_by("title")
    return render(request, "guidance/situation_list.html", {"situations": situations})


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
            write_answer(request.session, slug, current.slug, form.cleaned_answer())
            return _see_other(reverse("guidance:question", args=[slug]))
    else:
        current = next_question(catalog, facts, evaluate(catalog, facts))
        if current is None:
            return redirect("guidance:plan", slug=slug)
        form = AnswerForm(current, initial_answer=facts.get(current.slug))
    context = {"catalog": catalog, "question": current, "form": form, "has_answers": bool(facts)}
    return render(request, "guidance/question.html", context)


@dataclass(frozen=True, slots=True)
class DependencyLine:
    title: str
    suggestion: bool  # RECOMMENDED: sugestão de ordem, não exigência (RN08)


@dataclass(frozen=True, slots=True)
class ChannelLine:
    kind_label: str
    channel: ChannelDef


@dataclass(frozen=True, slots=True)
class StepView:
    step: PlanStep
    required_for: tuple[str, ...]
    after: tuple[DependencyLine, ...]
    channels: tuple[ChannelLine, ...]
    costs: tuple[str, ...]
    deadlines: tuple[str, ...]


def _step_view(catalog: Catalog, step: PlanStep) -> StepView:
    def title(slug: str) -> str:
        return catalog.procedures[slug].title

    def line(dependency: DependencyDef) -> DependencyLine:
        return DependencyLine(title(dependency.before), dependency.kind == "RECOMMENDED")

    procedure = step.procedure
    return StepView(
        step=step,
        required_for=tuple(title(slug) for slug in step.required_for),
        after=tuple(line(d) for d in step.after),
        channels=tuple(
            ChannelLine(ServiceChannel.Kind(c.kind).label, c) for c in procedure.channels
        ),
        costs=tuple(d.text for d in procedure.details if d.kind == "COST"),
        deadlines=tuple(d.text for d in procedure.details if d.kind == "DEADLINE"),
    )


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
    if next_question(catalog, facts, evaluate(catalog, facts)) is not None:
        return redirect("guidance:question", slug=slug)  # plano só com perguntas encerradas
    try:
        result = build_plan(catalog, facts)
    except DependencyCycleError as error:
        logger.error("ciclo entre dependências: situação=%s procedimentos=%s", slug, error.nodes)
        return render(
            request,
            "guidance/error.html",
            {"message": "Não foi possível montar o plano agora. Tente novamente mais tarde."},
            status=500,
        )
    context = {
        "catalog": catalog,
        "plan": result,
        "steps": [_step_view(catalog, step) for step in result.steps],
        "uncovered": _uncovered_lines(catalog, result.uncovered),
        "undetermined": [catalog.procedures[s].title for s in result.undetermined],
    }
    return render(request, "guidance/plan.html", context)


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
            write_answer(request.session, slug, current.slug, form.cleaned_answer())
            return _see_other(reverse("guidance:question", args=[slug]))  # recalcula (invariante 8)
    else:
        form = AnswerForm(current, initial_answer=facts.get(current.slug))
    context = {"catalog": catalog, "question": current, "form": form, "has_answers": bool(facts)}
    return render(request, "guidance/question.html", context)


@require_POST
def restart(request: HttpRequest, slug: str) -> HttpResponse:
    _load(slug)
    clear_situation(request.session, slug)
    return _see_other(reverse("guidance:question", args=[slug]))
