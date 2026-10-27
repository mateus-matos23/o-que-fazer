import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

BEFORE = [("catalog", "0007_alter_triagechoice_icon")]
AFTER = [("catalog", "0008_triagechoice_exactly_one_destination")]


@pytest.mark.django_db(transaction=True)
def test_0008_deletes_choices_without_destination_and_keeps_the_rest() -> None:
    executor = MigrationExecutor(connection)
    executor.migrate(BEFORE)
    old = executor.loader.project_state(BEFORE).apps
    node = old.get_model("catalog", "TriageNode").objects.create(slug="inicio", text="t")
    inner = old.get_model("catalog", "TriageNode").objects.create(slug="sub", text="t")
    choice = old.get_model("catalog", "TriageChoice")
    choice.objects.create(node=node, label="Fora", order=1)  # ramo "fora da cobertura"
    choice.objects.create(node=node, label="Volta", order=2, next_node=inner)

    executor = MigrationExecutor(connection)  # recarrega o grafo depois de migrar para trás
    executor.migrate(AFTER)

    new = executor.loader.project_state(AFTER).apps
    labels = list(new.get_model("catalog", "TriageChoice").objects.values_list("label", flat=True))
    assert labels == ["Volta"]
