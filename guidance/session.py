"""Fatos da sessão Django: {situation_slug: {question_slug: [option_slugs] | "unknown"}}."""

import logging
from typing import Any

from django.contrib.sessions.backends.base import SessionBase

from guidance.engine.evaluation import validate_facts
from guidance.engine.model import Answer, Catalog, Facts, Unknown

logger = logging.getLogger(__name__)
KEY = "facts"
UNKNOWN = "unknown"


def _parse(raw: Any) -> Answer:
    if raw == UNKNOWN:
        return Unknown.UNKNOWN
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return frozenset(raw)
    raise ValueError("formato inesperado")


def read_facts(session: SessionBase, catalog: Catalog) -> Facts:
    """Descarta (com log) respostas inválidas no catálogo atual; a pergunta volta a ser feita."""
    stored = session.get(KEY, {}).get(catalog.situation_slug, {})
    if not isinstance(stored, dict):
        stored = {}
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
        session[KEY] = {**session.get(KEY, {}), catalog.situation_slug: _serialize(facts)}
    return facts


def _serialize(facts: Facts) -> dict[str, Any]:
    return {
        slug: UNKNOWN if isinstance(answer, Unknown) else sorted(answer)
        for slug, answer in facts.items()
    }


def write_answer(
    session: SessionBase, situation_slug: str, question_slug: str, answer: Answer
) -> None:
    all_facts = session.get(KEY, {})
    current = all_facts.get(situation_slug, {})
    current[question_slug] = UNKNOWN if isinstance(answer, Unknown) else sorted(answer)
    all_facts[situation_slug] = current
    session[KEY] = all_facts
    session.modified = True
