"""Tests for Resend email service (mock mode + endpoints)."""
import pytest

from email_service import send_password_reset, send_shipment_update, send_welcome


@pytest.fixture(autouse=True)
def _no_resend(monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setenv("AUTH_REQUIRED", "0")
    yield


@pytest.mark.asyncio
async def test_welcome_mock():
    r = await send_welcome("alice@example.com", name="Alice")
    assert r["source"] == "mock"
    assert r["to"] == "alice@example.com"
    assert "ShipLogix" in r["subject"]


@pytest.mark.asyncio
async def test_password_reset_mock():
    r = await send_password_reset("bob@example.com", "https://app/reset?token=abc")
    assert r["source"] == "mock"
    assert "Reset" in r["subject"]


@pytest.mark.asyncio
async def test_shipment_update_mock():
    r = await send_shipment_update("carol@example.com", "SHP-1", "in_transit", "2026-04-30")
    assert r["source"] == "mock"
    assert "SHP-1" in r["subject"]


def test_welcome_endpoint(client):
    r = client.post(
        "/api/notifications/welcome",
        json={"email": "dave@example.com", "name": "Dave"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "mock"
    assert body["to"] == "dave@example.com"


def test_reset_endpoint_public(client):
    """Reset must be reachable without auth."""
    r = client.post(
        "/api/notifications/password-reset",
        json={"email": "ev@example.com", "reset_link": "https://app/reset"},
    )
    assert r.status_code == 200
    assert r.json()["source"] == "mock"


def test_shipment_update_endpoint_404(client):
    r = client.post(
        "/api/notifications/shipment-update",
        json={"email": "f@example.com", "shipment_id": "DOES-NOT-EXIST"},
    )
    assert r.status_code == 404
