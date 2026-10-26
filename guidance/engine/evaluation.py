"""Avaliação ternária (Kleene) de regras e procedimentos. Decide o que se aplica, nunca a ordem."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from guidance.engine.model import Catalog, ConditionDef, Facts, ProcedureDef, RuleDef, Tri, Unknown


@dataclass(frozen=True, slots=True)
class Evaluation:
    status: Tri
    rules: tuple[tuple[RuleDef, Tri], ...]  # resultado por regra: base da explicação (RF19)


def validate_facts(catalog: Catalog, facts: Facts) -> None:
    for slug, answer in facts.items():
        question = catalog.questions.get(slug)
        if question is None:
            raise ValueError(f"pergunta {slug!r} não existe no catálogo")
        if isinstance(answer, Unknown):
            if not question.allows_unknown:
                raise ValueError(f"a pergunta {slug!r} não aceita 'não sei'")
            continue
        invalid = sorted(answer - {option.slug for option in question.options})
        if invalid:
            raise ValueError(f"opções inexistentes na pergunta {slug!r}: {', '.join(invalid)}")
        if question.kind == "SINGLE" and len(answer) != 1:
            raise ValueError(
                f"a pergunta {slug!r} exige exatamente uma opção, recebeu {len(answer)}"
            )


def evaluate_condition(condition: ConditionDef, facts: Facts) -> Tri:
    answer = facts.get(condition.question)
    if answer is None or isinstance(answer, Unknown):
        return Tri.UNDETERMINED
    matches = not answer.isdisjoint(condition.options)
    if matches == (condition.operator == "ANY_OF"):
        return Tri.APPLICABLE
    return Tri.NOT_APPLICABLE


def evaluate_rule(rule: RuleDef, facts: Facts) -> Tri:
    """E de Kleene: um NOT_APPLICABLE basta; sem ele, um UNDETERMINED contamina."""
    results = {evaluate_condition(condition, facts) for condition in rule.conditions}
    if Tri.NOT_APPLICABLE in results:
        return Tri.NOT_APPLICABLE
    if Tri.UNDETERMINED in results:
        return Tri.UNDETERMINED
    return Tri.APPLICABLE


class _Conditional(Protocol):
    @property
    def rule(self) -> RuleDef | None: ...


def visible_items[T: _Conditional](items: Iterable[T], facts: Facts) -> tuple[tuple[T, Tri], ...]:
    """Requisitos e canais condicionais (RF25): sem regra vale sempre; NOT_APPLICABLE sai;
    UNDETERMINED fica, para a interface marcar como "pode valer". Mantém a ordem."""
    pairs = ((i, Tri.APPLICABLE if i.rule is None else evaluate_rule(i.rule, facts)) for i in items)
    return tuple((i, t) for i, t in pairs if t is not Tri.NOT_APPLICABLE)


def evaluate_procedure(procedure: ProcedureDef, facts: Facts) -> Evaluation:
    """OU de Kleene das regras; sem regras o procedimento é sempre aplicável."""
    results = tuple((rule, evaluate_rule(rule, facts)) for rule in procedure.rules)
    statuses = {status for _, status in results}
    if not results or Tri.APPLICABLE in statuses:
        status = Tri.APPLICABLE
    elif Tri.UNDETERMINED in statuses:
        status = Tri.UNDETERMINED
    else:
        status = Tri.NOT_APPLICABLE
    return Evaluation(status, results)


def evaluate(catalog: Catalog, facts: Facts) -> dict[str, Evaluation]:
    validate_facts(catalog, facts)
    return {
        slug: evaluate_procedure(catalog.procedures[slug], facts) for slug in catalog.candidates
    }


def pending_rule_questions(
    catalog: Catalog, facts: Facts, evaluations: dict[str, Evaluation]
) -> Counter[str]:
    """Perguntas citadas por regras indeterminadas que ainda importam, com a contagem de regras:
    de candidatos indeterminados, de dependências condicionais de etapas aplicáveis e de
    requisitos ou canais condicionais de procedimentos aplicáveis. Inclui as já respondidas."""
    pending: Counter[str] = Counter()
    for evaluation in evaluations.values():
        if evaluation.status is not Tri.UNDETERMINED:
            continue
        pending.update(
            {
                condition.question
                for rule, status in evaluation.rules
                if status is Tri.UNDETERMINED
                for condition in rule.conditions
            }
        )
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
            pending.update({c.question for c in rule.conditions})
    # Requisito ou canal condicional indeterminado de procedimento aplicável.
    # shortcut: itens condicionais de pré-requisitos puxados e de esclarecimentos não geram
    # pergunta (a marca "pode valer" persiste); pontuar sobre as etapas de build_plan quando
    # houver conteúdo assim.
    for slug, evaluation in evaluations.items():
        if evaluation.status is not Tri.APPLICABLE:
            continue
        procedure = catalog.procedures[slug]
        item_rules = [i.rule for i in procedure.requirements] + [i.rule for i in procedure.channels]
        for rule in item_rules:
            if rule is not None and evaluate_rule(rule, facts) is Tri.UNDETERMINED:
                pending.update({c.question for c in rule.conditions})
    return pending
