"""Slice 1 结构化一日活动计划编辑页。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kindergarten_manager.application.workspace import DailyPlanContext
from kindergarten_manager.ui.errors import user_error_message
from kindergarten_manager.ui.pages.single_export import export_current_day
from kindergarten_manager.ui.ports import DesktopServices

EditorKind = Literal["text", "lines", "areas", "process"]


@dataclass(frozen=True, slots=True)
class FieldDefinition:
    object_name: str
    label: str
    path: tuple[str, str]
    kind: EditorKind = "text"


FIELD_GROUPS: tuple[tuple[str, tuple[FieldDefinition, ...]], ...] = (
    (
        "01 晨间活动",
        (
            FieldDefinition(
                "morning_physical_cycle", "体能活动", ("morning_activity", "physical_cycle")
            ),
            FieldDefinition("morning_group_game", "集体游戏", ("morning_activity", "group_game")),
            FieldDefinition("morning_free_game", "自主游戏", ("morning_activity", "free_game")),
            FieldDefinition(
                "morning_focus_guidance", "重点指导", ("morning_activity", "focus_guidance")
            ),
            FieldDefinition(
                "morning_objectives",
                "活动目标（逐行）",
                ("morning_activity", "objectives"),
                "lines",
            ),
            FieldDefinition(
                "morning_guidance_points",
                "指导要点（逐行）",
                ("morning_activity", "guidance_points"),
                "lines",
            ),
        ),
    ),
    (
        "02 晨间谈话",
        (
            FieldDefinition("morning_talk_topic", "谈话话题", ("morning_talk", "topic")),
            FieldDefinition(
                "morning_talk_questions", "问题设计（逐行）", ("morning_talk", "questions"), "lines"
            ),
        ),
    ),
    (
        "03 集体活动",
        (
            FieldDefinition("group_activity_theme", "活动主题", ("group_activity", "theme")),
            FieldDefinition(
                "group_activity_objectives",
                "活动目标（逐行）",
                ("group_activity", "objectives"),
                "lines",
            ),
            FieldDefinition(
                "group_activity_preparation",
                "活动准备（逐行）",
                ("group_activity", "preparation"),
                "lines",
            ),
            FieldDefinition("group_activity_focus", "活动重点", ("group_activity", "focus")),
            FieldDefinition(
                "group_activity_difficulty", "活动难点", ("group_activity", "difficulty")
            ),
            FieldDefinition(
                "group_activity_process",
                "活动过程（按环节分格）",
                ("group_activity", "process"),
                "process",
            ),
        ),
    ),
    (
        "04 室内区域游戏",
        (
            FieldDefinition(
                "indoor_area_names", "游戏区域（逐行）", ("indoor_area_game", "areas"), "areas"
            ),
            FieldDefinition(
                "indoor_focus_guidance", "重点指导", ("indoor_area_game", "focus_guidance")
            ),
            FieldDefinition(
                "indoor_objectives", "活动目标（逐行）", ("indoor_area_game", "objectives"), "lines"
            ),
            FieldDefinition(
                "indoor_guidance_points",
                "指导要点（逐行）",
                ("indoor_area_game", "guidance_points"),
                "lines",
            ),
            FieldDefinition(
                "indoor_support_strategies",
                "支持策略（逐行）",
                ("indoor_area_game", "support_strategies"),
                "lines",
            ),
        ),
    ),
    (
        "05 下午户外游戏",
        (
            FieldDefinition(
                "afternoon_outdoor_area_names",
                "游戏区域（逐行）",
                ("afternoon_outdoor_game", "areas"),
                "areas",
            ),
            FieldDefinition(
                "afternoon_focus_guidance", "重点指导", ("afternoon_outdoor_game", "focus_guidance")
            ),
            FieldDefinition(
                "afternoon_objectives",
                "活动目标（逐行）",
                ("afternoon_outdoor_game", "objectives"),
                "lines",
            ),
            FieldDefinition(
                "afternoon_guidance_points",
                "指导要点（逐行）",
                ("afternoon_outdoor_game", "guidance_points"),
                "lines",
            ),
            FieldDefinition(
                "afternoon_support_strategies",
                "支持策略（逐行）",
                ("afternoon_outdoor_game", "support_strategies"),
                "lines",
            ),
        ),
    ),
    (
        "一日活动反思",
        (
            FieldDefinition(
                "daily_reflection_highlights", "活动亮点", ("daily_reflection", "highlights")
            ),
            FieldDefinition("daily_reflection_issues", "存在问题", ("daily_reflection", "issues")),
            FieldDefinition(
                "daily_reflection_adjustments", "调整策略", ("daily_reflection", "adjustments")
            ),
        ),
    ),
)


class ProcessEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(("环节标题", "步骤内容（逐行）"))
        self.table.setObjectName("group_activity_process_table")
        layout.addWidget(self.table)
        add = QPushButton("增加活动环节")
        add.setObjectName("add_group_activity_process")
        add.clicked.connect(self._append_row)
        layout.addWidget(add)
        self._append_row()

    def set_value(self, value: object) -> None:
        self.table.setRowCount(0)
        if isinstance(value, list):
            for step in value:
                if isinstance(step, dict):
                    lines = step.get("lines")
                    self._append_row(
                        str(step.get("heading", "")),
                        "\n".join(str(item) for item in lines) if isinstance(lines, list) else "",
                        is_ai_added=step.get("is_ai_added") is True,
                    )
        if self.table.rowCount() == 0:
            self._append_row()

    def value(self) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for row in range(self.table.rowCount()):
            heading_item = self.table.item(row, 0)
            lines_item = self.table.item(row, 1)
            heading = heading_item.text().strip() if heading_item else ""
            lines = _lines(lines_item.text() if lines_item else "")
            if heading or lines:
                result.append(
                    {
                        "heading": heading,
                        "lines": lines,
                        "is_ai_added": bool(
                            heading_item and heading_item.data(Qt.ItemDataRole.UserRole) is True
                        ),
                    }
                )
        return result

    def _append_row(
        self,
        heading: str = "",
        lines: str = "",
        *,
        is_ai_added: bool = False,
    ) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        heading_item = QTableWidgetItem(heading)
        heading_item.setData(Qt.ItemDataRole.UserRole, is_ai_added)
        self.table.setItem(row, 0, heading_item)
        self.table.setItem(row, 1, QTableWidgetItem(lines))


class DailyPlanPage(QWidget):
    def __init__(self, services: DesktopServices) -> None:
        super().__init__()
        self._services = services
        self._content: dict[str, Any] = {}
        self._fields: dict[str, QWidget] = {}
        self._loading_context = False

        layout = QVBoxLayout(self)
        context = QHBoxLayout()
        self.class_context = QComboBox()
        self.class_context.setObjectName("class_context")
        self.class_context.setAccessibleName("班级")
        context.addWidget(QLabel("班级"))
        context.addWidget(self.class_context)
        self.plan_date = QDateEdit()
        self.plan_date.setObjectName("plan_date")
        self.plan_date.setAccessibleName("教案日期")
        self.plan_date.setCalendarPopup(True)
        context.addWidget(QLabel("日期"))
        context.addWidget(self.plan_date)
        layout.addLayout(context)

        self.calendar_warnings = QLabel("")
        self.calendar_warnings.setObjectName("calendar_warnings")
        self.calendar_warnings.setWordWrap(True)
        layout.addWidget(self.calendar_warnings)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_host = QWidget()
        form_layout = QVBoxLayout(form_host)
        for title, definitions in FIELD_GROUPS:
            group = QGroupBox(title)
            form = QFormLayout(group)
            for definition in definitions:
                editor = self._build_editor(definition)
                self._fields[definition.object_name] = editor
                form.addRow(definition.label, editor)
            form_layout.addWidget(group)
        scroll.setWidget(form_host)
        layout.addWidget(scroll)

        save = QPushButton("保存教案")
        save.setObjectName("save_plan")
        save.clicked.connect(self.save)
        layout.addWidget(save)
        self.save_status = QLabel("尚未保存")
        self.save_status.setObjectName("save_status")
        layout.addWidget(self.save_status)

        export = QPushButton("导出当天 Word")
        export.setObjectName("export_day")
        export.clicked.connect(self.export)
        layout.addWidget(export)
        self.export_status = QLabel("")
        self.export_status.setObjectName("export_status")
        layout.addWidget(self.export_status)

        self.class_context.currentIndexChanged.connect(self._context_changed)
        self.plan_date.dateChanged.connect(self._context_changed)

    def reload(self) -> None:
        try:
            context = self._services.load_plan_context()
            self._apply_context(context)
            self._load_content()
        except Exception as error:
            self.save_status.setText(user_error_message(error, "教案加载失败，请检查设置后重试"))

    def save(self) -> None:
        for _title, definitions in FIELD_GROUPS:
            for definition in definitions:
                _write(
                    self._content,
                    definition.path,
                    self._editor_value(self._fields[definition.object_name], definition.kind),
                )
        try:
            self._services.save_current_plan(self._content)
        except Exception as error:
            self.save_status.setText(user_error_message(error, "保存失败，请检查设置后重试"))
            return
        self.save_status.setText("已保存")

    def export(self) -> None:
        export_current_day(parent=self, services=self._services, status=self.export_status)

    def _context_changed(self) -> None:
        if self._loading_context or self.class_context.currentIndex() < 0:
            return
        class_id = self.class_context.currentData()
        selected_date = self.plan_date.date().toPython()
        if not isinstance(class_id, int) or not isinstance(selected_date, date):
            return
        try:
            context = self._services.select_plan_context(class_id, selected_date)
            self._apply_context(context)
            self._load_content()
        except Exception as error:
            self.save_status.setText(user_error_message(error, "切换教案失败，请重试"))

    def _apply_context(self, context: DailyPlanContext) -> None:
        self._loading_context = True
        try:
            self.class_context.clear()
            for item in context.classes:
                self.class_context.addItem(item.name, item.id)
            selected_index = self.class_context.findData(context.selected_class_id)
            self.class_context.setCurrentIndex(max(selected_index, 0))
            self.plan_date.setDate(
                QDate(context.plan_date.year, context.plan_date.month, context.plan_date.day)
            )
            self.calendar_warnings.setText("；".join(context.warnings))
        finally:
            self._loading_context = False

    def _load_content(self) -> None:
        self._content = self._services.load_current_plan()
        for _title, definitions in FIELD_GROUPS:
            for definition in definitions:
                self._set_editor(
                    self._fields[definition.object_name],
                    definition.kind,
                    _read(self._content, definition.path),
                )

    @staticmethod
    def _build_editor(definition: FieldDefinition) -> QWidget:
        if definition.kind == "text":
            editor: QWidget = QLineEdit()
        elif definition.kind in {"lines", "areas"}:
            plain = QPlainTextEdit()
            plain.setMaximumHeight(80)
            editor = plain
        else:
            editor = ProcessEditor()
        editor.setObjectName(definition.object_name)
        editor.setAccessibleName(definition.label)
        return editor

    @staticmethod
    def _set_editor(editor: QWidget, kind: EditorKind, value: object) -> None:
        if kind == "text" and isinstance(editor, QLineEdit):
            editor.setText(str(value or ""))
        elif kind in {"lines", "areas"} and isinstance(editor, QPlainTextEdit):
            editor.setPlainText(
                "\n".join(str(item) for item in value) if isinstance(value, list) else ""
            )
        elif kind == "process" and isinstance(editor, ProcessEditor):
            editor.set_value(value)

    @staticmethod
    def _editor_value(editor: QWidget, kind: EditorKind) -> object:
        if kind == "text" and isinstance(editor, QLineEdit):
            return editor.text().strip()
        if kind in {"lines", "areas"} and isinstance(editor, QPlainTextEdit):
            return _lines(editor.toPlainText())
        if kind == "process" and isinstance(editor, ProcessEditor):
            return editor.value()
        return ""


def _read(content: dict[str, Any], path: tuple[str, str]) -> object:
    section = content.get(path[0])
    return section.get(path[1]) if isinstance(section, dict) else None


def _write(content: dict[str, Any], path: tuple[str, str], value: object) -> None:
    section = content.setdefault(path[0], {})
    if not isinstance(section, dict):
        section = {}
        content[path[0]] = section
    section[path[1]] = value


def _lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]
