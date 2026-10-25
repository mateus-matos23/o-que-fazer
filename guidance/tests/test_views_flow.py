import logging
from typing import Literal

import pytest
from django.http import HttpResponse
from django.test import Client

from guidance.engine.model import OptionDef, QuestionDef, Unknown
from guidance.forms import UNKNOWN_VALUE, AnswerForm

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
PLAN = "/s/cpf-irregular/plano/"
QUESTION = "cpf-situacao-cadastral"


def _post(client: Client, value: str | None, question: str = QUESTION) -> HttpResponse:
    data = {"question": question}
    if value is not None:
        data["answer"] = value
    response = client.post(URL, data)
    assert isinstance(response, HttpResponse)
    return response


def _plan(client: Client) -> str:
    response = client.get(URL, follow=True)
    assert response.redirect_chain[-1] == (PLAN, 302)
    return response.content.decode()


def test_lists_situations(loaded: dict[str, int], client: Client) -> None:
    assert "Meu CPF está irregular" in client.get("/").content.decode()


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
    return QuestionDef("q", "Pergunta?", kind, unknown, 1, options)


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
