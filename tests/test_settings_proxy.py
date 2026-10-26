import importlib
import logging

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


def test_request_errors_are_logged_with_debug_off() -> None:
    assert settings.DEBUG is False
    record = logging.LogRecord("django.request", logging.ERROR, __file__, 0, "erro", None, None)
    handlers: list[logging.Handler] = []
    logger: logging.Logger | None = logging.getLogger("django.request")
    while logger is not None:
        handlers += logger.handlers
        logger = logger.parent if logger.propagate else None
    # `type is`: o pytest instala no root um handler de captura que herda de StreamHandler.
    assert any(
        type(h) is logging.StreamHandler and h.level <= logging.ERROR and h.filter(record)
        for h in handlers
    )
