import logging
import re
from typing import Literal

import pytest
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import Client

from guidance.engine.effect import AnswerEffect
from guidance.engine.model import OptionDef, QuestionDef, Unknown
from guidance.forms import UNKNOWN_VALUE, AnswerForm
from guidance.presentation import EffectView

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
PLAN = "/s/cpf-irregular/plano/"
PREFERENCE = "/s/cpf-irregular/atendimento/"
QUESTION = "cpf-situacao-cadastral"


def _post(client: Client, value: str | None, question: str = QUESTION) -> HttpResponse:
    data = {"question": question}
    if value is not None:
        data["answer"] = value
    response = client.post(URL, data)
    assert isinstance(response, HttpResponse)
    return response


def _choose_preference(client: Client, value: str = "tanto-faz") -> None:
    response = client.post(PREFERENCE, {"preference": value})
    assert (response.status_code, response["Location"]) == (303, PLAN)


def _plan(client: Client) -> str:
    response = client.get(URL, follow=True)
    assert response.redirect_chain[-1] == (PREFERENCE, 302)
    _choose_preference(client)
    return client.get(PLAN).content.decode()


def test_lists_situations(loaded: dict[str, int], client: Client) -> None:
    assert "Meu CPF está irregular" in client.get("/situacoes/").content.decode()


def test_unknown_situation_is_404(loaded: dict[str, int], client: Client) -> None:
    assert client.get("/s/nao-existe/").status_code == 404


def test_question_renders_radios_with_unknown(loaded: dict[str, int], client: Client) -> None:
    html = client.get(URL).content.decode()
    assert html.count('type="radio"') == 6
    assert "Não sei" in html
    assert 'lang="pt-BR"' in html


def test_answer_then_plan(loaded: dict[str, int], client: Client) -> None:
    response = _post(client, "suspenso")
    assert (response.status_code, response["Location"]) == (303, URL)
    assert 'data-slug="regularizar-cpf-suspenso"' in _plan(client)


def test_unknown_answer_gives_clarification(loaded: dict[str, int], client: Client) -> None:
    assert _post(client, UNKNOWN_VALUE).status_code == 303
    assert 'data-slug="consultar-situacao-cpf"' in _plan(client)


def test_changing_answer_changes_plan(loaded: dict[str, int], client: Client) -> None:
    _post(client, "suspenso")
    _post(client, UNKNOWN_VALUE)
    html = _plan(client)
    assert 'data-slug="consultar-situacao-cpf"' in html
    assert 'data-slug="regularizar-cpf-suspenso"' not in html


@pytest.mark.parametrize("value", ["inexistente", None])
def test_invalid_post_keeps_session(
    loaded: dict[str, int], client: Client, value: str | None
) -> None:
    response = _post(client, value)
    assert response.status_code == 200
    assert "errorlist" in response.content.decode()
    assert "facts" not in client.session


@pytest.mark.parametrize("question", ["", "outra-pergunta"])
def test_foreign_question_is_400(loaded: dict[str, int], client: Client, question: str) -> None:
    assert _post(client, "suspenso", question).status_code == 400


def test_invalid_session_entries_are_discarded(
    loaded: dict[str, int], client: Client, caplog: pytest.LogCaptureFixture
) -> None:
    session = client.session
    session["facts"] = {"cpf-irregular": {QUESTION: ["removida"], "fantasma": "unknown"}}
    session.save()
    with caplog.at_level(logging.WARNING, logger="guidance.session"):
        assert client.get(URL).status_code == 200  # pergunta volta a ser feita
    assert len(caplog.records) == 2
    assert client.session["facts"]["cpf-irregular"] == {}
    session = client.session
    session["facts"] = {"cpf-irregular": "lixo"}
    session.save()
    assert client.get(URL).status_code == 200


def test_csrf_enforced(loaded: dict[str, int]) -> None:
    client = Client(enforce_csrf_checks=True)
    assert client.post(URL, {"question": QUESTION, "answer": "suspenso"}).status_code == 403


def _question(kind: Literal["SINGLE", "MULTIPLE"], unknown: bool) -> QuestionDef:
    options = (OptionDef("a", "A"), OptionDef("b", "B"))
    return QuestionDef("q", "Pergunta?", "", kind, unknown, 1, options)


def test_form_single() -> None:
    form = AnswerForm(_question("SINGLE", True), {"answer": UNKNOWN_VALUE})
    assert form.is_valid() and form.cleaned_answer() is Unknown.UNKNOWN
    assert len(AnswerForm(_question("SINGLE", True))["answer"].subwidgets) == 3
    assert len(AnswerForm(_question("SINGLE", False))["answer"].subwidgets) == 2
    assert not AnswerForm(_question("SINGLE", False), {"answer": UNKNOWN_VALUE}).is_valid()
    assert not AnswerForm(_question("SINGLE", True), {}).is_valid()


def test_form_multiple() -> None:
    empty = AnswerForm(_question("MULTIPLE", False), {})
    assert empty.is_valid() and empty.cleaned_answer() == frozenset()
    both = AnswerForm(_question("MULTIPLE", True), {"answer": ["a"], "unknown": "on"})
    assert not both.is_valid()
    only = AnswerForm(_question("MULTIPLE", True), {"unknown": "on"})
    assert only.is_valid() and only.cleaned_answer() is Unknown.UNKNOWN
    assert not AnswerForm(_question("MULTIPLE", False), {"answer": ["z"]}).is_valid()


