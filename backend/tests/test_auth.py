"""Tests for Supabase JWT auth middleware (backend/auth.py)."""
import os
import time

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from auth import AuthUser, get_current_user, require_tier

JWT_SECRET = "test-secret-do-not-use-in-prod"


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    yield


def _build_app() -> TestClient:
    app = FastAPI()

    @app.get("/whoami")
    def whoami(user: AuthUser = Depends(get_current_user)):
        return {"user_id": user.user_id, "tier": user.tier, "role": user.role}

    @app.get("/pro-only")
    def pro_only(user: AuthUser = Depends(require_tier("pro", "business"))):
        return {"ok": True, "tier": user.tier}

    return TestClient(app)


def _token(sub: str, tier: str = "pro", email: str = "test@example.com") -> str:
    payload = {
        "sub": sub,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": int(time.time()) + 3600,
        "app_metadata": {"tier": tier},
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_missing_token_when_required_returns_401():
    client = _build_app()
    r = client.get("/whoami")
    assert r.status_code == 401


def test_invalid_token_returns_401():
    client = _build_app()
    r = client.get("/whoami", headers={"Authorization": "Bearer garbage.not.jwt"})
    assert r.status_code == 401


def test_valid_token_yields_user():
    client = _build_app()
    token = _token("user-123", tier="pro")
    r = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == "user-123"
    assert body["tier"] == "pro"
    assert body["role"] == "authenticated"


def test_tier_gate_allows_allowed_tier():
    client = _build_app()
    token = _token("user-1", tier="business")
    r = client.get("/pro-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


def test_tier_gate_rejects_disallowed_tier():
    client = _build_app()
    token = _token("user-1", tier="free")
    r = client.get("/pro-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_dev_mode_allows_anonymous(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "0")
    monkeypatch.setenv("DEV_DEFAULT_TIER", "pro")
    client = _build_app()
    r = client.get("/whoami")
    assert r.status_code == 200
    assert r.json()["user_id"] == "dev-user"
    assert r.json()["tier"] == "pro"
