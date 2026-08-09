"""Slice 1 桌面工作区用例门面。"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol

from kindergarten_manager.application.dto import CancellationToken
from kindergarten_manager.application.exports import (
    DailyPlanExportSnapshot,
    DayRenderer,
    ExportService,
)
from kindergarten_manager.application.lesson_plans import LessonPlanEditorState, LessonPlanService
from kindergarten_manager.application.settings import SettingsService
from kindergarten_manager.domain.calendar import activity_date_text, teaching_week
from kindergarten_manager.domain.content import PlanContentV1


class WorkspaceError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass(frozen=True, slots=True)
class ClassContext:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class SetupContextRecord:
    teacher_name: str
    semester_id: int
    semester_name: str
    semester_start_date: date
    semester_end_date: date
    classes: tuple[ClassContext, ...]


@dataclass(frozen=True, slots=True)
class DailyPlanContext:
    classes: tuple[ClassContext, ...]
    selected_class_id: int
    plan_date: date
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlanExportRecord:
    plan_id: int
    content_revision: int
    plan_date: date
    author_name: str
    content_json: str
    class_name: str
    age_group: str
    semester_name: str
    semester_start_date: date
    semester_end_date: date
    kindergarten_name: str


class WorkspaceRepositoryPort(Protocol):
    def load_setup_context(self) -> SetupContextRecord | None: ...

    def get_author_name(self) -> str: ...

    def load_export_record(self, plan_id: int) -> PlanExportRecord | None: ...


class DailyPlanWorkspace:
    """协调设置、当前教案和单日导出的 Application Layer 用例。"""

    def __init__(
        self,
        *,
        settings: SettingsService,
        plans: LessonPlanService,
        repository: WorkspaceRepositoryPort,
        renderer: DayRenderer,
        today: Callable[[], date],
        setup_complete: bool,
    ) -> None:
        self.setup_complete = setup_complete
        self._settings = settings
        self._plans = plans
        self._repository = repository
        self._today = today
        self._current_plan: LessonPlanEditorState | None = None
        self._exports = ExportService(renderer, snapshot_reader=self)

    def complete_setup(self, values: dict[str, str]) -> None:
        self._settings.save_profile(values.get("teacher_name", ""), "system")
        self._settings.save_kindergarten(values.get("kindergarten_name", ""))
        current_date = self._today()
        semester = self._settings.create_or_update_semester(
            semester_id=None,
            name=values.get("semester_name", ""),
            start_date=date(current_date.year, 1, 1),
            end_date=date(current_date.year, 12, 31),
            is_current=True,
        )
        class_view = self._settings.create_or_update_class(
            class_id=None,
            name=values.get("class_name", ""),
            age_group="middle",
        )
        self._current_plan = self._plans.open_or_create(
            class_view.id,
            current_date,
            semester.id,
        )
        self.setup_complete = True

    def load_plan_context(self) -> DailyPlanContext:
        setup = self._required_setup_context()
        selected_class_id = (
            self._current_plan.class_id if self._current_plan is not None else setup.classes[0].id
        )
        selected_date = (
            self._current_plan.plan_date if self._current_plan is not None else self._today()
        )
        return self.select_plan_context(selected_class_id, selected_date)

    def select_plan_context(self, class_id: int, plan_date: date) -> DailyPlanContext:
        setup = self._required_setup_context()
        if class_id not in {item.id for item in setup.classes}:
            raise WorkspaceError("plan.invalid_context", "所选班级不存在")
        self._current_plan = self._plans.open_or_create(
            class_id,
            plan_date,
            setup.semester_id,
        )
        return DailyPlanContext(
            classes=setup.classes,
            selected_class_id=class_id,
            plan_date=plan_date,
            warnings=self._current_plan.warnings,
        )

    def load_current_plan(self) -> dict[str, Any]:
        if not self.setup_complete:
            return PlanContentV1.empty().model_dump()
        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        return self._current_plan.content.model_dump()

    def save_current_plan(self, content: dict[str, Any]) -> None:
        normalized = PlanContentV1.model_validate(content)
        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        saved = self._plans.save_version(
            self._current_plan.id,
            self._current_plan.content_revision,
            normalized,
        )
        self._current_plan = replace(
            self._current_plan,
            content=normalized,
            content_revision=saved.content_revision,
        )

    def suggested_export_filename(self) -> str:
        current_date = self._current_plan.plan_date if self._current_plan else self._today()
        setup = self._required_setup_context()
        class_id = self._current_plan.class_id if self._current_plan else setup.classes[0].id
        class_name = next(item.name for item in setup.classes if item.id == class_id)
        return f"一日活动计划-{_filename_part(class_name)}-{current_date.isoformat()}.docx"

    def export_current_day(self, destination: Path) -> None:
        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "没有可导出的当天教案")
        snapshot = self._exports.prepare_single(self._current_plan.id)
        self._exports.export_single(snapshot, destination, CancellationToken())

    def load_export_snapshot(self, plan_id: int) -> DailyPlanExportSnapshot | None:
        record = self._repository.load_export_record(plan_id)
        if record is None:
            return None
        content = PlanContentV1.model_validate(json.loads(record.content_json))
        calendar_week = teaching_week(
            record.plan_date,
            record.semester_start_date,
            record.semester_end_date,
        )
        canonical = content.canonical_json()
        return DailyPlanExportSnapshot(
            plan_id=record.plan_id,
            content_revision=record.content_revision,
            plan_date=record.plan_date,
            teaching_week_text=calendar_week.text or "",
            activity_date_text=activity_date_text(record.plan_date),
            semester_name=record.semester_name,
            semester_start_date=record.semester_start_date,
            semester_end_date=record.semester_end_date,
            kindergarten_name=record.kindergarten_name,
            class_name=record.class_name,
            age_group=record.age_group,
            author_name=record.author_name,
            content=content,
            content_sha256=sha256(canonical.encode()).hexdigest(),
        )

    def _required_setup_context(self) -> SetupContextRecord:
        setup = self._repository.load_setup_context()
        if setup is None or not setup.classes:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        return setup


def _filename_part(value: str) -> str:
    forbidden = '<>:"/\\|?*'
    cleaned = "".join(
        "_" if character in forbidden or ord(character) < 32 else character for character in value
    )
    return cleaned.strip(" .") or "未命名班级"
