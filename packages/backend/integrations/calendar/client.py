"""Timor 在线工作日适配器。"""

from datetime import date
from typing import Any

import httpx

TIMOR_URL = "https://timor.tech/api/holiday/info/{calendar_date}"


def map_timor_payload(payload: object) -> str | None:
    if not isinstance(payload, dict) or payload.get("code") != 0:
        return None
    type_value = payload.get("type")
    if not isinstance(type_value, dict):
        return None
    day_type = type_value.get("type")
    if day_type in (0, 3):
        return "workday"
    if day_type in (1, 2):
        return "non_workday"
    return None


class TimorWorkdayClient:
    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        self._transport = transport

    def check(self, calendar_date: date) -> str | None:
        try:
            with httpx.Client(
                transport=self._transport,
                follow_redirects=False,
                trust_env=False,
                timeout=httpx.Timeout(5.0, connect=2.0),
            ) as client:
                response = client.get(TIMOR_URL.format(calendar_date=calendar_date.isoformat()))
            if response.is_redirect or response.status_code != 200:
                return None
            payload: Any = response.json()
        except httpx.HTTPError, OSError, RuntimeError, ValueError:
            return None
        return map_timor_payload(payload)
