from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment
from schemas import ShipmentOut

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("/", response_model=list[ShipmentOut])
def list_anomalies(
    carrier: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Shipment).filter(Shipment.is_anomaly == True)  # noqa: E712
    if carrier:
        q = q.filter(Shipment.carrier == carrier)
    if status:
        q = q.filter(Shipment.status == status)
    return q.order_by(Shipment.delay_hours.desc()).offset(skip).limit(limit).all()


@router.get("/summary")
def anomaly_summary(db: Session = Depends(get_db)):
    all_count = db.query(Shipment).count()
    anomaly_rows = db.query(Shipment).filter(Shipment.is_anomaly == True).all()  # noqa: E712
    anomaly_count = len(anomaly_rows)

    by_carrier: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for s in anomaly_rows:
        by_carrier[s.carrier] = by_carrier.get(s.carrier, 0) + 1
        by_status[s.status] = by_status.get(s.status, 0) + 1

    return {
        "total_anomalies": anomaly_count,
        "anomaly_rate": round(anomaly_count / all_count * 100, 2) if all_count else 0.0,
        "by_carrier": sorted(
            [{"carrier": k, "count": v} for k, v in by_carrier.items()],
            key=lambda x: x["count"], reverse=True,
        ),
        "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
    }
