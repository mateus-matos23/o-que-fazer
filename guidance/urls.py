from django.urls import path

from guidance import views

app_name = "guidance"
urlpatterns = [
    path("", views.situation_list, name="situation_list"),
    path("s/<slug:slug>/", views.question, name="question"),
    path("s/<slug:slug>/plano/", views.plan, name="plan"),
]
