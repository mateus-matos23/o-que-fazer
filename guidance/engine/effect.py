"""Efeito de uma resposta no plano: compara o plano de antes com o de depois."""

from dataclasses import dataclass

from guidance.engine.model import Catalog, Facts
from guidance.engine.plan import build_plan


@dataclass(frozen=True, slots=True)
class AnswerEffect:
    entered: tuple[str, ...]  # slugs que entraram nas etapas do plano
    left: tuple[str, ...]  # slugs que estavam nas etapas e saíram
    in_play: int  # procedimentos em análise (plan.undetermined) no plano de depois


def answer_effect(catalog: Catalog, before: Facts, after: Facts) -> AnswerEffect:
    """ "No plano" = etapas de build_plan. DependencyCycleError propaga (invariante 5)."""
    plan_before = build_plan(catalog, before)
    plan_after = build_plan(catalog, after)
    slugs_before = {step.procedure.slug for step in plan_before.steps}
    slugs_after = {step.procedure.slug for step in plan_after.steps}
    return AnswerEffect(
        # entered segue a ordem das etapas; left, a do catálogo (as etapas de antes já não valem)
        tuple(s.procedure.slug for s in plan_after.steps if s.procedure.slug not in slugs_before),
        tuple(slug for slug in catalog.procedures if slug in slugs_before - slugs_after),
        len(plan_after.undetermined),
    )
