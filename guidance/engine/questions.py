"""Próxima pergunta: a de maior impacto (RN02); sem impacto, para (RN10)."""

from collections import Counter

from guidance.engine.evaluation import Evaluation
from guidance.engine.model import Catalog, Facts, QuestionDef, Tri


def next_question(
    catalog: Catalog, facts: Facts, evaluations: dict[str, Evaluation]
) -> QuestionDef | None:
    """Pontuação = candidatos indeterminados com regra indeterminada que cita a pergunta."""
    scores: Counter[str] = Counter()
    for evaluation in evaluations.values():
        if evaluation.status is not Tri.UNDETERMINED:
            continue
        asked = {
            condition.question
            for rule, status in evaluation.rules
            if status is Tri.UNDETERMINED
            for condition in rule.conditions
            if condition.question not in facts  # UNKNOWN conta como respondida: nunca repetir
        }
        scores.update(asked)
    best = [catalog.questions[slug] for slug in scores]  # só pontuação > 0 entra no Counter
    return min(best, key=lambda q: (-scores[q.slug], q.order, q.slug), default=None)
