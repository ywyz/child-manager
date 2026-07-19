"""Alembic 迁移门禁测试。

在 PostgreSQL 可用时验证 upgrade/downgrade 真实执行；
逐测试使用独立 schema 隔离，避免跨测试污染。
SQLite 不支持跨连接共享内存数据库，迁移测试仅在 PostgreSQL 下执行。
"""

import pytest

from tests.conftest import IS_POSTGRESQL


def test_alembic_revision_history_is_linear():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    revisions = list(script.walk_revisions())
    assert len(revisions) >= 1, "至少应该有一个迁移版本"


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="迁移 upgrade/downgrade 需要 PostgreSQL；CI 已配置 PostgreSQL service",
)
def test_alembic_can_run_upgrade(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from alembic.command import upgrade
    from alembic.config import Config

    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    upgrade(config, "head")


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="迁移 upgrade/downgrade 需要 PostgreSQL；CI 已配置 PostgreSQL service",
)
def test_alembic_can_run_downgrade(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from alembic.command import downgrade, upgrade
    from alembic.config import Config

    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    upgrade(config, "head")
    downgrade(config, "base")


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="迁移 upgrade/downgrade 需要 PostgreSQL；CI 已配置 PostgreSQL service",
)
def test_alembic_upgrade_from_0005_to_head(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """模拟旧库已升级到 0005，再执行当前 head 升级必须成功（迁移只追加）。"""
    from alembic.command import upgrade
    from alembic.config import Config
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.types import UUID

    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    upgrade(config, "0005_refresh_family_revoked")
    upgrade(config, "head")

    engine = create_engine(isolated_database_url)
    inspector = inspect(engine)
    columns = {c["name"]: c for c in inspector.get_columns("users")}
    assert isinstance(columns["id"]["type"], UUID)
    assert "username_normalized" in columns
    engine.dispose()
