from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPlainTextEdit, QPushButton
from pytestqt.qtbot import QtBot

from kindergarten_manager.application.ai_generation import CoordinatorState, PreviewView
from kindergarten_manager.application.ai_settings import AiSettingsView
from kindergarten_manager.application.dto import CommandResult, OperationAccepted
from kindergarten_manager.ui.ports import DesktopServices
from kindergarten_manager.ui.widgets.ai_preview import AiPreviewPanel
from tests.desktop.helpers import pending_module, pending_symbol


def _flow():
    module = pending_module("kindergarten_manager.ui.widgets.ai_preview")
    flow_type = pending_symbol(module, "AiPreviewFlow")
    return flow_type()


def test_ai_entry_is_optional_and_unconfigured_state_does_not_block_manual_flow() -> None:
    flow = _flow()

    assert flow.entry_visible is True
    assert flow.generation_enabled is False
    assert flow.status_text == "未配置 AI，可继续手工编辑和导出"


def test_duplicate_start_shows_fixed_single_operation_message() -> None:
    flow = _flow()
    flow.configure(enabled=True)
    operation_id = UUID(int=1)
    flow.mark_started(operation_id)

    assert not flow.request_start("morning_talk")
    assert flow.status_text == "AI 正在生成，请稍候"
    assert flow.notice_text == "已有 AI 任务正在运行"


def test_per_section_preview_failure_and_retry_remain_independent() -> None:
    flow = _flow()
    flow.configure(enabled=True)
    operation_id = UUID(int=2)
    flow.mark_started(operation_id)
    flow.show_preview(operation_id, "morning_talk", "preview-1", {"topic": "春天"})
    flow.show_failure(operation_id, "morning_activity", "生成失败")

    assert flow.preview_for("morning_talk").can_adopt
    assert flow.failure_for("morning_activity").can_retry
    assert flow.request_retry("morning_activity") == "morning_activity"
    assert flow.preview_for("morning_talk").preview_id == "preview-1"


def test_adopt_and_reject_emit_only_explicit_preview_intents() -> None:
    flow = _flow()
    operation_id = UUID(int=3)
    flow.configure(enabled=True)
    flow.mark_started(operation_id)
    flow.show_preview(operation_id, "morning_talk", "preview-2", {"topic": "春天"})

    assert flow.request_adopt("preview-2") == ("adopt", "preview-2")
    assert flow.request_reject("preview-2") == ("reject", "preview-2")
    assert flow.preview_for("morning_talk").status == "ready"


def test_page_change_invalidates_epoch_and_discards_late_signal() -> None:
    flow = _flow()
    operation_id = UUID(int=4)
    flow.configure(enabled=True)
    epoch = flow.page_epoch
    flow.mark_started(operation_id)

    flow.leave_page()
    flow.show_preview(
        operation_id,
        "morning_talk",
        "late-preview",
        {"topic": "迟到"},
        page_epoch=epoch,
    )

    assert flow.page_epoch != epoch
    assert flow.preview_for("morning_talk") is None


@dataclass
class FakeAiServices:
    state: CoordinatorState = field(default_factory=lambda: CoordinatorState(None, (), {}, ()))
    starts: list[tuple[str, str]] = field(default_factory=list)
    adopted: list[object] = field(default_factory=list)
    rejected: list[object] = field(default_factory=list)

    def load_ai_settings(self) -> AiSettingsView:
        return AiSettingsView("https://ai.example.test/v1", "fixture", True, True, {})

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
        del operation_id
        self.state = CoordinatorState(None, (), {}, ())
        return CommandResult.success(None, message="AI 生成已取消")


def test_actual_panel_wires_per_section_preview_adopt_and_retry(qtbot: QtBot) -> None:
    services = FakeAiServices()
    content_refreshes: list[bool] = []
    panel = AiPreviewPanel(
        cast(DesktopServices, services),
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
    assert content_refreshes == [True]
    services.state = CoordinatorState(None, (), {"morning_talk": "ai.invalid_output"}, ())
    panel.refresh()
    retry = panel.findChild(QPushButton, "retry_morning_talk")
    assert retry is not None and retry.isVisible()
    qtbot.mouseClick(retry, Qt.MouseButton.LeftButton)
    assert services.starts[-1] == ("morning_talk", "观察春天")
