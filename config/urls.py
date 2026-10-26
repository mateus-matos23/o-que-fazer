"""Rotas raiz: admin somente leitura e as páginas do cidadão (`guidance.urls`)."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("guidance.urls")),
]
