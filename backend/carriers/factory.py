from .base import CarrierAdapter
from .dhl import DHLAdapter
from .fedex import FedExAdapter
from .ups import UPSAdapter
from .usps import USPSAdapter

_REGISTRY: dict[str, type[CarrierAdapter]] = {
    "fedex": FedExAdapter,
    "ups":   UPSAdapter,
    "usps":  USPSAdapter,
    "dhl":   DHLAdapter,
}


def get_adapter(carrier: str) -> CarrierAdapter:
    key = carrier.lower().strip()
    cls = _REGISTRY.get(key)
    if cls is None:
        # Unknown carrier — use FedEx adapter in mock-only mode
        return FedExAdapter()
    return cls()


def list_carriers() -> list[str]:
    return list(_REGISTRY.keys())
