# Toda opção de triagem passa a ter exatamente um destino (nó ou situação).

from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps


def delete_choices_without_destination(
    apps: StateApps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    # Eram os ramos "fora da cobertura"; o conteúdo é recarregado do TOML por `load_content`.
    apps.get_model("catalog", "TriageChoice").objects.filter(
        next_node__isnull=True, situation__isnull=True
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0007_alter_triagechoice_icon"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="triagechoice",
            name="triage_choice_at_most_one_destination",
        ),
        migrations.RunPython(delete_choices_without_destination, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="triagechoice",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("next_node__isnull", True), ("situation__isnull", True), _connector="XOR"
                ),
                name="triage_choice_exactly_one_destination",
            ),
        ),
        migrations.AlterField(
            model_name="triagechoice",
            name="icon",
            field=models.CharField(
                blank=True,
                choices=[
                    ("family", "Família"),
                    ("vehicle", "Veículo"),
                    ("lost", "Perda"),
                    ("problem", "Problema"),
                    ("leaving", "Saída"),
                    ("retirement", "Aposentadoria"),
                ],
                max_length=20,
            ),
        ),
    ]
