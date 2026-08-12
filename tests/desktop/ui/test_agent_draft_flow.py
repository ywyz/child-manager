from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QPushButton, QTableWidget
from pytestqt.qtbot import QtBot

from tests.desktop.helpers import pending_module, pending_symbol


@dataclass(frozen=True, slots=True)
class FakePatchOperation:
    field_path: str
    before_display: str
    after_display: str


@dataclass(frozen=True, slots=True)
class FakePatch:
    patch_id: UUID
    tool_name: str
    operations: tuple[FakePatchOperation, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FakeAgentState:
    running_operation_id: UUID | None
    status: str
    message: str
    patches: tuple[FakePatch, ...] = ()


class AgentUiError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class FakeAgentServices:
    state: FakeAgentState = field(
        default_factory=lambda: FakeAgentState(None, "idle", "Agent 已就绪")
    )
    starts: list[tuple[str, object]] = field(default_factory=list)
    cancelled: list[UUID] = field(default_factory=list)
    rejected: list[UUID] = field(default_factory=list)

    def load_agent_state(self) -> FakeAgentState:
        return self.state

    def start_agent_turn(self, intent: str, context_request: object) -> object:
        if "直接修改" in intent or "总是允许" in intent:
            raise AgentUiError("agent.tool_not_allowed", "当前阶段仅支持读取和草拟")
        if self.state.running_operation_id is not None:
            raise AgentUiError("agent.operation_in_progress", "已有 Agent 任务正在运行")
        self.starts.append((intent, context_request))
        operation_id = UUID(int=len(self.starts))
        self.state = FakeAgentState(operation_id, "running", "Agent 正在处理，请稍候")
        return SimpleNamespace(operation_id=operation_id)

    def cancel_agent_turn(self, operation_id: UUID) -> object:
        self.cancelled.append(operation_id)
        self.state = FakeAgentState(None, "cancelled", "Agent 操作已取消")
        return SimpleNamespace(status="cancelled", message="Agent 操作已取消")

    def reject_agent_patch(self, patch_id: UUID) -> object:
        self.rejected.append(patch_id)
        self.state = FakeAgentState(None, "idle", "草案已丢弃")
        return SimpleNamespace(status="ok", message="草案已丢弃")


def _panel(qtbot: QtBot, services: FakeAgentServices) -> Any:
    module = pending_module(
        "kindergarten_manager.ui.widgets.agent_draft",
        red_label="SLICE2B_RED",
    )
    panel_type = pending_symbol(module, "AgentDraftPanel", red_label="SLICE2B_RED")
    panel = panel_type(
        services,
        context_request=lambda: {
            "class_id": 7,
            "semester_id": 8,
            "lesson_plan_id": 9,
            "plan_date": "2026-09-07",
        },
    )
    qtbot.addWidget(panel)
    panel.show()
    return panel


def _ready_patch() -> FakePatch:
    return FakePatch(
        patch_id=UUID(int=41),
        tool_name="lesson_plan.draft_section_patch",
        operations=(
            FakePatchOperation(
                field_path="content.morning_talk.topic",
                before_display="春天里的种子",
                after_display="观察种子发芽",
            ),
            FakePatchOperation(
                field_path="content.morning_talk.questions",
                before_display="你发现了什么？",
                after_display="种子发生了什么变化？",
            ),
        ),
        warnings=("这只是草案，不会修改教案",),
    )


def test_panel_has_a_fixed_non_blocking_status_and_intent_area(qtbot: QtBot) -> None:
    panel = _panel(qtbot, FakeAgentServices())

    status = panel.findChild(QLabel, "agent_status")
    intent = panel.findChild(QPlainTextEdit, "agent_intent")
    start = panel.findChild(QPushButton, "start_agent_turn")
    cancel = panel.findChild(QPushButton, "cancel_agent_turn")

    assert status is not None and status.isVisible() and status.text() == "Agent 已就绪"
    assert intent is not None and intent.isVisible()
    assert start is not None and start.isEnabled()
    assert cancel is not None and not cancel.isEnabled()


def test_panel_displays_each_draft_operation_as_a_read_only_field_diff(
    qtbot: QtBot,
) -> None:
    patch = _ready_patch()
    services = FakeAgentServices(
        state=FakeAgentState(None, "draft_ready", "Agent 草案已生成", (patch,))
    )
    panel = _panel(qtbot, services)
    table = panel.findChild(QTableWidget, "agent_draft_fields")

    assert table is not None and table.isVisible()
    assert table.rowCount() == 2
    assert [table.item(0, column).text() for column in range(3)] == [
        "content.morning_talk.topic",
        "春天里的种子",
        "观察种子发芽",
    ]
    assert not bool(table.editTriggers())
    assert panel.findChild(QPushButton, "discard_agent_patch") is not None


def test_running_panel_refreshes_when_the_background_result_becomes_ready(
    qtbot: QtBot,
) -> None:
    services = FakeAgentServices(
        state=FakeAgentState(UUID(int=7), "running", "Agent 正在处理，请稍候")
    )
    panel = _panel(qtbot, services)
    table = panel.findChild(QTableWidget, "agent_draft_fields")
    assert table is not None and table.rowCount() == 0

    services.state = FakeAgentState(
        None,
        "draft_ready",
        "Agent 草案已生成",
        (_ready_patch(),),
    )

    qtbot.waitUntil(lambda: table.rowCount() == 2, timeout=1_000)
    assert panel.findChild(QLabel, "agent_status").text() == "Agent 草案已生成"


def test_running_turn_disables_duplicate_start_and_keeps_cancel_available(
    qtbot: QtBot,
) -> None:
    services = FakeAgentServices(
        state=FakeAgentState(UUID(int=7), "running", "Agent 正在处理，请稍候")
    )
    panel = _panel(qtbot, services)
    status = panel.findChild(QLabel, "agent_status")
    start = panel.findChild(QPushButton, "start_agent_turn")
    cancel = panel.findChild(QPushButton, "cancel_agent_turn")

    assert status is not None and status.text() == "Agent 正在处理，请稍候"
    assert start is not None and not start.isEnabled()
    assert cancel is not None and cancel.isEnabled()
    qtbot.mouseClick(start, Qt.MouseButton.LeftButton)
    assert services.starts == []


def test_intent_submission_uses_current_scope_and_cancel_targets_current_turn(
    qtbot: QtBot,
) -> None:
    services = FakeAgentServices()
    panel = _panel(qtbot, services)
    intent = panel.findChild(QPlainTextEdit, "agent_intent")
    start = panel.findChild(QPushButton, "start_agent_turn")
    cancel = panel.findChild(QPushButton, "cancel_agent_turn")
    assert intent is not None and start is not None and cancel is not None
    intent.setPlainText("请提出晨间谈话修改草案")

    qtbot.mouseClick(start, Qt.MouseButton.LeftButton)
    assert services.starts == [
        (
            "请提出晨间谈话修改草案",
            {
                "class_id": 7,
                "semester_id": 8,
                "lesson_plan_id": 9,
                "plan_date": "2026-09-07",
            },
        )
    ]
    assert cancel.isEnabled()

    qtbot.mouseClick(cancel, Qt.MouseButton.LeftButton)
    assert services.cancelled == [UUID(int=1)]


@pytest.mark.parametrize("close_panel", [False, True], ids=["switch-page", "close-panel"])
def test_page_switch_and_close_discard_late_agent_results(
    qtbot: QtBot,
    close_panel: bool,
) -> None:
    operation_id = UUID(int=17)
    services = FakeAgentServices(
        state=FakeAgentState(operation_id, "running", "Agent 正在处理，请稍候")
    )
    panel = _panel(qtbot, services)

    if close_panel:
        panel.close()
    else:
        panel.leave_page()

    services.state = FakeAgentState(
        None,
        "draft_ready",
        "不应显示的迟到草案",
        (_ready_patch(),),
    )
    panel.refresh()
    table = panel.findChild(QTableWidget, "agent_draft_fields")

    assert services.cancelled == [operation_id]
    assert table is not None and table.rowCount() == 0


@pytest.mark.parametrize("intent_text", ["直接修改当前教案", "以后总是允许直接修改"])
def test_write_wording_never_creates_a_write_or_always_allow_path(
    qtbot: QtBot,
    intent_text: str,
) -> None:
    services = FakeAgentServices()
    panel = _panel(qtbot, services)
    intent = panel.findChild(QPlainTextEdit, "agent_intent")
    start = panel.findChild(QPushButton, "start_agent_turn")
    assert intent is not None and start is not None
    intent.setPlainText(intent_text)

    qtbot.mouseClick(start, Qt.MouseButton.LeftButton)

    status = panel.findChild(QLabel, "agent_status")
    button_texts = {button.text() for button in panel.findChildren(QPushButton)}
    assert status is not None and "仅支持读取和草拟" in status.text()
    assert services.starts == []
    assert "确认写入" not in button_texts
    assert "总是允许" not in button_texts
    assert panel.findChild(QPushButton, "confirm_agent_patch") is None
    assert panel.findChild(QPushButton, "always_allow_agent") is None
