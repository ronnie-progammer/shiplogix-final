from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment
from schemas import RouteStats

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("/", response_model=list[RouteStats])
def list_routes(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).all()

    stats: dict[tuple, dict] = defaultdict(
        lambda: {
            "total": 0, "delivered": 0, "on_time": 0,
            "delay_sum": 0.0,
            "carrier_counts": defaultdict(int),
        }
    )

    for s in shipments:
        key = (s.origin, s.destination)
        r = stats[key]
        r["total"] += 1
        if s.status == "delivered":
            r["delivered"] += 1
            if s.delay_hours == 0.0:
                r["on_time"] += 1
        r["delay_sum"] += s.delay_hours or 0.0
        r["carrier_counts"][s.carrier] += 1

    result = []
    for (origin, destination), d in stats.items():
        on_time_rate = round(d["on_time"] / d["delivered"] * 100, 1) if d["delivered"] else 0.0
        avg_delay = round(d["delay_sum"] / d["total"], 2) if d["total"] else 0.0
        most_used = max(d["carrier_counts"], key=d["carrier_counts"].get)
        result.append(
            RouteStats(
                origin=origin,
                destination=destination,
                total_shipments=d["total"],
                delivered_count=d["delivered"],
                on_time_rate=on_time_rate,
                avg_delay_hours=avg_delay,
                most_used_carrier=most_used,
            )
        )
    return sorted(result, key=lambda x: x.total_shipments, reverse=True)
