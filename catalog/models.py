from __future__ import annotations

from django.db import models
from django.db.models import F, Q

from sources.models import Agency, Jurisdiction, SourceSnapshot

START_NODE = "inicio"  # slug do primeiro nó do funil de triagem


class Cited(models.Model):
    """Toda afirmação em nome de um órgão cita a versão da fonte e o trecho literal."""

    snapshot = models.ForeignKey(SourceSnapshot, on_delete=models.PROTECT, related_name="+")
    excerpt = models.TextField()

    class Meta:
        abstract = True


class Situation(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    candidates: models.ManyToManyField[Procedure, models.Model] = models.ManyToManyField(
        "Procedure", related_name="situations", blank=True
    )

    def __str__(self) -> str:
        return self.slug


class Question(models.Model):
    class Kind(models.TextChoices):
        SINGLE = "SINGLE", "Escolha única"
        MULTIPLE = "MULTIPLE", "Escolha múltipla"

    slug = models.SlugField(unique=True)
    text = models.TextField()
    help_text = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=Kind)
    allows_unknown = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    situations = models.ManyToManyField(Situation, related_name="questions", blank=True)

    def __str__(self) -> str:
        return self.slug


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    slug = models.SlugField()
    label = models.CharField(max_length=200)
    out_of_coverage = models.BooleanField(default=False)  # sem orientação oficial nesta versão

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["question", "slug"], name="unique_option_per_question"),
        ]

    def __str__(self) -> str:
        return f"{self.question.slug}:{self.slug}"


class Procedure(Cited):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name="procedures")
    jurisdiction = models.CharField(max_length=10, choices=Jurisdiction)
    clarifies = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="clarification_steps",
    )

    def __str__(self) -> str:
        return self.slug


class ProcedureDetail(Cited):
    class Kind(models.TextChoices):
        COST = "COST", "Custo"
        DEADLINE = "DEADLINE", "Prazo"

    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="details")
    kind = models.CharField(max_length=10, choices=Kind)
    text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["procedure", "kind"], name="unique_detail_per_kind"),
        ]

    def __str__(self) -> str:
        return f"{self.procedure.slug}:{self.kind}"


class Requirement(Cited):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="requirements")
    description = models.TextField()
    rule = models.ForeignKey(
        "Rule", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    def __str__(self) -> str:
        return f"{self.procedure.slug}: {self.description[:50]}"


class ServiceChannel(Cited):
    class Kind(models.TextChoices):
        ONLINE = "ONLINE", "Online"
        IN_PERSON = "IN_PERSON", "Presencial"
        PHONE = "PHONE", "Telefone"
        APP = "APP", "Aplicativo"
        EMAIL = "EMAIL", "E-mail"

    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="channels")
    kind = models.CharField(max_length=10, choices=Kind)
    description = models.TextField()
    url = models.URLField(max_length=500, blank=True)
    rule = models.ForeignKey(
        "Rule", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    def __str__(self) -> str:
        return f"{self.procedure.slug}:{self.kind}"


class Rule(Cited):
    slug = models.SlugField(unique=True)
    procedure = models.ForeignKey(
        Procedure, on_delete=models.CASCADE, null=True, blank=True, related_name="rules"
    )
    explanation = models.TextField()

    def __str__(self) -> str:
        return self.slug


class Condition(models.Model):
    class Operator(models.TextChoices):
        ANY_OF = "ANY_OF", "Qualquer uma de"
        NONE_OF = "NONE_OF", "Nenhuma de"

    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="conditions")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="+")
    operator = models.CharField(max_length=10, choices=Operator)
    options = models.ManyToManyField(AnswerOption, related_name="+")

    def __str__(self) -> str:
        return f"{self.rule.slug}: {self.question.slug} {self.operator}"


class Dependency(Cited):
    """`before` deve ser feito antes de `after`."""

    class Kind(models.TextChoices):
        MANDATORY = "MANDATORY", "Obrigatória"
        CONDITIONAL = "CONDITIONAL", "Condicional"
        RECOMMENDED = "RECOMMENDED", "Recomendada"

    before = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="dependents")
    after = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="prerequisites")
    kind = models.CharField(max_length=12, choices=Kind)
    rule = models.ForeignKey(
        Rule, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(kind="CONDITIONAL", rule__isnull=False)
                    | ~Q(kind="CONDITIONAL") & Q(rule__isnull=True)
                ),
                name="conditional_dependency_has_rule",
            ),
            models.CheckConstraint(condition=~Q(before=F("after")), name="dependency_not_self"),
            models.UniqueConstraint(fields=["before", "after"], name="unique_dependency_pair"),
        ]

    def __str__(self) -> str:
        return f"{self.before.slug} -> {self.after.slug} ({self.kind})"


class TriageNode(models.Model):
    """Pergunta ampla do funil. É encaminhamento (RN02): não afirma nada, então não cita fonte."""

    slug = models.SlugField(unique=True)
    text = models.TextField()
    help_text = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.slug


class TriageChoice(models.Model):
    class Icon(models.TextChoices):
        # Cada valor tem um SVG em guidance/templates/guidance/icons/<valor>.svg.
        DOCUMENT = "document", "Documento"
        WORK = "work", "Trabalho"
        FAMILY = "family", "Família"
        VEHICLE = "vehicle", "Veículo"
        OTHER = "other", "Outro assunto"
        LOST = "lost", "Perda"
        PROBLEM = "problem", "Problema"
        FIRST_TIME = "first-time", "Primeira vez"
        LEAVING = "leaving", "Saída"
        FIRST_JOB = "first-job", "Primeiro emprego"

    node = models.ForeignKey(TriageNode, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=200)
    icon = models.CharField(max_length=20, choices=Icon.choices, blank=True)  # decorativo
    order = models.PositiveSmallIntegerField()
    # CASCADE no destino; PROTECT na situação vale porque `_replace` apaga os nós antes.
    next_node = models.ForeignKey(
        TriageNode, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    situation = models.ForeignKey(
        Situation, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["node", "order"], name="unique_choice_order_per_node"),
            # Ambos nulos = ramo fora da cobertura.
            models.CheckConstraint(
                condition=Q(next_node__isnull=True) | Q(situation__isnull=True),
                name="triage_choice_at_most_one_destination",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.node.slug}:{self.order}"
