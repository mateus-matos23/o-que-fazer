"""Próxima pergunta: a de maior impacto (RN02); sem impacto, para (RN10)."""

from collections import Counter

from guidance.engine.evaluation import Evaluation, evaluate_rule
from guidance.engine.model import Catalog, Facts, QuestionDef, Tri


def next_question(
    catalog: Catalog, facts: Facts, evaluations: dict[str, Evaluation]
) -> QuestionDef | None:
    """Pontuação = candidatos indeterminados (e dependências condicionais indeterminadas de
    candidatos aplicáveis, e requisitos ou canais condicionais de candidatos aplicáveis) com regra
    indeterminada que cita a pergunta. Perguntas já respondidas, inclusive com "não sei", não
    pontuam."""
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
    # CONDITIONAL indeterminada sobre etapa aplicável: a resposta pode puxar pré-requisito.
    for dependency in catalog.dependencies:
        after = evaluations.get(dependency.after)
        rule = dependency.rule
        if (
            dependency.kind == "CONDITIONAL"
            and rule is not None
            and after is not None
            and after.status is Tri.APPLICABLE
            and evaluate_rule(rule, facts) is Tri.UNDETERMINED
        ):
            scores.update({c.question for c in rule.conditions if c.question not in facts})
    # Requisito ou canal condicional indeterminado de procedimento aplicável.
    # shortcut: itens condicionais de pré-requisitos puxados e de esclarecimentos não geram
    # pergunta (a marca "pode valer" persiste); pontuar sobre as etapas de build_plan quando
    # houver conteúdo assim.
    for evaluation_slug, evaluation in evaluations.items():
        if evaluation.status is not Tri.APPLICABLE:
            continue
        procedure = catalog.procedures[evaluation_slug]
        item_rules = [i.rule for i in procedure.requirements] + [i.rule for i in procedure.channels]
        for rule in item_rules:
            if rule is not None and evaluate_rule(rule, facts) is Tri.UNDETERMINED:
                scores.update({c.question for c in rule.conditions if c.question not in facts})
    best = [catalog.questions[slug] for slug in scores]  # só pontuação > 0 entra no Counter
    return min(best, key=lambda q: (-scores[q.slug], q.order, q.slug), default=None)
