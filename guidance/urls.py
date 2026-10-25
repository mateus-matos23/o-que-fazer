from django.urls import path

from guidance import views

app_name = "guidance"
urlpatterns = [
    path("", views.triage, name="home"),
    path("comecar/<slug:slug>/", views.triage, name="triage"),
    path("situacoes/", views.situation_list, name="situation_list"),
    path("fora-da-cobertura/", views.uncovered, name="uncovered"),
    path("onde-resolvo/", views.search, name="search"),
    path("onde-resolvo/<slug:slug>/", views.procedure_detail, name="procedure"),
    path("s/<slug:slug>/", views.question, name="question"),
    path("s/<slug:slug>/plano/", views.plan, name="plan"),
    path("s/<slug:slug>/respostas/", views.review, name="review"),
    path("s/<slug:slug>/respostas/<slug:question_slug>/", views.edit_answer, name="edit_answer"),
    path("s/<slug:slug>/recomecar/", views.restart, name="restart"),
]
