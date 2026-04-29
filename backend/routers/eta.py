"""ETA prediction endpoints — predicts arrival times with confidence intervals."""
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from ml.eta import eta_predictor
from models import Shipment

router = APIRouter(prefix="/api/eta", tags=["eta"])

ACTIVE_STATUSES = ("in_transit", "at_risk", "delayed")


def _ensure_model(db: Session) -> None:
    """Lazy-load the model from disk on first request, training from
    delivered shipments if no artifacts exist yet.
    """
    if eta_predictor.ready:
        return
    delivered = db.query(Shipment).filter(Shipment.status == "delivered").all()
    if not delivered:
        return
    df = pd.DataFrame([
        {
            "carrier": s.carrier,
            "origin": s.origin,
            "destination": s.destination,
            "weather_region": s.weather_region or "Unknown",
            "transit_days": s.transit_days,
            "month": s.month or 1,
            "delay_hours": s.delay_hours or 0.0,
            "status": s.status,
            "ship_date": s.ship_date,
        }
        for s in delivered
    ])
    eta_predictor.load_or_train(df)


def _shipment_to_row(s: Shipment) -> dict:
    return {
        "id": s.id,
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
        "estimated_arrival": s.estimated_arrival,
    }


def _enrich(s: Shipment) -> dict:
    df = pd.DataFrame([_shipment_to_row(s)])
    enriched = eta_predictor.predict_eta(df).iloc[0].to_dict()
    return {
        "id": s.id,
        "shipment_id": s.shipment_id,
        "carrier": s.carrier,
        "origin": s.origin,
        "destination": s.destination,
        "status": s.status,
        "ship_date": s.ship_date,
        "estimated_arrival": s.estimated_arrival,
        "actual_arrival": s.actual_arrival,
        "predicted_eta": enriched.get("predicted_eta"),
        "predicted_eta_lower": enriched.get("predicted_eta_lower"),
        "predicted_eta_upper": enriched.get("predicted_eta_upper"),
        "predicted_transit_hours": float(enriched.get("predicted_transit_hours", 0.0)),
        "eta_confidence_hours": float(enriched.get("eta_confidence_hours", 0.0)),
        "model_ready": eta_predictor.ready,
    }


@router.get("/")
def list_eta_predictions(
    status: Optional[str] = Query(None, description="Filter by shipment status"),
    carrier: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Predicted ETAs for in-flight shipments. Defaults to active statuses."""
    _ensure_model(db)
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    else:
        q = q.filter(Shipment.status.in_(ACTIVE_STATUSES))
    if carrier:
        q = q.filter(Shipment.carrier == carrier)

    rows = q.order_by(Shipment.ship_date.desc()).offset(skip).limit(limit).all()
    if not rows:
        return []
    df = pd.DataFrame([_shipment_to_row(s) for s in rows])
    enriched = eta_predictor.predict_eta(df)
    out = []
    for shipment, (_, pred) in zip(rows, enriched.iterrows()):
        out.append({
            "id": shipment.id,
            "shipment_id": shipment.shipment_id,
            "carrier": shipment.carrier,
            "origin": shipment.origin,
            "destination": shipment.destination,
            "status": shipment.status,
            "ship_date": shipment.ship_date,
            "estimated_arrival": shipment.estimated_arrival,
            "predicted_eta": pred.get("predicted_eta"),
            "predicted_eta_lower": pred.get("predicted_eta_lower"),
            "predicted_eta_upper": pred.get("predicted_eta_upper"),
            "predicted_transit_hours": float(pred.get("predicted_transit_hours", 0.0)),
            "eta_confidence_hours": float(pred.get("eta_confidence_hours", 0.0)),
            "model_ready": eta_predictor.ready,
        })
    return out


@router.get("/summary")
def eta_summary(db: Session = Depends(get_db)):
    """Aggregate health of the ETA model + in-flight prediction counts."""
    _ensure_model(db)
    in_flight = (
        db.query(Shipment).filter(Shipment.status.in_(ACTIVE_STATUSES)).count()
    )
    delivered = db.query(Shipment).filter(Shipment.status == "delivered").count()
    return {
        "model_ready": eta_predictor.ready,
        "in_flight_count": in_flight,
        "training_sample_count": delivered,
        "feature_columns": ["carrier", "origin", "destination", "weather_region", "transit_days", "month"],
        "confidence_level": 0.95,
    }


@router.get("/{shipment_id}")
def get_eta(shipment_id: str, db: Session = Depends(get_db)):
    """Predicted ETA + 95% confidence interval for one shipment."""
    _ensure_model(db)
    s = (
        db.query(Shipment)
        .filter(Shipment.shipment_id == shipment_id.strip().upper())
        .first()
    )
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return _enrich(s)
