from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QWidget,
)
from pytestqt.qtbot import QtBot

from kindergarten_manager.application.ai_generation import CoordinatorState, PreviewView
from kindergarten_manager.application.ai_settings import AiSettingsView
from kindergarten_manager.application.dto import CommandResult, OperationAccepted
from kindergarten_manager.application.settings import SettingsError
from kindergarten_manager.application.workspace import (
    ClassContext,
    DailyPlanContext,
    DesktopSettingsContext,
)
from kindergarten_manager.domain.content import PlanContentV1
from kindergarten_manager.ui.pages.first_run import build_first_run_daily_plan_window
from tests.desktop.helpers import implemented


@dataclass
class FakeDesktopServices:
    destination: Path
    setup: dict[str, str] = field(default_factory=dict)
    saved_content: dict[str, Any] = field(default_factory=dict)
    exported: list[Path] = field(default_factory=list)
    selected_contexts: list[tuple[int, date]] = field(default_factory=list)
    settings_updates: list[dict[str, str]] = field(default_factory=list)
    failure: Exception | None = None

    def complete_setup(self, values: dict[str, str]) -> None:
        if self.failure is not None:
            raise self.failure
        self.setup = dict(values)

    def load_plan_context(self) -> DailyPlanContext:
        return DailyPlanContext(
            classes=(ClassContext(id=1, name=self.setup.get("class_name", "向日葵班")),),
            selected_class_id=1,
            plan_date=date(2026, 9, 7),
            today=date(2026, 8, 10),
            warnings=("所选日期不是工作日",),
        )

    def select_plan_context(self, class_id: int, plan_date: date) -> DailyPlanContext:
        self.selected_contexts.append((class_id, plan_date))
        return DailyPlanContext(
            classes=(ClassContext(id=1, name="向日葵班"),),
            selected_class_id=class_id,
            plan_date=plan_date,
            today=date(2026, 8, 10),
        )

    def load_current_plan(self) -> dict[str, Any]:
        return PlanContentV1.model_validate(self.saved_content).model_dump()

    def save_current_plan(self, content: dict[str, Any]) -> None:
        self.saved_content = dict(content)

    def load_settings(self) -> DesktopSettingsContext:
        return DesktopSettingsContext(
            theme=self.setup.get("theme", "system"),
            semester_name=self.setup.get("semester_name", "2026 秋季学期"),
            semester_start_date=date.fromisoformat(
                self.setup.get("semester_start_date", "2026-09-01")
            ),
            semester_end_date=date.fromisoformat(self.setup.get("semester_end_date", "2027-01-31")),
        )

    def update_settings(self, values: dict[str, str]) -> DesktopSettingsContext:
        self.settings_updates.append(dict(values))
        self.setup.update(values)
        return self.load_settings()

    def suggested_export_filename(self) -> str:
        return self.destination.name

    def export_current_day(self, destination: Path) -> None:
        self.exported.append(destination)

    def load_ai_settings(self) -> AiSettingsView:
        return AiSettingsView(None, None, False, False, {})

    def save_ai_settings(self, values: dict[str, object]) -> AiSettingsView:
        del values
        return self.load_ai_settings()

    def reset_ai_prompt(self, prompt_code: str) -> str:
        del prompt_code
        return "默认提示词"

    def load_ai_generation_state(self) -> CoordinatorState:
        return CoordinatorState(None, (), {}, ())

    def start_ai_generation(
        self,
        section_code: str,
        teacher_context: str,
    ) -> OperationAccepted:
        del section_code, teacher_context
        return OperationAccepted(UUID(int=1))

    def start_ai_batch(self, teacher_context: str) -> OperationAccepted:
        return self.start_ai_generation("batch", teacher_context)

    def adopt_ai_preview(self, preview_id: int) -> object:
        return preview_id

    def reject_ai_preview(self, preview_id: int) -> PreviewView:
        return PreviewView(preview_id, 1, "morning_talk", {}, "0" * 64, "rejected")

    def cancel_ai_generation(self, operation_id: UUID) -> CommandResult[None]:
        del operation_id
        return CommandResult.success(None, message="AI 生成已取消")


def _child(window: QWidget, widget_type: type[Any], name: str) -> Any:
    child = window.findChild(widget_type, name)
    assert child is not None, name
    return child


def _build(services: FakeDesktopServices) -> QWidget:
    return implemented(lambda: build_first_run_daily_plan_window(services=services))


