import re
from dataclasses import replace

import pytest
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client

from guidance.engine.plan import build_plan
from guidance.forms import AnswerForm
from guidance.tests import factories as f
from guidance.views import _step_view

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
QUESTION = "cpf-situacao-cadastral"
NOTE = "Podem ser feitas em qualquer ordem"


def _html(client: Client, url: str) -> str:
    return client.get(url).content.decode()


def _plan_html() -> str:
    always = f.rule("r")
    catalog = f.catalog(
        (),
        (f.procedure("a", always), f.procedure("b", always), f.procedure("c", always)),
        dependencies=(f.dep("a", "b"), f.dep("a", "c")),
    )
    plan = build_plan(catalog, {})
    return render_to_string(
        "guidance/plan.html",
        {
            "catalog": catalog,
            "plan": plan,
            "steps": [_step_view(catalog, s) for s in plan.steps],
            "undetermined": [],
        },
    )


@pytest.mark.parametrize("url", ["/", URL, URL + "respostas/"])
def test_pages_have_landmarks_skip_link_and_stylesheet(
    loaded: dict[str, int], client: Client, url: str
) -> None:
    html = _html(client, url)
    assert re.search(r'<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>', html)
    assert "<header" in html and '<main id="conteudo"' in html and "<footer" in html
    assert html.count("<h1") == 1
    assert 'href="/static/guidance/site.css"' in html


def test_stylesheet_and_fonts_are_served_locally() -> None:
    assert finders.find("guidance/site.css")
    for weight in ("Regular", "Bold"):
        assert finders.find(f"guidance/fonts/AtkinsonHyperlegibleNext-{weight}.woff2")


def test_progress_pluralizes_and_links_to_review(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, URL)
    assert "Você já respondeu 0 perguntas" in html and "Rever respostas" not in html
    client.post(URL, {"question": QUESTION, "answer": "suspenso"})
    html = _html(client, URL + f"respostas/{QUESTION}/")
    assert "Você já respondeu 1 pergunta." in html
    assert f'href="{URL}respostas/"' in html and "Rever respostas" in html


def test_form_error_is_associated_to_the_fieldset(loaded: dict[str, int], client: Client) -> None:
    html = client.post(URL, {"question": QUESTION, "answer": "inexistente"}).content.decode()
    assert '<fieldset aria-describedby="question-help form-errors">' in html
    errors = re.search(r'<div id="form-errors"[^>]*>(.*?)</div>', html, re.S)
    assert errors and "Erro:" in errors.group(1) and "errorlist" in errors.group(1)
    assert '<div id="form-errors" class="errors" tabindex="-1" autofocus>' in html
    assert "<title>Erro: " in html
    clean = _html(client, URL)
    assert '<fieldset aria-describedby="question-help">' in clean and "form-errors" not in clean
    assert "<title>Erro: " not in clean


def _form_html(help_text: str, data: dict[str, str] | None) -> str:
    question = replace(f.question("q"), help_text=help_text)
    return render_to_string(
        "guidance/_answer_form.html", {"question": question, "form": AnswerForm(question, data)}
    )


def test_help_text_is_rendered_and_described() -> None:
    html = _form_html("Dica.", None)
    assert '<p id="question-help" class="question-help">Dica.</p>' in html
    assert '<fieldset aria-describedby="question-help">' in html


def test_no_help_text_renders_nothing() -> None:
    html = _form_html("", None)
    assert "question-help" not in html and "aria-describedby" not in html


def test_help_text_and_errors_are_both_described() -> None:
    html = _form_html("Dica.", {"answer": "zzz"})
    assert '<fieldset aria-describedby="question-help form-errors">' in html


def test_route_groups_steps_by_layer_and_notes_only_parallel_groups() -> None:
    route = _plan_html().split('<ol class="route">')[1].split("</ol>")[0]
    first, second = route.split('<span class="route-number">')[1:]
    assert "</span>1</span>" in first and 'href="#etapa-a"' in first and NOTE not in first
    assert "</span>2</span>" in second and NOTE in second
    assert 'href="#etapa-b"' in second and 'href="#etapa-c"' in second
