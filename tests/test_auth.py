"""Tests for auth token secret configuration and JWT behavior."""

from __future__ import annotations

import importlib

import pytest

from api.models.user import UserRole


@pytest.fixture
def auth_module(monkeypatch):
    def _load(secret: str | None, env: str | None = None):
        if secret is None:
            monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        else:
            monkeypatch.setenv("JWT_SECRET_KEY", secret)

        if env is None:
            monkeypatch.delenv("ENV", raising=False)
        else:
            monkeypatch.setenv("ENV", env)

        import api.auth as auth

        return importlib.reload(auth)

    return _load


def test_create_and_decode_token_uses_env_secret(auth_module):
    auth = auth_module("a" * 40)
    token = auth.create_access_token(user_id=123, role=UserRole.teacher)
    payload = auth._decode_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "teacher"


def test_missing_secret_raises_clear_error(auth_module):
    auth = auth_module(secret=None, env=None)

    with pytest.raises(RuntimeError, match="Missing required environment variable: JWT_SECRET_KEY"):
        auth.create_access_token(user_id=1, role=UserRole.teacher)


def test_short_secret_raises_validation_error(auth_module):
    auth = auth_module(secret="too-short")

    with pytest.raises(RuntimeError, match="must be at least"):
        auth.create_access_token(user_id=1, role=UserRole.teacher)


def test_development_env_allows_gated_fallback_secret(auth_module):
    auth = auth_module(secret=None, env="development")

    token = auth.create_access_token(user_id=9, role=UserRole.parent)
    payload = auth._decode_token(token)

    assert payload["sub"] == "9"
    assert payload["role"] == "parent"
