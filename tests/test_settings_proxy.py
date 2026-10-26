import importlib

import pytest
from django.conf import settings

import config.settings as settings_module


def _reload_settings() -> object:
    return importlib.reload(settings_module)


def test_proxy_header_is_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DJANGO_BEHIND_PROXY", raising=False)
    assert not hasattr(_reload_settings(), "SECURE_PROXY_SSL_HEADER")


def test_proxy_header_is_set_behind_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DJANGO_BEHIND_PROXY", "1")
    try:
        assert getattr(_reload_settings(), "SECURE_PROXY_SSL_HEADER") == (  # noqa: B009
            "HTTP_X_FORWARDED_PROTO",
            "https",
        )
    finally:
        monkeypatch.undo()
        _reload_settings()


def test_whitenoise_runs_right_after_security_middleware() -> None:
    assert settings.MIDDLEWARE[:2] == [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ]
