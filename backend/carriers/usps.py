import os
import xml.etree.ElementTree as ET
from typing import Optional

import httpx

from .base import CarrierAdapter

_TRACK_URL = "https://secure.shippingapis.com/ShippingAPI.dll"


class USPSAdapter(CarrierAdapter):
    name = "USPS"

    def __init__(self):
        self._user_id = os.getenv("USPS_USER_ID", "")

    async def track(self, tracking_number: str) -> Optional[dict]:
        if not self._user_id:
            return self._mock(tracking_number)
        xml_request = (
            f'<TrackFieldRequest USERID="{self._user_id}">'
            f'<TrackID ID="{tracking_number}"/>'
            f'</TrackFieldRequest>'
        )
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    _TRACK_URL,
                    params={"API": "TrackV2", "XML": xml_request},
                )
                r.raise_for_status()
                root = ET.fromstring(r.text)
                track_info = root.find(".//TrackInfo")
                if track_info is None:
                    return self._mock(tracking_number)

                summary = track_info.findtext("TrackSummary/EventTime", "") or ""
                status  = track_info.findtext("TrackSummary/Event", "Unknown")
                city    = track_info.findtext("TrackSummary/EventCity", "")
                state   = track_info.findtext("TrackSummary/EventState", "")

                events = []
                for detail in track_info.findall("TrackDetail"):
                    events.append({
                        "timestamp": detail.findtext("EventDate", "") + " " + detail.findtext("EventTime", ""),
                        "description": detail.findtext("Event", ""),
                        "location": detail.findtext("EventCity", "") + ", " + detail.findtext("EventState", ""),
                    })

                return {
                    "tracking_number": tracking_number,
                    "carrier": self.name,
                    "status": status,
                    "location": f"{city}, {state}".strip(", "),
                    "estimated_delivery": None,
                    "events": events,
                    "source": "live",
                }
        except Exception:
            return self._mock(tracking_number)
