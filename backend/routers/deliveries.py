from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment
from schemas import ShipmentOut

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])


@router.get("/", response_model=list[ShipmentOut])
def list_deliveries(
    carrier: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Delivered shipments with planned vs actual arrival data."""
    q = db.query(Shipment).filter(Shipment.status == "delivered")
    if carrier:
        q = q.filter(Shipment.carrier == carrier)
    if date_from:
        q = q.filter(Shipment.ship_date >= date_from)
    if date_to:
        q = q.filter(Shipment.ship_date <= date_to)
    return q.order_by(Shipment.ship_date.desc()).offset(skip).limit(limit).all()


@router.get("/summary")
def delivery_summary(db: Session = Depends(get_db)):
    delivered = db.query(Shipment).filter(Shipment.status == "delivered").all()
    total = len(delivered)
    on_time = sum(1 for s in delivered if s.delay_hours == 0.0)
    avg_delay = round(sum(s.delay_hours for s in delivered) / total, 2) if total else 0.0
    return {
        "total_delivered": total,
        "on_time": on_time,
        "late": total - on_time,
        "on_time_rate": round(on_time / total * 100, 1) if total else 0.0,
        "avg_delay_hours": avg_delay,
    }
