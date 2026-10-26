"""Requisitos e canais condicionais (RF25): filtro, plano, perguntas, repositório e páginas."""

from dataclasses import replace

import pytest
from django.template.loader import render_to_string
from django.test import Client

from catalog.models import Requirement, Rule, ServiceChannel
from guidance.engine.evaluation import evaluate, visible_items
from guidance.engine.model import (
    Catalog,
    ChannelDef,
    Facts,
    ProcedureDef,
    RequirementDef,
    RuleDef,
    Tri,
    Unknown,
)
from guidance.engine.plan import build_plan
from guidance.engine.questions import next_question
from guidance.presentation import plan_context
from guidance.repository import clear_catalog_cache, load_catalog, load_procedure
from guidance.tests import factories as f

UNKNOWN = Unknown.UNKNOWN
YES: Facts = {"q": frozenset({"a"})}
NO: Facts = {"q": frozenset({"b"})}
WHEN_Q = f.rule("quando-q", f.cond("q", "ANY_OF", "a"))
WHEN_W = f.rule("quando-w", f.cond("w", "ANY_OF", "a"))
QUESTIONS = (f.question("q"), f.question("w", order=1))


def _req(text: str, rule: RuleDef | None = None) -> RequirementDef:
    return RequirementDef(text, f.CITATION, rule)


def _chan(name: str, rule: RuleDef | None = None) -> ChannelDef:
    return ChannelDef("ONLINE", name, "", f.CITATION, rule)


def _proc(
    slug: str,
    requirements: tuple[RequirementDef, ...] = (),
    channels: tuple[ChannelDef, ...] = (),
    *rules: RuleDef,
) -> ProcedureDef:
    return replace(f.procedure(slug, *rules), requirements=requirements, channels=channels)


def _pairs(facts: Facts, *items: RequirementDef) -> list[tuple[str, Tri]]:
    return [(r.description, t) for r, t in visible_items(items, facts)]


# Filtro


def test_filter_covers_the_three_states_and_item_without_rule() -> None:
    items = (_req("sem regra"), _req("com regra", WHEN_Q))
    assert _pairs(YES, *items) == [("sem regra", Tri.APPLICABLE), ("com regra", Tri.APPLICABLE)]
    assert _pairs(NO, *items) == [("sem regra", Tri.APPLICABLE)]
    assert _pairs({}, *items) == [("sem regra", Tri.APPLICABLE), ("com regra", Tri.UNDETERMINED)]


def test_filter_treats_dont_know_as_undetermined_not_negative() -> None:
    assert _pairs({"q": UNKNOWN}, _req("x", WHEN_Q)) == [("x", Tri.UNDETERMINED)]


def test_filter_preserves_original_order() -> None:
    items = (_req("1", WHEN_Q), _req("2"), _req("3", WHEN_Q), _req("4", WHEN_W))
    assert [name for name, _ in _pairs({"q": frozenset({"a"})}, *items)] == ["1", "2", "3", "4"]
    assert [name for name, _ in _pairs(NO, *items)] == ["2", "4"]


def test_filter_applies_to_channels_too() -> None:
    pairs = visible_items((_chan("a", WHEN_Q), _chan("b")), NO)
    assert [(c.description, t) for c, t in pairs] == [("b", Tri.APPLICABLE)]


# Plano (invariante 8)


def _plan_catalog() -> Catalog:
    proc = _proc(
        "p",
        (_req("r1"), _req("r2", WHEN_Q)),
        (_chan("c1", WHEN_Q), _chan("c2")),
    )
    return f.catalog(QUESTIONS, (proc,))


def _step_items(facts: Facts) -> tuple[list[tuple[str, Tri]], list[tuple[str, Tri]]]:
    step = build_plan(_plan_catalog(), facts).steps[0]
    return (
        [(r.description, t) for r, t in step.requirements],
        [(c.description, t) for c, t in step.channels],
    )


