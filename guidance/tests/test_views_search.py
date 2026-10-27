import re

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db

SEARCH = "/onde-resolvo/"


def _html(client: Client, url: str, **params: str) -> str:
    response = client.get(url, params)
    assert response.status_code == 200
    return response.content.decode()


def _result_slugs(html: str) -> list[str]:
    return re.findall(r'href="/onde-resolvo/([a-z0-9-]+)/"', html)


def test_home_links_to_direct_search(loaded: dict[str, int], client: Client) -> None:
    assert f'href="{SEARCH}"' in _html(client, "/")


def test_search_without_term_shows_only_the_form(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, SEARCH)
    assert 'role="search"' in html and '<label for="id_q">' in html
    assert "Resultados" not in html and "Erro:" not in html


def test_search_hint_describes_the_field(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, SEARCH)
    assert '<p id="search-hint" class="search-hint">Digite parte do nome do serviço.' in html
    assert 'aria-describedby="search-hint"' in html
    errors = _html(client, SEARCH, q="c")
    assert 'aria-describedby="search-hint search-errors" aria-invalid="true"' in errors


def test_search_hint_examples_find_services(loaded: dict[str, int], client: Client) -> None:
    hint = re.search(r"Exemplos: ([^<]+)\.</p>", _html(client, SEARCH))
    assert hint is not None
    for example in hint.group(1).split(", "):
        assert _result_slugs(_html(client, SEARCH, q=example)), example


def test_search_matches_title_case_insensitively_ordered_by_title(
    loaded: dict[str, int], client: Client
) -> None:
    slugs = _result_slugs(_html(client, SEARCH, q="SEGURO-DESEMPREGO"))
    assert slugs == ["seguro-desemprego", "seguro-desemprego-domestico"]


def test_search_matches_description(loaded: dict[str, int], client: Client) -> None:
    # "vida profissional" só aparece na descrição, não no título
    assert _result_slugs(_html(client, SEARCH, q="vida profissional")) == ["conferir-vinculos-ctps"]


def test_search_without_match_offers_situation_mode(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, SEARCH, q="passaporte")
    assert _result_slugs(html) == [] and 'Nenhum serviço encontrado para "passaporte"' in html
    assert 'href="/"' in html


@pytest.mark.parametrize("term", ["c", " c ", "x" * 101])
def test_search_rejects_too_short_or_too_long_terms(
    loaded: dict[str, int], client: Client, term: str
) -> None:
    html = _html(client, SEARCH, q=term)
    assert "<title>Erro: " in html and 'aria-invalid="true"' in html
    assert "Resultados" not in html


def test_search_escapes_the_term(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, SEARCH, q="<script>")
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_procedure_detail_shows_facts_without_applicability(
    loaded: dict[str, int], client: Client
) -> None:
    html = _html(client, SEARCH + "extrato-vinculos-caged/")
    assert "<h1>Solicitar o extrato de vínculos do CAGED</h1>" in html
    assert "Ministério do Trabalho e Emprego" in html and "Documento de identificação." in html
    assert "govbr-caged (site oficial)" in html
    assert "Coletado em 09/10/2026 21:00" in html  # 00h UTC no fuso de Fortaleza
    assert "Em média 30 dias corridos." in html
    assert "Não informado pela fonte oficial. Confirme o custo no canal" in html  # RN11
    assert "não confirma se ele se aplica" in html and "Por que esta etapa" not in html


def test_procedure_detail_unknown_slug_is_404(loaded: dict[str, int], client: Client) -> None:
    assert client.get(SEARCH + "inexistente/").status_code == 404
