from __future__ import annotations

import json
from collections.abc import Callable
from uuid import UUID

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from kindergarten_manager.ui.errors import user_error_message
from kindergarten_manager.ui.ports import DesktopServices

_SECTION_LABELS = (
    ("morning_activity", "晨间活动"),
    ("morning_talk", "晨间谈话"),
    ("indoor_area_game", "室内区域游戏"),
    ("afternoon_outdoor_game", "下午户外游戏"),
    ("daily_reflection", "一日活动反思"),
)


class AiPreviewPanel(QFrame):
    """实际教案页中的可选 AI 入口、逐栏预览与显式采用面板。"""

    def __init__(
        self,
        services: DesktopServices,
        *,
        on_save_visible_content: Callable[[], bool],
        on_content_changed: Callable[[], None],
    ) -> None:
        super().__init__()
        self.setObjectName("ai_preview_panel")
        self.setMinimumWidth(300)
        self.setMaximumWidth(360)
        self._services = services
        self._on_save_visible_content = on_save_visible_content
        self._on_content_changed = on_content_changed
        self._enabled = False
        self._operation_id: UUID | None = None
        self._preview_ids: dict[str, int] = {}
        self._generate_buttons: dict[str, QPushButton] = {}
        self._results: dict[str, QPlainTextEdit] = {}
        self._adopt_buttons: dict[str, QPushButton] = {}
        self._reject_buttons: dict[str, QPushButton] = {}
        self._retry_buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 14)
        heading = QLabel("AI 助手（可选）")
        heading.setProperty("role", "sectionTitle")
        layout.addWidget(heading)
        self.status = QLabel("未配置 AI，可继续手工编辑和导出")
        self.status.setObjectName("ai_generation_status")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.teacher_context = QPlainTextEdit()
        self.teacher_context.setObjectName("ai_teacher_context")
        self.teacher_context.setPlaceholderText("补充本次生成所需的教师背景（可选）")
        self.teacher_context.setMaximumHeight(72)
        layout.addWidget(self.teacher_context)

        actions = QHBoxLayout()
        self.batch_button = QPushButton("生成四栏")
        self.batch_button.setObjectName("generate_ai_batch")
        self.batch_button.clicked.connect(self._start_batch)
        actions.addWidget(self.batch_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancel_ai_generation")
        self.cancel_button.clicked.connect(self._cancel)
        actions.addWidget(self.cancel_button)
        layout.addLayout(actions)

        for section_code, label_text in _SECTION_LABELS:
            card = QFrame()
            card.setObjectName(f"ai_section_{section_code}")
            card_layout = QVBoxLayout(card)
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addStretch()
            generate = QPushButton("生成")
            generate.setObjectName(f"generate_{section_code}")
            generate.clicked.connect(
                lambda _checked=False, code=section_code: self._start_section(code)
            )
            row.addWidget(generate)
            card_layout.addLayout(row)
            result = QPlainTextEdit()
            result.setObjectName(f"ai_preview_{section_code}")
            result.setReadOnly(True)
            result.setMaximumHeight(100)
            result.hide()
            card_layout.addWidget(result)
            decisions = QHBoxLayout()
            adopt = QPushButton("采用")
            adopt.setObjectName(f"adopt_{section_code}")
            adopt.clicked.connect(lambda _checked=False, code=section_code: self._adopt(code))
            adopt.hide()
            decisions.addWidget(adopt)
            reject = QPushButton("拒绝")
            reject.setObjectName(f"reject_{section_code}")
            reject.clicked.connect(lambda _checked=False, code=section_code: self._reject(code))
            reject.hide()
            decisions.addWidget(reject)
            retry = QPushButton("重试")
            retry.setObjectName(f"retry_{section_code}")
            retry.clicked.connect(
                lambda _checked=False, code=section_code: self._start_section(code)
            )
            retry.hide()
            decisions.addWidget(retry)
            card_layout.addLayout(decisions)
            layout.addWidget(card)
            self._generate_buttons[section_code] = generate
            self._results[section_code] = result
            self._adopt_buttons[section_code] = adopt
            self._reject_buttons[section_code] = reject
            self._retry_buttons[section_code] = retry
        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self._reload_configuration()
        self.refresh()

    def refresh(self) -> None:
        try:
            state = self._services.load_ai_generation_state()
        except Exception as error:
            self._set_enabled(False)
            self.status.setText(user_error_message(error, "AI 状态加载失败；手工编辑仍可使用"))
            return
        self._operation_id = state.running_operation_id
        self._set_enabled(self._enabled and self._operation_id is None)
        self.cancel_button.setEnabled(self._operation_id is not None)
        if not self._enabled:
            self.status.setText("未配置 AI，可继续手工编辑和导出")
        elif self._operation_id is not None:
            self.status.setText("AI 正在生成，请稍候")
        elif state.failed_sections:
            self.status.setText("生成失败，可重试失败栏目")
        elif state.previews:
            self.status.setText("AI 预览已生成，请确认采用或拒绝")
        else:
            self.status.setText("AI 已就绪")

        previews = {preview.section_code: preview for preview in state.previews}
        for section_code, _label in _SECTION_LABELS:
            preview = previews.get(section_code)
            failed = state.failed_sections.get(section_code)
            result = self._results[section_code]
            if preview is not None:
                self._preview_ids[section_code] = preview.preview_id
                result.setPlainText(
                    json.dumps(preview.output, ensure_ascii=False, indent=2, sort_keys=True)
                )
                result.show()
                self._adopt_buttons[section_code].show()
                self._reject_buttons[section_code].show()
            else:
                self._preview_ids.pop(section_code, None)
                result.hide()
                self._adopt_buttons[section_code].hide()
                self._reject_buttons[section_code].hide()
            self._retry_buttons[section_code].setVisible(failed is not None)
            if failed is not None:
                self._retry_buttons[section_code].setToolTip(failed)

    def context_changed(self) -> None:
        self._timer.start()
        self._reload_configuration()
        self.refresh()

    def leave_page(self) -> None:
        self._timer.stop()
        if self._operation_id is not None:
            self._services.cancel_ai_generation(self._operation_id)
            self._operation_id = None

    def _reload_configuration(self) -> None:
        try:
            self._enabled = self._services.load_ai_settings().enabled
        except Exception as error:
            self._enabled = False
            self.status.setText(user_error_message(error, "AI 设置加载失败；手工编辑仍可使用"))

    def _set_enabled(self, enabled: bool) -> None:
        self.batch_button.setEnabled(enabled)
        for button in self._generate_buttons.values():
            button.setEnabled(enabled)

    def _start_section(self, section_code: str) -> None:
        if not self._on_save_visible_content():
            self.status.setText("请先解决当前教案保存失败后再生成")
            return
        try:
            accepted = self._services.start_ai_generation(
                section_code,
                self.teacher_context.toPlainText(),
            )
        except Exception as error:
            self.status.setText(user_error_message(error, "AI 生成启动失败"))
            return
        self._operation_id = accepted.operation_id
        self.refresh()

    def _start_batch(self) -> None:
        if not self._on_save_visible_content():
            self.status.setText("请先解决当前教案保存失败后再生成")
            return
        try:
            accepted = self._services.start_ai_batch(self.teacher_context.toPlainText())
        except Exception as error:
            self.status.setText(user_error_message(error, "AI 一键生成启动失败"))
            return
        self._operation_id = accepted.operation_id
        self.refresh()

    def _adopt(self, section_code: str) -> None:
        preview_id = self._preview_ids.get(section_code)
        if preview_id is None:
            return
        if not self._on_save_visible_content():
            self.status.setText("请先解决当前教案保存失败后再采用")
            return
        try:
            self._services.adopt_ai_preview(preview_id)
            self._on_content_changed()
        except Exception as error:
            self.status.setText(user_error_message(error, "AI 预览采用失败"))
            return
        self.refresh()

    def _reject(self, section_code: str) -> None:
        preview_id = self._preview_ids.get(section_code)
        if preview_id is None:
            return
        try:
            self._services.reject_ai_preview(preview_id)
        except Exception as error:
            self.status.setText(user_error_message(error, "AI 预览拒绝失败"))
            return
        self.refresh()

    def _cancel(self) -> None:
        if self._operation_id is None:
            return
        result = self._services.cancel_ai_generation(self._operation_id)
        self.status.setText(result.message)
        self.refresh()
