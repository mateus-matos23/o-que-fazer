import logging

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
    Situation,
    TriageChoice,
    TriageNode,
)
from guidance.engine.effect import answer_effect
from guidance.engine.evaluation import evaluate, visible_items
from guidance.engine.model import Answer, Catalog, Facts
from guidance.engine.ordering import DependencyCycleError
from guidance.engine.plan import build_plan
from guidance.engine.questions import next_question
from guidance.forms import AnswerForm, ChannelPreferenceForm, SearchForm
from guidance.presentation import (
    EffectView,
    answer_lines,
    channel_lines,
    detail_texts,
    effect_view,
    plan_context,
    requirement_lines,
)
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


def _effect_view(request: HttpRequest, catalog: Catalog) -> EffectView | None:
    """Consome o aviso de uso único."""
    return effect_view(catalog, pop_effect(request.session, catalog))


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
        situations = Situation.objects.order_by("title")
        return render(request, "guidance/situation_list.html", {"situations": situations})
    return render(request, "guidance/triage.html", {"node": node, "is_start": True})


@require_GET
def triage(request: HttpRequest, slug: str) -> HttpResponse:
    if slug == START_NODE:
        return redirect("guidance:home")  # o início tem uma só URL
    node = _triage_node(slug)
    if node is None:
        raise Http404("Pergunta não encontrada")
    return render(request, "guidance/triage.html", {"node": node, "is_start": False})


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


@require_GET
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
        **plan_context(catalog, result, preference),
        "effect": _effect_view(request, catalog),
    }
    return render(request, "guidance/plan.html", context)


@require_GET
def review(request: HttpRequest, slug: str) -> HttpResponse:
    catalog = _load(slug)
    facts = read_facts(request.session, catalog)
    lines = answer_lines(catalog, facts)
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


@require_GET
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


@require_GET
def procedure_detail(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        procedure = load_procedure(slug)
    except ProcedureNotFound:
        raise Http404("Serviço não encontrado") from None
    context = {
        "procedure": procedure,
        # Sem fatos: itens com regra aparecem marcados como "pode valer".
        "requirements": requirement_lines(visible_items(procedure.requirements, {})),
        "channels": channel_lines(visible_items(procedure.channels, {})),
        "costs": detail_texts(procedure, "COST"),
        "deadlines": detail_texts(procedure, "DEADLINE"),
    }
    return render(request, "guidance/procedure.html", context)
