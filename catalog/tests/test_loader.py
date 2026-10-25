# ruff: noqa: E501
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command

from catalog.loader import load_content
from catalog.models import (
    AnswerOption,
    Dependency,
    Procedure,
    Question,
    Requirement,
    Rule,
    ServiceChannel,
    TriageNode,
)
from sources.models import Agency, Jurisdiction, Source, SourceImport, SourceSnapshot
from sources.toml_schema import ContentError

pytestmark = pytest.mark.django_db

HTML = (
    "<p>Texto sobre A. Texto  sobre\nB. Texto sobre C. Regra de aplicação. Regra condicional.</p>"
)

JOURNEY = """
[[situations]]
slug = "sit"
title = "Situação"
candidates = ["proc-a", "proc-b"]

[[questions]]
slug = "q1"
text = "Pergunta?"
kind = "SINGLE"
allows_unknown = true
situations = ["sit"]
options = [{slug = "sim", label = "Sim"}, {slug = "nao", label = "Não"}]

[[questions]]
slug = "q2"
text = "Outra?"
kind = "MULTIPLE"
situations = ["sit"]
options = [{slug = "x", label = "X"}]

[[procedures]]
slug = "proc-a"
title = "A"
description = "d"
agency = "mte"
jurisdiction = "FEDERAL"
source = "pagina"
excerpt = "Texto sobre A"
clarifies = "q1"
requirements = [{description = "r", source = "pagina", excerpt = "Texto sobre B"}]
channels = [{kind = "ONLINE", description = "c", url = "https://x.gov.br", source = "pagina", excerpt = "Texto sobre B"}]
details = [{kind = "COST", text = "grátis", source = "pagina", excerpt = "Texto sobre C"}]

[[procedures]]
slug = "proc-b"
title = "B"
description = "d"
agency = "mte"
jurisdiction = "FEDERAL"
source = "pagina"
excerpt = "Texto sobre B"

[[procedures]]
slug = "proc-c"
title = "C"
description = "d"
agency = "mte"
jurisdiction = "FEDERAL"
source = "pagina"
excerpt = "Texto sobre C"

[[rules]]
slug = "r-app"
procedure = "proc-a"
explanation = "e"
source = "pagina"
excerpt = "Regra de aplicação"
conditions = [{question = "q1", operator = "ANY_OF", options = ["sim"]}]

[[rules]]
slug = "r-cond"
explanation = "e"
source = "pagina"
excerpt = "Regra condicional"
conditions = [{question = "q2", operator = "NONE_OF", options = ["x"]}]

[[dependencies]]
before = "proc-a"
after = "proc-b"
kind = "CONDITIONAL"
rule = "r-cond"
source = "pagina"
excerpt = "Texto sobre A"

[[dependencies]]
before = "proc-b"
after = "proc-c"
kind = "RECOMMENDED"
source = "pagina"
excerpt = "Texto sobre B"
"""

EXPECTED = {
    "Situation": 1,
    "Question": 2,
    "AnswerOption": 3,
    "Procedure": 3,
    "ProcedureDetail": 1,
    "Requirement": 1,
    "ServiceChannel": 1,
    "Rule": 2,
    "Condition": 2,
    "Dependency": 2,
    "TriageNode": 0,
    "TriageChoice": 0,
}


def add_import(source: Source, html: str, when: datetime) -> SourceSnapshot:
    snapshot = SourceSnapshot.objects.create(
        source=source, content_sha256=f"{hash(html) & 0xFFFFFFFF:064x}", raw_text=html
    )
    SourceImport.objects.create(
        source=source, fetched_at=when, outcome=SourceImport.Outcome.OK, snapshot=snapshot
    )
    return snapshot


@pytest.fixture
def source() -> Source:
    agency = Agency.objects.create(slug="mte", name="MTE", jurisdiction=Jurisdiction.FEDERAL)
    source = Source.objects.create(
        slug="pagina",
        agency=agency,
        url="https://example.gov.br/p",
        format=Source.Format.HTML,
        jurisdiction=Jurisdiction.FEDERAL,
    )
    add_import(source, HTML, datetime(2026, 1, 1, tzinfo=UTC))
    return source


