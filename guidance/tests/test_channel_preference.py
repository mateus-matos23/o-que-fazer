"""Preferência de atendimento (RN14): só reordena canais; nunca esconde nem muda o plano."""

import dataclasses
import re
from typing import Literal

import pytest
from django.contrib.sessions.backends.base import SessionBase
from django.test import Client

from guidance.engine.channels import PREFERENCES, lacks_preferred, order_channels
from guidance.engine.model import ChannelDef, Tri
from guidance.engine.plan import build_plan
from guidance.session import (
    PREFERENCE_KEY,
    read_channel_preference,
    write_channel_preference,
)
from guidance.tests.factories import CITATION, catalog, procedure
from guidance.views import _step_view

pytestmark = pytest.mark.django_db

URL = "/s/cpf-irregular/"
PLAN = URL + "plano/"
PREFERENCE = URL + "atendimento/"
QUESTION = "cpf-situacao-cadastral"
OTHER = "/s/desligamento-do-trabalho/atendimento/"


def _channel(
    kind: Literal["ONLINE", "IN_PERSON", "PHONE", "APP", "EMAIL"], name: str
) -> ChannelDef:
    return ChannelDef(kind, name, "", CITATION)


MIXED = [
    _channel("IN_PERSON", "p1"),
    _channel("EMAIL", "e"),
    _channel("ONLINE", "o"),
    _channel("PHONE", "t"),
    _channel("APP", "a"),
    _channel("IN_PERSON", "p2"),
]


PAIRS = [(c, Tri.APPLICABLE) for c in MIXED]


def _names(pairs: tuple[tuple[ChannelDef, Tri], ...]) -> list[str]:
    return [c.description for c, _ in pairs]


@pytest.mark.parametrize(
    ("slug", "expected"),
    [
        ("internet", ["o", "a", "p1", "e", "t", "p2"]),
        ("telefone", ["t", "p1", "e", "o", "a", "p2"]),
        ("presencial", ["p1", "p2", "e", "o", "t", "a"]),
        ("tanto-faz", ["p1", "e", "o", "t", "a", "p2"]),
    ],
)
def test_order_is_stable_per_preference_and_drops_nothing(slug: str, expected: list[str]) -> None:
    ordered = order_channels(PAIRS, PREFERENCES[slug])
    assert _names(ordered) == expected
    assert sorted(_names(ordered)) == sorted(c.description for c in MIXED)


def test_no_preference_keeps_order() -> None:
    assert order_channels(PAIRS, None) == tuple(PAIRS)


def test_email_is_in_no_group() -> None:
    assert all("EMAIL" not in p.kinds for p in PREFERENCES.values())


def test_lacks_preferred() -> None:
    only_phone = [_channel("PHONE", "t")]
    assert lacks_preferred(only_phone, PREFERENCES["presencial"])
    assert not lacks_preferred([], PREFERENCES["internet"])
    assert not lacks_preferred(only_phone, PREFERENCES["telefone"])
    assert not lacks_preferred(only_phone, PREFERENCES["tanto-faz"])
    assert not lacks_preferred(only_phone, None)


@pytest.fixture
def session(client: Client) -> SessionBase:
    return client.session


def test_session_roundtrip(session: SessionBase) -> None:
    assert read_channel_preference(session) is None
    write_channel_preference(session, "telefone")
    assert read_channel_preference(session) == PREFERENCES["telefone"]


@pytest.mark.parametrize("raw", ["invalida", 3, ["telefone"], None, {"a": 1}])
def test_session_invalid_value_is_none(session: SessionBase, raw: object) -> None:
    session[PREFERENCE_KEY] = raw
    assert read_channel_preference(session) is None


def test_preference_is_global_across_situations(loaded: dict[str, int], client: Client) -> None:
    assert client.post(PREFERENCE, {"preference": "presencial"}).status_code == 303
    html = client.get(OTHER).content.decode()
    assert re.search(r'value="presencial"[^>]*checked', html)


def _answer(client: Client) -> None:
    assert client.post(URL, {"question": QUESTION, "answer": "suspenso"}).status_code == 303


def _checked(html: str) -> list[str]:
    return re.findall(r'value="([^"]+)"[^>]*checked', html)


def test_last_question_goes_to_preference_then_plan(loaded: dict[str, int], client: Client) -> None:
    _answer(client)
    response = client.get(URL)
    assert (response.status_code, response["Location"]) == (302, PREFERENCE)
    page = client.get(PREFERENCE)
    assert page.status_code == 200
    assert "Como você prefere ser atendido?" in page.text
    assert "Nenhum canal some do plano." in page.text
    assert page.text.count('type="radio"') == 4
    done = client.post(PREFERENCE, {"preference": "telefone"})
    assert (done.status_code, done["Location"]) == (303, PLAN)
    assert client.get(URL)["Location"] == PLAN


