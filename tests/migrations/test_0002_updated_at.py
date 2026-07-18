"""updated_at 字段迁移测试。

冻结 Schema 已将 updated_at 下沉到 0001_identity_and_audit；
本迁移保留以保持 Alembic 链完整，不再执行额外变更。
"""

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
    upgrade(config, "0002_updated_at")

    engine = create_engine(isolated_database_url)
    yield engine
    engine.dispose()


@pytest.mark.skipif(not IS_POSTGRESQL, reason="updated_at 迁移需要 PostgreSQL")
@pytest.mark.parametrize(
    "table_name",
    ["user_roles", "refresh_tokens", "audit_events"],
)
def test_updated_at_column_exists(upgraded_engine: Engine, table_name: str) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns(table_name)}
    assert "updated_at" in columns
    assert columns["updated_at"]["nullable"] is False
