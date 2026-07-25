from datetime import UTC, datetime, timedelta

from packages.backend.identity.login_throttle import MemoryLoginThrottle

NOW = datetime(2026, 7, 24, 12, 0, tzinfo=UTC)


def test_backup_login_throttle_has_independent_account_source_and_global_limits() -> None:
    throttle = MemoryLoginThrottle(
        account_failure_limit=1,
        source_failure_limit=2,
        global_failure_limit=3,
        window=timedelta(minutes=15),
    )

    account = throttle.record_failure(
        account="admin",
        source="203.0.113.1",
        purpose="backup_authentication",
        now=NOW,
    )
    source = throttle.record_failure(
        account="teacher",
        source="203.0.113.1",
        purpose="backup_authentication",
        now=NOW,
    )
    global_limit = throttle.record_failure(
        account="other",
        source="198.51.100.2",
        purpose="backup_authentication",
        now=NOW,
    )

    assert account.account_limited
    assert not account.source_limited
    assert not account.global_limited
    assert source.source_limited
    assert global_limit.global_limited
    assert "admin" not in repr(vars(throttle))
    assert "teacher" not in repr(vars(throttle))


def test_backup_success_clears_only_account_bucket_and_not_passkey_or_global_state() -> None:
    throttle = MemoryLoginThrottle(
        account_failure_limit=1,
        source_failure_limit=1,
        global_failure_limit=1,
        window=timedelta(minutes=15),
    )
    throttle.record_failure(
        account="admin",
        source="203.0.113.1",
        purpose="backup_authentication",
        now=NOW,
    )

    throttle.record_success(
        account="admin",
        source="203.0.113.1",
        purpose="backup_authentication",
        now=NOW,
    )

    backup = throttle.check(
        account="admin",
        source="203.0.113.1",
        purpose="backup_authentication",
        now=NOW,
    )
    passkey = throttle.check(
        account="admin",
        source="203.0.113.1",
        purpose="authentication",
        now=NOW,
    )
    assert not backup.account_limited
    assert backup.source_limited
    assert backup.global_limited
    assert not passkey.account_limited
    assert not passkey.source_limited
    assert not passkey.global_limited
