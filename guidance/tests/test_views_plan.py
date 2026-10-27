import logging
import re
from datetime import UTC, datetime

import pytest
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import Client

from catalog.models import AnswerOption
from guidance.engine.model import Catalog
from guidance.engine.ordering import DependencyCycleError
from guidance.engine.plan import build_plan
from guidance.forms import UNKNOWN_VALUE
from guidance.presentation import step_view, uncovered_lines
from guidance.repository import clear_catalog_cache
from guidance.tests import factories as f
from sources.models import SourceImport

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
PLAN = URL + "plano/"
QUESTION = "cpf-situacao-cadastral"


def _answer(client: Client, value: str) -> None:
    assert client.post(URL, {"question": QUESTION, "answer": value}).status_code == 303


def _get(client: Client, url: str) -> HttpResponse:
    response = client.get(url)
    assert isinstance(response, HttpResponse)
    return response


def _html(client: Client, url: str) -> str:
    response = _get(client, url)
    assert response.status_code == 200
    return response.content.decode()


def test_plan_shows_step_details(loaded: dict[str, int], client: Client) -> None:
    _answer(client, "suspenso")
    html = _html(client, PLAN)
    assert "Orientação a partir das suas respostas. Quem confirma é o órgão." in html
    assert 'id="etapa-regularizar-cpf-suspenso"' in html
    assert "<h2>" in html and "Por que esta etapa" in html
    assert 'class="layer-number"' not in html  # um só passo: sem número nos cards
    assert "<strong>Onde:</strong> Receita Federal" in html
    assert "Formulário online para regularizar CPF suspenso." in html
    assert "Online:" in html and "Presencial:" in html  # tipo legível
    assert (
        'href="https://servicos.receita.fazenda.gov.br/Servicos/CPF/regularizar/Default.asp"'
        in html
    )
    assert re.search(r"<dt>Custo</dt>\s*<dd>Gratuito, exceto em unidades conveniadas", html)
    assert re.search(
        r'<dt>Prazo</dt>\s*<dd><span class="not-informed">Não informado</span></dd>', html
    )  # RN11
    assert "(site oficial)" in html
    assert "Coletado em 09/10/2026 21:00" in html  # RN12
    assert "Atualizado pelo órgão em" in html
    assert "Rever respostas" in html and "Recomeçar" in html


def test_empty_plan_message() -> None:
    catalog = f.catalog((), (f.procedure("p"),), ())
    plan = build_plan(catalog, {})
    html = render_to_string(
        "guidance/plan.html",
        {"catalog": catalog, "plan": plan, "steps": [], "undetermined": []},
    )
    assert "Nenhuma providência encontrada para as respostas dadas." in html


def test_uncovered_warning_only_with_out_of_coverage_option(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client, "suspenso")
    assert "Limite de cobertura" not in _html(client, PLAN)
    AnswerOption.objects.filter(question__slug=QUESTION, slug="suspenso").update(
        out_of_coverage=True
    )
    clear_catalog_cache()  # edição direta no banco; em produção o conteúdo só muda por load_content
    html = _html(client, PLAN)
    assert "Limite de cobertura" in html
    assert "Não encontramos orientação oficial para esta resposta nesta versão." in html
    assert 'data-slug="regularizar-cpf-suspenso"' in html  # as etapas seguem no plano


def test_uncovered_warning_shows_without_steps() -> None:
    catalog = f.catalog((f.question("q", uncovered=("a",)),), (), ())
    plan = build_plan(catalog, {"q": frozenset({"a"})})
    html = render_to_string(
        "guidance/plan.html",
        {
            "catalog": catalog,
            "plan": plan,
            "steps": [],
            "uncovered": uncovered_lines(catalog, plan.uncovered),
            "undetermined": [],
        },
    )
    assert "Limite de cobertura" in html and "q Você respondeu: a." in html


def test_unknown_gives_clarification_and_undetermined(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client, UNKNOWN_VALUE)
    html = _html(client, PLAN)
    assert 'data-slug="consultar-situacao-cpf"' in html
    assert 'Você respondeu "Não sei" para:' in html
    assert f"{URL}respostas/{QUESTION}/" in html
    section = html.split("Pode se aplicar, mas faltam informações")[1]
    assert section.count("<li>") == 3


def test_pending_question_redirects(loaded: dict[str, int], client: Client) -> None:
    response = _get(client, PLAN)
    assert (response.status_code, response["Location"]) == (302, URL)


