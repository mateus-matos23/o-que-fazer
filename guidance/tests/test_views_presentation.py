import re
from dataclasses import replace

import pytest
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client

from guidance.engine.channels import PREFERENCES
from guidance.engine.model import (
    Catalog,
    ChannelDef,
    ChannelKind,
    Facts,
    ProcedureDef,
    RequirementDef,
    Tri,
)
from guidance.engine.plan import build_plan
from guidance.forms import AnswerForm
from guidance.presentation import channel_lines, plan_context, primary_channel
from guidance.tests import factories as f

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
QUESTION = "cpf-situacao-cadastral"
NOTE = "Pode fazer em qualquer ordem"


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


def _layers(html: str) -> list[str]:
    return html.split('<ol class="layers">')[1].split("</ol>")[0].split("<li>\n")[1:]


def test_layers_number_steps_and_note_only_parallel_groups() -> None:
    html = _plan_html()
    assert '<p class="plan-summary">2 passos. Comece pelo 1.</p>' in html
    first, second = _layers(html)
    assert "</span>1</span>" in first and "Comece aqui" in first and NOTE not in first
    assert 'id="etapa-a"' in first
    assert "</span>2</span>" in second and "Comece aqui" not in second and NOTE in second
    assert 'id="etapa-b"' in second and 'id="etapa-c"' in second


def test_single_step_has_no_layer_head() -> None:
    html = _render_plan(f.catalog((), (_procedure("a"),)))
    assert '<p class="plan-summary">1 passo.</p>' in html
    assert "layer-head" not in html and "Comece aqui" not in html


def test_single_parallel_layer_notes_order_without_number() -> None:
    html = _render_plan(f.catalog((), (_procedure("a"), _procedure("b"))))
    assert '<p class="plan-summary">1 passo.</p>' in html
    assert NOTE in html and "layer-number" not in html and "Comece aqui" not in html


def _procedure(slug: str, *requirements: str) -> ProcedureDef:
    procedure = f.procedure(slug, f.rule("r"))
    return replace(
        procedure,
        requirements=tuple(RequirementDef(text, f.CITATION) for text in requirements),
    )


def test_each_step_keeps_its_details_collapsed() -> None:
    html = _plan_html()
    for card in html.split('<article id="etapa-')[1:]:
        details = card.split("<details>")[1].split("</details>")[0]
        assert details.lstrip().startswith("<summary>Ver detalhes")
        assert '<dl class="facts">' in details and "<dt>Fonte</dt>" in details
    assert html.count("<details>") == 3 and "<details open" not in html


def test_identical_requirement_is_not_merged_across_steps() -> None:
    catalog = f.catalog(
        (),
        (_procedure("a", "RG original"), _procedure("b", "RG original")),
        dependencies=(f.dep("a", "b"),),
    )
    assert _render_plan(catalog).count("<li>RG original</li>") == 2  # um por etapa (RF12)


def test_plan_drops_repeated_sections_and_needs_no_script() -> None:
    html = _plan_html()
    for removed in (
        "Comece por aqui",
        "O que separar antes",
        "Resumo",
        "imprimir",
        "journey-steps",
    ):
        assert removed not in html, removed
    assert re.findall(r"<script[^>]*>", html) == [LIBRAS_SCRIPT] and "onclick" not in html


def test_empty_plan_has_no_summary_or_layers() -> None:
    html = _render_plan(f.catalog((), (f.procedure("p"),), candidates=()))
    assert "Nenhuma providência" in html
    assert "plan-summary" not in html and 'class="layers"' not in html


def _channel(name: str, kind: ChannelKind = "ONLINE", url: str = "https://x.gov.br") -> ChannelDef:
    return ChannelDef(kind, name, url, f.CITATION)


@pytest.mark.parametrize(
    ("pairs", "preference", "expected"),
    [
        (((_channel("site"), Tri.APPLICABLE),), None, "site"),
        # a preferência reordena os canais e o botão segue a nova ordem
        (
            ((_channel("site"), Tri.APPLICABLE), (_channel("balcão", "IN_PERSON"), Tri.APPLICABLE)),
            "presencial",
            "balcão",
        ),
        # canal sem endereço não vira botão
        (
            ((_channel("fone", "PHONE", ""), Tri.APPLICABLE), (_channel("site"), Tri.APPLICABLE)),
            None,
            "site",
        ),
        # canal que só "pode valer" (regra indeterminada) também não
        (
            (
                (replace(_channel("talvez"), rule=f.rule("r")), Tri.UNDETERMINED),
                (_channel("site"), Tri.APPLICABLE),
            ),
            None,
            "site",
        ),
        (((_channel("fone", "PHONE", ""), Tri.APPLICABLE),), None, None),
        ((), None, None),
    ],
)
def test_primary_channel_is_first_preferred_channel_with_url(
    pairs: tuple[tuple[ChannelDef, Tri], ...], preference: str | None, expected: str | None
) -> None:
    lines = channel_lines(pairs, PREFERENCES[preference] if preference else None)
    chosen = primary_channel(lines)
    assert (chosen.channel.description if chosen else None) == expected


LIBRAS_SCRIPT = '<script type="module" src="/static/guidance/libras.js">'


@pytest.mark.parametrize("url", ["/", URL, URL + "plano/", "/onde-resolvo/?q=cpf"])
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


def _journey_steps(current: str) -> list[tuple[str, str]]:
    html = render_to_string("guidance/_journey_steps.html", {"current": current})
    return [
        (
            "current" if "aria-current" in attrs else "done" if "(concluída)" in rest else "next",
            label,
        )
        for attrs, label, rest in re.findall(r"<li([^>]*)>(\w+)(.*?)</li>", html)
    ]


@pytest.mark.parametrize(
    ("current", "expected"),
    [
        ("questions", ["current", "next", "next"]),
        ("preference", ["done", "current", "next"]),
    ],
)
def test_journey_steps_mark_done_and_current(current: str, expected: list[str]) -> None:
    steps = _journey_steps(current)
    assert [label for _, label in steps] == ["Perguntas", "Atendimento", "Plano"]
    assert [state for state, _ in steps] == expected


def test_question_page_shows_journey_steps(loaded: dict[str, int], client: Client) -> None:
    assert '<li class="current" aria-current="step">Perguntas</li>' in _html(client, URL)
