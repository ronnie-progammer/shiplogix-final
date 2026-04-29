"""Resend transactional email client with mock fallback.

Real send happens when `RESEND_API_KEY` is configured. Without it we
return `{"id": "mock-...", "source": "mock"}` so local dev never blocks
on outbound email and tests run hermetically.
"""
from __future__ import annotations

import os
import uuid
from typing import Optional

import httpx

RESEND_ENDPOINT = "https://api.resend.com/emails"
DEFAULT_FROM = os.getenv("EMAIL_FROM", "ShipLogix <noreply@shiplogix.dev>")


def _api_key() -> Optional[str]:
    return os.getenv("RESEND_API_KEY")


def _mock_response(to: str, subject: str) -> dict:
    return {
        "id": f"mock-{uuid.uuid4().hex[:12]}",
        "to": to,
        "subject": subject,
        "source": "mock",
    }


async def _send(to: str, subject: str, html: str, text: Optional[str] = None) -> dict:
    key = _api_key()
    if not key:
        return _mock_response(to, subject)

    body = {
        "from": DEFAULT_FROM,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        body["text"] = text

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {key}"},
            json=body,
        )
        r.raise_for_status()
        data = r.json()
        data["source"] = "resend"
        return data


async def send_welcome(to: str, name: str = "") -> dict:
    greeting = f"Hi {name}," if name else "Welcome,"
    html = f"""
    <h2>{greeting}</h2>
    <p>Welcome to ShipLogix — AI-powered supply chain visibility.</p>
    <p>Your dashboard is ready. Track shipments, monitor carriers, and get
    ML-driven ETAs and anomaly alerts.</p>
    """
    return await _send(to, "Welcome to ShipLogix", html)


async def send_password_reset(to: str, reset_link: str) -> dict:
    html = f"""
    <h2>Reset your password</h2>
    <p>Click below to reset your ShipLogix password. This link expires in 1 hour.</p>
    <p><a href="{reset_link}">Reset password</a></p>
    """
    return await _send(to, "Reset your ShipLogix password", html)


async def send_shipment_update(
    to: str, shipment_id: str, status: str, predicted_eta: Optional[str] = None
) -> dict:
    eta_line = f"<p>Predicted arrival: <strong>{predicted_eta}</strong></p>" if predicted_eta else ""
    html = f"""
    <h2>Shipment update — {shipment_id}</h2>
    <p>Status: <strong>{status.replace('_', ' ').title()}</strong></p>
    {eta_line}
    <p>Track live: <a href="https://shiplogix.dev/track/{shipment_id}">shiplogix.dev/track/{shipment_id}</a></p>
    """
    return await _send(to, f"ShipLogix update — {shipment_id}", html)
