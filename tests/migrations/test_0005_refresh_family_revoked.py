"""refresh_tokens family_revoked_at 列迁移测试。"""

import os
from collections.abc import Iterator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from tests.conftest import IS_POSTGRESQL


@pytest.fixture
def upgraded_engine(isolated_database_url: str) -> Iterator[Engine]:
    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0005_refresh_family_revoked")

    engine = create_engine(isolated_database_url)
    yield engine
    engine.dispose()


@pytest.mark.skipif(not IS_POSTGRESQL, reason="family_revoked_at 迁移需要 PostgreSQL")
def test_family_revoked_at_column_exists(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("refresh_tokens")}
    assert "family_revoked_at" in columns


@pytest.mark.skipif(not IS_POSTGRESQL, reason="family_revoked_at 迁移需要 PostgreSQL")
def test_family_revoked_at_column_is_nullable_datetime(
    upgraded_engine: Engine,
) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("refresh_tokens")}
    column = columns["family_revoked_at"]
    assert column["nullable"] is True
    assert str(column["type"]).lower() in {
        "timestamp with time zone",
        "datetime_with_timezone",
        "timestamp",
    }
