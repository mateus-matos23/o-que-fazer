from django.urls import path

from guidance import views

app_name = "guidance"
urlpatterns = [
    path("", views.home, name="home"),
    path("comecar/<slug:slug>/", views.triage, name="triage"),
    path("onde-resolvo/", views.search, name="search"),
    path("onde-resolvo/<slug:slug>/", views.procedure_detail, name="procedure"),
    path("s/<slug:slug>/", views.question, name="question"),
    path("s/<slug:slug>/plano/", views.plan, name="plan"),
    path("s/<slug:slug>/atendimento/", views.channel_preference, name="channel_preference"),
    path("s/<slug:slug>/respostas/", views.review, name="review"),
    path("s/<slug:slug>/respostas/<slug:question_slug>/", views.edit_answer, name="edit_answer"),
    path("s/<slug:slug>/recomecar/", views.restart, name="restart"),
]
