"""Alembic 空库升级基础。"""

import os
import subprocess

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_passkey_contract_revision_is_declared_as_head() -> None:
    heads = ScriptDirectory.from_config(Config("alembic.ini")).get_heads()

    assert heads == ["0003_passkey_contract"]


def test_empty_database_can_upgrade_to_identity_head(isolated_database_url: str) -> None:
    environment = os.environ | {"CHILD_MANAGER_DATABASE_URL": isolated_database_url}
    upgrade = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )
    current = subprocess.run(
        ["uv", "run", "alembic", "current"],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert upgrade.returncode == 0, upgrade.stderr
    assert current.returncode == 0, current.stderr
    assert "0003_passkey_contract" in current.stdout


def test_migrations_reject_missing_database_url() -> None:
    environment = {
        key: value for key, value in os.environ.items() if key != "CHILD_MANAGER_DATABASE_URL"
    }

    current = subprocess.run(
        ["uv", "run", "alembic", "current"],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert current.returncode != 0
    assert "CHILD_MANAGER_DATABASE_URL" in current.stderr
