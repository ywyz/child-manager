from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QPushButton
from pytestqt.qtbot import QtBot

from kindergarten_manager.application.ai_generation import CoordinatorState, PreviewView
from kindergarten_manager.application.ai_settings import AiSettingsView
from kindergarten_manager.application.dto import CommandResult, OperationAccepted
from kindergarten_manager.ui.ports import DesktopServices
from kindergarten_manager.ui.widgets.ai_preview import AiPreviewPanel


@dataclass
class FakeAiServices:
    enabled: bool = True
    state: CoordinatorState = field(default_factory=lambda: CoordinatorState(None, (), {}, ()))
    starts: list[tuple[str, str]] = field(default_factory=list)
    adopted: list[object] = field(default_factory=list)
    rejected: list[object] = field(default_factory=list)
    cancelled: list[UUID] = field(default_factory=list)

    def load_ai_settings(self) -> AiSettingsView:
        return AiSettingsView(
            "https://ai.example.test/v1" if self.enabled else None,
            "fixture" if self.enabled else None,
            self.enabled,
            self.enabled,
            {},
        )

    def load_ai_generation_state(self) -> CoordinatorState:
        return self.state

    def start_ai_generation(self, section_code: str, teacher_context: str) -> OperationAccepted:
        self.starts.append((section_code, teacher_context))
        operation_id = UUID(int=len(self.starts))
        self.state = CoordinatorState(operation_id, (), {}, ())
        return OperationAccepted(operation_id)

    def start_ai_batch(self, teacher_context: str) -> OperationAccepted:
        return self.start_ai_generation("batch", teacher_context)

    def adopt_ai_preview(self, preview_id: int) -> object:
        self.adopted.append(preview_id)
        self.state = CoordinatorState(None, (), {}, ())
        return object()

    def reject_ai_preview(self, preview_id: int) -> PreviewView:
        self.rejected.append(preview_id)
        self.state = CoordinatorState(None, (), {}, ())
        return PreviewView(preview_id, 1, "morning_talk", {}, "0" * 64, "rejected")

    def cancel_ai_generation(self, operation_id: UUID) -> CommandResult[None]:
        self.cancelled.append(operation_id)
        self.state = CoordinatorState(None, (), {}, ())
        return CommandResult.success(None, message="AI 生成已取消")


def test_actual_panel_keeps_unconfigured_ai_optional(qtbot: QtBot) -> None:
    services = FakeAiServices(enabled=False)
    panel = AiPreviewPanel(
        cast(DesktopServices, services),
        on_save_visible_content=lambda: True,
        on_content_changed=lambda: None,
    )
    qtbot.addWidget(panel)
    panel.show()

    status = panel.findChild(QLabel, "ai_generation_status")
    generate = panel.findChild(QPushButton, "generate_morning_talk")
    assert status is not None and "未配置 AI" in status.text()
    assert generate is not None and not generate.isEnabled()


def test_actual_panel_shows_success_and_failure_independently(qtbot: QtBot) -> None:
    services = FakeAiServices(
        state=CoordinatorState(
            None,
            ("morning_talk",),
            {"morning_activity": "ai.invalid_output"},
            (PreviewView(7, 1, "morning_talk", {"topic": "春天"}, "0" * 64, "ready"),),
        )
    )
    panel = AiPreviewPanel(
        cast(DesktopServices, services),
        on_save_visible_content=lambda: True,
        on_content_changed=lambda: None,
    )
    qtbot.addWidget(panel)
    panel.show()

    preview = panel.findChild(QPlainTextEdit, "ai_preview_morning_talk")
    adopt = panel.findChild(QPushButton, "adopt_morning_talk")
    retry = panel.findChild(QPushButton, "retry_morning_activity")
    assert preview is not None and preview.isVisible() and "春天" in preview.toPlainText()
    assert adopt is not None and adopt.isVisible()
    assert retry is not None and retry.isVisible()