def test_invalid_post_stays_with_error(loaded: dict[str, int], client: Client) -> None:
    for data in ({}, {"preference": "fax"}):
        response = client.post(PREFERENCE, data)
        assert response.status_code == 200
        assert 'id="form-errors"' in response.text
        assert 'aria-describedby="question-help form-errors"' in response.text
    assert read_channel_preference(client.session) is None


def test_unknown_situation_is_404(loaded: dict[str, int], client: Client) -> None:
    assert client.get("/s/nao-existe/atendimento/").status_code == 404


def test_change_link_leads_to_page_with_current_option(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client)
    client.post(PREFERENCE, {"preference": "presencial"})
    plan = client.get(PLAN).text
    assert "Canais ordenados pela sua preferência: Pessoalmente." in plan
    assert f'<a href="{PREFERENCE}">Mudar</a>' in plan
    assert _checked(client.get(PREFERENCE).text) == ["presencial"]


def test_plan_without_preference_or_tanto_faz_shows_only_the_link(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client)
    for _ in range(2):
        plan = client.get(PLAN).text
        assert "Escolher como prefere ser atendido" in plan
        assert "Canais ordenados pela sua preferência" not in plan
        client.post(PREFERENCE, {"preference": "tanto-faz"})


def test_effect_survives_preference_page_and_reaches_plan(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client)
    client.get(URL)
    assert "answer-effect" not in client.get(PREFERENCE).text
    client.post(PREFERENCE, {"preference": "internet"})
    plan = client.get(PLAN).text
    assert "Por causa dessa resposta, entrou no seu plano:" in plan
    assert "Regularizar o CPF suspenso" in plan.split('<div class="answer-effect">')[1]
    assert "Por causa dessa resposta" not in client.get(PLAN).text


def _steps(html: str) -> list[tuple[str, str]]:
    return re.findall(
        r'<article id="etapa-[^"]+" class="step" data-slug="([^"]+)">(.*?)</article>', html, re.S
    )


def _channel_items(article: str) -> list[str]:
    channels = article.split("<dt>Canais</dt>")[1].split("<dt>Custo</dt>")[0]
    return re.findall(r"<li>(.*?)</li>", channels, re.S)


def test_plan_steps_and_order_do_not_depend_on_preference(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client)
    seen = {}
    for slug in PREFERENCES:
        client.post(PREFERENCE, {"preference": slug})
        steps = _steps(client.get(PLAN).text)
        assert steps
        seen[slug] = steps
    baseline = [s for s, _ in seen["tanto-faz"]]
    for steps in seen.values():
        assert [s for s, _ in steps] == baseline
        for (_, article), (_, original) in zip(steps, seen["tanto-faz"], strict=True):
            assert sorted(_channel_items(article)) == sorted(_channel_items(original))


def test_plan_orders_channels_and_warns_when_missing(
    loaded: dict[str, int], client: Client
) -> None:
    _answer(client)
    client.post(PREFERENCE, {"preference": "presencial"})
    steps = _steps(client.get(PLAN).text)
    for _, article in steps:
        items = _channel_items(article)
        has_in_person = any(i.startswith("Presencial:") for i in items)
        notice = "Atendimento presencial não informado na fonte para esta etapa."
        assert (notice in article) is (not has_in_person)
        if has_in_person:
            assert items[0].startswith("Presencial:")
    client.post(PREFERENCE, {"preference": "tanto-faz"})
    assert "não informado na fonte para esta etapa" not in client.get(PLAN).text


def test_step_view_orders_and_warns_without_preferred_channel() -> None:
    proc = dataclasses.replace(
        procedure("p"), channels=(_channel("PHONE", "t"), _channel("ONLINE", "o"))
    )
    cat = catalog((), (proc,))
    step = build_plan(cat, {}).steps[0]
    view = _step_view(cat, step, PREFERENCES["internet"])
    assert [line.channel.description for line in view.channels] == ["o", "t"]
    assert view.channel_notice == ""
    presencial = _step_view(cat, step, PREFERENCES["presencial"])
    assert [line.channel.description for line in presencial.channels] == ["t", "o"]
    assert presencial.channel_notice == PREFERENCES["presencial"].missing_notice
    assert _step_view(cat, step).channel_notice == ""
