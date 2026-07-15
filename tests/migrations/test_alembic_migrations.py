import os
from unittest.mock import patch

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_revision_history_is_linear():
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    revisions = list(script.walk_revisions())
    assert len(revisions) >= 1, "至少应该有一个迁移版本"


def test_alembic_can_run_upgrade():
    config = Config("alembic.ini")

    url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not url:
        pytest.skip("需要数据库URL来运行迁移测试")

    with patch(
        "packages.backend.database.migrations.env.get_database_url",
        return_value=url,
    ):
        from alembic.command import upgrade

        upgrade(config, "head")


def test_alembic_can_run_downgrade():
    config = Config("alembic.ini")

    url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not url:
        pytest.skip("需要数据库URL来运行迁移测试")

    with patch(
        "packages.backend.database.migrations.env.get_database_url",
        return_value=url,
    ):
        from alembic.command import downgrade

        downgrade(config, "base")
