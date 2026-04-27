import os
from typing import Optional

import httpx

from .base import CarrierAdapter

_TRACK_URL = "https://api-eu.dhl.com/track/shipments"


class DHLAdapter(CarrierAdapter):
    name = "DHL"

    def __init__(self):
        self._api_key = os.getenv("DHL_API_KEY", "")

    async def track(self, tracking_number: str) -> Optional[dict]:
        if not self._api_key:
            return self._mock(tracking_number)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    _TRACK_URL,
                    headers={"DHL-API-Key": self._api_key},
                    params={"trackingNumber": tracking_number},
                )
                r.raise_for_status()
                data = r.json()
                shipment = data["shipments"][0]
                events = [
                    {
                        "timestamp": e.get("timestamp", ""),
                        "description": e.get("description", ""),
                        "location": e.get("location", {}).get("address", {}).get("addressLocality", ""),
                    }
                    for e in shipment.get("events", [])
                ]
                est_delivery = None
                for e in shipment.get("estimatedTimeOfDelivery", []):
                    est_delivery = e
                    break

                return {
                    "tracking_number": tracking_number,
                    "carrier": self.name,
                    "status": shipment.get("status", {}).get("description", "Unknown"),
                    "location": shipment.get("status", {}).get("location", {})
                        .get("address", {}).get("addressLocality", ""),
                    "estimated_delivery": est_delivery,
                    "events": events,
                    "source": "live",
                }
        except Exception:
            return self._mock(tracking_number)
