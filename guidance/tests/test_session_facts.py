from typing import Any

import pytest
from django.contrib.sessions.backends.base import SessionBase
from django.test import Client

from guidance.engine.model import Unknown
from guidance.session import KEY, clear_situation, read_facts, write_answer
from guidance.tests.factories import catalog, procedure, question

pytestmark = pytest.mark.django_db

CAT = catalog((question("q"),), (procedure("p1"),))


@pytest.fixture
def session(client: Client) -> SessionBase:
    return client.session


def test_roundtrip_keeps_unknown_and_options(session: SessionBase) -> None:
    write_answer(session, CAT.situation_slug, "q", Unknown.UNKNOWN)
    assert read_facts(session, CAT) == {"q": Unknown.UNKNOWN}
    write_answer(session, CAT.situation_slug, "q", frozenset({"a"}))
    assert read_facts(session, CAT) == {"q": frozenset({"a"})}


@pytest.mark.parametrize("raw", ["lixo", ["q"], None, {CAT.situation_slug: "lixo"}])
def test_corrupted_facts_are_ignored(session: SessionBase, raw: Any) -> None:
    session[KEY] = raw
    assert read_facts(session, CAT) == {}
    write_answer(session, CAT.situation_slug, "q", frozenset({"a"}))
    assert read_facts(session, CAT) == {"q": frozenset({"a"})}


def test_clear_situation_with_corrupted_facts(session: SessionBase) -> None:
    session[KEY] = "lixo"
    clear_situation(session, CAT.situation_slug)
    assert read_facts(session, CAT) == {}


def test_clear_situation_keeps_other_situations(session: SessionBase) -> None:
    write_answer(session, CAT.situation_slug, "q", frozenset({"a"}))
    write_answer(session, "outra", "q", frozenset({"b"}))
    clear_situation(session, CAT.situation_slug)
    assert read_facts(session, CAT) == {}
    assert session[KEY] == {"outra": {"q": ["b"]}}
