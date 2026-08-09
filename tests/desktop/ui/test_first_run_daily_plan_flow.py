from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QWidget,
)
from pytestqt.qtbot import QtBot

from kindergarten_manager.application.settings import SettingsError
from kindergarten_manager.application.workspace import ClassContext, DailyPlanContext
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
            warnings=("所选日期不是工作日",),
        )

    def select_plan_context(self, class_id: int, plan_date: date) -> DailyPlanContext:
        self.selected_contexts.append((class_id, plan_date))
        return DailyPlanContext(
            classes=(ClassContext(id=1, name="向日葵班"),),
            selected_class_id=class_id,
            plan_date=plan_date,
        )

    def load_current_plan(self) -> dict[str, Any]:
        return PlanContentV1.model_validate(self.saved_content).model_dump()

    def save_current_plan(self, content: dict[str, Any]) -> None:
        self.saved_content = dict(content)

    def suggested_export_filename(self) -> str:
        return self.destination.name

    def export_current_day(self, destination: Path) -> None:
        self.exported.append(destination)


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
    qtbot.mouseClick(_child(window, QPushButton, "complete_setup"), Qt.MouseButton.LeftButton)

    assert services.setup == values
    stack = _child(window, QStackedWidget, "main_stack")
    assert stack.currentIndex() == 1
    assert _child(window, QComboBox, "class_context").currentText() == "向日葵班"
    assert _child(window, QDateEdit, "plan_date").date().toPython() == date(2026, 9, 7)
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
