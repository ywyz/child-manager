"""文本与视觉模型预配置及可恢复默认提示词设置页。"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from kindergarten_manager.ui.errors import user_error_message
from kindergarten_manager.ui.ports import DesktopServices

_PROMPTS = (
    ("morning_activity", "晨间活动"),
    ("morning_talk", "晨间谈话"),
    ("indoor_area_game", "室内区域游戏"),
    ("afternoon_outdoor_game", "下午户外游戏"),
    ("daily_reflection", "一日活动反思"),
    ("group_activity", "集体活动原稿拆分"),
)


class AiSettingsPage(QWidget):
    def __init__(self, services: DesktopServices, *, on_back: Callable[[], None]) -> None:
        super().__init__()
        self.setObjectName("ai_settings_page")
        self._services = services
        self._prompt_editors: dict[str, QPlainTextEdit] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        heading = QHBoxLayout()
        title = QLabel("AI 设置（可选）")
        title.setProperty("role", "pageTitle")
        heading.addWidget(title)
        heading.addStretch()
        back = QPushButton("返回设置")
        back.setObjectName("back_to_settings")
        back.clicked.connect(on_back)
        heading.addWidget(back)
        outer.addLayout(heading)

        note = QLabel(
            "文本与视觉模型均使用 OpenAI 兼容接口。API Key 仅写入操作系统凭据存储，"
            "不进入 SQLite、日志或页面回显；未配置 AI 不影响手工编辑与导出。"
        )
        note.setWordWrap(True)
        note.setProperty("role", "muted")
        outer.addWidget(note)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        content = QVBoxLayout(host)
        model_card = QFrame()
        model_card.setObjectName("settings_card")
        model_form = QFormLayout(model_card)
        self.enabled = QCheckBox("启用当前模型")
        self.enabled.setObjectName("ai_enabled")
        model_form.addRow("状态", self.enabled)
        self.base_url = QLineEdit()
        self.base_url.setObjectName("ai_base_url")
        self.base_url.setPlaceholderText("https://provider.example/v1 或回环 HTTP 地址")
        model_form.addRow("API 地址", self.base_url)
        self.model_name = QLineEdit()
        self.model_name.setObjectName("ai_model_name")
        model_form.addRow("模型名", self.model_name)
        self.api_key = QLineEdit()
        self.api_key.setObjectName("ai_api_key")
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("留空表示保留现有凭据")
        model_form.addRow("API Key", self.api_key)
        content.addWidget(model_card)

        vision_card = QFrame()
        vision_card.setObjectName("settings_card")
        vision_form = QFormLayout(vision_card)
        vision_note = QLabel("下一期视觉任务预配置；本期不上传照片，也不发起视觉请求。")
        vision_note.setWordWrap(True)
        vision_note.setProperty("role", "muted")
        vision_form.addRow(vision_note)
        self.vision_enabled = QCheckBox("启用视觉模型")
        self.vision_enabled.setObjectName("vision_ai_enabled")
        vision_form.addRow("状态", self.vision_enabled)
        self.vision_base_url = QLineEdit()
        self.vision_base_url.setObjectName("vision_ai_base_url")
        self.vision_base_url.setPlaceholderText("https://provider.example/v1 或回环 HTTP 地址")
        vision_form.addRow("视觉 API 地址", self.vision_base_url)
        self.vision_model_name = QLineEdit()
        self.vision_model_name.setObjectName("vision_ai_model_name")
        vision_form.addRow("视觉模型名", self.vision_model_name)
        self.vision_api_key = QLineEdit()
        self.vision_api_key.setObjectName("vision_ai_api_key")
        self.vision_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.vision_api_key.setPlaceholderText("留空表示保留现有凭据")
        vision_form.addRow("视觉 API Key", self.vision_api_key)
        content.addWidget(vision_card)

        prompt_title = QLabel("提示词覆盖")
        prompt_title.setProperty("role", "sectionTitle")
        content.addWidget(prompt_title)
        for prompt_code, label_text in _PROMPTS:
            card = QFrame()
            card.setObjectName("field_card")
            layout = QVBoxLayout(card)
            label_row = QHBoxLayout()
            label = QLabel(label_text)
            label.setProperty("role", "fieldLabel")
            label_row.addWidget(label)
            label_row.addStretch()
            reset = QPushButton("恢复内置默认")
            reset.setObjectName(f"reset_prompt_{prompt_code}")
            reset.clicked.connect(lambda _checked=False, code=prompt_code: self._reset_prompt(code))
            label_row.addWidget(reset)
            layout.addLayout(label_row)
            editor = QPlainTextEdit()
            editor.setObjectName(f"prompt_{prompt_code}")
            editor.setMinimumHeight(100)
            self._prompt_editors[prompt_code] = editor
            layout.addWidget(editor)
            content.addWidget(card)
        content.addStretch()
        scroll.setWidget(host)
        outer.addWidget(scroll, 1)

        self.status = QLabel("")
        self.status.setObjectName("ai_settings_status")
        self.status.setWordWrap(True)
        outer.addWidget(self.status)
        save = QPushButton("保存 AI 设置")
        save.setObjectName("save_ai_settings")
        save.setProperty("kind", "primary")
        save.clicked.connect(self.save)
        outer.addWidget(save)

    def reload(self) -> None:
        try:
            view = self._services.load_ai_settings()
        except Exception as error:
            self.status.setText(user_error_message(error, "AI 设置加载失败，请重试"))
            return
        self.enabled.setChecked(bool(view.enabled))
        self.base_url.setText(view.base_url or "")
        self.model_name.setText(view.model_name or "")
        self.api_key.clear()
        self.api_key.setPlaceholderText(
            "已安全保存；留空表示保留" if view.credential_configured else "输入 API Key"
        )
        self.vision_enabled.setChecked(bool(view.vision_enabled))
        self.vision_base_url.setText(view.vision_base_url or "")
        self.vision_model_name.setText(view.vision_model_name or "")
        self.vision_api_key.clear()
        self.vision_api_key.setPlaceholderText(
            "已安全保存；留空表示保留" if view.vision_credential_configured else "输入视觉 API Key"
        )
        for code, editor in self._prompt_editors.items():
            editor.setPlainText(view.prompts[code])
        self.status.setText("")

    def save(self) -> None:
        values: dict[str, object] = {
            "enabled": self.enabled.isChecked(),
            "base_url": self.base_url.text(),
            "model_name": self.model_name.text(),
            "api_key": self.api_key.text(),
            "vision_enabled": self.vision_enabled.isChecked(),
            "vision_base_url": self.vision_base_url.text(),
            "vision_model_name": self.vision_model_name.text(),
            "vision_api_key": self.vision_api_key.text(),
            "prompts": {
                code: editor.toPlainText() for code, editor in self._prompt_editors.items()
            },
        }
        try:
            self._services.save_ai_settings(values)
        except Exception as error:
            self.status.setText(user_error_message(error, "AI 设置保存失败，请检查输入"))
            return
        self.reload()
        self.status.setText("AI 设置已保存；Key 未在页面回显")

    def _reset_prompt(self, prompt_code: str) -> None:
        try:
            default = self._services.reset_ai_prompt(prompt_code)
        except Exception as error:
            self.status.setText(user_error_message(error, "恢复默认提示词失败"))
            return
        self._prompt_editors[prompt_code].setPlainText(default)
        self.status.setText("已恢复内置默认提示词")

    def _show_unavailable(self) -> None:
        self.enabled.setChecked(False)
        self.enabled.setEnabled(False)
        self.status.setText("当前环境不支持 AI 凭据；手工编辑与导出仍可使用")