def test_plan_step_items_follow_the_answer() -> None:
    assert _step_items(YES) == (
        [("r1", Tri.APPLICABLE), ("r2", Tri.APPLICABLE)],
        [("c1", Tri.APPLICABLE), ("c2", Tri.APPLICABLE)],
    )
    assert _step_items(NO) == ([("r1", Tri.APPLICABLE)], [("c2", Tri.APPLICABLE)])
    assert _step_items({"q": UNKNOWN}) == (
        [("r1", Tri.APPLICABLE), ("r2", Tri.UNDETERMINED)],
        [("c1", Tri.UNDETERMINED), ("c2", Tri.APPLICABLE)],
    )


# Próxima pergunta


def _ask(cat: Catalog, facts: Facts) -> str | None:
    chosen = next_question(cat, facts, evaluate(cat, facts))
    return chosen.slug if chosen else None


def test_question_scored_by_item_of_applicable_procedure() -> None:
    cat = f.catalog(QUESTIONS, (_proc("p", (_req("r", WHEN_Q),)),))
    assert _ask(cat, {}) == "q"
    assert _ask(cat, YES) is None
    cat = f.catalog(QUESTIONS, (_proc("p", (), (_chan("c", WHEN_Q),)),))
    assert _ask(cat, {}) == "q"


def test_question_not_scored_when_procedure_is_not_applicable() -> None:
    gate = f.rule("gate", f.cond("w", "ANY_OF", "a"))
    cat = f.catalog(QUESTIONS, (_proc("p", (_req("r", WHEN_Q),), (), gate),))
    assert _ask(cat, {"w": frozenset({"b"})}) is None  # NOT_APPLICABLE
    assert _ask(cat, {}) == "w"  # UNDETERMINED: só a pergunta do procedimento pontua


def test_question_not_repeated_after_dont_know() -> None:
    cat = f.catalog(QUESTIONS, (_proc("p", (_req("r", WHEN_Q),)),))
    assert _ask(cat, {"q": UNKNOWN}) is None


def test_priority_between_loops_is_deterministic() -> None:
    # w: 1 (candidato indeterminado) + 1 (requisito); q: 1 requisito. w vence por pontuação.
    gate = f.rule("gate", f.cond("w", "ANY_OF", "a"))
    cat = f.catalog(
        QUESTIONS,
        (
            _proc("p", (_req("r", WHEN_Q),), (), gate),
            _proc("s", (_req("r", WHEN_W),)),
        ),
    )
    assert _ask(cat, {}) == "w"
    # Empate (cada pergunta com 1 ponto): ordem e slug decidem, não a ordem dos laços.
    tie = f.catalog(QUESTIONS, (_proc("s", (_req("r", WHEN_W),), (_chan("c", WHEN_Q),)),))
    assert _ask(tie, {}) == "q"
    assert _ask(tie, {}) == _ask(tie, {})


# Repositório


@pytest.mark.django_db
def test_repository_fills_item_rule_and_keeps_query_count(loaded: dict[str, int]) -> None:
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    def count() -> int:
        clear_catalog_cache()  # mede a montagem, não o acerto de cache
        with CaptureQueriesContext(connection) as ctx:
            load_catalog("cpf-irregular")
        return len(ctx)

    baseline = count()
    rule = Rule.objects.filter(procedure__isnull=True).first() or Rule.objects.first()
    assert rule is not None
    for requirement in Requirement.objects.all():
        requirement.rule = rule
        requirement.save()
    for channel in ServiceChannel.objects.all():
        channel.rule = rule
        channel.save()

    with_rules = count()
    assert with_rules == baseline + 6  # condições, perguntas e opções, por requisito e por canal
    for i in range(5):
        template = Requirement.objects.first()
        assert template is not None
        Requirement.objects.create(
            procedure=template.procedure,
            description=f"extra {i}",
            rule=rule,
            snapshot=template.snapshot,
            excerpt="x",
        )
    assert count() == with_rules
    procedures = load_catalog("cpf-irregular").procedures.values()
    rules = [i.rule for p in procedures for i in p.requirements] + [
        i.rule for p in procedures for i in p.channels
    ]
    assert rules and all(r is not None and r.slug == rule.slug for r in rules)


