import os
import subprocess
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config

from packages.backend.identity.secret_tokens import SecretPurpose, verify_secret


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


def _prepare_last_admin_recovery(
    database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[UUID, UUID]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", database_url)
    command.upgrade(Config("alembic.ini"), "head")
    started = _run_cli(
        database_url,
        "init-admin",
        "start",
        input_text="测试幼儿园\nadmin\n测试管理员\nowner-ref-001\noperator-ref-002\n",
    )
    assert started.returncode == 0
    native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    now = datetime.now(UTC)
    recovery_request_id = uuid4()
    recovery_code_id = uuid4()
    with psycopg.connect(native_url) as connection:
        bootstrap = connection.execute(
            "SELECT id, kindergarten_id, user_id FROM bootstrap_initializations"
        ).fetchone()
        assert bootstrap is not None
        bootstrap_id, kindergarten_id, user_id = bootstrap
        connection.execute(
            """UPDATE users SET status='active', activated_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (now, kindergarten_id, user_id),
        )
        connection.execute(
            """UPDATE bootstrap_initializations SET activated_at=%s, updated_at=now()
            WHERE id=%s""",
            (now, bootstrap_id),
        )
        connection.execute(
            """INSERT INTO recovery_codes
            (id, kindergarten_id, user_id, code_hash, issued_at, consumed_at)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                recovery_code_id,
                kindergarten_id,
                user_id,
                "consumed-recovery-code-digest",
                now,
                now,
            ),
        )
        connection.execute(
            """INSERT INTO account_recovery_requests
            (id, kindergarten_id, user_id, recovery_code_id, status, requested_at, expires_at)
            VALUES (%s,%s,%s,%s,'pending_verification',%s,%s)""",
            (
                recovery_request_id,
                kindergarten_id,
                user_id,
                recovery_code_id,
                now,
                now + timedelta(hours=24),
            ),
        )
    return UUID(str(recovery_request_id)), UUID(str(user_id))


def test_init_admin_cli_exposes_start_activate_and_migration_commands(
    isolated_database_url: str,
) -> None:
    help_result = _run_cli(isolated_database_url, "--help")

    assert help_result.returncode == 0
    assert {"init-admin", "migrate-passkeys"} <= set(help_result.stdout.split())
    init_help = _run_cli(isolated_database_url, "init-admin", "--help")
    assert init_help.returncode == 0
    assert {"start", "activate", "recover-last-admin"} <= set(init_help.stdout.split())
    recovery_help = _run_cli(isolated_database_url, "init-admin", "recover-last-admin", "--help")
    assert recovery_help.returncode == 0
    assert "--recovery-request-id" in recovery_help.stdout
    assert "--recovery-code" not in recovery_help.stdout
    assert "--owner-reference" not in recovery_help.stdout
    assert "--operator-reference" not in recovery_help.stdout


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


