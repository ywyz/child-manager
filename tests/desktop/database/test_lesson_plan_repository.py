from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from kindergarten_manager.application.lesson_plans import LessonPlanError
from kindergarten_manager.domain.content import PlanContentV1
from kindergarten_manager.infrastructure.database.repositories import LessonPlanRepository
from tests.desktop.helpers import implemented


def _database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE class_groups (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE semesters (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE lesson_plans (
                id INTEGER PRIMARY KEY,
                class_id INTEGER NOT NULL REFERENCES class_groups(id) ON DELETE RESTRICT,
                semester_id INTEGER NOT NULL REFERENCES semesters(id) ON DELETE RESTRICT,
                plan_date TEXT NOT NULL,
                author_name TEXT NOT NULL,
                content_schema_version INTEGER NOT NULL CHECK (content_schema_version = 1),
                content_json TEXT NOT NULL,
                content_revision INTEGER NOT NULL CHECK (content_revision >= 1),
                archived_at_utc_ms INTEGER,
                created_at_utc_ms INTEGER NOT NULL,
                updated_at_utc_ms INTEGER NOT NULL,
                CONSTRAINT uq_lesson_plans_class_date UNIQUE (class_id, plan_date)
            );
            INSERT INTO class_groups(id, name) VALUES (1, '向日葵班');
            INSERT INTO semesters(id, name) VALUES (1, '2026 秋季');
            """
        )


def test_repository_enforces_one_current_plan_and_survives_reopen(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    _database(database)
    repository = LessonPlanRepository(database)

    first = implemented(
        lambda: repository.open_or_create(
            class_id=1,
            semester_id=1,
            plan_date=date(2026, 9, 7),
            author_name="测试教师",
            now_utc_ms=1,
        )
    )
    same = implemented(
        lambda: repository.open_or_create(
            class_id=1,
            semester_id=1,
            plan_date=date(2026, 9, 7),
            author_name="另一教师",
            now_utc_ms=2,
        )
    )
    saved = implemented(
        lambda: repository.save_content(
            plan_id=first.id,
            base_revision=first.content_revision,
            content=PlanContentV1(),
            now_utc_ms=3,
        )
    )
    reopened = implemented(
        lambda: LessonPlanRepository(database).open_or_create(
            class_id=1,
            semester_id=1,
            plan_date=date(2026, 9, 7),
            author_name="测试教师",
            now_utc_ms=4,
        )
    )

    assert first.id == same.id == reopened.id
    assert saved.content_revision == reopened.content_revision == 2
    assert reopened.author_name == "测试教师"


def test_repository_rejects_stale_revision_without_changing_content(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    _database(database)
    repository = LessonPlanRepository(database)
    plan = implemented(
        lambda: repository.open_or_create(
            class_id=1,
            semester_id=1,
            plan_date=date(2026, 9, 7),
            author_name="测试教师",
            now_utc_ms=1,
        )
    )

    with pytest.raises(LessonPlanError) as captured:
        implemented(
            lambda: repository.save_content(
                plan_id=plan.id,
                base_revision=plan.content_revision + 1,
                content=PlanContentV1(),
                now_utc_ms=2,
            )
        )

    assert captured.value.error_code == "plan.stale_editor_state"
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT content_revision FROM lesson_plans WHERE id = ?", (plan.id,)
        ).fetchone() == (1,)
