from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment
from schemas import ShipmentOut

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.get("/", response_model=list[ShipmentOut])
def list_shipments(
    status: Optional[str] = Query(None),
    carrier: Optional[str] = Query(None),
    risk_label: Optional[str] = Query(None),
    is_anomaly: Optional[bool] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    if carrier:
        q = q.filter(Shipment.carrier == carrier)
    if risk_label:
        q = q.filter(Shipment.risk_label == risk_label)
    if is_anomaly is not None:
        q = q.filter(Shipment.is_anomaly == is_anomaly)
    if date_from:
        q = q.filter(Shipment.ship_date >= date_from)
    if date_to:
        q = q.filter(Shipment.ship_date <= date_to)
    return q.order_by(Shipment.ship_date.desc()).offset(skip).limit(limit).all()


@router.get("/{shipment_id}", response_model=ShipmentOut)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    s = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return s
