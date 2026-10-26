import re
from dataclasses import replace

import pytest
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client

from guidance.engine.model import Catalog, Facts, ProcedureDef, RequirementDef
from guidance.engine.plan import build_plan
from guidance.forms import AnswerForm
from guidance.presentation import plan_context
from guidance.tests import factories as f

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
QUESTION = "cpf-situacao-cadastral"
NOTE = "Podem ser feitas em qualquer ordem"


def _html(client: Client, url: str) -> str:
    return client.get(url).content.decode()


def _render_plan(catalog: Catalog, facts: Facts | None = None) -> str:
    plan = build_plan(catalog, facts or {})
    context = {"catalog": catalog, "plan": plan, **plan_context(catalog, plan, None)}
    return render_to_string("guidance/plan.html", context)


def _plan_html() -> str:
    always = f.rule("r")
    catalog = f.catalog(
        (),
        (f.procedure("a", always), f.procedure("b", always), f.procedure("c", always)),
        dependencies=(f.dep("a", "b"), f.dep("a", "c")),
    )
    return _render_plan(catalog)


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


def _procedure(slug: str, *requirements: str) -> ProcedureDef:
    procedure = f.procedure(slug, f.rule("r"))
    return replace(
        procedure,
        requirements=tuple(RequirementDef(text, f.CITATION) for text in requirements),
    )


def _section(html: str, heading_id: str) -> str:
    match = re.search(
        rf'<section class="[^"]*" aria-labelledby="{heading_id}">(.*?)</section>', html, re.S
    )
    assert match, heading_id
    return match.group(1)


def test_start_here_with_single_first_step_links_it() -> None:
    catalog = f.catalog((), (_procedure("a"), _procedure("b")), dependencies=(f.dep("a", "b"),))
    html = _render_plan(catalog)
    start = _section(html, "comece-por-aqui")
    assert '<h2 id="comece-por-aqui">Comece por aqui</h2>' in start
    assert '<a href="#etapa-a">a</a>' in start
    assert "qualquer uma destas" not in html


def test_start_here_lists_every_first_layer_step() -> None:
    catalog = f.catalog(
        (), (_procedure("a"), _procedure("b"), _procedure("c")), dependencies=(f.dep("a", "c"),)
    )
    start = _section(_render_plan(catalog), "comece-por-aqui")
    assert "Pode começar por qualquer uma destas:" in start
    assert '<a href="#etapa-a">a</a>' in start and '<a href="#etapa-b">b</a>' in start
    assert "#etapa-c" not in start


def test_start_here_absent_without_steps() -> None:
    catalog = f.catalog((), (f.procedure("p"),), candidates=())
    html = _render_plan(catalog)
    assert "Nenhuma providência" in html
    assert "Comece por aqui" not in html and "start-here" not in html


def test_prepare_groups_requirements_by_step_in_order() -> None:
    catalog = f.catalog(
        (),
        (_procedure("a", "Documento A1", "Documento A2"), _procedure("b", "Documento B")),
        dependencies=(f.dep("a", "b"),),
    )
    prepare = _section(_render_plan(catalog), "o-que-separar-antes")
    assert (
        prepare.index("<h3>a</h3>") < prepare.index("Documento A1") < prepare.index("Documento A2")
    )
    assert (
        prepare.index("Documento A2") < prepare.index("<h3>b</h3>") < prepare.index("Documento B")
    )
    assert "Documento A1" in prepare and "Documento B" in prepare


def test_identical_requirement_is_not_merged_across_steps() -> None:
    catalog = f.catalog(
        (),
        (_procedure("a", "RG original"), _procedure("b", "RG original")),
        dependencies=(f.dep("a", "b"),),
    )
    html = _render_plan(catalog)
    prepare = _section(html, "o-que-separar-antes")
    assert prepare.count("<li>RG original</li>") == 2
    assert prepare.count("<h3>") == 2
    assert html.count("<li>RG original</li>") == 4  # também segue na etapa (RF12)


def test_step_without_requirement_stays_out_of_prepare() -> None:
    catalog = f.catalog(
        (), (_procedure("a", "Documento"), _procedure("b")), dependencies=(f.dep("a", "b"),)
    )
    prepare = _section(_render_plan(catalog), "o-que-separar-antes")
    assert "<h3>a</h3>" in prepare and "<h3>b</h3>" not in prepare


