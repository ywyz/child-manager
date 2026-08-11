from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from datetime import date
from typing import Any

import pytest

from kindergarten_manager.application.settings import SettingsError, SettingsService
from tests.desktop.conftest import FictionalBusinessData, FixedClock
from tests.desktop.helpers import implemented


class RecordingSettingsRepository:
    def __init__(self) -> None:
        self.state: dict[str, Any] = {
            "profile": None,
            "kindergarten": None,
            "semesters": {},
            "classes": {},
            "areas": {},
        }
        self.fail_on_area_replace = False

    @contextmanager
    def transaction(self) -> Iterator[None]:
        before = deepcopy(self.state)
        try:
            yield
        except Exception:
            self.state = before
            raise

    def upsert_profile(self, teacher_name: str, theme: str, now_utc_ms: int) -> dict[str, Any]:
        self.state["profile"] = (teacher_name, theme, now_utc_ms)
        return {"teacher_display_name": teacher_name, "theme": theme}

    def upsert_kindergarten(self, name: str, now_utc_ms: int) -> dict[str, Any]:
        self.state["kindergarten"] = (name, "Asia/Shanghai", now_utc_ms)
        return {"name": name, "timezone": "Asia/Shanghai"}

    def upsert_semester(self, values: dict[str, Any]) -> dict[str, Any]:
        semester_id = values.get("id") or (len(self.state["semesters"]) + 1)
        if values["is_current"]:
            for semester in self.state["semesters"].values():
                semester["is_current"] = False
        saved = {**values, "id": semester_id}
        self.state["semesters"][semester_id] = saved
        return saved

    def upsert_class(self, values: dict[str, Any]) -> dict[str, Any]:
        class_id = values.get("id") or (len(self.state["classes"]) + 1)
        saved = {**values, "id": class_id}
        self.state["classes"][class_id] = saved
        return saved

    def replace_class_areas(
        self,
        class_id: int,
        indoor: tuple[str, ...],
        outdoor: tuple[str, ...],
        now_utc_ms: int,
    ) -> dict[str, Any]:
        self.state["areas"][class_id] = (indoor, outdoor, now_utc_ms)
        if self.fail_on_area_replace:
            raise RuntimeError("synthetic area write failure")
        saved = dict(self.state["classes"][class_id])
        saved.update(indoor_areas=indoor, outdoor_areas=outdoor)
        return saved


def _service(repository: RecordingSettingsRepository, clock: FixedClock) -> SettingsService:
    return SettingsService(repository, now_utc_ms=clock.now_utc_ms)


def test_minimum_first_run_settings_are_trimmed_and_saved_per_aggregate(
    fictional_business_data: FictionalBusinessData,
    fixed_clock: FixedClock,
) -> None:
    repository = RecordingSettingsRepository()
    service = _service(repository, fixed_clock)

    profile = implemented(
        lambda: service.save_profile(f"  {fictional_business_data.teacher_name}  ", "system")
    )
    kindergarten = implemented(
        lambda: service.save_kindergarten(f"  {fictional_business_data.kindergarten_name}  ")
    )
    semester = implemented(
        lambda: service.create_or_update_semester(
            semester_id=None,
            name=fictional_business_data.semester_name,
            start_date=date(2026, 9, 1),
            end_date=date(2027, 1, 31),
            is_current=True,
        )
    )
    class_view = implemented(
        lambda: service.create_or_update_class(
            class_id=None,
            name=fictional_business_data.class_name,
            age_group="middle",
        )
    )
    with_areas = implemented(
        lambda: service.set_class_areas(
            class_view.id,
            indoor=fictional_business_data.indoor_areas,
            outdoor=fictional_business_data.outdoor_areas,
        )
    )

    assert profile.teacher_display_name == fictional_business_data.teacher_name
    assert kindergarten.timezone == "Asia/Shanghai"
    assert semester.is_current is True
    assert with_areas.indoor_areas == fictional_business_data.indoor_areas


@pytest.mark.parametrize(
    "action",
    [
        lambda service: service.save_profile("   ", "system"),
        lambda service: service.save_kindergarten(""),
        lambda service: service.create_or_update_semester(
            semester_id=None,
            name="反向学期",
            start_date=date(2027, 1, 1),
            end_date=date(2026, 1, 1),
            is_current=True,
        ),
        lambda service: service.create_or_update_class(
            class_id=None,
            name="测试班",
            age_group="unknown",
        ),
    ],
)
def test_invalid_first_run_values_are_rejected(
    action: Any,
    fixed_clock: FixedClock,
) -> None:
    service = _service(RecordingSettingsRepository(), fixed_clock)
    with pytest.raises(SettingsError):
        implemented(lambda: action(service))


def test_area_failure_rolls_back_whole_aggregate(fixed_clock: FixedClock) -> None:
    repository = RecordingSettingsRepository()
    service = _service(repository, fixed_clock)
    repository.state["classes"][1] = {"id": 1, "name": "向日葵班", "age_group": "middle"}
    before = deepcopy(repository.state)
    repository.fail_on_area_replace = True

    with pytest.raises(RuntimeError, match="synthetic"):
        implemented(
            lambda: service.set_class_areas(
                1,
                indoor=("建构区",),
                outdoor=("沙水区",),
            )
        )

    assert repository.state == before
