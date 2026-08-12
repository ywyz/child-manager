"""Slice 1 桌面工作区用例门面。"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol

from kindergarten_manager.application.ai_generation import AdoptedContent
from kindergarten_manager.application.dto import CancellationToken
from kindergarten_manager.application.exports import (
    DailyPlanExportSnapshot,
    DayRenderer,
    ExportService,
)
from kindergarten_manager.application.lesson_plans import LessonPlanEditorState, LessonPlanService
from kindergarten_manager.application.settings import SettingsError, SettingsService
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
    theme: str
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
    today: date
    warnings: tuple[str, ...] = ()
    teaching_week_text: str = ""


@dataclass(frozen=True, slots=True)
class DesktopSettingsContext:
    theme: str
    semester_name: str
    semester_start_date: date
    semester_end_date: date


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

    def load_tool_plan(self, plan_id: int) -> dict[str, object] | None: ...

    def load_tool_context(self, plan_id: int) -> dict[str, object] | None: ...

    def load_tool_semester(self, semester_id: int) -> tuple[date, date] | None: ...

    def load_tool_class_areas(self, class_id: int) -> tuple[dict[str, object], ...]: ...


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
        try:
            semester_start = date.fromisoformat(values.get("semester_start_date", ""))
            semester_end = date.fromisoformat(values.get("semester_end_date", ""))
        except ValueError as error:
            raise SettingsError(
                "settings.invalid_semester_dates",
                "请选择有效的学期开始日期和结束日期",
            ) from error
        if semester_end < semester_start:
            raise SettingsError(
                "settings.invalid_semester_dates",
                "学期结束日期不能早于开始日期",
            )
        self._settings.save_profile(values.get("teacher_name", ""), "system")
        self._settings.save_kindergarten(values.get("kindergarten_name", ""))
        current_date = self._today()
        semester = self._settings.create_or_update_semester(
            semester_id=None,
            name=values.get("semester_name", ""),
            start_date=semester_start,
            end_date=semester_end,
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

    def load_settings(self) -> DesktopSettingsContext:
        setup = self._required_setup_context()
        return DesktopSettingsContext(
            theme=setup.theme,
            semester_name=setup.semester_name,
            semester_start_date=setup.semester_start_date,
            semester_end_date=setup.semester_end_date,
        )

    def update_settings(self, values: dict[str, str]) -> DesktopSettingsContext:
        theme = values.get("theme", "")
        if theme not in {"system", "light", "dark"}:
            raise SettingsError("settings.invalid_theme", "主题设置无效")
        try:
            semester_start = date.fromisoformat(values.get("semester_start_date", ""))
            semester_end = date.fromisoformat(values.get("semester_end_date", ""))
        except ValueError as error:
            raise SettingsError(
                "settings.invalid_semester_dates",
                "请选择有效的学期开始日期和结束日期",
            ) from error
        setup = self._required_setup_context()
        semester = self._settings.create_or_update_semester(
            semester_id=setup.semester_id,
            name=values.get("semester_name", ""),
            start_date=semester_start,
            end_date=semester_end,
            is_current=True,
        )
        profile = self._settings.save_profile(setup.teacher_name, theme)
        return DesktopSettingsContext(
            theme=profile.theme,
            semester_name=semester.name,
            semester_start_date=semester.start_date,
            semester_end_date=semester.end_date,
        )

    def select_plan_context(self, class_id: int, plan_date: date) -> DailyPlanContext:
        setup = self._required_setup_context()
        if class_id not in {item.id for item in setup.classes}:
            raise WorkspaceError("plan.invalid_context", "所选班级不存在")
        self._current_plan = self._plans.open_or_create(
            class_id,
            plan_date,
            setup.semester_id,
        )
        calendar_week = teaching_week(
            plan_date,
            setup.semester_start_date,
            setup.semester_end_date,
        )
        return DailyPlanContext(
            classes=setup.classes,
            selected_class_id=class_id,
            plan_date=plan_date,
            today=self._today(),
            warnings=self._current_plan.warnings,
            teaching_week_text=calendar_week.text or "",
        )

    def load_current_plan(self) -> dict[str, Any]:
        if not self.setup_complete:
            return PlanContentV1.empty().model_dump()
        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        return self._current_plan.content.model_dump()

    def current_plan_id(self) -> int:
        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        return self._current_plan.id

    def current_plan_state(self) -> LessonPlanEditorState:
        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        return self._current_plan

    def read_agent_current(self, plan_id: int) -> dict[str, object]:
        record = self._repository.load_tool_plan(plan_id)
        if record is None:
            raise WorkspaceError("plan.not_found", "当前教案不存在")
        return record

    def read_agent_context(self, plan_id: int) -> dict[str, object]:
        record = self._repository.load_tool_context(plan_id)
        if record is None:
            raise WorkspaceError("plan.not_found", "当前教案上下文不存在")
        return record

    def read_agent_calendar(self, semester_id: int, plan_date: date) -> dict[str, object]:
        semester = self._repository.load_tool_semester(semester_id)
        if semester is None:
            raise WorkspaceError("settings.semester_not_found", "当前学期不存在")
        from kindergarten_manager.domain.calendar import evaluate_calendar

        evaluation = evaluate_calendar(
            plan_date,
            semester_start=semester[0],
            semester_end=semester[1],
        )
        return {"plan_date": plan_date.isoformat(), "warnings": evaluation.warnings}

    def read_agent_class_areas(self, class_id: int) -> dict[str, object]:
        return {"areas": self._repository.load_tool_class_areas(class_id)}

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

    def apply_ai_adoption(self, adopted: AdoptedContent) -> LessonPlanEditorState:
        """将已提交的 AI 采用结果同步回唯一编辑器状态。"""

        if self._current_plan is None:
            self.load_plan_context()
        if self._current_plan is None:
            raise WorkspaceError("plan.context_missing", "首次设置尚未完成")
        self._current_plan = replace(
            self._current_plan,
            content=PlanContentV1.model_validate(adopted.content),
            content_revision=adopted.content_revision,
        )
        return self._current_plan

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
