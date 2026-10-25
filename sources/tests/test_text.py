import pytest

from sources.models import SourceSnapshot
from sources.text import contains_excerpt, normalize_whitespace, snapshot_text


def test_normalize_whitespace() -> None:
    assert normalize_whitespace("  a \n\t b  ") == "a b"


def test_normalize_glues_punctuation_split_by_tags() -> None:
    snapshot = SourceSnapshot(raw_text="<p>é <b>gratuita</b>, exceto (<span> R$ 7,00</span>).</p>")
    assert snapshot_text(snapshot) == "é gratuita, exceto (R$ 7,00)."
    assert contains_excerpt(snapshot_text(snapshot), "gratuita, exceto (R$ 7,00).")


def test_html_text_drops_tags_and_decodes_entities() -> None:
    snapshot = SourceSnapshot(raw_text="<p>Taxa:  <b>R$&nbsp;10</b>\n e   &amp; mais</p>")
    assert snapshot_text(snapshot) == "Taxa: R$ 10 e & mais"


def test_json_collects_nested_strings_only() -> None:
    snapshot = SourceSnapshot(
        raw_text="ignorado",
        raw_json={"a": "um", "b": [{"c": "dois  três"}, ["quatro"], 5, None], "n": 1},
    )
    assert snapshot_text(snapshot) == "um dois três quatro"


@pytest.mark.parametrize("excerpt", ["alfa beta", "alfa\nbeta", "  alfa \t beta "])
def test_excerpt_matches_across_whitespace(excerpt: str) -> None:
    assert contains_excerpt("alfa beta gama", excerpt)


@pytest.mark.parametrize("excerpt", ["delta", "", "   "])
def test_excerpt_absent_or_empty(excerpt: str) -> None:
    assert not contains_excerpt("alfa beta gama", excerpt)
