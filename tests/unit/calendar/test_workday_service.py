from datetime import UTC, date, datetime, timedelta
from importlib import import_module

import httpx
import pytest


def _module():
    return import_module("packages.backend.integrations.calendar.service")


def test_local_result_wins_conflict_and_uses_one_hour_cache() -> None:
    module = _module()
    now = datetime(2026, 3, 2, tzinfo=UTC)
    result = module.combine_workday_results(
        calendar_date=date(2026, 3, 2),
        local_result="workday",
        online_result="non_workday",
        checked_at=now,
    )

    assert result.result_code == "workday"
    assert result.source_code == "combined"
    assert result.expires_at == now + timedelta(hours=1)


def test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls() -> None:
    module = _module()
    now = datetime(2026, 3, 2, tzinfo=UTC)
    confirmed = module.combine_workday_results(
        calendar_date=date(2026, 3, 2),
        local_result="workday",
        online_result="workday",
        checked_at=now,
    )
    unavailable = module.combine_workday_results(
        calendar_date=date(2026, 3, 3),
        local_result=None,
        online_result=None,
        checked_at=now,
    )

    assert confirmed.expires_at == now + timedelta(hours=24)
    assert unavailable.result_code == "unknown"
    assert unavailable.source_code == "unavailable"
    assert unavailable.expires_at == now + timedelta(minutes=5)


def test_timor_mapping_rejects_nonzero_missing_unknown_and_redirect_responses() -> None:
    module = import_module("packages.backend.integrations.calendar.client")

    assert module.map_timor_payload({"code": 0, "type": {"type": 0}}) == "workday"
    assert module.map_timor_payload({"code": 0, "type": {"type": 3}}) == "workday"
    assert module.map_timor_payload({"code": 0, "type": {"type": 1}}) == "non_workday"
    assert module.map_timor_payload({"code": 0, "type": {"type": 2}}) == "non_workday"
    assert module.map_timor_payload({"code": 1, "type": {"type": 0}}) is None
    assert module.map_timor_payload({"code": 0, "type": {"type": 9}}) is None
    assert module.map_timor_payload({"code": 0}) is None


def test_timor_client_uses_fixed_url_no_redirect_and_fixed_timeouts() -> None:
    module = import_module("packages.backend.integrations.calendar.client")
    requests: list[httpx.Request] = []

    def redirect(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            302,
            headers={"Location": "https://untrusted.example/redirect"},
            request=request,
        )

    result = module.TimorWorkdayClient(httpx.MockTransport(redirect)).check(date(2026, 3, 2))

    assert result is None
    assert [str(request.url) for request in requests] == [
        "https://timor.tech/api/holiday/info/2026-03-02"
    ]
    assert requests[0].extensions["timeout"] == {
        "connect": 2.0,
        "read": 5.0,
        "write": 5.0,
        "pool": 5.0,
    }


def test_timor_client_softly_degrades_timeout_and_fixed_payloads() -> None:
    module = import_module("packages.backend.integrations.calendar.client")

    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("calendar timeout", request=request)

    def confirmed(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"code": 0, "type": {"type": 3}},
            request=request,
        )

    assert module.TimorWorkdayClient(httpx.MockTransport(timeout)).check(date(2026, 3, 2)) is None
    assert (
        module.TimorWorkdayClient(httpx.MockTransport(confirmed)).check(date(2026, 3, 2))
        == "workday"
    )


def test_unsupported_local_calendar_range_softly_falls_back_to_online(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    now = datetime(2026, 3, 2, tzinfo=UTC)

    def unsupported(_value: date) -> bool:
        raise NotImplementedError

    class OnlineClient:
        @staticmethod
        def check(_value: date) -> str:
            return "workday"

    monkeypatch.setattr(module, "is_workday", unsupported)

    result = module.resolve_uncached_workday(
        date(2200, 3, 2),
        now=now,
        online_client=OnlineClient(),
    )

    assert result.result_code == "workday"
    assert result.source_code == "online"
