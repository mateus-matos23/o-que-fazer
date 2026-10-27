import re

import pytest
from django.db import IntegrityError, connection, transaction
from django.template.loader import get_template
from django.test import Client
from django.test.utils import CaptureQueriesContext

from catalog.models import Situation, TriageChoice, TriageNode

pytestmark = pytest.mark.django_db


def _html(client: Client, url: str) -> str:
    response = client.get(url)
    assert response.status_code == 200
    return response.content.decode()


def _links(html: str) -> list[str]:
    ul = re.search(r'<ul class="choice-cards">(.*?)</ul>', html, re.DOTALL)
    assert ul
    return re.findall(r'href="([^"]+)"', ul.group(1))


def test_root_shows_start_node(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, "/")
    assert "<h1>Sobre o que é o que aconteceu com você?</h1>" in html
    assert '<p class="question-help">Escolha o assunto mais próximo.' in html
    assert _links(html) == [
        "/comecar/documentos/",
        "/comecar/trabalho/",
        "/comecar/familia/",
        "/comecar/veiculo/",
        "/comecar/aposentadoria/",
        "/fora-da-cobertura/",
    ]
    assert 'href="/situacoes/"' in html and 'href="/onde-resolvo/"' in html
    assert "Voltar ao início" not in html


def test_choice_icon_is_decorative_and_optional(loaded: dict[str, int], client: Client) -> None:
    cards = _html(client, "/").split('<ul class="choice-cards">')[1].split("</ul>")[0]
    assert cards.count('<span class="icon-tile"><svg class="icon" aria-hidden="true"') == 6
    TriageChoice.objects.filter(node__slug="inicio").update(icon="")
    cards = _html(client, "/").split('<ul class="choice-cards">')[1].split("</ul>")[0]
    assert "icon-tile" not in cards and "<svg" not in cards


@pytest.mark.parametrize("icon", TriageChoice.Icon.values)
def test_every_icon_has_a_template(icon: str) -> None:
    assert get_template(f"guidance/icons/{icon}.svg")


def test_root_has_constant_query_count(loaded: dict[str, int], client: Client) -> None:
    with CaptureQueriesContext(connection) as queries:
        _html(client, "/")
    assert len(queries) <= 2  # nó + escolhas (com next_node e situation por join)


def test_inner_node_links_to_situations(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, "/comecar/documentos/")
    assert "<title>O que aconteceu com seus documentos? - O que Fazer?</title>" in html
    assert _links(html) == [
        "/s/perda-de-documentos/",
        "/s/cpf-irregular/",
        "/fora-da-cobertura/",
        "/fora-da-cobertura/",
    ]
    assert 'href="/">Voltar ao início' in html
    assert "question-help" not in html


def test_trabalho_node(loaded: dict[str, int], client: Client) -> None:
    assert _links(_html(client, "/comecar/trabalho/"))[0] == "/s/desligamento-do-trabalho/"


def test_familia_node_links_to_falecimento(loaded: dict[str, int], client: Client) -> None:
    assert _links(_html(client, "/comecar/familia/")) == [
        "/s/falecimento-na-familia/",
        "/fora-da-cobertura/",
        "/fora-da-cobertura/",
    ]


def test_aposentadoria_node_links_to_situation(loaded: dict[str, int], client: Client) -> None:
    assert _links(_html(client, "/comecar/aposentadoria/")) == [
        "/s/aposentadoria/",
        "/fora-da-cobertura/",
    ]


def test_unknown_node_is_404(loaded: dict[str, int], client: Client) -> None:
    assert client.get("/comecar/nao-existe/").status_code == 404


def test_start_slug_url_redirects_to_home(client: Client) -> None:
    response = client.get("/comecar/inicio/")
    assert (response.status_code, response["Location"]) == (302, "/")


def test_post_is_not_allowed(loaded: dict[str, int], client: Client) -> None:
    assert client.post("/situacoes/").status_code == 405
    assert client.post("/").status_code == 405


def test_uncovered_page_lists_situations_and_search(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, "/fora-da-cobertura/")
    assert "<h1>Ainda não orientamos essa situação</h1>" in html
    for situation in Situation.objects.all():
        assert f'href="/s/{situation.slug}/"' in html and situation.title in html
    assert 'href="/onde-resolvo/"' in html and 'href="/"' in html


def test_situation_list_still_works(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, "/situacoes/")
    assert "<h1>O que aconteceu?</h1>" in html and "Meu CPF está irregular" in html


def test_home_without_start_node_shows_situation_list(client: Client) -> None:
    Situation.objects.create(slug="sit", title="Minha situação")
    assert not TriageNode.objects.exists()
    html = _html(client, "/")
    assert "<h1>O que aconteceu?</h1>" in html and 'href="/s/sit/"' in html


def test_choice_rejects_two_destinations(db: None) -> None:
    node = TriageNode.objects.create(slug="inicio", text="t")
    situation = Situation.objects.create(slug="s", title="S")
    with pytest.raises(IntegrityError), transaction.atomic():
        TriageChoice.objects.create(
            node=node, label="x", order=1, next_node=node, situation=situation
        )
