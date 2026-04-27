import os
from typing import Optional

import httpx

from .base import CarrierAdapter

_TOKEN_URL = "https://onlinetools.ups.com/security/v1/oauth/token"
_TRACK_URL = "https://onlinetools.ups.com/api/track/v1/details/{}"


class UPSAdapter(CarrierAdapter):
    name = "UPS"

    def __init__(self):
        self._client_id     = os.getenv("UPS_CLIENT_ID", "")
        self._client_secret = os.getenv("UPS_CLIENT_SECRET", "")

    async def _get_token(self) -> Optional[str]:
        if not (self._client_id and self._client_secret):
            return None
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                _TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(self._client_id, self._client_secret),
            )
            r.raise_for_status()
            return r.json()["access_token"]

    async def track(self, tracking_number: str) -> Optional[dict]:
        if not (self._client_id and self._client_secret):
            return self._mock(tracking_number)
        try:
            token = await self._get_token()
            if not token:
                return self._mock(tracking_number)
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    _TRACK_URL.format(tracking_number),
                    headers={
                        "Authorization": f"Bearer {token}",
                        "transId": "shiplogiz-001",
                        "transactionSrc": "ShipLogiz",
                    },
                )
                r.raise_for_status()
                data = r.json()
                shipment = data["trackResponse"]["shipment"][0]
                pkg = shipment["package"][0]
                activity = pkg.get("activity", [])
                events = [
                    {
                        "timestamp": a.get("date", "") + " " + a.get("time", ""),
                        "description": a.get("status", {}).get("description", ""),
                        "location": a.get("location", {}).get("address", {}).get("city", ""),
                    }
                    for a in activity
                ]
                return {
                    "tracking_number": tracking_number,
                    "carrier": self.name,
                    "status": pkg.get("currentStatus", {}).get("description", "Unknown"),
                    "location": activity[0].get("location", {}).get("address", {}).get("city", "") if activity else "",
                    "estimated_delivery": pkg.get("deliveryDate", [{}])[0].get("date"),
                    "events": events,
                    "source": "live",
                }
        except Exception:
            return self._mock(tracking_number)