def test_preview_uses_teacher_facing_labels_instead_of_raw_json(qtbot: QtBot) -> None:
    services = FakeAiServices(
        state=CoordinatorState(
            None,
            ("morning_activity",),
            {},
            (
                PreviewView(
                    7,
                    1,
                    "morning_activity",
                    {
                        "schema_version": 1,
                        "physical_cycle": "跨跳体能大循环",
                        "group_game": "小兔搬家",
                        "free_game": "跳圈",
                        "focus_guidance": "指导双脚并拢落地",
                        "objectives": ["发展跳跃能力", "提高身体协调性"],
                        "guidance_points": ["检查场地", "分层摆放器材"],
                    },
                    "0" * 64,
                    "ready",
                ),
            ),
        )
    )
    panel = AiPreviewPanel(
        cast(DesktopServices, services),
        on_save_visible_content=lambda: True,
        on_content_changed=lambda: None,
    )
    qtbot.addWidget(panel)
    panel.show()

    preview = panel.findChild(QPlainTextEdit, "ai_preview_morning_activity")
    assert preview is not None
    rendered = preview.toPlainText()
    assert "体能大循环：跨跳体能大循环" in rendered
    assert "集体体育游戏：小兔搬家" in rendered
    assert "1. 发展跳跃能力" in rendered
    assert "schema_version" not in rendered
    assert not rendered.lstrip().startswith("{")


def test_actual_panel_disables_duplicate_start_while_operation_runs(qtbot: QtBot) -> None:
    services = FakeAiServices(state=CoordinatorState(UUID(int=9), (), {}, ()))
    panel = AiPreviewPanel(
        cast(DesktopServices, services),
        on_save_visible_content=lambda: True,
        on_content_changed=lambda: None,
    )
    qtbot.addWidget(panel)
    panel.show()

    status = panel.findChild(QLabel, "ai_generation_status")
    generate = panel.findChild(QPushButton, "generate_morning_talk")
    assert status is not None and status.text() == "AI 正在生成，请稍候"
    assert generate is not None and not generate.isEnabled()


def test_actual_panel_wires_per_section_preview_adopt_and_retry(qtbot: QtBot) -> None:
    services = FakeAiServices()
    content_refreshes: list[bool] = []
    prepared: list[bool] = []
    panel = AiPreviewPanel(
        cast(DesktopServices, services),
        on_save_visible_content=lambda: prepared.append(True) or True,
        on_content_changed=lambda: content_refreshes.append(True),
    )
    qtbot.addWidget(panel)
    panel.show()
    context = panel.findChild(QPlainTextEdit, "ai_teacher_context")
    generate = panel.findChild(QPushButton, "generate_morning_talk")
    assert context is not None and generate is not None
    context.setPlainText("观察春天")

    qtbot.mouseClick(generate, Qt.MouseButton.LeftButton)

    assert services.starts == [("morning_talk", "观察春天")]
    assert prepared == [True]
    services.state = CoordinatorState(
        None,
        ("morning_talk",),
        {},
        (PreviewView(7, 1, "morning_talk", {"topic": "春天"}, "0" * 64, "ready"),),
    )
    panel.refresh()
    preview = panel.findChild(QPlainTextEdit, "ai_preview_morning_talk")
    adopt = panel.findChild(QPushButton, "adopt_morning_talk")
    assert preview is not None and preview.isVisible() and "春天" in preview.toPlainText()
    assert adopt is not None

    qtbot.mouseClick(adopt, Qt.MouseButton.LeftButton)

    assert services.adopted == [7]
    assert prepared == [True, True]
    assert content_refreshes == [True]
    services.state = CoordinatorState(
        None,
        ("morning_talk",),
        {},
        (PreviewView(8, 1, "morning_talk", {"topic": "夏天"}, "0" * 64, "ready"),),
    )
    panel.refresh()
    reject = panel.findChild(QPushButton, "reject_morning_talk")
    assert reject is not None
    qtbot.mouseClick(reject, Qt.MouseButton.LeftButton)
    assert services.rejected == [8]
    services.state = CoordinatorState(None, (), {"morning_talk": "ai.invalid_output"}, ())
    panel.refresh()
    retry = panel.findChild(QPushButton, "retry_morning_talk")
    assert retry is not None and retry.isVisible()
    qtbot.mouseClick(retry, Qt.MouseButton.LeftButton)
    assert services.starts[-1] == ("morning_talk", "观察春天")
    panel.leave_page()
    assert services.cancelled == [UUID(int=2)]
    assert not panel._timer.isActive()
