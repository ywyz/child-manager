from datetime import UTC, date, datetime, timedelta
from importlib import import_module

import psycopg
from alembic import command
from alembic.config import Config


def test_workday_cache_is_tenant_scoped_and_upserts_one_date(
    isolated_database_url: str,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    repository_class = import_module(
        "packages.backend.integrations.calendar.repository"
    ).WorkdayCacheRepository
    from uuid import uuid4

    kindergarten_id = uuid4()
    other_kindergarten_id = uuid4()
    now = datetime(2026, 3, 2, tzinfo=UTC)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s,'缓存测试园')",
            (kindergarten_id,),
        )
        repository = repository_class(connection)
        repository.put(
            kindergarten_id,
            calendar_date=date(2026, 3, 2),
            result_code="workday",
            source_code="local",
            source_version="test",
            detail={},
            checked_at=now,
            expires_at=now + timedelta(hours=24),
        )
        repository.put(
            kindergarten_id,
            calendar_date=date(2026, 3, 2),
            result_code="non_workday",
            source_code="local",
            source_version="test",
            detail={},
            checked_at=now,
            expires_at=now + timedelta(hours=24),
        )
        assert repository.get(kindergarten_id, date(2026, 3, 2), now) is not None
        assert repository.get(other_kindergarten_id, date(2026, 3, 2), now) is None
        assert connection.execute("SELECT count(*) FROM workday_cache").fetchone() == (1,)
