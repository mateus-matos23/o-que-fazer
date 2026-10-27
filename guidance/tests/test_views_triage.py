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


SITUATIONS = {
    "perda-de-documentos": "Perdi um ou mais documentos",
    "cpf-irregular": "Meu CPF está com problema",
    "desligamento-do-trabalho": "Saí do meu emprego",
    "transferencia-de-veiculo": "Comprei, vendi ou recebi um veículo usado",
    "falecimento-na-familia": "Alguém da minha família faleceu",
    "aposentadoria": "Quero pedir minha aposentadoria",
}


def test_root_lists_the_six_situations(loaded: dict[str, int], client: Client) -> None:
    html = _html(client, "/")
    assert "<h1>O que aconteceu com você?</h1>" in html
    assert '<p class="question-help">Toque na situação mais parecida com a sua.</p>' in html
    assert _links(html) == [f"/s/{slug}/" for slug in SITUATIONS]
    for slug, label in SITUATIONS.items():
        assert f'href="/s/{slug}/"' in html and f"<span>{label}</span>" in html
    assert "/fora-da-cobertura/" not in html and "Ver todas as situações" not in html
    assert 'href="/onde-resolvo/"' in html
    assert "Voltar ao início" not in html


@pytest.mark.parametrize("url", ["/fora-da-cobertura/", "/situacoes/"])
def test_removed_pages_are_404(loaded: dict[str, int], client: Client, url: str) -> None:
    assert client.get(url).status_code == 404


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


def test_unknown_node_is_404(loaded: dict[str, int], client: Client) -> None:
    assert client.get("/comecar/nao-existe/").status_code == 404


def test_start_slug_url_redirects_to_home(client: Client) -> None:
    response = client.get("/comecar/inicio/")
    assert (response.status_code, response["Location"]) == (302, "/")


def test_post_is_not_allowed(loaded: dict[str, int], client: Client) -> None:
    assert client.post("/").status_code == 405


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


def test_choice_rejects_no_destination(db: None) -> None:
    node = TriageNode.objects.create(slug="inicio", text="t")
    with pytest.raises(IntegrityError), transaction.atomic():
        TriageChoice.objects.create(node=node, label="x", order=1)


def test_inner_node_links_to_situation_and_back_home(db: None, client: Client) -> None:
    situation = Situation.objects.create(slug="sit", title="Minha situação")
    node = TriageNode.objects.create(slug="sub", text="Qual destas?")
    TriageChoice.objects.create(node=node, label="Esta", order=1, situation=situation)
    html = _html(client, "/comecar/sub/")
    assert "<title>Qual destas? - O que Fazer?</title>" in html
    assert _links(html) == ["/s/sit/"]
    assert 'href="/">Voltar ao início' in html
