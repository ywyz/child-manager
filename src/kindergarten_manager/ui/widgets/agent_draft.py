"""Slice 2B 的只读 Agent 意图与字段级草案面板。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol
from uuid import UUID

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class _AgentDraftServices(Protocol):
    def load_agent_state(self) -> Any: ...

    def start_agent_turn(self, intent: str, context_request: object) -> Any: ...

    def cancel_agent_turn(self, operation_id: UUID) -> Any: ...

    def reject_agent_patch(self, patch_id: UUID) -> Any: ...


class AgentDraftPanel(QFrame):
    def __init__(
        self,
        services: _AgentDraftServices,
        *,
        context_request: Callable[[], object],
    ) -> None:
        super().__init__()
        self.setObjectName("agent_draft_panel")
        self._services = services
        self._context_request = context_request
        self._operation_id: UUID | None = None
        self._patch_id: UUID | None = None
        self._accept_results = True
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(100)
        self._refresh_timer.timeout.connect(self.refresh)

        layout = QVBoxLayout(self)
        heading = QLabel("Agent 草案（只读）")
        heading.setProperty("role", "sectionTitle")
        layout.addWidget(heading)

        self.status = QLabel("Agent 已就绪")
        self.status.setObjectName("agent_status")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.intent = QPlainTextEdit()
        self.intent.setObjectName("agent_intent")
        self.intent.setPlaceholderText("描述要读取的信息或希望生成的修改草案")
        self.intent.setMaximumHeight(88)
        layout.addWidget(self.intent)

        actions = QHBoxLayout()
        self.start_button = QPushButton("提交意图")
        self.start_button.setObjectName("start_agent_turn")
        self.start_button.clicked.connect(self._start)
        actions.addWidget(self.start_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancel_agent_turn")
        self.cancel_button.clicked.connect(self._cancel)
        actions.addWidget(self.cancel_button)
        layout.addLayout(actions)

        self.text_draft = QPlainTextEdit()
        self.text_draft.setObjectName("agent_draft_text")
        self.text_draft.setReadOnly(True)
        self.text_draft.setVisible(False)
        layout.addWidget(self.text_draft)

        self.fields = QTableWidget(0, 3)
        self.fields.setObjectName("agent_draft_fields")
        self.fields.setHorizontalHeaderLabels(("字段", "修改前", "草案"))
        self.fields.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.fields)

        self.discard_button = QPushButton("丢弃草案")
        self.discard_button.setObjectName("discard_agent_patch")
        self.discard_button.clicked.connect(self._discard)
        layout.addWidget(self.discard_button)
        layout.addStretch()
        self.refresh()

    def refresh(self) -> None:
        if not self._accept_results:
            self._clear_draft()
            return
        try:
            state = self._services.load_agent_state()
        except Exception:
            self.status.setText("Agent 状态加载失败；手工编辑仍可使用")
            self._set_running(False)
            return
        self._operation_id = state.running_operation_id
        self.status.setText(state.message)
        self._set_running(self._operation_id is not None)
        if self._operation_id is not None:
            self._refresh_timer.start()
        else:
            self._refresh_timer.stop()
        self._clear_draft()
        assistant_content = getattr(state, "assistant_content", None)
        if isinstance(assistant_content, str) and assistant_content.strip():
            self.text_draft.setPlainText(assistant_content)
            self.text_draft.setVisible(True)
        patches = tuple(state.patches)
        if not patches:
            return
        patch = patches[0]
        self._patch_id = patch.patch_id
        for operation in patch.operations:
            row = self.fields.rowCount()
            self.fields.insertRow(row)
            for column, value in enumerate(
                (operation.field_path, operation.before_display, operation.after_display)
            ):
                self.fields.setItem(row, column, QTableWidgetItem(value))
        self.discard_button.setEnabled(True)

    def leave_page(self) -> None:
        self._accept_results = False
        self._refresh_timer.stop()
        if self._operation_id is not None:
            self._services.cancel_agent_turn(self._operation_id)
            self._operation_id = None
        self._clear_draft()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.leave_page()
        super().closeEvent(event)

    def _start(self) -> None:
        if self._operation_id is not None:
            return
        intent = self.intent.toPlainText().strip()
        if not intent:
            self.status.setText("请输入读取或草拟意图")
            return
        try:
            accepted = self._services.start_agent_turn(intent, self._context_request())
        except Exception as error:
            if getattr(error, "code", None) == "agent.tool_not_allowed":
                self.status.setText("当前阶段仅支持读取和草拟")
            else:
                self.status.setText("Agent 意图提交失败；手工编辑仍可使用")
            return
        self._accept_results = True
        self._operation_id = accepted.operation_id
        self.refresh()

    def _cancel(self) -> None:
        if self._operation_id is None:
            return
        result = self._services.cancel_agent_turn(self._operation_id)
        self._operation_id = None
        self.status.setText(result.message)
        self.refresh()

    def _discard(self) -> None:
        if self._patch_id is None:
            return
        result = self._services.reject_agent_patch(self._patch_id)
        self._patch_id = None
        self.status.setText(result.message)
        self.refresh()

    def _set_running(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)

    def _clear_draft(self) -> None:
        self._patch_id = None
        self.text_draft.clear()
        self.text_draft.setVisible(False)
        self.fields.setRowCount(0)
        self.discard_button.setEnabled(False)
