"""Fatos da sessão Django: {situation_slug: {question_slug: [option_slugs] | "unknown"}}."""

import logging
from typing import Any

from django.contrib.sessions.backends.base import SessionBase

from guidance.engine.channels import PREFERENCES, ChannelPreference
from guidance.engine.effect import AnswerEffect
from guidance.engine.evaluation import validate_facts
from guidance.engine.model import Answer, Catalog, Facts, Unknown

logger = logging.getLogger(__name__)
KEY = "facts"
EFFECT_KEY = "answer_effect"
UNKNOWN = "unknown"
PREFERENCE_KEY = "channel_preference"


def _parse(raw: Any) -> Answer:
    if raw == UNKNOWN:
        return Unknown.UNKNOWN
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return frozenset(raw)
    raise ValueError("formato inesperado")


def _stored_facts(session: SessionBase) -> dict[str, Any]:
    stored = session.get(KEY, {})
    return stored if isinstance(stored, dict) else {}


def _situation_facts(all_facts: dict[str, Any], situation_slug: str) -> dict[str, Any]:
    stored = all_facts.get(situation_slug, {})
    return stored if isinstance(stored, dict) else {}


def read_facts(session: SessionBase, catalog: Catalog) -> Facts:
    """Descarta (com log) respostas inválidas no catálogo atual; a pergunta volta a ser feita."""
    all_facts = _stored_facts(session)
    stored = _situation_facts(all_facts, catalog.situation_slug)
    facts: dict[str, Answer] = {}
    for question_slug, raw in stored.items():
        try:
            answer = _parse(raw)
            validate_facts(catalog, {question_slug: answer})
        except ValueError as error:
            logger.warning(
                "resposta descartada: situação=%s pergunta=%s (%s)",
                catalog.situation_slug,
                question_slug,
                error,
            )
            continue
        facts[question_slug] = answer
    if len(facts) != len(stored):
        session[KEY] = {**all_facts, catalog.situation_slug: _serialize(facts)}
    return facts


def _serialize(facts: Facts) -> dict[str, Any]:
    return {
        slug: UNKNOWN if isinstance(answer, Unknown) else sorted(answer)
        for slug, answer in facts.items()
    }


def write_answer(
    session: SessionBase, situation_slug: str, question_slug: str, answer: Answer
) -> None:
    all_facts = _stored_facts(session)
    current = _situation_facts(all_facts, situation_slug)
    current[question_slug] = UNKNOWN if isinstance(answer, Unknown) else sorted(answer)
    all_facts[situation_slug] = current
    session[KEY] = all_facts
    session.modified = True


def clear_situation(session: SessionBase, situation_slug: str) -> None:
    all_facts = _stored_facts(session)
    if all_facts.pop(situation_slug, None) is not None:
        session[KEY] = all_facts


def write_effect(session: SessionBase, situation_slug: str, effect: AnswerEffect) -> None:
    """Aviso de uso único: só slugs e o inteiro; os fatos continuam sendo a única verdade."""
    session[EFFECT_KEY] = {
        **_stored_effects(session),
        situation_slug: {
            "entered": list(effect.entered),
            "left": list(effect.left),
            "in_play": effect.in_play,
        },
    }


def _stored_effects(session: SessionBase) -> dict[str, Any]:
    stored = session.get(EFFECT_KEY, {})
    return stored if isinstance(stored, dict) else {}


def _known_slugs(raw: Any, catalog: Catalog) -> tuple[str, ...] | None:
    if not isinstance(raw, list):
        return None
    if not all(isinstance(slug, str) and slug in catalog.procedures for slug in raw):
        return None
    return tuple(raw)


def pop_effect(session: SessionBase, catalog: Catalog) -> AnswerEffect | None:
    """Lê e apaga o aviso da situação. Formato corrompido ou slug desconhecido vira None."""
    stored = _stored_effects(session)
    if catalog.situation_slug not in stored:
        return None
    raw = stored.pop(catalog.situation_slug)
    session[EFFECT_KEY] = stored
    if not isinstance(raw, dict):
        return None
    entered = _known_slugs(raw.get("entered"), catalog)
    left = _known_slugs(raw.get("left"), catalog)
    in_play = raw.get("in_play")
    if entered is None or left is None or type(in_play) is not int or in_play < 0:
        return None
    return AnswerEffect(entered, left, in_play)


def read_channel_preference(session: SessionBase) -> ChannelPreference | None:
    """Global (vale para todas as situações). Valor desconhecido ou corrompido vira None."""
    raw = session.get(PREFERENCE_KEY)
    return PREFERENCES.get(raw) if isinstance(raw, str) else None


def write_channel_preference(session: SessionBase, value: str) -> None:
    session[PREFERENCE_KEY] = value
