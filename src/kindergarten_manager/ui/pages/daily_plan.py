"""Slice 1 结构化一日活动计划编辑页。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Literal

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
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
        "03 室内区域游戏",
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
        "04 下午户外游戏",
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
        "05 集体活动",
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
        "06 一日活动反思",
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

SECTION_ROWS: dict[str, tuple[tuple[str, ...], ...]] = {
    "01 晨间活动": (
        ("morning_physical_cycle", "morning_group_game"),
        ("morning_free_game", "morning_focus_guidance"),
        ("morning_objectives", "morning_guidance_points"),
    ),
    "02 晨间谈话": (("morning_talk_topic",), ("morning_talk_questions",)),
    "03 室内区域游戏": (
        ("indoor_area_names", "indoor_focus_guidance"),
        ("indoor_objectives", "indoor_guidance_points"),
        ("indoor_support_strategies",),
    ),
    "04 下午户外游戏": (
        ("afternoon_outdoor_area_names", "afternoon_focus_guidance"),
        ("afternoon_objectives", "afternoon_guidance_points"),
        ("afternoon_support_strategies",),
    ),
    "05 集体活动": (
        ("group_activity_theme", "group_activity_preparation"),
        ("group_activity_objectives",),
        ("group_activity_focus", "group_activity_difficulty"),
        ("group_activity_process",),
    ),
    "06 一日活动反思": (
        ("daily_reflection_highlights", "daily_reflection_issues"),
        ("daily_reflection_adjustments",),
    ),
}


class ProcessEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(("环节标题", "步骤内容（逐行）"))
        self.table.setObjectName("group_activity_process_table")
        self.table.setMinimumHeight(260)
        self.table.setWordWrap(True)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 180)
        self.table.verticalHeader().setDefaultSectionSize(72)
        layout.addWidget(self.table, 1)
        add = QPushButton("增加活动环节")
        add.setObjectName("add_group_activity_process")
        add.clicked.connect(self._append_row)
        layout.addWidget(add)
        self.setMinimumHeight(320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        self.setObjectName("daily_plan_page")
        self._services = services
        self._content: dict[str, Any] = {}
        self._fields: dict[str, QWidget] = {}
        self._loading_context = False
        self._home_date: date | None = None
        self._teaching_week_text = ""
        self._section_buttons: list[QPushButton] = []
        self._week_day_buttons: list[QPushButton] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        top = QFrame()
        top.setObjectName("top_context")
        context = QHBoxLayout(top)
        context.setContentsMargins(18, 12, 18, 12)
        context.setSpacing(10)
        title_block = QVBoxLayout()
        title = QLabel("一日活动计划")
        title.setProperty("role", "pageTitle")
        title_block.addWidget(title)
        self.context_summary = QLabel("选择班级与日期开始编辑")
        self.context_summary.setObjectName("context_summary")
        self.context_summary.setProperty("role", "muted")
        title_block.addWidget(self.context_summary)
        context.addLayout(title_block)
        context.addSpacing(12)
        self.class_context = QComboBox()
        self.class_context.setObjectName("class_context")
        self.class_context.setAccessibleName("班级")
        self.class_context.setMinimumWidth(130)
        context.addWidget(QLabel("班级"))
        context.addWidget(self.class_context)
        self.plan_date = QDateEdit()
        self.plan_date.setObjectName("plan_date")
        self.plan_date.setAccessibleName("教案日期")
        self.plan_date.setCalendarPopup(True)
        self.plan_date.setDisplayFormat("yyyy年M月d日")
        context.addWidget(QLabel("日期"))
        context.addWidget(self.plan_date)
        context.addStretch()
        self.save_status = QLabel("尚未保存")
        self.save_status.setObjectName("save_status")
        self.save_status.setProperty("tone", "status")
        context.addWidget(self.save_status)
        save = QPushButton("保存教案")
        save.setObjectName("save_plan")
        save.clicked.connect(self.save)
        context.addWidget(save)
        export = QPushButton("导出当天 Word")
        export.setObjectName("export_day")
        export.setProperty("kind", "primary")
        export.clicked.connect(self.export)
        context.addWidget(export)
        layout.addWidget(top)

        week = QFrame()
        week.setObjectName("week_strip")
        week_layout = QVBoxLayout(week)
        week_layout.setContentsMargins(14, 10, 14, 12)
        week_layout.setSpacing(8)
        week_controls = QHBoxLayout()
        previous = QPushButton("← 上一周")
        previous.setObjectName("previous_week")
        previous.clicked.connect(lambda: self._move_week(-7))
        week_controls.addWidget(previous)
        week_controls.addStretch()
        self.week_range = QLabel("")
        self.week_range.setObjectName("week_range")
        self.week_range.setProperty("role", "sectionTitle")
        week_controls.addWidget(self.week_range)
        week_controls.addStretch()
        current = QPushButton("回到本周")
        current.setObjectName("current_week")
        current.clicked.connect(self._return_home_week)
        week_controls.addWidget(current)
        following = QPushButton("下一周 →")
        following.setObjectName("next_week")
        following.clicked.connect(lambda: self._move_week(7))
        week_controls.addWidget(following)
        week_layout.addLayout(week_controls)
        days = QHBoxLayout()
        days.setSpacing(8)
        for index in range(5):
            day_button = QPushButton()
            day_button.setObjectName(f"week_day_{index}")
            day_button.setMinimumHeight(52)
            day_button.clicked.connect(
                lambda _checked=False, weekday=index: self._select_weekday(weekday)
            )
            days.addWidget(day_button, 1)
            self._week_day_buttons.append(day_button)
        week_layout.addLayout(days)
        layout.addWidget(week)

        self.calendar_warnings = QLabel("")
        self.calendar_warnings.setObjectName("calendar_warnings")
        self.calendar_warnings.setWordWrap(True)
        self.calendar_warnings.setProperty("tone", "warning")
        self.calendar_warnings.hide()
        layout.addWidget(self.calendar_warnings)

        work = QHBoxLayout()
        work.setSpacing(12)
        navigation = QFrame()
        navigation.setObjectName("section_navigation")
        navigation.setFixedWidth(205)
        navigation_layout = QVBoxLayout(navigation)
        navigation_layout.setContentsMargins(12, 14, 12, 14)
        navigation_layout.setSpacing(8)
        catalog_title = QLabel("当天栏目")
        catalog_title.setProperty("role", "sectionTitle")
        navigation_layout.addWidget(catalog_title)
        self.section_stack = QStackedWidget()
        self.section_stack.setObjectName("section_editor_stack")
        for index, (section_title, definitions) in enumerate(FIELD_GROUPS):
            button = QPushButton(section_title)
            button.setObjectName(f"section_nav_{index}")
            button.setMinimumHeight(42)
            button.clicked.connect(
                lambda _checked=False, selected=index: self._select_section(selected)
            )
            navigation_layout.addWidget(button)
            self._section_buttons.append(button)
            self.section_stack.addWidget(self._build_section_page(section_title, definitions))
        navigation_layout.addStretch()
        navigation_note = QLabel("字段结构与 Word 模板一致")
        navigation_note.setWordWrap(True)
        navigation_note.setProperty("role", "muted")
        navigation_layout.addWidget(navigation_note)
        work.addWidget(navigation)
        work.addWidget(self.section_stack, 1)
        layout.addLayout(work, 1)

        self.export_status = QLabel("")
        self.export_status.setObjectName("export_status")
        self.export_status.setProperty("role", "muted")
        layout.addWidget(self.export_status)

        self.class_context.currentIndexChanged.connect(self._context_changed)
        self.plan_date.dateChanged.connect(self._context_changed)
        self._select_section(0)

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
        self._refresh_week_strip()

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
            if self._home_date is None:
                self._home_date = context.plan_date
            self._teaching_week_text = context.teaching_week_text
            self.calendar_warnings.setText("；".join(context.warnings))
            self.calendar_warnings.setVisible(bool(context.warnings))
            self.context_summary.setText(
                f"{context.plan_date:%Y年%m月%d日} · {context.teaching_week_text or '学期日期'}"
            )
            self._refresh_week_strip()
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
        self._refresh_week_strip()

    def _build_section_page(
        self,
        title: str,
        definitions: tuple[FieldDefinition, ...],
    ) -> QScrollArea:
        definitions_by_name = {item.object_name: item for item in definitions}
        scroll = QScrollArea()
        scroll.setObjectName(f"section_page_{len(self._section_buttons)}")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        host = QWidget()
        grid = QGridLayout(host)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        heading = QLabel(title)
        heading.setProperty("role", "pageTitle")
        grid.addWidget(heading, 0, 0, 1, 2)
        for row_index, names in enumerate(SECTION_ROWS[title], start=1):
            if len(names) == 1:
                grid.addWidget(
                    self._build_field_card(definitions_by_name[names[0]]),
                    row_index,
                    0,
                    1,
                    2,
                )
            else:
                grid.addWidget(self._build_field_card(definitions_by_name[names[0]]), row_index, 0)
                grid.addWidget(self._build_field_card(definitions_by_name[names[1]]), row_index, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(len(SECTION_ROWS[title]) + 1, 1)
        scroll.setWidget(host)
        return scroll

    def _build_field_card(self, definition: FieldDefinition) -> QFrame:
        card = QFrame()
        card.setObjectName("field_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 12)
        card_layout.setSpacing(6)
        label = QLabel(definition.label)
        label.setProperty("role", "fieldLabel")
        card_layout.addWidget(label)
        editor = self._build_editor(definition)
        self._fields[definition.object_name] = editor
        card_layout.addWidget(editor, 1)
        return card

    def _select_section(self, selected: int) -> None:
        self.section_stack.setCurrentIndex(selected)
        for index, button in enumerate(self._section_buttons):
            button.setProperty("sectionActive", "true" if index == selected else "false")
            button.style().unpolish(button)
            button.style().polish(button)

    def _move_week(self, days: int) -> None:
        self.plan_date.setDate(self.plan_date.date().addDays(days))

    def _return_home_week(self) -> None:
        if self._home_date is not None:
            self.plan_date.setDate(
                QDate(self._home_date.year, self._home_date.month, self._home_date.day)
            )

    def _select_weekday(self, weekday: int) -> None:
        selected = self.plan_date.date().toPython()
        if not isinstance(selected, date):
            return
        week_start = selected - timedelta(days=selected.weekday())
        target = week_start + timedelta(days=weekday)
        self.plan_date.setDate(QDate(target.year, target.month, target.day))

    def _refresh_week_strip(self) -> None:
        selected = self.plan_date.date().toPython()
        if not isinstance(selected, date):
            return
        week_start = selected - timedelta(days=selected.weekday())
        week_end = week_start + timedelta(days=4)
        week_name = self._teaching_week_text or "当前周"
        self.week_range.setText(f"{week_name} · {week_start:%Y年%m月%d日}—{week_end:%m月%d日}")
        topic = str(_read(self._content, ("group_activity", "theme")) or "待填写主题")
        for index, button in enumerate(self._week_day_buttons):
            target = week_start + timedelta(days=index)
            button.setText(
                f"{('周一', '周二', '周三', '周四', '周五')[index]}  {target.day}\n"
                f"集体：{topic if target == selected else '点击查看'}"
            )
            button.setProperty("weekActive", "true" if target == selected else "false")
            button.style().unpolish(button)
            button.style().polish(button)

    @staticmethod
    def _build_editor(definition: FieldDefinition) -> QWidget:
        if definition.kind == "text":
            editor: QWidget = QLineEdit()
        elif definition.kind in {"lines", "areas"}:
            plain = QPlainTextEdit()
            minimum_height = 90
            if definition.object_name in {
                "morning_talk_questions",
                "indoor_support_strategies",
                "afternoon_support_strategies",
                "daily_reflection_adjustments",
            }:
                minimum_height = 120
            plain.setMinimumHeight(minimum_height)
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
