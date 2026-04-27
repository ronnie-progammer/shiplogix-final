from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment

router = APIRouter(prefix="/track", tags=["tracking"])

_STATUS_STEPS = ["processing", "in_transit", "out_for_delivery", "delivered"]

_STATUS_MAP = {
    "in_transit": "in_transit",
    "delayed": "in_transit",
    "at_risk": "in_transit",
    "delivered": "delivered",
}


def _step_index(status: str) -> int:
    mapped = _STATUS_MAP.get(status, "in_transit")
    try:
        return _STATUS_STEPS.index(mapped)
    except ValueError:
        return 1


@router.get("/{shipment_id}")
def public_track(shipment_id: str, db: Session = Depends(get_db)):
    s = db.query(Shipment).filter(
        Shipment.shipment_id == shipment_id.strip().upper()
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")

    step = _step_index(s.status)
    timeline = [
        {"step": "Order Processed", "done": step >= 0},
        {"step": "In Transit",      "done": step >= 1},
        {"step": "Out for Delivery","done": step >= 2},
        {"step": "Delivered",       "done": step >= 3},
    ]

    return {
        "shipment_id": s.shipment_id,
        "status": s.status,
        "origin": s.origin,
        "destination": s.destination,
        "carrier": s.carrier,
        "ship_date": s.ship_date,
        "estimated_arrival": s.estimated_arrival,
        "actual_arrival": s.actual_arrival,
        "delay_hours": s.delay_hours,
        "risk_label": s.risk_label,
        "is_anomaly": s.is_anomaly,
        "timeline": timeline,
    }