def test_recover_last_admin_matches_pre_registered_approvers_and_issues_once(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery_request_id, _user_id = _prepare_last_admin_recovery(isolated_database_url, monkeypatch)

    rejected = _run_cli(
        isolated_database_url,
        "init-admin",
        "recover-last-admin",
        "--recovery-request-id",
        str(recovery_request_id),
        input_text="wrong-owner\noperator-ref-002\n",
    )

    assert rejected.returncode != 0
    assert "恢复登记凭据" not in rejected.stdout + rejected.stderr
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT status, approved_at, enrollment_token_hash
            FROM account_recovery_requests WHERE id=%s""",
            (recovery_request_id,),
        ).fetchone() == ("pending_verification", None, None)
        assert connection.execute(
            """SELECT count(*) FROM identity_verification_approvals
            WHERE context_type='recovery' AND context_id=%s""",
            (recovery_request_id,),
        ).fetchone() == (0,)

    approved = _run_cli(
        isolated_database_url,
        "init-admin",
        "recover-last-admin",
        "--recovery-request-id",
        str(recovery_request_id),
        input_text="owner-ref-001\noperator-ref-002\n",
    )

    assert approved.returncode == 0
    combined_output = approved.stdout + approved.stderr
    credential_line = next(
        line for line in combined_output.splitlines() if "恢复登记凭据：" in line
    )
    enrollment_token = credential_line.split("恢复登记凭据：", 1)[1].strip()
    assert enrollment_token
    assert "http://" not in combined_output and "https://" not in combined_output
    assert "owner-ref-001" not in combined_output
    assert "operator-ref-002" not in combined_output
    with psycopg.connect(native_url) as connection:
        request = connection.execute(
            """SELECT status, approved_at, enrollment_token_hash,
                      enrollment_expires_at - approved_at
            FROM account_recovery_requests WHERE id=%s""",
            (recovery_request_id,),
        ).fetchone()
        assert request is not None
        assert request[0] == "approved"
        assert request[1] is not None
        assert verify_secret(
            SecretPurpose.RECOVERY_ENROLLMENT,
            secret=enrollment_token,
            digest=str(request[2]),
        )
        assert request[3].total_seconds() == 15 * 60
        approvals = connection.execute(
            """SELECT approver_kind, approver_reference, decision
            FROM identity_verification_approvals
            WHERE context_type='recovery' AND context_id=%s ORDER BY approver_kind""",
            (recovery_request_id,),
        ).fetchall()
        assert approvals == [
            ("operator", "operator-ref-002", "approved"),
            ("owner", "owner-ref-001", "approved"),
        ]
        audit_metadata = connection.execute(
            """SELECT actor_user_id, actor_role_codes, metadata::text FROM audit_events
            WHERE event_code='identity.recovery_approved' AND resource_id=%s""",
            (recovery_request_id,),
        ).fetchone()
        assert audit_metadata == (None, [], "{}")

    replay = _run_cli(
        isolated_database_url,
        "init-admin",
        "recover-last-admin",
        "--recovery-request-id",
        str(recovery_request_id),
        input_text="owner-ref-001\noperator-ref-002\n",
    )
    assert replay.returncode != 0
    assert enrollment_token not in replay.stdout + replay.stderr
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM identity_verification_approvals
            WHERE context_type='recovery' AND context_id=%s""",
            (recovery_request_id,),
        ).fetchone() == (2,)


def test_recover_last_admin_rejects_when_another_active_admin_exists(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery_request_id, _user_id = _prepare_last_admin_recovery(isolated_database_url, monkeypatch)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    second_admin_id = uuid4()
    with psycopg.connect(native_url) as connection:
        kindergarten = connection.execute("SELECT id FROM kindergartens").fetchone()
        admin_role = connection.execute("SELECT id FROM roles WHERE code='admin'").fetchone()
        assert kindergarten is not None
        assert admin_role is not None
        kindergarten_id = kindergarten[0]
        role_id = admin_role[0]
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status, activated_at, created_by, updated_by)
            VALUES (%s,%s,'backup-admin','backup-admin','备用管理员',%s,'active',now(),%s,%s)""",
            (
                second_admin_id,
                kindergarten_id,
                uuid4().bytes,
                second_admin_id,
                second_admin_id,
            ),
        )
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,now())""",
            (kindergarten_id, second_admin_id, role_id, second_admin_id),
        )

    result = _run_cli(
        isolated_database_url,
        "init-admin",
        "recover-last-admin",
        "--recovery-request-id",
        str(recovery_request_id),
        input_text="owner-ref-001\noperator-ref-002\n",
    )

    assert result.returncode != 0
    assert "恢复登记凭据" not in result.stdout + result.stderr
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            "SELECT status FROM account_recovery_requests WHERE id=%s",
            (recovery_request_id,),
        ).fetchone() == ("pending_verification",)
        assert connection.execute(
            """SELECT count(*) FROM identity_verification_approvals
            WHERE context_type='recovery' AND context_id=%s""",
            (recovery_request_id,),
        ).fetchone() == (0,)