@pytest.mark.django_db
def test_repository_item_without_rule_is_none(loaded: dict[str, int]) -> None:
    procedures = load_catalog("cpf-irregular").procedures.values()
    assert all(i.rule is None for p in procedures for i in p.requirements)
    assert all(i.rule is None for p in procedures for i in p.channels)


# Páginas


def _render(catalog: Catalog, facts: Facts) -> str:
    plan = build_plan(catalog, facts)
    context = {"catalog": catalog, "plan": plan, **plan_context(catalog, plan, None)}
    return render_to_string("guidance/plan.html", context)


MAYBE = "Pode valer para você:"


def test_plan_marks_undetermined_items_with_visible_text() -> None:
    html = _render(_plan_catalog(), {"q": UNKNOWN})
    assert f'<span class="maybe">{MAYBE}</span> quando-q' in html
    assert html.count(MAYBE) == 3  # requisito em "separar antes" e na etapa; canal na etapa


def test_plan_hides_not_applicable_items_everywhere() -> None:
    proc = _proc(
        "p", (_req("Doc comum"), _req("Doc escondido", WHEN_Q)), (_chan("Canal oculto", WHEN_Q),)
    )
    html = _render(f.catalog(QUESTIONS, (proc,)), NO)
    assert "Doc comum" in html
    assert "Doc escondido" not in html and "Canal oculto" not in html
    assert MAYBE not in html


def test_prepare_section_skips_step_whose_items_are_all_hidden() -> None:
    proc = _proc("p", (_req("Doc escondido", WHEN_Q),))
    html = _render(f.catalog(QUESTIONS, (proc,)), NO)
    assert "O que separar antes" not in html


def test_all_hidden_shows_notice_instead_of_not_informed() -> None:
    proc = _proc("p", (_req("R", WHEN_Q),), (_chan("C", WHEN_Q),))
    html = _render(f.catalog(QUESTIONS, (proc,)), NO)
    assert html.count("Nenhum dos itens da fonte vale para o que você informou.") == 2
    assert "Não informado" in html  # custo e prazo continuam sem fonte
    assert html.count('<span class="not-informed">Não informado</span>') == 3  # custo, prazo, data


def test_procedure_without_items_still_says_not_informed() -> None:
    html = _render(f.catalog(QUESTIONS, (_proc("p"),)), NO)
    assert "Nenhum dos itens" not in html


def test_hidden_channel_does_not_trigger_preference_notice() -> None:
    from guidance.engine.channels import PREFERENCES
    from guidance.presentation import step_view

    cat = f.catalog(QUESTIONS, (_proc("p", (), (_chan("C", WHEN_Q),)),))
    step = build_plan(cat, NO).steps[0]
    view = step_view(cat, step, PREFERENCES["telefone"])
    assert view.channels == () and view.channel_notice == ""


@pytest.mark.django_db
def test_procedure_detail_marks_items_that_have_a_rule(
    loaded: dict[str, int], client: Client
) -> None:
    requirement = Requirement.objects.filter(procedure__slug="extrato-vinculos-caged").first()
    channel = ServiceChannel.objects.filter(procedure__slug="extrato-vinculos-caged").first()
    rule = Rule.objects.first()
    assert requirement and channel and rule
    requirement.rule = channel.rule = rule
    requirement.save()
    channel.save()
    html = client.get("/onde-resolvo/extrato-vinculos-caged/").content.decode()
    assert f'<span class="maybe">{MAYBE}</span> {rule.explanation}' in html
    assert requirement.description in html
    assert load_procedure("extrato-vinculos-caged").requirements[0].rule is not None


def test_pulled_prerequisite_item_is_marked_but_asks_nothing() -> None:
    # Limite conhecido (shortcut em next_question): só candidatos APPLICABLE pontuam por item.
    cat = f.catalog(
        QUESTIONS,
        (_proc("main"), _proc("pre", (_req("Doc", WHEN_Q),))),
        candidates=("main",),
        dependencies=(f.dep("pre", "main"),),
    )
    assert _ask(cat, {}) is None
    assert MAYBE in _render(cat, {})
