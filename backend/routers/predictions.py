from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment
from schemas import ShipmentOut

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/", response_model=list[ShipmentOut])
def list_predictions(
    risk_label: Optional[str] = Query(None),
    carrier: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Shipment)
    if risk_label:
        q = q.filter(Shipment.risk_label == risk_label)
    if carrier:
        q = q.filter(Shipment.carrier == carrier)
    if status:
        q = q.filter(Shipment.status == status)
    return (
        q.order_by(Shipment.delay_risk_score.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/summary")
def prediction_summary(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).all()
    total = len(shipments)
    high = sum(1 for s in shipments if s.risk_label == "High")
    medium = sum(1 for s in shipments if s.risk_label == "Medium")
    low = sum(1 for s in shipments if s.risk_label == "Low")
    avg_score = (
        round(sum(s.delay_risk_score or 0 for s in shipments) / total, 4) if total else 0.0
    )
    return {
        "total_scored": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "avg_delay_risk_score": avg_score,
        "high_pct": round(high / total * 100, 1) if total else 0.0,
        "medium_pct": round(medium / total * 100, 1) if total else 0.0,
        "low_pct": round(low / total * 100, 1) if total else 0.0,
    }
