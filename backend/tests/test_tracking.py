from models import Shipment


def _make_shipment(db, **kwargs):
    defaults = dict(
        shipment_id="SHP-TEST01",
        origin="New York, NY",
        destination="Los Angeles, CA",
        carrier="FedEx",
        status="in_transit",
        ship_date="2024-01-01",
        estimated_arrival="2024-01-05",
        delay_hours=0.0,
        transit_days=4,
        month=1,
    )
    defaults.update(kwargs)
    s = Shipment(**defaults)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_track_found(client, db):
    _make_shipment(db, shipment_id="TRK-001", status="delivered")
    r = client.get("/track/TRK-001")
    assert r.status_code == 200
    body = r.json()
    assert body["shipment_id"] == "TRK-001"
    assert body["status"] == "delivered"
    assert len(body["timeline"]) == 4
    assert body["timeline"][-1]["done"] is True


def test_track_not_found(client):
    r = client.get("/track/NONEXISTENT")
    assert r.status_code == 404


def test_track_case_insensitive(client, db):
    _make_shipment(db, shipment_id="TRK-002", status="in_transit")
    r = client.get("/track/trk-002")
    assert r.status_code == 200
    assert r.json()["shipment_id"] == "TRK-002"


def test_track_delayed_timeline(client, db):
    _make_shipment(db, shipment_id="TRK-003", status="delayed", delay_hours=6.0)
    r = client.get("/track/TRK-003")
    assert r.status_code == 200
    body = r.json()
    assert body["delay_hours"] == 6.0
    assert body["timeline"][0]["done"] is True
    assert body["timeline"][-1]["done"] is False
