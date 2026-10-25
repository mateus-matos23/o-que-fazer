from django.contrib import admin

from sources.admin import ReadOnlyAdmin

from .models import (
    AnswerOption,
    Condition,
    Dependency,
    Procedure,
    ProcedureDetail,
    Question,
    Requirement,
    Rule,
    ServiceChannel,
    Situation,
)


@admin.register(Situation)
class SituationAdmin(ReadOnlyAdmin):
    list_display = ("slug", "title")


@admin.register(Question)
class QuestionAdmin(ReadOnlyAdmin):
    list_display = ("slug", "kind", "allows_unknown", "order")


@admin.register(AnswerOption)
class AnswerOptionAdmin(ReadOnlyAdmin):
    list_display = ("question", "slug", "label")


@admin.register(Procedure)
class ProcedureAdmin(ReadOnlyAdmin):
    list_display = ("slug", "title", "agency", "jurisdiction", "clarifies")


@admin.register(ProcedureDetail)
class ProcedureDetailAdmin(ReadOnlyAdmin):
    list_display = ("procedure", "kind", "text")


@admin.register(Requirement)
class RequirementAdmin(ReadOnlyAdmin):
    list_display = ("procedure", "description")


@admin.register(ServiceChannel)
class ServiceChannelAdmin(ReadOnlyAdmin):
    list_display = ("procedure", "kind", "url")


@admin.register(Rule)
class RuleAdmin(ReadOnlyAdmin):
    list_display = ("slug", "procedure")


@admin.register(Condition)
class ConditionAdmin(ReadOnlyAdmin):
    list_display = ("rule", "question", "operator")


@admin.register(Dependency)
class DependencyAdmin(ReadOnlyAdmin):
    list_display = ("before", "after", "kind", "rule")
    list_filter = ("kind",)
