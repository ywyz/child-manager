from collections.abc import Iterator

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

REVISION = "0007_ai_prompts_jobs"
TABLES = {
    "ai_model_profiles",
    "ai_model_profile_capabilities",
    "prompt_definitions",
    "prompt_versions",
    "background_jobs",
    "prompt_test_runs",
}


@pytest.fixture
def m4_database(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def test_0007_follows_lesson_plans() -> None:
    script = ScriptDirectory.from_config(Config("alembic.ini"))
    revisions = {revision.revision: revision.down_revision for revision in script.walk_revisions()}

    assert revisions[REVISION] == "0006_lesson_plans"


def test_0007_creates_all_tenant_scoped_ai_prompt_and_job_tables(
    m4_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    tables = {
        str(row[0])
        for row in m4_database.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
        ).fetchall()
    }
    assert tables >= TABLES
    columns = {
        (str(row[0]), str(row[1]), str(row[2]))
        for row in m4_database.execute(
            """SELECT table_name, column_name, is_nullable
            FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name=ANY(%s)""",
            (list(TABLES),),
        ).fetchall()
    }
    for table in TABLES:
        assert (table, "kindergarten_id", "NO") in columns
        assert (table, "created_at", "NO") in columns
        assert (table, "updated_at", "NO") in columns


def test_model_revision_and_prompt_run_frozen_context_are_database_enforced(
    m4_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    column_names = {
        str(row[0])
        for row in m4_database.execute(
            """SELECT column_name FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name='prompt_test_runs'"""
        ).fetchall()
    }
    assert {
        "input_context",
        "input_sha256",
        "prompt_content",
        "prompt_content_sha256",
        "result_schema_code",
        "result_schema_version",
        "model_call_snapshot",
        "input_summary",
    } <= column_names
    assert (
        not {
            "api_key",
            "api_key_ciphertext",
            "api_key_nonce",
            "api_key_key_id",
        }
        & column_names
    )

    definitions = " ".join(
        str(row[0])
        for row in m4_database.execute(
            """SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=current_schema()
              AND t.relname IN ('ai_model_profiles','prompt_test_runs','background_jobs')"""
        ).fetchall()
    )
    assert "call_config_revision >= 1" in definitions
    assert "model_call_snapshot" in definitions
    assert "prompt_test_runs" in definitions or "FOREIGN KEY" in definitions


def test_background_job_batch_and_execution_attempt_constraints_are_frozen(
    m4_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    definitions = " ".join(
        str(row[0])
        for row in m4_database.execute(
            """SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=current_schema() AND t.relname='background_jobs'"""
        ).fetchall()
    )
    for job_type in (
        "ai.batch",
        "ai.morning_activity",
        "ai.morning_talk",
        "ai.group_activity_split",
        "ai.group_activity_add_step",
        "ai.indoor_area_game",
        "ai.afternoon_outdoor_game",
        "ai.daily_reflection",
        "prompt.test",
        "word.export",
    ):
        assert job_type in definitions
    assert "ai.section" not in definitions
    assert "attempt_count IS NULL" in definitions
    assert "max_attempts IS NULL" in definitions
    assert "max_attempts = 3" in definitions
    assert "parent_job_id" in definitions
    assert "retry_of_job_id" in definitions


def test_model_activation_and_job_terminal_invariants_are_database_enforced(
    m4_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    constraints = {
        str(row[0]): str(row[1])
        for row in m4_database.execute(
            """SELECT c.conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=current_schema()
              AND t.relname IN ('ai_model_profiles','background_jobs')"""
        ).fetchall()
    }
    assert "risk_confirmed_by IS NULL" in constraints["ck_ai_model_profiles_risk_confirmation"]
    assert "risk_confirmed_at IS NULL" in constraints["ck_ai_model_profiles_risk_confirmation"]
    assert "risk_confirmed_by IS NOT NULL" in constraints["ck_ai_model_profiles_enable_ready"]
    key_envelope = constraints["ck_ai_model_profiles_key_envelope"]
    assert "api_key_nonce IS NOT NULL" in key_envelope
    assert "api_key_encryption_version IS NOT NULL" in key_envelope
    assert "finished_at IS NOT NULL" in constraints["ck_background_jobs_terminal_finished"]
    assert "error_code IS NOT NULL" in constraints["ck_background_jobs_failure_error"]
    assert (
        "requested_resource_version > 0"
        in constraints["ck_background_jobs_requested_resource_version"]
    )
    assert "parent_job_id <> id" in constraints["ck_background_jobs_parent_not_self"]
    assert "retry_of_job_id <> id" in constraints["ck_background_jobs_retry_not_self"]

    default_index = m4_database.execute(
        """SELECT pg_get_indexdef(i.indexrelid)
        FROM pg_index i
        JOIN pg_class idx ON idx.oid=i.indexrelid
        JOIN pg_namespace n ON n.oid=idx.relnamespace
        WHERE n.nspname=current_schema() AND idx.relname='uq_ai_model_profiles_default'"""
    ).fetchone()
    assert default_index is not None
    assert "is_default AND is_active" in str(default_index[0])

    prompt_constraints = {
        str(row[0]): str(row[1])
        for row in m4_database.execute(
            """SELECT c.conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=current_schema()
              AND t.relname IN ('prompt_versions','prompt_test_runs')"""
        ).fetchall()
    }
    assert "published_by IS NOT NULL" in prompt_constraints["ck_prompt_versions_publication"]
    assert "output_content IS NOT NULL" in prompt_constraints["ck_prompt_test_runs_outcome"]
    assert "error_code IS NOT NULL" in prompt_constraints["ck_prompt_test_runs_outcome"]
    assert (
        "model_call_snapshot - ARRAY"
        in prompt_constraints["ck_prompt_test_runs_model_call_snapshot"]
    )
    assert "input_summary - ARRAY" in prompt_constraints["ck_prompt_test_runs_input_summary"]


def test_migration_seeds_exactly_seven_system_versions_per_existing_kindergarten(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "0006_lesson_plans")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES "
            "('01900000-0000-7000-8000-000000000001','迁移种子测试园')"
        )
    command.upgrade(config, REVISION)
    with psycopg.connect(native_url) as connection:
        assert connection.execute("SELECT count(*) FROM prompt_definitions").fetchone() == (7,)
        assert connection.execute(
            """SELECT count(*) FROM prompt_versions
            WHERE source_type='system' AND lifecycle_state='published'"""
        ).fetchone() == (7,)
        assert connection.execute(
            "SELECT count(DISTINCT content_sha256) FROM prompt_versions"
        ).fetchone() == (7,)
