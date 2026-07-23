from datetime import UTC, datetime, timedelta

from packages.backend.identity.auth_throttle import (
    GLOBAL_THROTTLE_SOURCE,
    MemoryAuthThrottle,
    subject_throttle_source,
)

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)


def test_public_identity_throttle_is_partitioned_by_source_and_purpose() -> None:
    throttle = MemoryAuthThrottle(failure_limit=3, window=timedelta(minutes=15))

    for offset in range(3):
        throttle.record_failure(
            source="203.0.113.9",
            purpose="authentication",
            now=NOW + timedelta(seconds=offset),
        )

    blocked = throttle.check(
        source="203.0.113.9",
        purpose="authentication",
        now=NOW + timedelta(seconds=3),
    )
    other_purpose = throttle.check(
        source="203.0.113.9",
        purpose="recovery",
        now=NOW + timedelta(seconds=3),
    )
    other_source = throttle.check(
        source="198.51.100.7",
        purpose="authentication",
        now=NOW + timedelta(seconds=3),
    )

    assert not blocked.allowed
    assert 1 <= blocked.retry_after_seconds <= 900
    assert other_purpose.allowed
    assert other_source.allowed


def test_success_resets_only_the_matching_source_and_purpose() -> None:
    throttle = MemoryAuthThrottle(failure_limit=1, window=timedelta(minutes=15))
    throttle.record_failure(source="203.0.113.9", purpose="invitation", now=NOW)
    throttle.record_failure(source="203.0.113.9", purpose="recovery", now=NOW)

    throttle.record_success(source="203.0.113.9", purpose="invitation", now=NOW)

    assert throttle.check(source="203.0.113.9", purpose="invitation", now=NOW).allowed
    assert not throttle.check(source="203.0.113.9", purpose="recovery", now=NOW).allowed


def test_failures_expire_as_one_window_without_leaking_account_keys() -> None:
    throttle = MemoryAuthThrottle(failure_limit=1, window=timedelta(minutes=15))
    throttle.record_failure(source="203.0.113.9", purpose="authentication", now=NOW)

    assert not throttle.check(
        source="203.0.113.9",
        purpose="authentication",
        now=NOW + timedelta(minutes=14),
    ).allowed
    assert throttle.check(
        source="203.0.113.9",
        purpose="authentication",
        now=NOW + timedelta(minutes=15, microseconds=1),
    ).allowed
    assert "login" not in vars(throttle) and "user" not in vars(throttle)


def test_source_subject_and_global_scopes_have_independent_limits() -> None:
    throttle = MemoryAuthThrottle(
        failure_limit=2,
        subject_failure_limit=3,
        global_failure_limit=4,
        window=timedelta(minutes=15),
    )
    subject_source = subject_throttle_source(purpose="recovery", subject="admin")

    for source, count in (
        ("203.0.113.9", 2),
        (subject_source, 3),
        (GLOBAL_THROTTLE_SOURCE, 4),
    ):
        for offset in range(count):
            throttle.record_failure(
                source=source,
                purpose="recovery",
                now=NOW + timedelta(seconds=offset),
            )

    assert not throttle.check(
        source="203.0.113.9", purpose="recovery", now=NOW + timedelta(seconds=5)
    ).allowed
    assert not throttle.check(
        source=subject_source, purpose="recovery", now=NOW + timedelta(seconds=5)
    ).allowed
    assert not throttle.check(
        source=GLOBAL_THROTTLE_SOURCE,
        purpose="recovery",
        now=NOW + timedelta(seconds=5),
    ).allowed
    assert "admin" not in subject_source
