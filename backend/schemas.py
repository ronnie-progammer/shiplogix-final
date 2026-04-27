from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ShipmentBase(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    carrier: str
    status: str
    ship_date: str
    estimated_arrival: str
    actual_arrival: Optional[str] = None
    delay_hours: float = 0.0
    transit_days: int
    weather_region: Optional[str] = None
    month: Optional[int] = None
    delay_risk_score: Optional[float] = None
    risk_label: Optional[str] = None
    is_anomaly: bool = False


class ShipmentOut(ShipmentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CarrierStats(BaseModel):
    carrier: str
    total_shipments: int
    delivered_count: int
    on_time_count: int
    delayed_count: int
    at_risk_count: int
    in_transit_count: int
    on_time_rate: float
    avg_delay_hours: float
    anomaly_count: int


class RouteStats(BaseModel):
    origin: str
    destination: str
    total_shipments: int
    delivered_count: int
    on_time_rate: float
    avg_delay_hours: float
    most_used_carrier: str


class DashboardStats(BaseModel):
    total_shipments: int
    in_transit: int
    delayed: int
    at_risk: int
    delivered: int
    on_time_rate: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    anomaly_count: int
    shipments_by_day: list[dict]
    risk_distribution: list[dict]
    carrier_summary: list[dict]
    recent_anomalies: list[dict]
    status_breakdown: list[dict]
