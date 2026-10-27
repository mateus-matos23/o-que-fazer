# Adiciona o ícone "retirement" às opções de TriageChoice.icon (escrita à mão, sem banco).

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_triagechoice_icon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="triagechoice",
            name="icon",
            field=models.CharField(
                blank=True,
                choices=[
                    ("document", "Documento"),
                    ("work", "Trabalho"),
                    ("family", "Família"),
                    ("vehicle", "Veículo"),
                    ("other", "Outro assunto"),
                    ("lost", "Perda"),
                    ("problem", "Problema"),
                    ("first-time", "Primeira vez"),
                    ("leaving", "Saída"),
                    ("first-job", "Primeiro emprego"),
                    ("retirement", "Aposentadoria"),
                ],
                max_length=20,
            ),
        ),
    ]