def test_prepare_absent_without_requirements() -> None:
    catalog = f.catalog((), (_procedure("a"), _procedure("b")), dependencies=(f.dep("a", "b"),))
    html = _render_plan(catalog)
    assert "O que separar antes" not in html and "prepare" not in html


def test_print_hint_is_plain_text_without_script() -> None:
    html = _plan_html()
    assert "Para guardar este plano, use a opção de imprimir do navegador." in html
    assert re.findall(r"<script[^>]*>", html) == [LIBRAS_SCRIPT] and "onclick" not in html


LIBRAS_SCRIPT = '<script type="module" src="/static/guidance/libras.js">'


@pytest.mark.parametrize(
    "url", ["/", "/situacoes/", URL, URL + "plano/", "/onde-resolvo/?q=cpf", "/fora-da-cobertura/"]
)
def test_libras_button_is_hidden_until_script_and_loads_nothing_external(
    loaded: dict[str, int], client: Client, url: str
) -> None:
    if url.endswith("plano/"):  # o plano exige uma resposta
        client.post(URL, {"question": QUESTION, "answer": "suspenso"})
    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode()
    assert '<aside id="libras" class="libras" aria-label="Tradução para Libras" hidden>' in html
    assert LIBRAS_SCRIPT in html
    assert "vlibras.gov.br" not in html  # o endereço externo só existe no script, usado a pedido


def test_review_has_no_libras(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, URL + "respostas/")
    assert 'id="libras"' not in html and "libras.js" not in html


def test_libras_script_is_served_locally_and_loads_the_official_plugin() -> None:
    path = finders.find("guidance/libras.js")
    assert isinstance(path, str)
    with open(path, encoding="utf-8") as handle:
        assert '"https://vlibras.gov.br/app/vlibras-plugin.js"' in handle.read()


def test_stylesheet_has_print_rules() -> None:
    css = _stylesheet()
    assert "@media print" in css
    print_block = css.split("@media print", 1)[1]
    assert "p.channel-preference" in print_block and ".edit-answer" in print_block
    assert ".libras," in print_block
    assert ".answer-effect" in print_block
    assert 'a[href^="http"]::after' in print_block and "break-inside: avoid" in print_block


def test_screen_text_is_at_least_16px() -> None:
    screen = _stylesheet().split("@media print", 1)[0]
    sizes = re.findall(r"font-size:\s*([\d.]+)(rem|px)", screen)
    assert sizes
    assert [s for s in sizes if float(s[0]) < (1 if s[1] == "rem" else 16)] == []


def test_screen_targets_are_at_least_44px() -> None:
    screen = _stylesheet().split("@media print", 1)[0]
    heights = [int(h) for h in re.findall(r"min-height:\s*(\d+)px", screen)]
    assert heights
    assert [h for h in heights if h < 44] == []


def _stylesheet() -> str:
    path = finders.find("guidance/site.css")
    assert isinstance(path, str)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _journey_steps(current: str, preference: object = None) -> list[tuple[str, str]]:
    html = render_to_string(
        "guidance/_journey_steps.html", {"current": current, "preference": preference}
    )
    return [
        (
            "current" if "aria-current" in attrs else "done" if "(concluída)" in rest else "next",
            label,
        )
        for attrs, label, rest in re.findall(r"<li([^>]*)>(\w+)(.*?)</li>", html)
    ]


@pytest.mark.parametrize(
    ("current", "preference", "expected"),
    [
        ("questions", None, ["done", "current", "next", "next"]),
        ("preference", None, ["done", "done", "current", "next"]),
        ("plan", object(), ["done", "done", "done", "current"]),
        ("plan", None, ["done", "done", "next", "current"]),  # plano sem preferência escolhida
    ],
)
def test_journey_steps_mark_done_and_current(
    current: str, preference: object, expected: list[str]
) -> None:
    steps = _journey_steps(current, preference)
    assert [label for _, label in steps] == ["Assunto", "Perguntas", "Atendimento", "Plano"]
    assert [state for state, _ in steps] == expected


def test_question_page_shows_journey_steps(loaded: dict[str, int], client: Client) -> None:
    assert '<li class="current" aria-current="step">Perguntas</li>' in _html(client, URL)
