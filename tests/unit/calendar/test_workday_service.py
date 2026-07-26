from datetime import UTC, date, datetime, timedelta
from importlib import import_module


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
