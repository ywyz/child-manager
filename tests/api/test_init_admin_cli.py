import os
import subprocess

import pytest
from alembic import command
from alembic.config import Config


def _run_cli(database_url: str, input_text: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["CHILD_MANAGER_DATABASE_URL"] = database_url
    return subprocess.run(
        ["uv", "run", "python", "-m", "packages.backend.bootstrap", "init-admin"],
        input=input_text,
        text=True,
        capture_output=True,
        env=environment,
        check=False,
        start_new_session=True,
    )


def test_init_admin_is_single_transaction_non_echoing_and_idempotent(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    password = "管理员足够长的安全测试密码 2026"
    answers = f"测试幼儿园\nadmin\n测试管理员\n{password}\n{password}\n"
    first = _run_cli(isolated_database_url, answers)
    assert first.returncode == 0
    assert password not in first.stdout + first.stderr
    second = _run_cli(isolated_database_url, answers)
    assert second.returncode == 0
    assert "系统已初始化" in second.stdout
