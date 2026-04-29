"""Stripe billing endpoints — subscription tier check + customer portal.

Real Stripe calls happen when `STRIPE_SECRET_KEY` is configured. In
mock mode we synthesize plausible responses (mock checkout/portal URLs,
free-tier subscription state) so dev and tests run without a Stripe
account.
"""
from __future__ import annotations

import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import AuthUser, get_current_user

router = APIRouter(prefix="/api/billing", tags=["billing"])

STRIPE_API = "https://api.stripe.com/v1"

PRICE_IDS = {
    "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_default"),
    "business": os.getenv("STRIPE_PRICE_BUSINESS", "price_business_default"),
}


def _stripe_key() -> Optional[str]:
    return os.getenv("STRIPE_SECRET_KEY")


def _success_url() -> str:
    return os.getenv("STRIPE_SUCCESS_URL", "https://shiplogix.dev/billing?status=success")


def _cancel_url() -> str:
    return os.getenv("STRIPE_CANCEL_URL", "https://shiplogix.dev/billing?status=cancel")


def _portal_return_url() -> str:
    return os.getenv("STRIPE_PORTAL_RETURN_URL", "https://shiplogix.dev/billing")


async def _stripe_post(path: str, data: dict) -> dict:
    key = _stripe_key()
    if not key:
        raise HTTPException(503, "Stripe not configured")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{STRIPE_API}{path}",
            data=data,
            auth=(key, ""),
        )
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return r.json()


class CheckoutRequest(BaseModel):
    tier: str  # "pro" | "business"


@router.get("/subscription")
async def get_subscription(user: AuthUser = Depends(get_current_user)):
    """Current user's subscription tier (from JWT claims)."""
    return {
        "user_id": user.user_id,
        "email": user.email,
        "tier": user.tier,
        "is_active": user.tier in {"pro", "business"},
        "source": "stripe" if _stripe_key() else "mock",
    }


@router.post("/checkout")
async def create_checkout_session(
    body: CheckoutRequest,
    user: AuthUser = Depends(get_current_user),
):
    """Create a Stripe Checkout session for the requested tier."""
    if body.tier not in PRICE_IDS:
        raise HTTPException(400, f"Unknown tier: {body.tier}")
    price_id = PRICE_IDS[body.tier]

    if not _stripe_key():
        return {
            "url": f"{_success_url()}&mock=1&tier={body.tier}",
            "session_id": f"cs_mock_{body.tier}",
            "source": "mock",
        }

    data = {
        "mode": "subscription",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
        "success_url": _success_url(),
        "cancel_url": _cancel_url(),
        "client_reference_id": user.user_id,
    }
    if user.email:
        data["customer_email"] = user.email
    session = await _stripe_post("/checkout/sessions", data)
    return {"url": session["url"], "session_id": session["id"], "source": "stripe"}


@router.post("/portal")
async def create_portal_session(user: AuthUser = Depends(get_current_user)):
    """Stripe customer-portal URL for managing the active subscription."""
    if not _stripe_key():
        return {
            "url": f"{_portal_return_url()}?mock=1",
            "source": "mock",
        }
    customer_id = os.getenv("STRIPE_DEMO_CUSTOMER")
    if not customer_id:
        raise HTTPException(
            400,
            "No Stripe customer linked to this user. Complete checkout first.",
        )
    data = {"customer": customer_id, "return_url": _portal_return_url()}
    session = await _stripe_post("/billing_portal/sessions", data)
    return {"url": session["url"], "source": "stripe"}


@router.get("/tiers")
def list_tiers():
    """Public catalog used by the frontend pricing page."""
    return {
        "tiers": [
            {"id": "free", "price_usd": 0, "shipments_per_month": 100, "features": ["Live tracking", "Basic dashboard"]},
            {"id": "pro", "price_usd": 49, "shipments_per_month": 5_000, "features": ["ETA prediction", "Anomaly alerts", "Email notifications"]},
            {"id": "business", "price_usd": 199, "shipments_per_month": 50_000, "features": ["Multi-user", "API access", "Priority support"]},
        ]
    }
