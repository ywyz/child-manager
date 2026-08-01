"""T129 Word 导出迁移与数据库不变量 RED。"""

from collections.abc import Iterator

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

REVISION = "0010_word_exports"
TABLE = "daily_activity_plan_exports"
REQUIRED_COLUMNS = {
    "id",
    "kindergarten_id",
    "plan_id",
    "plan_version",
    "snapshot_id",
    "job_id",
    "status",
    "display_filename",
    "storage_key",
    "context_snapshot",
    "content_snapshot",
    "content_schema_version",
    "content_sha256",
    "file_size",
    "file_sha256",
    "template_code",
    "template_filename",
    "template_sha256",
    "exported_by",
    "exported_at",
    "error_code",
    "error_summary",
    "file_missing_at",
    "created_at",
    "updated_at",
}


@pytest.fixture
def word_export_database(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def test_0010_follows_group_activity_sources() -> None:
    script = ScriptDirectory.from_config(Config("alembic.ini"))
    revisions = {revision.revision: revision.down_revision for revision in script.walk_revisions()}

    assert REVISION in revisions, "T129 尚未增加 0010_word_exports 迁移"
    assert revisions[REVISION] == "0009_group_activity_sources"


def test_export_table_has_frozen_input_and_long_term_history_columns(
    word_export_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    columns = {
        str(row[0])
        for row in word_export_database.execute(
            """SELECT column_name FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name=%s""",
            (TABLE,),
        ).fetchall()
    }

    assert columns >= REQUIRED_COLUMNS
    assert not {"absolute_path", "file_content", "deleted_at", "expires_at"} & columns


def test_export_uses_same_tenant_composite_foreign_keys(
    word_export_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    rows = word_export_database.execute(
        """SELECT target.relname,
                  string_agg(source_column.attname, ',' ORDER BY source_key.ordinality),
                  string_agg(target_column.attname, ',' ORDER BY source_key.ordinality)
        FROM pg_constraint AS foreign_key
        JOIN pg_class AS source ON source.oid=foreign_key.conrelid
        JOIN pg_namespace AS namespace ON namespace.oid=source.relnamespace
        JOIN pg_class AS target ON target.oid=foreign_key.confrelid
        JOIN unnest(foreign_key.conkey) WITH ORDINALITY AS source_key(attnum, ordinality)
          ON TRUE
        JOIN unnest(foreign_key.confkey) WITH ORDINALITY AS target_key(attnum, ordinality)
          ON target_key.ordinality=source_key.ordinality
        JOIN pg_attribute AS source_column
          ON source_column.attrelid=source.oid AND source_column.attnum=source_key.attnum
        JOIN pg_attribute AS target_column
          ON target_column.attrelid=target.oid AND target_column.attnum=target_key.attnum
        WHERE foreign_key.contype='f' AND namespace.nspname=current_schema()
          AND source.relname=%s
        GROUP BY foreign_key.oid,target.relname""",
        (TABLE,),
    ).fetchall()
    foreign_keys = {(str(row[0]), str(row[1]), str(row[2])) for row in rows}

    assert (
        "daily_activity_plans",
        "kindergarten_id,plan_id",
        "kindergarten_id,id",
    ) in foreign_keys
    assert (
        "background_jobs",
        "kindergarten_id,plan_id,job_id",
        "kindergarten_id,plan_id,id",
    ) in foreign_keys
    assert ("users", "kindergarten_id,exported_by", "kindergarten_id,id") in foreign_keys
    assert (
        "daily_activity_plan_snapshots",
        "kindergarten_id,plan_id,snapshot_id",
        "kindergarten_id,plan_id,id",
    ) in foreign_keys


def test_export_status_uniqueness_and_success_failure_shapes_are_database_enforced(
    word_export_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    constraints = "\n".join(
        str(row[0])
        for row in word_export_database.execute(
            """SELECT pg_get_constraintdef(constraint_row.oid)
            FROM pg_constraint AS constraint_row
            JOIN pg_class AS table_row ON table_row.oid=constraint_row.conrelid
            JOIN pg_namespace AS namespace ON namespace.oid=table_row.relnamespace
            WHERE namespace.nspname=current_schema() AND table_row.relname=%s""",
            (TABLE,),
        ).fetchall()
    )
    indexes = "\n".join(
        str(row[0])
        for row in word_export_database.execute(
            """SELECT indexdef FROM pg_indexes
            WHERE schemaname=current_schema() AND tablename=%s""",
            (TABLE,),
        ).fetchall()
    )

    for value in ("pending", "succeeded", "failed"):
        assert value in constraints
    assert "file_size" in constraints and "file_sha256" in constraints
    assert "error_code" in constraints and "exported_at" in constraints
    assert "storage_key" in indexes and "job_id" in indexes
    assert "context_snapshot <> '{}'::jsonb" in constraints
    assert "content_snapshot <> '{}'::jsonb" in constraints

    trigger = word_export_database.execute(
        """SELECT pg_get_triggerdef(trigger_row.oid)
        FROM pg_trigger AS trigger_row
        JOIN pg_class AS table_row ON table_row.oid=trigger_row.tgrelid
        WHERE table_row.relname=%s AND NOT trigger_row.tgisinternal
          AND pg_get_triggerdef(trigger_row.oid) ILIKE '%%job_type%%'""",
        (TABLE,),
    ).fetchone()
    assert trigger is not None


def test_0010_can_downgrade_to_0009_and_upgrade_again(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, REVISION)
    command.downgrade(config, "0009_group_activity_sources")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute("SELECT to_regclass(%s)", (TABLE,)).fetchone() == (None,)
    command.upgrade(config, REVISION)
    with psycopg.connect(native_url) as connection:
        assert connection.execute("SELECT to_regclass(%s)", (TABLE,)).fetchone() == (TABLE,)
