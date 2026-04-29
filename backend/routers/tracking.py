import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from ml.eta import eta_predictor
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

    eta_block = None
    if s.status != "delivered":
        df = pd.DataFrame([{
            "shipment_id": s.shipment_id,
            "carrier": s.carrier,
            "origin": s.origin,
            "destination": s.destination,
            "weather_region": s.weather_region or "Unknown",
            "transit_days": s.transit_days,
            "month": s.month or 1,
            "delay_hours": s.delay_hours or 0.0,
            "status": s.status,
            "ship_date": s.ship_date,
        }])
        pred = eta_predictor.predict_eta(df).iloc[0].to_dict()
        eta_block = {
            "predicted_eta": pred.get("predicted_eta"),
            "predicted_eta_lower": pred.get("predicted_eta_lower"),
            "predicted_eta_upper": pred.get("predicted_eta_upper"),
            "predicted_transit_hours": float(pred.get("predicted_transit_hours", 0.0)),
            "eta_confidence_hours": float(pred.get("eta_confidence_hours", 0.0)),
            "model_ready": eta_predictor.ready,
        }

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
        "eta": eta_block,
        "timeline": timeline,
    }