@pytest.fixture
def content(tmp_path: Path, source: Source) -> Path:
    (tmp_path / "journey.toml").write_text(JOURNEY)
    return tmp_path


def counts() -> list[int]:
    return list(load_content_counts().values())


def load_content_counts() -> dict[str, int]:
    from catalog.loader import _COUNTED

    return {m.__name__: m._default_manager.count() for m in _COUNTED}


def test_happy_path(content: Path) -> None:
    assert load_content(content) == EXPECTED
    assert Procedure.objects.get(slug="proc-a").clarifies == Question.objects.get(slug="q1")
    assert Rule.objects.get(slug="r-cond").conditions.get().options.get().slug == "x"


def _option_flags() -> dict[str, bool]:
    return {o.slug: o.out_of_coverage for o in AnswerOption.objects.filter(question__slug="q1")}


def test_out_of_coverage_true_false_and_absent(content: Path) -> None:
    load_content(content)
    assert _option_flags() == {"sim": False, "nao": False}
    (content / "journey.toml").write_text(
        _bump(
            '{slug = "sim", label = "Sim"}, {slug = "nao", label = "Não"}',
            '{slug = "sim", label = "Sim", out_of_coverage = true}, '
            '{slug = "nao", label = "Não", out_of_coverage = false}',
        )
    )
    load_content(content)
    assert _option_flags() == {"sim": True, "nao": False}


def test_help_text_is_stored_and_defaults_to_empty(content: Path) -> None:
    (content / "journey.toml").write_text(
        _bump('text = "Pergunta?"', 'text = "Pergunta?"\nhelp = "Dica."')
    )
    load_content(content)
    assert Question.objects.get(slug="q1").help_text == "Dica."
    assert Question.objects.get(slug="q2").help_text == ""


def _item_rule_only() -> str:
    """r-cond deixa de servir a dependência e passa a condicionar um requisito e um canal."""
    text = _bump('kind = "CONDITIONAL"\nrule = "r-cond"', 'kind = "MANDATORY"')
    text = text.replace('{description = "r", source', '{description = "r", rule = "r-cond", source')
    return text.replace(
        'url = "https://x.gov.br", source', 'url = "https://x.gov.br", rule = "r-cond", source'
    )


def test_item_rule_is_stored_and_keeps_rule_from_being_orphan(content: Path) -> None:
    (content / "journey.toml").write_text(_item_rule_only())
    load_content(content)
    rule = Rule.objects.get(slug="r-cond")
    assert Requirement.objects.get().rule == rule
    assert ServiceChannel.objects.get().rule == rule


def test_item_without_rule_has_none(content: Path) -> None:
    load_content(content)
    assert Requirement.objects.get().rule is None
    assert ServiceChannel.objects.get().rule is None


def test_reload_replaces_content_referenced_by_items(content: Path) -> None:
    (content / "journey.toml").write_text(_item_rule_only())
    load_content(content)
    load_content(content)  # PROTECT: itens saem antes das regras
    assert Requirement.objects.get().rule == Rule.objects.get(slug="r-cond")


def test_idempotent(content: Path) -> None:
    load_content(content)
    assert load_content(content) == EXPECTED


def test_removed_procedure_disappears(content: Path) -> None:
    load_content(content)
    shorter = (
        JOURNEY.split('[[procedures]]\nslug = "proc-c"')[0]
        + '[[rules]]\nslug = "r-cond"'
        + JOURNEY.split('[[rules]]\nslug = "r-cond"')[1].split("[[dependencies]]")[0]
        + "[[dependencies]]"
        + JOURNEY.split("[[dependencies]]")[1]
    ).split('[[dependencies]]\nbefore = "proc-b"')[0]
    (content / "journey.toml").write_text(shorter)
    load_content(content)
    assert not Procedure.objects.filter(slug="proc-c").exists()
    assert Dependency.objects.count() == 1


