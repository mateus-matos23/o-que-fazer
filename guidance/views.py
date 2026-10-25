from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from catalog.models import Situation
from guidance.engine.evaluation import evaluate
from guidance.engine.plan import build_plan
from guidance.engine.questions import next_question
from guidance.forms import AnswerForm
from guidance.repository import SituationNotFound, load_catalog
from guidance.session import read_facts, write_answer


def situation_list(request: HttpRequest) -> HttpResponse:
    situations = Situation.objects.order_by("title")
    return render(request, "guidance/situation_list.html", {"situations": situations})


@require_http_methods(["GET", "POST"])
def question(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        catalog = load_catalog(slug)
    except SituationNotFound:
        raise Http404("Situação não encontrada") from None
    facts = read_facts(request.session, catalog)
    if request.method == "POST":
        current = catalog.questions.get(request.POST.get("question", ""))
        if current is None:
            return HttpResponseBadRequest("Pergunta inválida para esta situação.")
        form = AnswerForm(current, request.POST, facts.get(current.slug))
        if form.is_valid():
            write_answer(request.session, slug, current.slug, form.cleaned_answer())
            response = HttpResponseRedirect(reverse("guidance:question", args=[slug]))
            response.status_code = 303  # PRG: o navegador refaz a requisição como GET
            return response
    else:
        current = next_question(catalog, facts, evaluate(catalog, facts))
        if current is None:
            return redirect("guidance:plan", slug=slug)
        form = AnswerForm(current, initial_answer=facts.get(current.slug))
    context = {"catalog": catalog, "question": current, "form": form}
    return render(request, "guidance/question.html", context)


def plan(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        catalog = load_catalog(slug)
    except SituationNotFound:
        raise Http404("Situação não encontrada") from None
    result = build_plan(catalog, read_facts(request.session, catalog))
    return render(request, "guidance/plan.html", {"catalog": catalog, "plan": result})
