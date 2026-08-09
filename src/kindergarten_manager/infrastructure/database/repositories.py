"""Slice 1 具体 SQLite Repository 接口；行为在 GREEN 实现。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from kindergarten_manager.application.lesson_plans import LessonPlanEditorState, SaveResult
from kindergarten_manager.domain.content import PlanContentV1


class SettingsRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def transaction(self) -> object:
        raise NotImplementedError("T025 尚未实现 SQLite 设置事务")

    def upsert_profile(self, teacher_name: str, theme: str, now_utc_ms: int) -> dict[str, object]:
        raise NotImplementedError("T025 尚未实现 SQLite 教师资料保存")

    def upsert_kindergarten(self, name: str, now_utc_ms: int) -> dict[str, object]:
        raise NotImplementedError("T025 尚未实现 SQLite 园所资料保存")

    def upsert_semester(self, values: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("T025 尚未实现 SQLite 学期保存")

    def upsert_class(self, values: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("T025 尚未实现 SQLite 班级保存")

    def replace_class_areas(
        self,
        class_id: int,
        indoor: tuple[str, ...],
        outdoor: tuple[str, ...],
        now_utc_ms: int,
    ) -> dict[str, object]:
        raise NotImplementedError("T025 尚未实现 SQLite 班级区域保存")


class LessonPlanRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def open_or_create(
        self,
        *,
        class_id: int,
        semester_id: int,
        plan_date: date,
        author_name: str,
        now_utc_ms: int,
    ) -> LessonPlanEditorState:
        raise NotImplementedError("T025 尚未实现 SQLite 教案读取")

    def save_content(
        self,
        *,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        now_utc_ms: int,
    ) -> SaveResult:
        raise NotImplementedError("T025 尚未实现 SQLite 教案保存")