def test_cycle_gives_generic_500_and_logs(
    loaded: dict[str, int],
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def boom(catalog: Catalog, facts: object, evaluations: object) -> None:
        raise DependencyCycleError(["a", "b"])

    monkeypatch.setattr("guidance.views.build_plan", boom)
    _answer(client, "suspenso")
    with caplog.at_level(logging.ERROR, logger="guidance.views"):
        response = _get(client, PLAN)
    html = response.content.decode()
    assert response.status_code == 500
    assert "Não foi possível montar o plano agora." in html
    assert "<section" not in html and "regularizar" not in html and "a, b" not in html
    assert "['a', 'b']" in caplog.text


def test_dates_use_local_timezone(loaded: dict[str, int], client: Client) -> None:
    SourceImport.objects.update(fetched_at=datetime(2026, 10, 10, 1, 0, tzinfo=UTC))
    _answer(client, "suspenso")
    assert "Coletado em 09/10/2026 22:00" in _html(client, PLAN)


def test_review_lists_answers_and_edit_changes_plan(loaded: dict[str, int], client: Client) -> None:
    assert "Rever respostas" not in _html(client, URL)
    _answer(client, "suspenso")
    assert "Rever respostas" in _html(client, URL + "respostas/" + QUESTION + "/")
    html = _html(client, URL + "respostas/")
    assert "Suspenso" in html and "Alterar" in html
    edit = _html(client, f"{URL}respostas/{QUESTION}/")
    assert re.search(r'<input[^>]*value="suspenso"[^>]*checked', edit)
    response = client.post(f"{URL}respostas/{QUESTION}/", {"answer": UNKNOWN_VALUE})
    assert (response.status_code, response["Location"]) == (303, URL)
    assert "Não sei" in _html(client, URL + "respostas/")
    plan = _html(client, PLAN)
    assert 'data-slug="consultar-situacao-cpf"' in plan
    assert 'data-slug="regularizar-cpf-suspenso"' not in plan


def test_edit_invalid_and_foreign_question(loaded: dict[str, int], client: Client) -> None:
    response = client.post(f"{URL}respostas/{QUESTION}/", {"answer": "inexistente"})
    assert response.status_code == 200 and "errorlist" in response.content.decode()
    assert _get(client, f"{URL}respostas/outra-situacao-pergunta/").status_code == 404


def test_restart_clears_only_that_situation(loaded: dict[str, int], client: Client) -> None:
    _answer(client, "suspenso")
    session = client.session
    session["facts"] = {**session["facts"], "outra": {"q": ["a"]}}
    session.save()
    response = client.post(URL + "recomecar/")
    assert (response.status_code, response["Location"]) == (303, URL)
    assert client.session["facts"] == {"outra": {"q": ["a"]}}
    assert _get(client, URL + "recomecar/").status_code == 405


def test_recommended_is_marked_as_suggestion() -> None:
    always = f.rule("r")
    catalog = f.catalog(
        (),
        (f.procedure("a", always), f.procedure("b", always)),
        dependencies=(f.dep("a", "b", "RECOMMENDED"),),
    )
    plan = build_plan(catalog, {})
    html = render_to_string(
        "guidance/plan.html",
        {
            "catalog": catalog,
            "plan": plan,
            "steps": [step_view(catalog, s) for s in plan.steps],
            "undetermined": [],
        },
    )
    assert "<strong>Depois de:</strong> a (sugestão)" in html


def test_real_journey_starts_with_every_first_layer_step(
    loaded: dict[str, int], client: Client
) -> None:
    perda = "/s/perda-de-documentos/"
    response = client.post(
        perda, {"question": "documentos-perdidos", "answer": ["cpf", "cin", "cnh"]}
    )
    assert response.status_code == 303
    client.post(perda, {"question": "declarou-imposto-de-renda", "answer": "sim"})
    html = _html(client, perda + "plano/")
    assert '<p class="plan-summary">4 etapas. Comece pelo passo 1.</p>' in html
    first, second = html.split('<span class="layer-number">')[1:]
    assert "Comece aqui" in first and "Pode fazer em qualquer ordem" in first
    for slug in ("registrar-ocorrencia-extravio", "segunda-via-cin", "segunda-via-cpf"):
        assert f'id="etapa-{slug}"' in first
    assert 'id="etapa-segunda-via-cnh"' in second  # depende do B.O. (camada 2)
    assert "RG atual, caso possua." in html  # requisitos seguem no detalhe de cada etapa


def test_step_button_goes_to_the_official_online_channel(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client, "suspenso")
    card = _html(client, PLAN).split('<article id="etapa-regularizar-cpf-suspenso"')[1]
    button = card.split("<details>")[0]
    assert (
        '<a class="button" href="https://servicos.receita.fazenda.gov.br/Servicos/CPF/'
        'regularizar/Default.asp" target="_blank" rel="noopener noreferrer">'
        "Ir para o site oficial" in button
    )
    assert "Ver a página oficial do serviço" not in button


def test_external_links_open_in_a_new_tab(loaded: dict[str, int], client: Client) -> None:
    _answer(client, "suspenso")
    for url in (PLAN, "/onde-resolvo/extrato-vinculos-caged/"):
        links = re.findall(r'<a [^>]*href="https?://[^>]*>', _html(client, url))
        assert links
        for link in links:
            assert 'target="_blank" rel="noopener noreferrer"' in link, link
