"""首次设置应用用例。"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import date
from typing import Protocol


class SettingsError(ValueError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass(frozen=True, slots=True)
class SettingsView:
    teacher_display_name: str
    theme: str


@dataclass(frozen=True, slots=True)
class KindergartenView:
    name: str
    timezone: str


@dataclass(frozen=True, slots=True)
class SemesterView:
    id: int
    name: str
    start_date: date
    end_date: date
    is_current: bool


@dataclass(frozen=True, slots=True)
class ClassView:
    id: int
    name: str
    age_group: str
    indoor_areas: tuple[str, ...] = ()
    outdoor_areas: tuple[str, ...] = ()


class SettingsRepositoryPort(Protocol):
    def transaction(self) -> AbstractContextManager[None]: ...

    def upsert_profile(
        self, teacher_name: str, theme: str, now_utc_ms: int
    ) -> dict[str, object]: ...

    def upsert_kindergarten(self, name: str, now_utc_ms: int) -> dict[str, object]: ...

    def upsert_semester(self, values: dict[str, object]) -> dict[str, object]: ...

    def upsert_class(self, values: dict[str, object]) -> dict[str, object]: ...

    def replace_class_areas(
        self,
        class_id: int,
        indoor: tuple[str, ...],
        outdoor: tuple[str, ...],
        now_utc_ms: int,
    ) -> dict[str, object]: ...


class SettingsService:
    def __init__(
        self,
        repository: SettingsRepositoryPort,
        *,
        now_utc_ms: Callable[[], int],
    ) -> None:
        self.repository = repository
        self.now_utc_ms = now_utc_ms

    def save_profile(self, teacher_display_name: str, theme: str) -> SettingsView:
        teacher_name = _required_text(teacher_display_name, maximum=50, label="教师姓名")
        if theme not in {"system", "light", "dark"}:
            raise SettingsError("settings.invalid_theme", "主题设置无效")
        with self.repository.transaction():
            saved = self.repository.upsert_profile(teacher_name, theme, self.now_utc_ms())
        return SettingsView(
            teacher_display_name=str(saved["teacher_display_name"]),
            theme=str(saved["theme"]),
        )

    def save_kindergarten(self, name: str) -> KindergartenView:
        normalized = _required_text(name, maximum=100, label="幼儿园名称")
        with self.repository.transaction():
            saved = self.repository.upsert_kindergarten(normalized, self.now_utc_ms())
        return KindergartenView(name=str(saved["name"]), timezone=str(saved["timezone"]))

    def create_or_update_semester(
        self,
        *,
        semester_id: int | None,
        name: str,
        start_date: date,
        end_date: date,
        is_current: bool,
    ) -> SemesterView:
        normalized = _required_text(name, maximum=100, label="学期名称")
        if end_date < start_date:
            raise SettingsError("settings.invalid_semester_dates", "学期结束日期不能早于开始日期")
        values: dict[str, object] = {
            "id": semester_id,
            "name": normalized,
            "start_date": start_date,
            "end_date": end_date,
            "is_current": is_current,
            "now_utc_ms": self.now_utc_ms(),
        }
        with self.repository.transaction():
            saved = self.repository.upsert_semester(values)
        return _semester_view(saved)

    def create_or_update_class(
        self,
        *,
        class_id: int | None,
        name: str,
        age_group: str,
    ) -> ClassView:
        normalized = _required_text(name, maximum=50, label="班级名称")
        if age_group not in {"nursery", "small", "middle", "large", "mixed"}:
            raise SettingsError("settings.invalid_age_group", "年龄段设置无效")
        values: dict[str, object] = {
            "id": class_id,
            "name": normalized,
            "age_group": age_group,
            "now_utc_ms": self.now_utc_ms(),
        }
        with self.repository.transaction():
            saved = self.repository.upsert_class(values)
        return _class_view(saved)

    def set_class_areas(
        self,
        class_id: int,
        *,
        indoor: tuple[str, ...],
        outdoor: tuple[str, ...],
    ) -> ClassView:
        normalized_indoor = _areas(indoor)
        normalized_outdoor = _areas(outdoor)
        with self.repository.transaction():
            saved = self.repository.replace_class_areas(
                class_id,
                normalized_indoor,
                normalized_outdoor,
                self.now_utc_ms(),
            )
        return _class_view(saved)


def _required_text(value: str, *, maximum: int, label: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise SettingsError("settings.invalid_value", f"{label}不能为空且不能超过 {maximum} 字")
    return normalized


def _areas(values: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(_required_text(value, maximum=50, label="区域名称") for value in values)
    folded = tuple(value.casefold() for value in normalized)
    if len(folded) != len(set(folded)):
        raise SettingsError("settings.duplicate_area", "班级区域不能重复")
    return normalized


def _semester_view(saved: dict[str, object]) -> SemesterView:
    start = saved["start_date"]
    end = saved["end_date"]
    return SemesterView(
        id=int(str(saved["id"])),
        name=str(saved["name"]),
        start_date=start if isinstance(start, date) else date.fromisoformat(str(start)),
        end_date=end if isinstance(end, date) else date.fromisoformat(str(end)),
        is_current=bool(saved["is_current"]),
    )


def _class_view(saved: dict[str, object]) -> ClassView:
    indoor = saved.get("indoor_areas", ())
    outdoor = saved.get("outdoor_areas", ())
    indoor_values = indoor if isinstance(indoor, (tuple, list)) else ()
    outdoor_values = outdoor if isinstance(outdoor, (tuple, list)) else ()
    return ClassView(
        id=int(str(saved["id"])),
        name=str(saved["name"]),
        age_group=str(saved["age_group"]),
        indoor_areas=tuple(str(value) for value in indoor_values),
        outdoor_areas=tuple(str(value) for value in outdoor_values),
    )
