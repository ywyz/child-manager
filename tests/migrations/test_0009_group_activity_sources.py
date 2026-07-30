"""T119 集体活动来源迁移 RED。"""

from collections.abc import Iterator

import psycopg
import pytest
from alembic import command
from alembic.config import Config


@pytest.fixture
def group_activity_source_database(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def _columns(connection: psycopg.Connection[tuple[object, ...]]) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            """SELECT column_name FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name='lesson_plan_sources'"""
        ).fetchall()
    }


def _foreign_keys(
    connection: psycopg.Connection[tuple[object, ...]],
) -> set[tuple[str, str, str]]:
    rows = connection.execute(
        """SELECT target_table.relname,
                 string_agg(source_column.attname, ',' ORDER BY source_key.ordinality),
                 string_agg(target_column.attname, ',' ORDER BY source_key.ordinality)
        FROM pg_constraint AS foreign_key
        JOIN pg_class AS source_table ON source_table.oid=foreign_key.conrelid
        JOIN pg_namespace AS source_namespace ON source_namespace.oid=source_table.relnamespace
        JOIN pg_class AS target_table ON target_table.oid=foreign_key.confrelid
        JOIN unnest(foreign_key.conkey) WITH ORDINALITY AS source_key(attnum, ordinality)
          ON TRUE
        JOIN unnest(foreign_key.confkey) WITH ORDINALITY AS target_key(attnum, ordinality)
          ON target_key.ordinality=source_key.ordinality
        JOIN pg_attribute AS source_column
          ON source_column.attrelid=source_table.oid AND source_column.attnum=source_key.attnum
        JOIN pg_attribute AS target_column
          ON target_column.attrelid=target_table.oid AND target_column.attnum=target_key.attnum
        WHERE foreign_key.contype='f'
          AND source_namespace.nspname=current_schema()
          AND source_table.relname='lesson_plan_sources'
        GROUP BY foreign_key.oid,target_table.relname"""
    ).fetchall()
    return {(str(row[0]), str(row[1]), str(row[2])) for row in rows}


def test_source_table_keeps_only_metadata_and_hash(
    group_activity_source_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    columns = _columns(group_activity_source_database)

    assert {
        "id",
        "kindergarten_id",
        "plan_id",
        "source_type",
        "original_filename",
        "source_sha256",
        "extracted_character_count",
        "extracted_text",
        "uploaded_by",
        "created_at",
        "updated_at",
    } <= columns
    assert "payload" not in columns
    assert "binary_content" not in columns
    assert "absolute_path" not in columns


def test_source_uses_tenant_composite_foreign_keys_for_plan_and_uploader(
    group_activity_source_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    foreign_keys = _foreign_keys(group_activity_source_database)

    assert {
        ("daily_activity_plans", "kindergarten_id,plan_id", "kindergarten_id,id"),
        ("users", "kindergarten_id,uploaded_by", "kindergarten_id,id"),
    } <= foreign_keys
