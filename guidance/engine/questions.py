"""Próxima pergunta: a de maior impacto (RN02); sem impacto, para (RN10)."""

from collections import Counter

from guidance.engine.evaluation import Evaluation, pending_rule_questions
from guidance.engine.model import Catalog, Facts, QuestionDef


def next_question(
    catalog: Catalog, facts: Facts, evaluations: dict[str, Evaluation]
) -> QuestionDef | None:
    """Pontuação = candidatos indeterminados (e dependências condicionais indeterminadas de
    candidatos aplicáveis, e requisitos ou canais condicionais de candidatos aplicáveis) com regra
    indeterminada que cita a pergunta. Perguntas já respondidas, inclusive com "não sei", não
    pontuam."""
    pending = pending_rule_questions(catalog, facts, evaluations)
    scores = Counter({slug: n for slug, n in pending.items() if slug not in facts})
    # UNKNOWN conta como respondida: nunca repetir
    best = [catalog.questions[slug] for slug in scores]  # só pontuação > 0 entra no Counter
    return min(best, key=lambda q: (-scores[q.slug], q.order, q.slug), default=None)