def test_first_run_collects_minimum_settings_and_opens_structured_editor(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    services = FakeDesktopServices(tmp_path / "当天教案.docx")
    window = _build(services)
    qtbot.addWidget(window)
    window.show()

    values = {
        "teacher_name": "测试教师",
        "kindergarten_name": "星河幼儿园",
        "semester_name": "2026 秋季学期",
        "class_name": "向日葵班",
    }
    for object_name, value in values.items():
        _child(window, QLineEdit, object_name).setText(value)
    semester_dates = {
        "semester_start_date": QDate(2026, 9, 1),
        "semester_end_date": QDate(2027, 1, 31),
    }
    for object_name, value in semester_dates.items():
        _child(window, QDateEdit, object_name).setDate(value)
    qtbot.mouseClick(_child(window, QPushButton, "complete_setup"), Qt.MouseButton.LeftButton)

    assert services.setup == {
        **values,
        "semester_start_date": "2026-09-01",
        "semester_end_date": "2027-01-31",
    }
    stack = _child(window, QStackedWidget, "main_stack")
    assert stack.currentIndex() == 1
    assert _child(window, QComboBox, "class_context").currentText() == "向日葵班"
    assert _child(window, QDateEdit, "plan_date").date().toPython() == date(2026, 9, 7)
    assert _child(window, QWidget, "ai_preview_panel") is not None
    assert not _child(window, QPushButton, "generate_morning_talk").isEnabled()
    assert "不是工作日" in _child(window, QWidget, "calendar_warnings").property("text")
    for field_name in (
        "morning_physical_cycle",
        "morning_group_game",
        "morning_free_game",
        "morning_focus_guidance",
        "morning_objectives",
        "morning_guidance_points",
        "morning_talk_topic",
        "morning_talk_questions",
        "group_activity_theme",
        "group_activity_objectives",
        "group_activity_preparation",
        "group_activity_focus",
        "group_activity_difficulty",
        "group_activity_process",
        "indoor_area_names",
        "indoor_focus_guidance",
        "indoor_objectives",
        "indoor_guidance_points",
        "indoor_support_strategies",
        "afternoon_outdoor_area_names",
        "afternoon_focus_guidance",
        "afternoon_objectives",
        "afternoon_guidance_points",
        "afternoon_support_strategies",
        "daily_reflection_highlights",
        "daily_reflection_issues",
        "daily_reflection_adjustments",
    ):
        assert window.findChild(QWidget, field_name) is not None


def test_daily_plan_uses_week_workspace_and_gives_collective_activity_room(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    services = FakeDesktopServices(tmp_path / "当天教案.docx")
    services.setup = {"teacher_name": "测试教师"}
    window = _build(services)
    qtbot.addWidget(window)
    window.resize(1366, 768)
    window.show()
    qtbot.waitExposed(window)

    navigation = _child(window, QWidget, "section_navigation")
    editor_stack = _child(window, QStackedWidget, "section_editor_stack")
    assert navigation.isVisible()
    assert editor_stack.isVisible()
    assert editor_stack.currentIndex() == 0

    expected_sections = (
        "01 晨间活动",
        "02 晨间谈话",
        "03 室内区域游戏",
        "04 下午户外游戏",
        "05 集体活动",
        "06 一日活动反思",
    )
    section_buttons = [
        _child(window, QPushButton, f"section_nav_{index}")
        for index in range(len(expected_sections))
    ]
    assert tuple(button.text() for button in section_buttons) == expected_sections

    qtbot.mouseClick(section_buttons[4], Qt.MouseButton.LeftButton)
    assert editor_stack.currentIndex() == 4
    process_table = _child(window, QTableWidget, "group_activity_process_table")
    assert process_table.minimumHeight() >= 240
    assert process_table.horizontalHeader().stretchLastSection()

    qtbot.mouseClick(_child(window, QPushButton, "next_week"), Qt.MouseButton.LeftButton)
    assert services.selected_contexts[-1] == (1, date(2026, 9, 14))
    assert _child(window, QDateEdit, "plan_date").date().toPython() == date(2026, 9, 14)

    qtbot.mouseClick(_child(window, QPushButton, "today"), Qt.MouseButton.LeftButton)
    assert services.selected_contexts[-1] == (1, date(2026, 8, 10))
    assert _child(window, QDateEdit, "plan_date").date().toPython() == date(2026, 8, 10)


def test_light_theme_overrides_dark_system_palette_for_readable_text(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    original_palette = QPalette(app.palette())
    dark_system_palette = QPalette(original_palette)
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.Text,
    ):
        dark_system_palette.setColor(role, QColor("#ffffff"))
    dark_system_palette.setColor(QPalette.ColorRole.Window, QColor("#181818"))
    dark_system_palette.setColor(QPalette.ColorRole.Button, QColor("#181818"))
    dark_system_palette.setColor(QPalette.ColorRole.Base, QColor("#181818"))
    app.setPalette(dark_system_palette)
    try:
        services = FakeDesktopServices(tmp_path / "当天教案.docx")
        services.setup = {"teacher_name": "测试教师"}
        window = _build(services)
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        title = next(
            label for label in window.findChildren(QLabel) if label.text() == "一日活动计划"
        )
        previous_week = _child(window, QPushButton, "previous_week")
        assert title.palette().color(QPalette.ColorRole.WindowText) == QColor("#183033")
        assert previous_week.palette().color(QPalette.ColorRole.ButtonText) == QColor("#183033")
    finally:
        app.setPalette(original_palette)


def test_desktop_theme_keeps_widget_fonts_in_points_for_windows_native_style(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    services = FakeDesktopServices(tmp_path / "当天教案.docx")
    services.setup = {"teacher_name": "测试教师", "theme": "light"}
    window = _build(services)
    qtbot.addWidget(window)
    window.show()
    window.ensurePolished()

    pixel_sized_widgets = [
        widget.objectName() or type(widget).__name__
        for widget in window.findChildren(QWidget)
        if widget.font().pixelSize() > 0
    ]
    assert pixel_sized_widgets == []


def test_settings_page_changes_theme_and_current_semester_without_restarting(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    services = FakeDesktopServices(tmp_path / "当天教案.docx")
    services.setup = {
        "teacher_name": "测试教师",
        "theme": "light",
        "semester_name": "2026 秋季学期",
        "semester_start_date": "2026-09-01",
        "semester_end_date": "2027-01-31",
    }
    window = _build(services)
    qtbot.addWidget(window)
    window.show()

    qtbot.mouseClick(_child(window, QPushButton, "open_settings"), Qt.MouseButton.LeftButton)
    assert _child(window, QStackedWidget, "main_stack").currentIndex() == 2
    theme = _child(window, QComboBox, "theme_preference")
    assert tuple(theme.itemText(index) for index in range(theme.count())) == (
        "跟随系统",
        "浅色",
        "深色",
    )
    assert theme.currentData() == "light"
    assert _child(window, QLineEdit, "semester_settings_name").text() == "2026 秋季学期"

    theme.setCurrentIndex(theme.findData("dark"))
    _child(window, QLineEdit, "semester_settings_name").setText("2027 春季学期")
    _child(window, QDateEdit, "semester_settings_start_date").setDate(QDate(2027, 2, 15))
    _child(window, QDateEdit, "semester_settings_end_date").setDate(QDate(2027, 7, 15))
    qtbot.mouseClick(_child(window, QPushButton, "save_settings"), Qt.MouseButton.LeftButton)

    assert services.settings_updates[-1] == {
        "theme": "dark",
        "semester_name": "2027 春季学期",
        "semester_start_date": "2027-02-15",
        "semester_end_date": "2027-07-15",
    }
    settings_page = _child(window, QWidget, "settings_page")
    assert settings_page.palette().color(QPalette.ColorRole.Window) == QColor("#101718")
    assert settings_page.palette().color(QPalette.ColorRole.WindowText) == QColor("#e7eeee")

    qtbot.mouseClick(_child(window, QPushButton, "back_to_plan"), Qt.MouseButton.LeftButton)
    assert _child(window, QStackedWidget, "main_stack").currentIndex() == 1


def test_save_restart_and_native_destination_adapter_form_daily_word_loop(
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    services = FakeDesktopServices(tmp_path / "当天教案.docx")
    services.setup = {
        "teacher_name": "测试教师",
        "kindergarten_name": "星河幼儿园",
        "semester_name": "2026 秋季学期",
        "class_name": "向日葵班",
    }
    first = _build(services)
    qtbot.addWidget(first)
    theme = _child(first, QLineEdit, "group_activity_theme")
    theme.setText("寻找秋天")
    qtbot.mouseClick(_child(first, QPushButton, "save_plan"), Qt.MouseButton.LeftButton)

    assert services.saved_content["group_activity"]["theme"] == "寻找秋天"
    assert "已保存" in _child(first, QWidget, "save_status").property("text")

    first.close()
    reopened = _build(services)
    qtbot.addWidget(reopened)
    assert _child(reopened, QLineEdit, "group_activity_theme").text() == "寻找秋天"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(services.destination), "Word 文档 (*.docx)"),
    )
    qtbot.mouseClick(_child(reopened, QPushButton, "export_day"), Qt.MouseButton.LeftButton)
    assert services.exported == [services.destination]


def test_existing_export_requires_confirmation_before_service_call(
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "已有教案.docx"
    destination.write_bytes(b"old-docx")
    services = FakeDesktopServices(destination)
    services.setup = {"teacher_name": "测试教师"}
    window = _build(services)
    qtbot.addWidget(window)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.No,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), "Word 文档 (*.docx)"),
    )
    qtbot.mouseClick(_child(window, QPushButton, "export_day"), Qt.MouseButton.LeftButton)
    assert services.exported == []

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Yes,
    )
    qtbot.mouseClick(_child(window, QPushButton, "export_day"), Qt.MouseButton.LeftButton)
    assert services.exported == [destination]


def test_ui_surfaces_stable_error_code_and_logs_only_safe_summary(
    qtbot: QtBot,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    services = FakeDesktopServices(tmp_path / "当天教案.docx")
    services.failure = SettingsError("settings.invalid_value", "秘密教师正文")
    window = _build(services)
    qtbot.addWidget(window)
    caplog.set_level(logging.ERROR)

    operation_logger = logging.getLogger("kindergarten_manager.ui.errors")
    operation_logger.disabled = True
    try:
        qtbot.mouseClick(_child(window, QPushButton, "complete_setup"), Qt.MouseButton.LeftButton)
    finally:
        operation_logger.disabled = False

    status = _child(window, QWidget, "setup_status").property("text")
    assert "settings.invalid_value" in status
    assert "秘密教师正文" not in caplog.text
    assert "settings.invalid_value" in caplog.text
