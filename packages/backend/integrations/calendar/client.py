"""Timor 在线工作日适配器。"""

import asyncio
from datetime import date
from typing import Any

import httpx

TIMOR_URL = "https://timor.tech/api/holiday/info/{calendar_date}"
TIMOR_TOTAL_TIMEOUT_SECONDS = 5.0


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
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport

    async def _check(self, calendar_date: date) -> str | None:
        async with asyncio.timeout(TIMOR_TOTAL_TIMEOUT_SECONDS):
            async with httpx.AsyncClient(
                transport=self._transport,
                follow_redirects=False,
                trust_env=False,
                timeout=httpx.Timeout(5.0, connect=2.0),
            ) as client:
                response = await client.get(
                    TIMOR_URL.format(calendar_date=calendar_date.isoformat())
                )
            if response.is_redirect or response.status_code != 200:
                return None
            payload: Any = response.json()
        return map_timor_payload(payload)

    def check(self, calendar_date: date) -> str | None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            return None
        try:
            return asyncio.run(self._check(calendar_date))
        except TimeoutError, httpx.HTTPError, OSError, RuntimeError, ValueError:
            return None
