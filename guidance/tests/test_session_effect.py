from typing import Any

import pytest
from django.contrib.sessions.backends.base import SessionBase
from django.test import Client

from guidance.engine.effect import AnswerEffect
from guidance.session import EFFECT_KEY, pop_effect, write_effect
from guidance.tests.factories import catalog, procedure, question

pytestmark = pytest.mark.django_db

CAT = catalog((question("q"),), (procedure("p1"), procedure("p2")))
OTHER = catalog((question("q"),), (procedure("p1"),))


@pytest.fixture
def session(client: Client) -> SessionBase:
    return client.session


def test_roundtrip_and_single_use(session: SessionBase) -> None:
    effect = AnswerEffect(("p1",), ("p2",), 2)
    write_effect(session, CAT.situation_slug, effect)
    assert pop_effect(session, CAT) == effect
    assert pop_effect(session, CAT) is None


def test_effect_is_per_situation(session: SessionBase) -> None:
    write_effect(session, "outra", AnswerEffect(("p1",), (), 0))
    assert pop_effect(session, CAT) is None
    assert "outra" in session[EFFECT_KEY]


@pytest.mark.parametrize(
    "raw",
    [
        "lixo",
        {"entered": ["fantasma"], "left": [], "in_play": 0},
        {"entered": "p1", "left": [], "in_play": 0},
        {"entered": [1], "left": [], "in_play": 0},
        {"entered": [], "left": [], "in_play": "2"},
        {"entered": [], "left": [], "in_play": True},
        {"entered": [], "left": [], "in_play": -1},
        {"entered": [], "left": []},
    ],
)
def test_corrupted_value_is_none(session: SessionBase, raw: Any) -> None:
    session[EFFECT_KEY] = {CAT.situation_slug: raw}
    assert pop_effect(session, CAT) is None
    assert pop_effect(session, CAT) is None


def test_corrupted_container_is_none(session: SessionBase) -> None:
    session[EFFECT_KEY] = "lixo"
    assert pop_effect(session, CAT) is None