def test_form_initial_answer() -> None:
    form = AnswerForm(_question("MULTIPLE", True), initial_answer=frozenset({"b"}))
    assert form["answer"].value() == ["b"]
    single = AnswerForm(_question("SINGLE", True), initial_answer=Unknown.UNKNOWN)
    assert single["answer"].value() == UNKNOWN_VALUE


DESLIGAMENTO = "/s/desligamento-do-trabalho/"
FORMA = "forma-de-termino"
VINCULO = "tipo-de-vinculo"
FGTS = "Sacar o FGTS por dispensa sem justa causa"
LEFT_NOTE = (
    "Sair do plano não quer dizer que você não tem direito: a confirmação é sempre do órgão."
)


def _answer_desligamento(client: Client, question: str, value: str) -> HttpResponse:
    response = client.post(DESLIGAMENTO, {"question": question, "answer": value})
    assert isinstance(response, HttpResponse)
    return response


def _effect_block(client: Client, url: str) -> str | None:
    response = client.get(url)
    assert response.status_code == 200
    match = re.search(r'<div class="answer-effect">.*?</div>', response.text, re.S)
    return match.group(0) if match else None


def test_post_and_edit_redirect_without_query(loaded: dict[str, int], client: Client) -> None:
    assert _post(client, "suspenso")["Location"] == URL
    response = client.post(f"{URL}respostas/{QUESTION}/", {"answer": UNKNOWN_VALUE})
    assert (response.status_code, response["Location"]) == (303, URL)


def test_effect_on_next_question_is_shown_once(loaded: dict[str, int], client: Client) -> None:
    _answer_desligamento(client, FORMA, "sem-justa-causa")
    block = _effect_block(client, DESLIGAMENTO)
    assert block is not None
    assert "Por causa dessa resposta, entrou no seu plano:" in block
    assert f"<li>{FGTS}</li>" in block
    assert "Ainda em análise: 2 providências." in block
    assert "Saiu do seu plano" not in block and LEFT_NOTE not in block
    assert _effect_block(client, DESLIGAMENTO) is None


def test_redirect_to_plan_keeps_effect_for_the_plan(loaded: dict[str, int], client: Client) -> None:
    _post(client, "suspenso")
    _choose_preference(client)
    assert client.get(URL)["Location"] == PLAN
    block = _effect_block(client, PLAN)
    assert block is not None and "Regularizar o CPF suspenso" in block
    assert _effect_block(client, PLAN) is None


def test_undetermined_to_not_applicable_is_not_shown_as_left(
    loaded: dict[str, int], client: Client
) -> None:
    _answer_desligamento(client, FORMA, "sem-justa-causa")
    _answer_desligamento(client, VINCULO, "domestico")
    block = _effect_block(client, f"{DESLIGAMENTO}plano/")
    assert block is not None
    assert "<li>Solicitar o seguro-desemprego do empregado doméstico</li>" in block
    assert "Saiu do seu plano" not in block and LEFT_NOTE not in block
    assert "Solicitar o seguro-desemprego</li>" not in block


def test_editing_with_same_value_shows_no_changes(loaded: dict[str, int], client: Client) -> None:
    _post(client, "suspenso")
    client.post(f"{URL}respostas/{QUESTION}/", {"answer": "suspenso"})
    assert _effect_block(client, PLAN) is None


def test_swapping_answer_shows_departure_with_note(loaded: dict[str, int], client: Client) -> None:
    _post(client, "suspenso")
    client.post(f"{URL}respostas/{QUESTION}/", {"answer": UNKNOWN_VALUE})
    block = _effect_block(client, PLAN)
    assert block is not None
    assert "<li>Consultar a situação cadastral do CPF</li>" in block
    assert "Saiu do seu plano:" in block and "<li>Regularizar o CPF suspenso</li>" in block
    assert LEFT_NOTE in block


def test_effect_of_one_situation_does_not_show_in_another(
    loaded: dict[str, int], client: Client
) -> None:
    _post(client, "suspenso")
    assert _effect_block(client, DESLIGAMENTO) is None
    assert _effect_block(client, PLAN) is not None


def test_singular_providencia() -> None:
    effect = EffectView((), (), 1)
    html = render_to_string("guidance/_answer_effect.html", {"effect": effect})
    assert "Ainda em análise: 1 providência." in html


def test_no_block_without_effect(
    loaded: dict[str, int], client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("guidance.views.answer_effect", lambda *_: AnswerEffect((), (), 0))
    _post(client, "suspenso")
    assert _effect_block(client, PLAN) is None


@pytest.mark.parametrize(
    "url",
    [
        PLAN,
        "/s/cpf-irregular/respostas/",
        "/onde-resolvo/",
        "/onde-resolvo/consultar-situacao-cpf/",
    ],
)
def test_read_only_pages_reject_post(loaded: dict[str, int], client: Client, url: str) -> None:
    assert client.get(url).status_code in {200, 302}  # o plano sem respostas volta à pergunta
    response = client.post(url)
    assert response.status_code == 405
    assert response["Allow"] == "GET"
