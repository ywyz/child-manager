from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import sqlalchemy as sa

from kindergarten_manager.infrastructure.database.models import metadata
from kindergarten_manager.infrastructure.database.upgrade import (
    DESKTOP_INITIAL_REVISION,
    upgrade_database,
)
from tests.desktop.helpers import implemented


def _schema_objects(database: Path) -> dict[str, str]:
    with sqlite3.connect(database) as connection:
        return {
            name: sql or ""
            for name, sql in connection.execute(
                "SELECT name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
            )
        }


def test_empty_database_upgrades_idempotently_with_named_integrity_contracts(
    tmp_path: Path,
) -> None:
    database = tmp_path / "desktop.sqlite3"

    first = implemented(lambda: upgrade_database(database))
    second = implemented(lambda: upgrade_database(database))
    objects = _schema_objects(database)

    assert first == second == DESKTOP_INITIAL_REVISION
    assert set(objects) == {
        "alembic_version",
        "app_profile",
        "kindergarten_settings",
        "class_groups",
        "class_areas",
        "semesters",
        "lesson_plans",
        "lesson_plan_versions",
        "calendar_overrides",
        "uq_class_groups_name_nocase",
        "uq_class_areas_class_type_name_nocase",
        "uq_semesters_one_current",
        "uq_lesson_plans_class_date",
        "trg_lesson_plan_versions_immutable_update",
        "trg_lesson_plan_versions_immutable_delete",
    }
    combined_sql = "\n".join(objects.values()).lower()
    for name in (
        "ck_app_profile_singleton",
        "ck_app_profile_theme",
        "ck_kindergarten_settings_singleton",
        "ck_kindergarten_settings_timezone",
        "ck_class_groups_age_group",
        "fk_class_areas_class_id_class_groups",
        "ck_class_areas_area_type",
        "uq_class_groups_name_nocase",
        "uq_class_areas_class_type_name_nocase",
        "ck_semesters_date_range",
        "uq_semesters_one_current",
        "fk_lesson_plans_class_id_class_groups",
        "fk_lesson_plans_semester_id_semesters",
        "uq_lesson_plans_class_date",
        "fk_lesson_plan_versions_plan_id_lesson_plans",
        "trg_lesson_plan_versions_immutable_update",
        "trg_lesson_plan_versions_immutable_delete",
    ):
        assert name in combined_sql
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_INITIAL_REVISION,
        )
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []

    migrations = Path("src/kindergarten_manager/infrastructure/database/migrations")
    assert (migrations / "env.py").is_file()
    assert (migrations / "versions" / "0001_desktop_initial.py").is_file()
    assert "render_as_batch=True" in (migrations / "env.py").read_text(encoding="utf-8")
    assert all(
        ".create_all(" not in source.read_text(encoding="utf-8")
        for source in Path("src/kindergarten_manager").rglob("*.py")
    )


def test_version_rows_are_immutable_at_database_boundary(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    implemented(lambda: upgrade_database(database))

    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "INSERT INTO app_profile VALUES (1, ?, ?, ?, NULL, 1, 1)",
            ("cn.kindergartenmanager.desktop", "测试教师", "system"),
        )
        connection.execute(
            "INSERT INTO kindergarten_settings VALUES (1, ?, ?, 1, 1)",
            ("星河幼儿园", "Asia/Shanghai"),
        )
        class_id = connection.execute(
            "INSERT INTO class_groups("
            "name, age_group, sort_order, is_active, created_at_utc_ms, updated_at_utc_ms"
            ") "
            "VALUES (?, ?, 0, 1, 1, 1) RETURNING id",
            ("向日葵班", "middle"),
        ).fetchone()[0]
        semester_id = connection.execute(
            "INSERT INTO semesters("
            "name, start_date, end_date, is_current, created_at_utc_ms, updated_at_utc_ms"
            ") "
            "VALUES (?, ?, ?, 1, 1, 1) RETURNING id",
            ("2026 秋季", "2026-09-01", "2027-01-31"),
        ).fetchone()[0]
        plan_id = connection.execute(
            "INSERT INTO lesson_plans(class_id, semester_id, plan_date, author_name, "
            "content_schema_version, content_json, content_revision, "
            "created_at_utc_ms, updated_at_utc_ms) "
            "VALUES (?, ?, ?, ?, 1, ?, 1, 1, 1) RETURNING id",
            (class_id, semester_id, "2026-09-07", "测试教师", '{"schema_version":1}'),
        ).fetchone()[0]
        version_id = connection.execute(
            "INSERT INTO lesson_plan_versions(lesson_plan_id, reason, description, author_name, "
            "content_schema_version, content_json, source_revision, created_at_utc_ms) "
            "VALUES (?, ?, NULL, ?, 1, ?, 1, 1) RETURNING id",
            (plan_id, "explicit_save", "测试教师", '{"schema_version":1}'),
        ).fetchone()[0]

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE lesson_plan_versions SET description = 'changed' WHERE id = ?",
                (version_id,),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("DELETE FROM lesson_plan_versions WHERE id = ?", (version_id,))


def test_sqlalchemy_metadata_exposes_named_constraints_and_indexes() -> None:
    constraint_names = {
        constraint.name
        for table in metadata.tables.values()
        for constraint in table.constraints
        if constraint.name is not None
    }
    index_names = {
        index.name
        for table in metadata.tables.values()
        for index in table.indexes
        if index.name is not None
    }

    assert "fk_lesson_plans_class_id_class_groups" in constraint_names
    assert "ck_lesson_plans_revision" in constraint_names
    assert "uq_lesson_plans_class_date" in index_names
    assert "uq_semesters_one_current" in index_names
    assert isinstance(metadata.naming_convention, dict)
    assert sa.ForeignKeyConstraint in {
        type(item) for table in metadata.tables.values() for item in table.constraints
    }