def test_sources_toml_is_ignored_and_files_merge(content: Path) -> None:
    (content / "sources.toml").write_text("lixo = 1")
    (content / "extra.toml").write_text(
        '[[situations]]\nslug = "sit-2"\ntitle = "T"\ncandidates = []\n'
    )
    assert load_content(content)["Situation"] == 2


def test_uses_latest_import(content: Path, source: Source) -> None:
    add_import(source, "<p>Nada</p>", datetime(2026, 2, 1, tzinfo=UTC) + timedelta(days=1))
    with pytest.raises(ContentError, match=r"journey\.toml: proc-a: procedimento: trecho não"):
        load_content(content)


def test_json_source_snapshot_is_searched(content: Path, source: Source) -> None:
    api = Source.objects.create(
        slug="api",
        agency=source.agency,
        url="https://example.gov.br/api",
        format=Source.Format.GOVBR_API,
        jurisdiction=Jurisdiction.FEDERAL,
    )
    snapshot = SourceSnapshot.objects.create(
        source=api, content_sha256="b" * 64, raw_text="{}", raw_json={"r": [{"t": "Texto sobre A"}]}
    )
    SourceImport.objects.create(
        source=api,
        fetched_at=datetime(2026, 1, 1, tzinfo=UTC),
        outcome=SourceImport.Outcome.OK,
        snapshot=snapshot,
    )
    (content / "journey.toml").write_text(
        JOURNEY.replace(
            'source = "pagina"\nexcerpt = "Texto sobre A"\nclarifies',
            'source = "api"\nexcerpt = "Texto sobre A"\nclarifies',
        )
    )
    assert load_content(content) == EXPECTED


def test_failed_import_only_is_not_ok(content: Path, source: Source) -> None:
    SourceImport.objects.filter(source=source).delete()
    SourceImport.objects.create(
        source=source,
        fetched_at=datetime(2026, 3, 1, tzinfo=UTC),
        outcome=SourceImport.Outcome.FAILED,
        error="HTTP 500",
    )
    with pytest.raises(ContentError, match="sem importação bem-sucedida; rode fetch_sources"):
        load_content(content)


def _bump(old: str, new: str) -> str:
    assert old in JOURNEY
    return JOURNEY.replace(old, new, 1)


