from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(20), unique=True, index=True, nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    carrier = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # in_transit | delayed | at_risk | delivered
    ship_date = Column(String(10), nullable=False)
    estimated_arrival = Column(String(10), nullable=False)
    actual_arrival = Column(String(20), nullable=True)
    delay_hours = Column(Float, default=0.0, nullable=False)
    transit_days = Column(Integer, nullable=False)
    weather_region = Column(String(50), nullable=True)
    month = Column(Integer, nullable=True)
    # ML-scored fields — populated by seed.py / refresh endpoint
    delay_risk_score = Column(Float, nullable=True)
    risk_label = Column(String(10), nullable=True)  # Low | Medium | High
    is_anomaly = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
