"""Tests for Stripe billing endpoints (mock mode)."""
import pytest


@pytest.fixture(autouse=True)
def _no_stripe(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.setenv("AUTH_REQUIRED", "0")
    yield


def test_list_tiers_public(client):
    r = client.get("/api/billing/tiers")
    assert r.status_code == 200
    tiers = r.json()["tiers"]
    ids = {t["id"] for t in tiers}
    assert {"free", "pro", "business"} <= ids


def test_subscription_dev_mode(client):
    r = client.get("/api/billing/subscription")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "mock"
    assert body["tier"] in {"free", "pro", "business"}


def test_checkout_mock_returns_url(client):
    r = client.post("/api/billing/checkout", json={"tier": "pro"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "mock"
    assert "url" in body
    assert "tier=pro" in body["url"]


def test_checkout_unknown_tier(client):
    r = client.post("/api/billing/checkout", json={"tier": "platinum"})
    assert r.status_code == 400


def test_portal_mock_returns_url(client):
    r = client.post("/api/billing/portal")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "mock"
    assert "url" in body
