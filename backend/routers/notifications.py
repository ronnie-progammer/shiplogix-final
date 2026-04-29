"""Notification endpoints — trigger transactional emails via Resend."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from auth import AuthUser, get_current_user
from database import get_db
from email_service import send_password_reset, send_shipment_update, send_welcome
from models import Shipment

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class WelcomeRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = ""


class ResetRequest(BaseModel):
    email: EmailStr
    reset_link: str


class ShipmentUpdateRequest(BaseModel):
    email: EmailStr
    shipment_id: str


@router.post("/welcome")
async def trigger_welcome(body: WelcomeRequest, _: AuthUser = Depends(get_current_user)):
    return await send_welcome(body.email, body.name or "")


@router.post("/password-reset")
async def trigger_reset(body: ResetRequest):
    """Public — caller is unauthenticated by design (forgot password flow)."""
    return await send_password_reset(body.email, body.reset_link)


@router.post("/shipment-update")
async def trigger_shipment_update(
    body: ShipmentUpdateRequest,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(get_current_user),
):
    s = (
        db.query(Shipment)
        .filter(Shipment.shipment_id == body.shipment_id.strip().upper())
        .first()
    )
    if not s:
        raise HTTPException(404, "Shipment not found")
    return await send_shipment_update(
        body.email,
        s.shipment_id,
        s.status,
        predicted_eta=s.estimated_arrival,
    )
