"""初始化管理员 CLI 测试。"""

import os
import subprocess
import sys

import pytest


@pytest.fixture
def cli_env(migrated_database_url: str) -> dict[str, str]:
    env = os.environ.copy()
    env["CHILD_MANAGER_DATABASE_URL"] = migrated_database_url
    env["CHILD_MANAGER_JWT_SIGNING_KEY"] = "test-jwt-signing-key-32bytes-long-12345"
    env["CHILD_MANAGER_CSRF_SIGNING_KEY"] = "test-csrf-signing-key-32bytes-long-1234"
    return env


def _run_cli(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "packages.backend.bootstrap"],
        input="管理员\nadmin\nValidPassword2024!\nValidPassword2024!\n",
        capture_output=True,
        text=True,
        env=env,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    )


def test_init_admin_cli_runs_once_and_reports_initialized(cli_env: dict[str, str]) -> None:
    first = _run_cli(cli_env)
    assert first.returncode == 0
    assert "初始化" in first.stdout or "管理员" in first.stdout

    second = _run_cli(cli_env)
    assert second.returncode == 0
    assert "系统已初始化" in second.stdout
