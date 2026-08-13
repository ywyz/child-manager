"""桌面外观与当前学期设置页。"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
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


class SettingsPage(QWidget):
    def __init__(
        self,
        services: DesktopServices,
        *,
        on_theme_changed: Callable[[str], None],
        on_back: Callable[[], None],
        on_open_ai_settings: Callable[[], None],
    ) -> None:
        super().__init__()
        self.setObjectName("settings_page")
        self._services = services
        self._on_theme_changed = on_theme_changed

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)
        heading = QHBoxLayout()
        title = QLabel("设置")
        title.setProperty("role", "pageTitle")
        heading.addWidget(title)
        heading.addStretch()
        back = QPushButton("返回一日活动计划")
        back.setObjectName("back_to_plan")
        back.clicked.connect(on_back)
        heading.addWidget(back)
        ai_settings = QPushButton("AI 设置（可选）")
        ai_settings.setObjectName("open_ai_settings")
        ai_settings.clicked.connect(on_open_ai_settings)
        heading.addWidget(ai_settings)
        outer.addLayout(heading)

        card = QFrame()
        card.setObjectName("settings_card")
        card.setMaximumWidth(760)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 26)
        card_layout.setSpacing(14)

        appearance_title = QLabel("外观")
        appearance_title.setProperty("role", "sectionTitle")
        card_layout.addWidget(appearance_title)
        appearance_note = QLabel("可跟随 Windows 系统，也可以固定为浅色或深色。")
        appearance_note.setProperty("role", "muted")
        card_layout.addWidget(appearance_note)
        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        self.theme = QComboBox()
        self.theme.setObjectName("theme_preference")
        self.theme.setAccessibleName("外观主题")
        for text, value in (("跟随系统", "system"), ("浅色", "light"), ("深色", "dark")):
            self.theme.addItem(text, value)
        form.addRow("外观主题", self.theme)

        basic_title = QLabel("幼儿园与当前班级")
        basic_title.setProperty("role", "sectionTitle")
        card_layout.addLayout(form)
        card_layout.addSpacing(8)
        card_layout.addWidget(basic_title)
        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        self.kindergarten_name = QLineEdit()
        self.kindergarten_name.setObjectName("kindergarten_settings_name")
        form.addRow("幼儿园名称", self.kindergarten_name)
        self.teacher_name = QLineEdit()
        self.teacher_name.setObjectName("teacher_settings_name")
        form.addRow("教师姓名", self.teacher_name)
        self.class_name = QLineEdit()
        self.class_name.setObjectName("class_settings_name")
        form.addRow("当前班级", self.class_name)
        self.age_group = QComboBox()
        self.age_group.setObjectName("class_settings_age_group")
        for text, value in (
            ("托班", "nursery"),
            ("小班", "small"),
            ("中班", "middle"),
            ("大班", "large"),
            ("混龄班", "mixed"),
        ):
            self.age_group.addItem(text, value)
        form.addRow("年龄段", self.age_group)
        self.indoor_areas = QPlainTextEdit()
        self.indoor_areas.setObjectName("class_settings_indoor_areas")
        self.indoor_areas.setMinimumHeight(90)
        form.addRow("室内区域（逐行）", self.indoor_areas)
        self.outdoor_areas = QPlainTextEdit()
        self.outdoor_areas.setObjectName("class_settings_outdoor_areas")
        self.outdoor_areas.setMinimumHeight(90)
        form.addRow("户外区域（逐行）", self.outdoor_areas)

        semester_title = QLabel("当前学期")
        semester_title.setProperty("role", "sectionTitle")
        card_layout.addLayout(form)
        card_layout.addSpacing(8)
        card_layout.addWidget(semester_title)
        self.semester_name = QLineEdit()
        self.semester_name.setObjectName("semester_settings_name")
        self.semester_name.setAccessibleName("当前学期名称")
        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.addRow("学期名称", self.semester_name)
        self.semester_start = self._date_editor("semester_settings_start_date", "学期开始日期")
        form.addRow("开始日期", self.semester_start)
        self.semester_end = self._date_editor("semester_settings_end_date", "学期结束日期")
        form.addRow("结束日期", self.semester_end)
        card_layout.addLayout(form)

        self.status = QLabel("")
        self.status.setObjectName("settings_status")
        self.status.setWordWrap(True)
        card_layout.addWidget(self.status)
        save = QPushButton("保存设置")
        save.setObjectName("save_settings")
        save.setProperty("kind", "primary")
        save.clicked.connect(self.save)
        card_layout.addWidget(save)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        row = QHBoxLayout(host)
        row.addStretch()
        row.addWidget(card, 1)
        row.addStretch()
        scroll.setWidget(host)
        outer.addWidget(scroll, 1)

    def reload(self) -> None:
        try:
            context = self._services.load_settings()
        except Exception as error:
            self.status.setText(user_error_message(error, "设置加载失败，请重试"))
            return
        self.theme.setCurrentIndex(max(self.theme.findData(context.theme), 0))
        self.kindergarten_name.setText(context.kindergarten_name)
        self.teacher_name.setText(context.teacher_name)
        self.class_name.setText(context.class_name)
        self.age_group.setCurrentIndex(max(self.age_group.findData(context.age_group), 0))
        self.indoor_areas.setPlainText("\n".join(context.indoor_areas))
        self.outdoor_areas.setPlainText("\n".join(context.outdoor_areas))
        self.semester_name.setText(context.semester_name)
        self.semester_start.setDate(
            QDate(
                context.semester_start_date.year,
                context.semester_start_date.month,
                context.semester_start_date.day,
            )
        )
        self.semester_end.setDate(
            QDate(
                context.semester_end_date.year,
                context.semester_end_date.month,
                context.semester_end_date.day,
            )
        )
        self.status.setText("")

    def save(self) -> None:
        values = {
            "theme": str(self.theme.currentData()),
            "kindergarten_name": self.kindergarten_name.text(),
            "teacher_name": self.teacher_name.text(),
            "class_name": self.class_name.text(),
            "age_group": str(self.age_group.currentData()),
            "indoor_areas": self.indoor_areas.toPlainText(),
            "outdoor_areas": self.outdoor_areas.toPlainText(),
            "semester_name": self.semester_name.text(),
            "semester_start_date": self.semester_start.date().toString("yyyy-MM-dd"),
            "semester_end_date": self.semester_end.date().toString("yyyy-MM-dd"),
        }
        try:
            saved = self._services.update_settings(values)
        except Exception as error:
            self.status.setText(user_error_message(error, "设置保存失败，请检查输入后重试"))
            return
        self._on_theme_changed(saved.theme)
        self.status.setText("设置已保存")

    @staticmethod
    def _date_editor(object_name: str, accessible_name: str) -> QDateEdit:
        editor = QDateEdit()
        editor.setObjectName(object_name)
        editor.setAccessibleName(accessible_name)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy年M月d日")
        return editor
