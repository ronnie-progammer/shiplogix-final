"""Tests for f3 ETA prediction endpoints."""
import random
from datetime import datetime, timedelta

import pandas as pd
import pytest

from ml.eta import ETAPredictor
from models import Shipment


def _make_shipment(db, **kwargs):
    defaults = dict(
        shipment_id="ETA-TEST01",
        origin="New York, NY",
        destination="Los Angeles, CA",
        carrier="FedEx",
        status="in_transit",
        ship_date="2026-04-20",
        estimated_arrival="2026-04-25",
        delay_hours=0.0,
        transit_days=5,
        weather_region="East Coast",
        month=4,
    )
    defaults.update(kwargs)
    s = Shipment(**defaults)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _seed_training_data(db, n=80):
    """Seed enough delivered shipments to train the ETA model.

    Idempotent across tests: returns early if already seeded so the
    session-scoped DB fixture doesn't collide on the unique shipment_id.
    """
    if db.query(Shipment).filter(Shipment.shipment_id.like("ETA-TRAIN-%")).count() >= n:
        return
    random.seed(7)
    routes = [
        ("New York, NY", "Los Angeles, CA"),
        ("Chicago, IL", "Houston, TX"),
        ("Miami, FL", "Atlanta, GA"),
    ]
    carriers = ["FedEx", "UPS", "DHL", "USPS"]
    for i in range(n):
        origin, dest = random.choice(routes)
        carrier = random.choice(carriers)
        transit_days = random.randint(2, 6)
        delay = random.gauss(2.0, 3.0)
        ship_dt = datetime(2026, 1, 1) + timedelta(days=i)
        est_arr = ship_dt + timedelta(days=transit_days)
        actual = est_arr + timedelta(hours=max(0.0, delay))
        existing = db.query(Shipment).filter(
            Shipment.shipment_id == f"ETA-TRAIN-{i:03d}"
        ).first()
        if existing:
            continue
        _make_shipment(
            db,
            shipment_id=f"ETA-TRAIN-{i:03d}",
            origin=origin,
            destination=dest,
            carrier=carrier,
            status="delivered",
            ship_date=ship_dt.strftime("%Y-%m-%d"),
            estimated_arrival=est_arr.strftime("%Y-%m-%d"),
            actual_arrival=actual.strftime("%Y-%m-%d %H:%M"),
            delay_hours=round(max(0.0, delay), 1),
            transit_days=transit_days,
            weather_region="East Coast",
            month=ship_dt.month,
        )


def test_eta_predictor_train_and_predict():
    """Predictor should produce floored confidence even without forest spread."""
    df = pd.DataFrame([
        {
            "shipment_id": f"S{i}",
            "carrier": "FedEx",
            "origin": "New York, NY",
            "destination": "Los Angeles, CA",
            "weather_region": "East Coast",
            "transit_days": 4,
            "month": 4,
            "delay_hours": float(i % 5),
            "status": "delivered",
            "ship_date": "2026-04-01",
        }
        for i in range(40)
    ])
    p = ETAPredictor()
    p.load_or_train(df)
    assert p.ready
    out = p.predict_eta(df.head(3))
    assert "predicted_eta" in out.columns
    assert out["predicted_eta"].iloc[0] is not None
    assert out["eta_confidence_hours"].iloc[0] >= 0


def test_eta_endpoint_404(client):
    r = client.get("/api/eta/UNKNOWN")
    assert r.status_code == 404


def test_eta_endpoint_returns_prediction(client, db):
    """Single-shipment ETA should return predicted timestamps + confidence."""
    _seed_training_data(db, n=60)
    _make_shipment(
        db,
        shipment_id="ETA-LIVE01",
        status="in_transit",
        ship_date="2026-04-25",
        estimated_arrival="2026-04-30",
        transit_days=5,
    )
    r = client.get("/api/eta/ETA-LIVE01")
    assert r.status_code == 200
    body = r.json()
    assert body["shipment_id"] == "ETA-LIVE01"
    assert body["predicted_eta"] is not None
    assert body["predicted_eta_lower"] is not None
    assert body["predicted_eta_upper"] is not None
    assert body["eta_confidence_hours"] >= 0
    assert body["predicted_transit_hours"] > 0


def test_eta_endpoint_case_insensitive(client, db):
    _seed_training_data(db, n=60)
    _make_shipment(db, shipment_id="ETA-CASE01", status="in_transit")
    r = client.get("/api/eta/eta-case01")
    assert r.status_code == 200
    assert r.json()["shipment_id"] == "ETA-CASE01"


def test_eta_list_filters_active(client, db):
    """List endpoint without status filter should only return active rows."""
    _seed_training_data(db, n=60)
    _make_shipment(db, shipment_id="ETA-ACTIVE", status="in_transit")
    _make_shipment(db, shipment_id="ETA-DONE", status="delivered")
    r = client.get("/api/eta/")
    assert r.status_code == 200
    rows = r.json()
    ids = {row["shipment_id"] for row in rows}
    assert "ETA-ACTIVE" in ids
    assert "ETA-DONE" not in ids


def test_eta_summary(client, db):
    _seed_training_data(db, n=40)
    _make_shipment(db, shipment_id="ETA-SUMM01", status="in_transit")
    r = client.get("/api/eta/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["confidence_level"] == 0.95
    assert body["in_flight_count"] >= 1
    assert body["training_sample_count"] >= 1
