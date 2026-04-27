from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from carriers import get_adapter
from database import get_db
from models import Shipment
from schemas import CarrierStats

router = APIRouter(prefix="/api/carriers", tags=["carriers"])


@router.get("/", response_model=list[CarrierStats])
def list_carriers(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).all()

    stats: dict[str, dict] = defaultdict(
        lambda: {
            "total": 0, "delivered": 0, "on_time": 0,
            "delayed": 0, "at_risk": 0, "in_transit": 0,
            "delay_sum": 0.0, "anomaly": 0,
        }
    )

    for s in shipments:
        c = stats[s.carrier]
        c["total"] += 1
        if s.status == "delivered":
            c["delivered"] += 1
            if s.delay_hours == 0.0:
                c["on_time"] += 1
        elif s.status == "delayed":
            c["delayed"] += 1
        elif s.status == "at_risk":
            c["at_risk"] += 1
        elif s.status == "in_transit":
            c["in_transit"] += 1
        c["delay_sum"] += s.delay_hours or 0.0
        if s.is_anomaly:
            c["anomaly"] += 1

    result = []
    for carrier_name, d in sorted(stats.items()):
        on_time_rate = round(d["on_time"] / d["delivered"] * 100, 1) if d["delivered"] else 0.0
        avg_delay = round(d["delay_sum"] / d["total"], 2) if d["total"] else 0.0
        result.append(
            CarrierStats(
                carrier=carrier_name,
                total_shipments=d["total"],
                delivered_count=d["delivered"],
                on_time_count=d["on_time"],
                delayed_count=d["delayed"],
                at_risk_count=d["at_risk"],
                in_transit_count=d["in_transit"],
                on_time_rate=on_time_rate,
                avg_delay_hours=avg_delay,
                anomaly_count=d["anomaly"],
            )
        )
    return sorted(result, key=lambda x: x.total_shipments, reverse=True)


@router.get("/live/{tracking_number}")
async def live_track(
    tracking_number: str,
    carrier: Optional[str] = Query(None, description="fedex|ups|usps|dhl"),
    db: Session = Depends(get_db),
):
    """Live carrier tracking — real API when keys present, mock fallback otherwise."""
    # Auto-detect carrier from DB if not provided
    if not carrier:
        row = db.query(Shipment.carrier).filter(
            Shipment.shipment_id == tracking_number.upper()
        ).first()
        carrier = row[0] if row else "fedex"

    adapter = get_adapter(carrier)
    result = await adapter.track(tracking_number)
    if result is None:
        raise HTTPException(status_code=502, detail="Carrier API unavailable")
    return result
