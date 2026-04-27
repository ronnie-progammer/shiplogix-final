from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Shipment

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).all()

    total = len(shipments)
    status_counts: dict[str, int] = defaultdict(int)
    risk_counts: dict[str, int] = defaultdict(int)
    anomaly_count = 0
    on_time_delivered = 0
    delivered_total = 0

    for s in shipments:
        status_counts[s.status] += 1
        if s.risk_label:
            risk_counts[s.risk_label] += 1
        if s.is_anomaly:
            anomaly_count += 1
        if s.status == "delivered":
            delivered_total += 1
            if s.delay_hours == 0.0:
                on_time_delivered += 1

    on_time_rate = round(on_time_delivered / delivered_total * 100, 1) if delivered_total else 0.0

    # Last 14 days trend
    today = datetime.utcnow().date()
    day_map: dict[str, int] = {}
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        day_map[day.isoformat()] = 0

    for s in shipments:
        if s.ship_date in day_map:
            day_map[s.ship_date] += 1

    shipments_by_day = [{"date": d, "count": c} for d, c in day_map.items()]

    # Carrier summary (top 5 by volume)
    carrier_map: dict[str, dict] = defaultdict(lambda: {"total": 0, "on_time": 0, "delayed": 0})
    for s in shipments:
        carrier_map[s.carrier]["total"] += 1
        if s.status == "delivered" and s.delay_hours == 0.0:
            carrier_map[s.carrier]["on_time"] += 1
        if s.status in ("delayed", "at_risk"):
            carrier_map[s.carrier]["delayed"] += 1

    carrier_summary = sorted(
        [
            {
                "carrier": name,
                "total": data["total"],
                "on_time_rate": round(data["on_time"] / data["total"] * 100, 1) if data["total"] else 0,
            }
            for name, data in carrier_map.items()
        ],
        key=lambda x: x["total"],
        reverse=True,
    )[:6]

    # Recent anomalies
    anomalies = [s for s in shipments if s.is_anomaly]
    recent_anomalies = sorted(anomalies, key=lambda x: x.created_at, reverse=True)[:5]

    status_breakdown = [
        {"status": k, "count": v}
        for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "total_shipments": total,
        "in_transit": status_counts.get("in_transit", 0),
        "delayed": status_counts.get("delayed", 0),
        "at_risk": status_counts.get("at_risk", 0),
        "delivered": status_counts.get("delivered", 0),
        "on_time_rate": on_time_rate,
        "high_risk_count": risk_counts.get("High", 0),
        "medium_risk_count": risk_counts.get("Medium", 0),
        "low_risk_count": risk_counts.get("Low", 0),
        "anomaly_count": anomaly_count,
        "shipments_by_day": shipments_by_day,
        "risk_distribution": [
            {"label": "High", "count": risk_counts.get("High", 0)},
            {"label": "Medium", "count": risk_counts.get("Medium", 0)},
            {"label": "Low", "count": risk_counts.get("Low", 0)},
        ],
        "carrier_summary": carrier_summary,
        "recent_anomalies": [
            {
                "id": s.id,
                "shipment_id": s.shipment_id,
                "origin": s.origin,
                "destination": s.destination,
                "carrier": s.carrier,
                "status": s.status,
                "delay_hours": s.delay_hours,
                "risk_label": s.risk_label,
            }
            for s in recent_anomalies
        ],
        "status_breakdown": status_breakdown,
    }
