from collections.abc import Iterator

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

REVISION = "0006_lesson_plans"
TABLES = {
    "daily_activity_plans",
    "daily_activity_plan_authors",
    "daily_activity_plan_snapshots",
    "workday_cache",
}


@pytest.fixture
def lesson_plan_database(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def test_0006_follows_backup_authentication_and_is_the_only_head() -> None:
    script = ScriptDirectory.from_config(Config("alembic.ini"))
    revisions = {revision.revision: revision.down_revision for revision in script.walk_revisions()}

    assert revisions[REVISION] == "0005_password_totp_backup_login"
    assert script.get_heads() == [REVISION]


def test_0006_creates_tenant_scoped_plan_snapshot_author_and_cache_tables(
    lesson_plan_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    tables = {
        str(row[0])
        for row in lesson_plan_database.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
        ).fetchall()
    }
    assert tables >= TABLES

    columns = {
        (str(row[0]), str(row[1]))
        for row in lesson_plan_database.execute(
            """SELECT table_name, column_name FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name=ANY(%s)""",
            (list(TABLES),),
        ).fetchall()
    }
    for table in TABLES:
        assert {
            (table, "kindergarten_id"),
            (table, "created_at"),
            (table, "updated_at"),
        } <= columns


def test_database_contains_unique_cas_week_and_unavailable_constraints(
    lesson_plan_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    definitions = " ".join(
        str(row[0])
        for row in lesson_plan_database.execute(
            """SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=current_schema() AND t.relname=ANY(%s)""",
            (list(TABLES),),
        ).fetchall()
    )
    assert "UNIQUE (kindergarten_id, class_id, plan_date)" in definitions
    assert "teaching_week_number" in definitions
    assert "source_code" in definitions and "unavailable" in definitions