ERRORS = {
    "candidate": (
        _bump('["proc-a", "proc-b"]', '["proc-a", "fantasma"]'),
        "sit: procedimento inexistente em candidates: fantasma",
    ),
    "question situation": (
        _bump('situations = ["sit"]', 'situations = ["nada"]'),
        "q1: situação inexistente: nada",
    ),
    "agency": (_bump('agency = "mte"', 'agency = "outro"'), "proc-a: órgão inexistente: outro"),
    "rule procedure": (
        _bump('procedure = "proc-a"', 'procedure = "zzz"'),
        "r-app: procedimento inexistente: zzz",
    ),
    "condition question": (
        _bump('question = "q2"', 'question = "zzz"'),
        "r-cond: pergunta inexistente: zzz",
    ),
    "option of other question": (
        _bump('options = ["x"]', 'options = ["sim"]'),
        "r-cond: opção sim não pertence à pergunta q2",
    ),
    "empty options": (_bump('options = ["x"]', "options = []"), "r-cond: condição sem opções"),
    "rule without conditions": (
        _bump(
            'conditions = [{question = "q2", operator = "NONE_OF", options = ["x"]}]',
            "conditions = []",
        ),
        "r-cond: regra sem condições",
    ),
    "reserved option": (
        _bump('{slug = "nao", label = "Não"}', '{slug = "nao-sei", label = "Não sei"}'),
        "q1: slug de opção reservado: nao-sei",
    ),
    "reserved option unknown": (
        _bump('{slug = "x", label = "X"}', '{slug = "unknown", label = "X"}'),
        "q2: slug de opção reservado: unknown",
    ),
    "clarifies without allows_unknown": (
        _bump('clarifies = "q1"', 'clarifies = "q2"'),
        "proc-a: clarifies: q2 não permite",
    ),
    "clarifies missing": (
        _bump('clarifies = "q1"', 'clarifies = "zzz"'),
        "proc-a: pergunta inexistente em clarifies: zzz",
    ),
    "conditional without rule": (
        _bump('kind = "CONDITIONAL"\nrule = "r-cond"', 'kind = "CONDITIONAL"'),
        "proc-a->proc-b: dependência CONDITIONAL sem rule",
    ),
    "rule on non conditional": (
        _bump('kind = "RECOMMENDED"', 'kind = "MANDATORY"\nrule = "r-cond"'),
        "proc-b->proc-c: rule só é permitida",
    ),
    "dependency rule with procedure": (
        _bump('rule = "r-cond"', 'rule = "r-app"'),
        "proc-a->proc-b: regra r-app define aplicabilidade",
    ),
    "dependency rule missing": (_bump('rule = "r-cond"', 'rule = "zzz"'), "regra inexistente: zzz"),
    "orphan rule": (
        _bump('kind = "CONDITIONAL"\nrule = "r-cond"', 'kind = "MANDATORY"'),
        "r-cond: regra órfã",
    ),
    "shared procedure, question linked to one situation": (
        JOURNEY + '\n[[situations]]\nslug = "sit2"\ntitle = "Outra"\ncandidates = ["proc-b"]\n',
        "r-cond: pergunta q2 não está ligada à situação sit2",
    ),
    "requirement rule question not linked": (
        _bump('{description = "r", source', '{description = "r", rule = "r-cond", source').replace(
            'situations = ["sit"]\noptions = [{slug = "x"',
            'situations = []\noptions = [{slug = "x"',
        ),
        "r-cond: pergunta q2 não está ligada à situação sit",
    ),
    "requirement rule missing": (
        _bump('{description = "r", source', '{description = "r", rule = "zzz", source'),
        "proc-a: requisito[0]: regra inexistente: zzz",
    ),
    "requirement rule with procedure": (
        _bump('{description = "r", source', '{description = "r", rule = "r-app", source'),
        "proc-a: requisito[0]: regra r-app define aplicabilidade",
    ),
    "channel rule missing": (
        _bump('url = "https://x.gov.br", source', 'url = "https://x.gov.br", rule = "zzz", source'),
        "proc-a: canal[0]: regra inexistente: zzz",
    ),
    "channel rule with procedure": (
        _bump(
            'url = "https://x.gov.br", source', 'url = "https://x.gov.br", rule = "r-app", source'
        ),
        "proc-a: canal[0]: regra r-app define aplicabilidade",
    ),
    "dependency procedure": (
        _bump('after = "proc-c"', 'after = "zzz"'),
        "proc-b->zzz: procedimento inexistente: zzz",
    ),
    "self dependency": (
        _bump('after = "proc-c"', 'after = "proc-b"'),
        "proc-b->proc-b: dependência de um procedimento sobre ele mesmo",
    ),
    "duplicate pair": (
        JOURNEY
        + '\n[[dependencies]]\nbefore = "proc-b"\nafter = "proc-c"\nkind = "MANDATORY"\nsource = "pagina"\nexcerpt = "Texto sobre B"\n',
        "proc-b->proc-c: par before/after duplicado",
    ),
    "cycle": (
        JOURNEY
        + '\n[[dependencies]]\nbefore = "proc-c"\nafter = "proc-a"\nkind = "RECOMMENDED"\nsource = "pagina"\nexcerpt = "Texto sobre B"\n',
        "ciclo entre dependências envolvendo: proc-a, proc-b, proc-c",
    ),
    "duplicate slug": (
        _bump('slug = "proc-b"', 'slug = "proc-a"'),
        "journey.toml: proc-a: slug duplicado em procedures",
    ),
    "duplicate detail": (
        _bump(
            'details = [{kind = "COST", text = "grátis", source = "pagina", excerpt = "Texto sobre C"}]',
            'details = [{kind = "COST", text = "a", source = "pagina", excerpt = "Texto sobre C"}, {kind = "COST", text = "b", source = "pagina", excerpt = "Texto sobre C"}]',
        ),
        "proc-a: detalhe duplicado: COST",
    ),
    "missing source": (
        _bump(
            'source = "pagina"\nexcerpt = "Texto sobre A"\nclarifies',
            'source = "zzz"\nexcerpt = "Texto sobre A"\nclarifies',
        ),
        "proc-a: procedimento: fonte inexistente: zzz",
    ),
    "excerpt absent": (
        _bump('excerpt = "Regra de aplicação"', 'excerpt = "não existe"'),
        "journey.toml: r-app: regra: trecho não encontrado na fonte pagina",
    ),
    "requirement excerpt absent": (
        _bump('excerpt = "Texto sobre B"}]\nchannels', 'excerpt = "não existe"}]\nchannels'),
        "proc-a: requisito[0]: trecho não encontrado",
    ),
    "invalid toml": ("[[situations\n", "journey.toml: -: TOML inválido"),
    "unknown key": (
        _bump('title = "Situação"', 'title = "Situação"\nextra = 1'),
        "journey.toml: sit: extra: chave desconhecida",
    ),
    "missing key": (
        _bump('title = "Situação"\n', ""),
        "journey.toml: sit: title: chave obrigatória ausente",
    ),
    "wrong type": (
        _bump("allows_unknown = true", 'allows_unknown = "sim"'),
        "q1: allows_unknown: esperado bool",
    ),
    "bad enum": (_bump('kind = "SINGLE"', 'kind = "TRIPLE"'), "q1: kind: valor 'TRIPLE'"),
    "long slug": (_bump('slug = "sit"', f'slug = "{"s" * 51}"'), "excede 50 caracteres"),
    "slug with space": (_bump('slug = "proc-c"', 'slug = "proc c"'), "proc c: slug: slug inválido"),
    "long title": (_bump('title = "Situação"', f'title = "{"t" * 201}"'), "sit: title: excede 200"),
    "order out of range": (
        _bump("allows_unknown = true", "allows_unknown = true\norder = -1"),
        "q1: order: fora da faixa 0..32767",
    ),
    "out_of_coverage not bool": (
        _bump('{slug = "x", label = "X"}', '{slug = "x", label = "X", out_of_coverage = "sim"}'),
        "q2: options[0].out_of_coverage: esperado bool",
    ),
    "help not string": (
        _bump('text = "Pergunta?"', 'text = "Pergunta?"\nhelp = 1'),
        "q1: help: esperado str",
    ),
    "unknown nested key": (
        _bump('{slug = "x", label = "X"}', '{slug = "x", label = "X", z = 1}'),
        "q2: options[0].z: chave desconhecida",
    ),
}


