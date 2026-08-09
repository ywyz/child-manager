"""首次设置应用服务接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


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


class SettingsService:
    def __init__(self, repository: object, *, now_utc_ms: object) -> None:
        self.repository = repository
        self.now_utc_ms = now_utc_ms

    def save_profile(self, teacher_display_name: str, theme: str) -> SettingsView:
        raise NotImplementedError("T026 尚未实现教师资料保存")

    def save_kindergarten(self, name: str) -> KindergartenView:
        raise NotImplementedError("T026 尚未实现园所资料保存")

    def create_or_update_semester(
        self,
        *,
        semester_id: int | None,
        name: str,
        start_date: date,
        end_date: date,
        is_current: bool,
    ) -> SemesterView:
        raise NotImplementedError("T026 尚未实现学期保存")

    def create_or_update_class(
        self,
        *,
        class_id: int | None,
        name: str,
        age_group: str,
    ) -> ClassView:
        raise NotImplementedError("T026 尚未实现班级保存")

    def set_class_areas(
        self,
        class_id: int,
        *,
        indoor: tuple[str, ...],
        outdoor: tuple[str, ...],
    ) -> ClassView:
        raise NotImplementedError("T026 尚未实现班级区域保存")
