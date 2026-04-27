import os
from typing import Optional

import httpx

from .base import CarrierAdapter

_TOKEN_URL = "https://apis.fedex.com/oauth/token"
_TRACK_URL = "https://apis.fedex.com/track/v1/trackingnumbers"


class FedExAdapter(CarrierAdapter):
    name = "FedEx"

    def __init__(self):
        self._client_id     = os.getenv("FEDEX_CLIENT_ID", "")
        self._client_secret = os.getenv("FEDEX_CLIENT_SECRET", "")
        self._token: Optional[str] = None

    async def _get_token(self) -> Optional[str]:
        if not (self._client_id and self._client_secret):
            return None
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                _TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
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
                r = await client.post(
                    _TRACK_URL,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={
                        "includeDetailedScans": True,
                        "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
                    },
                )
                r.raise_for_status()
                data = r.json()
                pkg = data["output"]["completeTrackResults"][0]["trackResults"][0]
                events = [
                    {
                        "timestamp": e.get("date", ""),
                        "description": e.get("eventDescription", ""),
                        "location": e.get("scanLocation", {}).get("city", ""),
                    }
                    for e in pkg.get("dateAndTimes", [])
                ]
                return {
                    "tracking_number": tracking_number,
                    "carrier": self.name,
                    "status": pkg.get("latestStatusDetail", {}).get("description", "Unknown"),
                    "location": pkg.get("lastUpdateTime", ""),
                    "estimated_delivery": pkg.get("estimatedDeliveryTimeWindow", {})
                        .get("window", {}).get("ends", None),
                    "events": events,
                    "source": "live",
                }
        except Exception:
            return self._mock(tracking_number)
