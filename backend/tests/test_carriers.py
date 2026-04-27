import pytest

from carriers.factory import get_adapter, list_carriers


def test_factory_known_carriers():
    known = list_carriers()
    assert set(known) >= {"fedex", "ups", "usps", "dhl"}


def test_factory_unknown_returns_adapter():
    adapter = get_adapter("acme-logistics")
    assert adapter is not None


@pytest.mark.asyncio
async def test_fedex_mock_fallback():
    """No env key → mock response, not an exception."""
    adapter = get_adapter("fedex")
    result = await adapter.track("TEST123456")
    assert result is not None
    assert result["carrier"] == "FedEx"
    assert result["source"] == "mock"


@pytest.mark.asyncio
async def test_ups_mock_fallback():
    adapter = get_adapter("ups")
    result = await adapter.track("1Z999AA10123456784")
    assert result is not None
    assert result["source"] == "mock"


@pytest.mark.asyncio
async def test_usps_mock_fallback():
    adapter = get_adapter("usps")
    result = await adapter.track("9400111899223456677")
    assert result is not None
    assert result["source"] == "mock"


@pytest.mark.asyncio
async def test_dhl_mock_fallback():
    adapter = get_adapter("dhl")
    result = await adapter.track("1234567890")
    assert result is not None
    assert result["source"] == "mock"


def test_live_track_endpoint_no_keys(client, db):
    from models import Shipment
    s = Shipment(
        shipment_id="SHP-CARR01", origin="NYC", destination="LAX",
        carrier="FedEx", status="in_transit", ship_date="2024-01-01",
        estimated_arrival="2024-01-05", delay_hours=0.0, transit_days=4, month=1,
    )
    db.add(s)
    db.commit()
    r = client.get("/api/carriers/live/SHP-CARR01")
    assert r.status_code == 200
    assert r.json()["source"] == "mock"
