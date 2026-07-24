from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

SETTINGS_REVISION = "0004_settings"
SETTINGS_TABLES = {"age_groups", "classes", "class_teachers", "semesters", "class_areas"}


@pytest.fixture
def settings_database(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def test_settings_revision_follows_passkey_contract() -> None:
    revisions = {
        revision.revision: revision.down_revision
        for revision in ScriptDirectory.from_config(Config("alembic.ini")).walk_revisions()
    }
    assert revisions.get(SETTINGS_REVISION) == "0003_passkey_contract"


def test_settings_migration_creates_the_five_tenant_scoped_tables(
    settings_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    tables = {
        str(row[0])
        for row in settings_database.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
        ).fetchall()
    }
    assert tables >= SETTINGS_TABLES

    columns = {
        (str(row[0]), str(row[1]))
        for row in settings_database.execute(
            """SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name=ANY(%s)""",
            (list(SETTINGS_TABLES),),
        ).fetchall()
    }
    for table in SETTINGS_TABLES:
        assert {
            (table, "kindergarten_id"),
            (table, "created_at"),
            (table, "updated_at"),
        } <= columns


def test_age_group_seed_is_fixed_and_idempotent(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "0003_passkey_contract")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, '种子测试园')",
            (uuid4(),),
        )
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    with psycopg.connect(native_url) as connection:
        exists = connection.execute("SELECT to_regclass('age_groups')").fetchone()
        rows = (
            connection.execute(
                "SELECT code, name, sort_order FROM age_groups ORDER BY sort_order"
            ).fetchall()
            if exists is not None and exists[0] is not None
            else []
        )
    assert rows == [
        ("toddler", "托班", 0),
        ("small", "小班", 1),
        ("middle", "中班", 2),
        ("large", "大班", 3),
    ]


def test_postgresql_enforces_semester_and_lead_teacher_uniqueness(
    settings_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    constraints = [
        (str(row[0]), str(row[1]))
        for row in settings_database.execute(
            """SELECT relation.relname, pg_get_constraintdef(constraint_row.oid)
            FROM pg_constraint AS constraint_row
            JOIN pg_class AS relation ON relation.oid=constraint_row.conrelid
            JOIN pg_namespace AS namespace ON namespace.oid=relation.relnamespace
            WHERE namespace.nspname=current_schema()
              AND relation.relname=ANY(%s)""",
            (list(SETTINGS_TABLES),),
        ).fetchall()
    ]
    indexes = [
        (str(row[0]), str(row[1]))
        for row in settings_database.execute(
            """SELECT tablename, indexdef FROM pg_indexes
            WHERE schemaname=current_schema() AND tablename=ANY(%s)""",
            (list(SETTINGS_TABLES),),
        ).fetchall()
    ]

    assert any(
        table == "semesters"
        and definition.startswith("CHECK")
        and "start_date <= end_date" in definition
        for table, definition in constraints
    )
    assert any(
        table == "semesters"
        and "EXCLUDE USING gist" in definition
        and "daterange(start_date, end_date, '[]'::text)" in definition
        for table, definition in constraints
    )
    assert any(
        table == "semesters"
        and "UNIQUE" in definition
        and "(kindergarten_id)" in definition
        and "WHERE is_current" in definition
        for table, definition in indexes
    )
    assert any(
        table == "class_teachers"
        and "UNIQUE" in definition
        and "(kindergarten_id, class_id)" in definition
        and "WHERE is_lead_teacher" in definition
        for table, definition in indexes
    )


def test_area_constraints_allow_empty_collections_but_reject_duplicate_names(
    settings_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    constraints = [
        str(row[0])
        for row in settings_database.execute(
            """SELECT pg_get_constraintdef(constraint_row.oid)
            FROM pg_constraint AS constraint_row
            JOIN pg_class AS relation ON relation.oid=constraint_row.conrelid
            JOIN pg_namespace AS namespace ON namespace.oid=relation.relnamespace
            WHERE namespace.nspname=current_schema() AND relation.relname='class_areas'"""
        ).fetchall()
    ]
    assert any("area_type" in definition and "indoor" in definition for definition in constraints)
    assert any("sort_order >= 0" in definition for definition in constraints)
    assert any(
        "UNIQUE (kindergarten_id, class_id, area_type, name_normalized)" in definition
        for definition in constraints
    )


def test_settings_relations_use_composite_tenant_foreign_keys(
    settings_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    constraints = [
        (str(row[0]), str(row[1]))
        for row in settings_database.execute(
            """SELECT relation.relname, pg_get_constraintdef(constraint_row.oid)
            FROM pg_constraint AS constraint_row
            JOIN pg_class AS relation ON relation.oid=constraint_row.conrelid
            JOIN pg_namespace AS namespace ON namespace.oid=relation.relnamespace
            WHERE namespace.nspname=current_schema()
              AND relation.relname=ANY(%s)
              AND constraint_row.contype='f'""",
            (list(SETTINGS_TABLES),),
        ).fetchall()
    ]
    expected_relations = {
        ("classes", "FOREIGN KEY (kindergarten_id, age_group_id)"),
        ("class_teachers", "FOREIGN KEY (kindergarten_id, class_id)"),
        ("class_teachers", "FOREIGN KEY (kindergarten_id, user_id)"),
        ("class_areas", "FOREIGN KEY (kindergarten_id, class_id)"),
    }
    for table, foreign_key in expected_relations:
        assert any(
            actual_table == table and foreign_key in definition
            for actual_table, definition in constraints
        )