@pytest.mark.parametrize(("text", "expected"), ERRORS.values(), ids=ERRORS.keys())
def test_error_writes_nothing(content: Path, text: str, expected: str) -> None:
    load_content(content)
    before = load_content_counts()
    (content / "journey.toml").write_text(text)
    with pytest.raises(ContentError) as info:
        load_content(content)
    assert any(expected in line for line in info.value.lines), info.value.lines
    assert all(line.startswith("journey.toml: ") for line in info.value.lines)
    assert load_content_counts() == before == EXPECTED


def test_error_on_empty_database_writes_nothing(content: Path) -> None:
    (content / "journey.toml").write_text(ERRORS["cycle"][0])
    with pytest.raises(ContentError):
        load_content(content)
    assert sum(load_content_counts().values()) == 0


def test_duplicate_slug_across_files(content: Path) -> None:
    load_content(content)
    (content / "other.toml").write_text(
        '[[situations]]\nslug = "sit"\ntitle = "T"\ncandidates = []\n'
    )
    with pytest.raises(ContentError) as info:
        load_content(content)
    assert "journey.toml: sit: slug duplicado em situations" in info.value.lines
    assert "other.toml: sit: slug duplicado em situations" in info.value.lines
    assert load_content_counts() == EXPECTED


def test_accumulates_errors(content: Path) -> None:
    text = _bump('agency = "mte"', 'agency = "outro"').replace(
        'excerpt = "Regra de aplicação"', 'excerpt = "não existe"'
    )
    (content / "journey.toml").write_text(text)
    with pytest.raises(ContentError) as info:
        load_content(content)
    assert len(info.value.lines) == 2
    assert "proc-a: órgão inexistente" in info.value.lines[0]
    assert "r-app: regra: trecho não encontrado" in info.value.lines[1]


