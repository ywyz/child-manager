import os
import subprocess

import psycopg
import pytest
from alembic import command
from alembic.config import Config


def _run_cli(
    database_url: str,
    *arguments: str,
    input_text: str = "",
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["CHILD_MANAGER_DATABASE_URL"] = database_url
    return subprocess.run(
        ["uv", "run", "python", "-m", "packages.backend.bootstrap", *arguments],
        input=input_text,
        text=True,
        capture_output=True,
        env=environment,
        check=False,
        start_new_session=True,
    )


def test_init_admin_cli_exposes_start_activate_and_migration_commands(
    isolated_database_url: str,
) -> None:
    help_result = _run_cli(isolated_database_url, "--help")

    assert help_result.returncode == 0
    assert {"init-admin", "migrate-passkeys"} <= set(help_result.stdout.split())
    init_help = _run_cli(isolated_database_url, "init-admin", "--help")
    assert init_help.returncode == 0
    assert {"start", "activate"} <= set(init_help.stdout.split())


def test_init_admin_start_creates_pending_account_and_one_time_secret_without_password(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    answers = "测试幼儿园\nadmin\n测试管理员\nowner-ref-001\noperator-ref-002\n"

    first = _run_cli(isolated_database_url, "init-admin", "start", input_text=answers)

    assert first.returncode == 0
    combined_output = first.stdout + first.stderr
    assert "密码" not in combined_output
    assert "初始化凭据" in combined_output
    assert "http://" not in combined_output and "https://" not in combined_output
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute("SELECT status FROM users").fetchone() == (
            "pending_registration",
        )
        secret_row = connection.execute(
            """SELECT token_digest, expires_at - created_at, consumed_at
            FROM bootstrap_initializations"""
        ).fetchone()
    assert secret_row is not None
    assert secret_row[0]
    assert secret_row[1].total_seconds() == 15 * 60
    assert secret_row[2] is None

    second = _run_cli(isolated_database_url, "init-admin", "start", input_text=answers)
    assert second.returncode == 0
    assert "系统已初始化" in second.stdout


def test_init_admin_activate_requires_two_distinct_pre_registered_approvers(
    isolated_database_url: str,
) -> None:
    result = _run_cli(
        isolated_database_url,
        "init-admin",
        "activate",
        "--bootstrap-id",
        "00000000-0000-7000-8000-000000000001",
    )

    assert result.returncode != 0
    assert "园所负责人" in result.stdout + result.stderr
    assert "独立运维" in result.stdout + result.stderr
