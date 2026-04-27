from abc import ABC, abstractmethod
from typing import Optional


class CarrierAdapter(ABC):
    """Normalized tracking adapter for a single carrier."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def track(self, tracking_number: str) -> Optional[dict]:
        """Return normalized tracking dict or None on failure."""
        ...

    def _mock(self, tracking_number: str) -> dict:
        return {
            "tracking_number": tracking_number,
            "carrier": self.name,
            "status": "in_transit",
            "location": "En route",
            "estimated_delivery": None,
            "events": [],
            "source": "mock",
        }
