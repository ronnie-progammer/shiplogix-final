"""Generate synthetic shipment data, run ML, and seed the database."""
import random
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Must run from backend/ directory
sys.path.insert(0, ".")

from database import Base, SessionLocal, engine
from ml.engine import MLEngine
from models import Shipment

CARRIERS = [
    "FedEx", "UPS", "DHL", "USPS", "Amazon Logistics",
    "OnTrac", "LaserShip", "Speedy Freight", "NationWide Carriers", "PrimeShip",
]

ROUTES = [
    ("Los Angeles, CA", "New York, NY"),
    ("Chicago, IL", "Houston, TX"),
    ("Phoenix, AZ", "Philadelphia, PA"),
    ("Dallas, TX", "San Antonio, TX"),
    ("San Diego, CA", "Seattle, WA"),
    ("Miami, FL", "Atlanta, GA"),
    ("Denver, CO", "Boston, MA"),
    ("Nashville, TN", "Detroit, MI"),
    ("Portland, OR", "Las Vegas, NV"),
    ("Minneapolis, MN", "St. Louis, MO"),
    ("Charlotte, NC", "Indianapolis, IN"),
    ("Columbus, OH", "Memphis, TN"),
]

WEATHER_REGIONS: dict[str, list[str]] = {
    "West Coast": ["Los Angeles, CA", "San Diego, CA", "Seattle, WA", "Portland, OR", "Las Vegas, NV"],
    "Midwest": ["Chicago, IL", "Detroit, MI", "Minneapolis, MN", "Columbus, OH", "St. Louis, MO", "Indianapolis, IN"],
    "South": ["Houston, TX", "Dallas, TX", "San Antonio, TX", "Atlanta, GA", "Miami, FL", "Memphis, TN", "Nashville, TN"],
    "East Coast": ["New York, NY", "Philadelphia, PA", "Boston, MA", "Charlotte, NC"],
    "Mountain": ["Phoenix, AZ", "Denver, CO"],
}

CARRIER_PERF: dict[str, dict] = {
    "FedEx":               {"on_time_base": 0.92, "avg_delay_hours": 4.2},
    "UPS":                 {"on_time_base": 0.90, "avg_delay_hours": 5.1},
    "DHL":                 {"on_time_base": 0.88, "avg_delay_hours": 6.3},
    "USPS":                {"on_time_base": 0.80, "avg_delay_hours": 10.5},
    "Amazon Logistics":    {"on_time_base": 0.94, "avg_delay_hours": 3.0},
    "OnTrac":              {"on_time_base": 0.82, "avg_delay_hours": 9.2},
    "LaserShip":           {"on_time_base": 0.78, "avg_delay_hours": 12.4},
    "Speedy Freight":      {"on_time_base": 0.85, "avg_delay_hours": 7.8},
    "NationWide Carriers": {"on_time_base": 0.87, "avg_delay_hours": 6.9},
    "PrimeShip":           {"on_time_base": 0.91, "avg_delay_hours": 4.5},
}


def _weather_region(city: str) -> str:
    for region, cities in WEATHER_REGIONS.items():
        if city in cities:
            return region
    return "Unknown"


def generate_shipments(n: int = 800) -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)

    now = datetime(2026, 4, 27)
    historical_n = int(n * 0.65)
    active_n = n - historical_n
    records = []

    def make_record(idx: int, ship_date: datetime, force_active: bool = False) -> dict:
        origin, destination = random.choice(ROUTES)
        carrier = random.choice(CARRIERS)
        perf = CARRIER_PERF[carrier]
        transit_days = random.randint(1, 7)
        estimated_arrival = ship_date + timedelta(days=transit_days)

        on_time = random.random() < perf["on_time_base"]
        if on_time:
            delay_hours = max(0.0, np.random.normal(0, 1.5))
        else:
            delay_hours = abs(np.random.normal(perf["avg_delay_hours"], 4.0))

        actual_arrival = estimated_arrival + timedelta(hours=delay_hours)

        if force_active:
            if delay_hours > 12:
                status = "delayed"
            elif delay_hours > 4:
                status = "at_risk"
            else:
                status = "in_transit"
            actual_arrival_str = None
            delay_hours_final = round(delay_hours, 1)
        elif actual_arrival <= now:
            status = "delivered"
            delay_hours_final = round(delay_hours, 1) if not on_time else 0.0
            actual_arrival_str = actual_arrival.strftime("%Y-%m-%d %H:%M")
        else:
            if delay_hours > 12:
                status = "delayed"
            elif delay_hours > 4:
                status = "at_risk"
            else:
                status = "in_transit"
            actual_arrival_str = None
            delay_hours_final = round(delay_hours, 1)

        return {
            "shipment_id": f"SHP-{20000 + idx}",
            "origin": origin,
            "destination": destination,
            "carrier": carrier,
            "status": status,
            "ship_date": ship_date.strftime("%Y-%m-%d"),
            "estimated_arrival": estimated_arrival.strftime("%Y-%m-%d"),
            "actual_arrival": actual_arrival_str,
            "delay_hours": delay_hours_final,
            "transit_days": transit_days,
            "weather_region": _weather_region(origin),
            "month": ship_date.month,
        }

    hist_start = now - timedelta(days=180)
    for i in range(historical_n):
        offset = random.randint(0, 170)
        ship_date = hist_start + timedelta(days=offset)
        records.append(make_record(i, ship_date, force_active=False))

    for i in range(active_n):
        ship_date = now - timedelta(days=random.randint(0, 8))
        records.append(make_record(historical_n + i, ship_date, force_active=True))

    return pd.DataFrame(records)


def run_seed(n: int = 800) -> None:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    existing = db.query(Shipment).count()
    if existing > 0:
        print(f"Database already has {existing} shipments — skipping seed. Delete shiplogiz.db to re-seed.")
        db.close()
        return

    print(f"Generating {n} synthetic shipments...")
    df = generate_shipments(n)

    print("Training ML models...")
    ml = MLEngine()
    ml.load_or_train(df)
    df = ml.score(df)
    df = ml.detect_anomalies(df)

    anomaly_count = int(df["is_anomaly"].sum())
    high_risk = int((df["risk_label"] == "High").sum())
    print(f"  → {anomaly_count} anomalies detected, {high_risk} high-risk predictions")

    print("Writing to database...")
    records = df.to_dict(orient="records")
    db.bulk_insert_mappings(Shipment, records)  # type: ignore[arg-type]
    db.commit()
    db.close()
    print(f"Seeded {len(records)} shipments. Done.")


if __name__ == "__main__":
    run_seed()