def test_command_prints_counts_and_wraps_errors(
    content: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("load_content", str(content))
    assert "Procedure: 3" in capsys.readouterr().out
    (content / "journey.toml").write_text("[[situations\n")
    with pytest.raises(CommandError, match=r"journey\.toml: -: TOML inválido"):
        call_command("load_content", str(content))


def test_tie_on_fetched_at_picks_highest_id(content: Path, source: Source) -> None:
    when = datetime(2026, 1, 1, tzinfo=UTC)
    add_import(source, "<p>Nada</p>", when)  # mesmo instante da importação da fixture, id maior
    with pytest.raises(ContentError, match="trecho não encontrado"):
        load_content(content)


@pytest.mark.parametrize("setup", ["empty", "only_sources", "missing"])
def test_no_content_files_preserves_catalog(content: Path, tmp_path: Path, setup: str) -> None:
    load_content(content)
    target = tmp_path / "outro"
    if setup != "missing":
        target.mkdir()
    if setup == "only_sources":
        (target / "sources.toml").write_text("")
    with pytest.raises(ContentError):
        load_content(target)
    assert load_content_counts() == EXPECTED


TRIAGE = """
[[triage]]
slug = "inicio"
text = "Assunto?"
help = "Dica."
options = [
  {label = "Um", next = "sub"},
  {label = "Dois", situation = "sit"},
  {label = "Três", uncovered = true},
  {label = "Quatro", uncovered = false, situation = "sit"},
]

[[triage]]
slug = "sub"
text = "Detalhe?"
options = [{label = "Fora", uncovered = true}, {label = "Volta", next = "inicio2"}]

[[triage]]
slug = "inicio2"
text = "Outro"
options = [{label = "Fim", uncovered = true}]
"""


def _triage(old: str = "", new: str = "") -> str:
    assert old in TRIAGE
    return JOURNEY + TRIAGE.replace(old, new, 1)


TRIAGE_ERRORS = {
    "missing start": (
        _triage('slug = "inicio"\n', 'slug = "comeco"\n'),
        "journey.toml: inicio: nó inicial ausente",
    ),
    "duplicate node": (
        _triage('slug = "sub"', 'slug = "inicio"'),
        "journey.toml: inicio: slug duplicado em triage",
    ),
    "no destination": (
        _triage('{label = "Três", uncovered = true}', '{label = "Três"}'),
        "inicio: options[2]: informe exatamente um entre next, situation e uncovered",
    ),
    "two destinations": (
        _triage(
            '{label = "Três", uncovered = true}',
            '{label = "Três", next = "sub", situation = "sit"}',
        ),
        "inicio: options[2]: informe exatamente um entre next, situation e uncovered",
    ),
    "uncovered false does not count": (
        _triage('{label = "Três", uncovered = true}', '{label = "Três", uncovered = false}'),
        "inicio: options[2]: informe exatamente um entre next, situation e uncovered",
    ),
    "unknown next": (
        _triage('next = "sub"', 'next = "nada"'),
        "inicio: options[0]: nó inexistente em next: nada",
    ),
    "unknown situation": (
        _triage('situation = "sit"', 'situation = "nada"'),
        "inicio: options[1]: situação inexistente: nada",
    ),
    "cycle": (
        _triage('next = "inicio2"', 'next = "inicio"'),
        "inicio: ciclo no funil de triagem envolvendo: inicio, sub",
    ),
    "self cycle": (
        _triage('{label = "Fim", uncovered = true}', '{label = "Fim", next = "inicio2"}'),
        "inicio2: ciclo no funil de triagem envolvendo: inicio2",
    ),
    "isolated cycle is also unreachable": (
        _triage()
        + '\n[[triage]]\nslug = "a"\ntext = "A"\noptions = [{label = "B", next = "b"}]\n'
        + '\n[[triage]]\nslug = "b"\ntext = "B"\noptions = [{label = "A", next = "a"}]\n',
        "a: ciclo no funil de triagem envolvendo: a, b",
    ),
    "empty text": (_triage('text = "Detalhe?"', 'text = "  "'), "sub: text vazio"),
    "empty label": (
        _triage('{label = "Fora", uncovered = true}', '{label = "", uncovered = true}'),
        "sub: options[0]: label vazio",
    ),
    "unreachable node": (
        _triage('{label = "Um", next = "sub"},', '{label = "Um", uncovered = true},'),
        "sub: nó inalcançável a partir de inicio",
    ),
    "situation not reachable": (
        _triage(
            '{label = "Dois", situation = "sit"},', '{label = "Dois", uncovered = true},'
        ).replace('{label = "Quatro", uncovered = false, situation = "sit"},', ""),
        "journey.toml: sit: situação não alcançável pelo funil de triagem",
    ),
    "node without options": (
        _triage('options = [{label = "Fim", uncovered = true}]', "options = []"),
        "inicio2: nó sem opções",
    ),
}


@pytest.mark.parametrize(("text", "expected"), TRIAGE_ERRORS.values(), ids=TRIAGE_ERRORS.keys())
def test_triage_error_writes_nothing(content: Path, text: str, expected: str) -> None:
    (content / "journey.toml").write_text(text)
    with pytest.raises(ContentError) as info:
        load_content(content)
    assert any(expected in line for line in info.value.lines), info.value.lines
    assert sum(load_content_counts().values()) == 0


def test_triage_stores_nodes_and_choices_in_order(content: Path) -> None:
    (content / "journey.toml").write_text(
        JOURNEY
        + TRIAGE.replace('{label = "Volta", next = "inicio2"}', '{label = "Volta", next = "fim"}')
        .replace('slug = "inicio2"', 'slug = "fim"')
        .replace('  {label = "Quatro", uncovered = false, situation = "sit"},\n', "")
    )
    counts = load_content(content)
    assert (counts["TriageNode"], counts["TriageChoice"]) == (3, 6)
    inicio = TriageNode.objects.get(slug="inicio")
    assert inicio.help_text == "Dica."
    first, second, third = inicio.choices.all()
    assert [c.order for c in (first, second, third)] == [1, 2, 3]
    assert first.next_node == TriageNode.objects.get(slug="sub")
    assert second.situation is not None and second.situation.slug == "sit"
    assert (third.next_node, third.situation) == (None, None)
    assert load_content(content) == counts  # recarga substitui tudo


def test_content_without_triage_is_valid(content: Path) -> None:
    assert load_content(content) == EXPECTED


def test_triage_duplicate_slug_across_files(content: Path) -> None:
    (content / "journey.toml").write_text(_triage().replace('"inicio2"', '"sub2"', 2))
    (content / "other.toml").write_text(
        '[[triage]]\nslug = "sub"\ntext = "T"\noptions = [{label = "x", uncovered = true}]\n'
    )
    with pytest.raises(ContentError) as info:
        load_content(content)
    assert "journey.toml: sub: slug duplicado em triage" in info.value.lines
    assert "other.toml: sub: slug duplicado em triage" in info.value.lines
