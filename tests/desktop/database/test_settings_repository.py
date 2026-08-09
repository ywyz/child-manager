from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from kindergarten_manager.application.settings import SettingsError, SettingsService
from kindergarten_manager.infrastructure.database.repositories import SettingsRepository
from kindergarten_manager.infrastructure.database.upgrade import upgrade_database
from tests.desktop.conftest import FixedClock
from tests.desktop.helpers import implemented


def test_sqlite_settings_persist_single_current_semester_and_atomic_areas(
    tmp_path: Path,
    fixed_clock: FixedClock,
) -> None:
    database = tmp_path / "desktop.sqlite3"
    implemented(lambda: upgrade_database(database))
    service = SettingsService(
        SettingsRepository(database),
        now_utc_ms=fixed_clock.now_utc_ms,
    )

    implemented(lambda: service.save_profile("测试教师", "system"))
    implemented(lambda: service.save_kindergarten("星河幼儿园"))
    first = implemented(
        lambda: service.create_or_update_semester(
            semester_id=None,
            name="2026 春季学期",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 6, 30),
            is_current=True,
        )
    )
    second = implemented(
        lambda: service.create_or_update_semester(
            semester_id=None,
            name="2026 秋季学期",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 1, 31),
            is_current=True,
        )
    )
    class_view = implemented(
        lambda: service.create_or_update_class(
            class_id=None,
            name="Sunflower 班",
            age_group="middle",
        )
    )
    implemented(
        lambda: service.set_class_areas(
            class_view.id,
            indoor=("建构区",),
            outdoor=("沙水区",),
        )
    )

    with pytest.raises(SettingsError):
        implemented(
            lambda: service.create_or_update_class(
                class_id=None,
                name="SUNFLOWER 班",
                age_group="middle",
            )
        )
    with pytest.raises(SettingsError):
        implemented(
            lambda: service.set_class_areas(
                class_view.id,
                indoor=("建构区", "建构区"),
                outdoor=("沙水区",),
            )
        )

    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT teacher_display_name, theme FROM app_profile"
        ).fetchall() == [("测试教师", "system")]
        assert connection.execute(
            "SELECT name, timezone FROM kindergarten_settings"
        ).fetchall() == [("星河幼儿园", "Asia/Shanghai")]
        assert connection.execute(
            "SELECT id, is_current FROM semesters ORDER BY id"
        ).fetchall() == [(first.id, 0), (second.id, 1)]
        assert connection.execute(
            "SELECT area_type, name FROM class_areas ORDER BY area_type, sort_order"
        ).fetchall() == [("indoor", "建构区"), ("outdoor", "沙水区")]
