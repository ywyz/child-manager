"""首次设置向导。"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from kindergarten_manager.ui.errors import user_error_message
from kindergarten_manager.ui.ports import DesktopServices

SETUP_FIELDS = {
    "teacher_name": "编写教师",
    "kindergarten_name": "幼儿园名称",
    "semester_name": "当前学期",
    "class_name": "班级名称",
}


def build_first_run_page(on_complete: Callable[[dict[str, str]], None]) -> QWidget:
    page = QWidget()
    page.setObjectName("first_run_page")
    outer = QHBoxLayout(page)
    outer.setContentsMargins(32, 28, 32, 28)
    outer.addStretch()
    card = QFrame()
    card.setObjectName("setup_card")
    card.setMaximumWidth(620)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(36, 30, 36, 30)
    layout.setSpacing(14)
    title = QLabel("开始使用幼儿园管理助手")
    title.setProperty("role", "pageTitle")
    layout.addWidget(title)
    description = QLabel("填写基础信息与学期日期，系统将创建第一份一日活动计划。")
    description.setProperty("role", "muted")
    description.setWordWrap(True)
    layout.addWidget(description)
    form = QFormLayout()
    form.setHorizontalSpacing(18)
    form.setVerticalSpacing(12)
    fields: dict[str, QLineEdit] = {}
    for object_name, label in SETUP_FIELDS.items():
        field = QLineEdit()
        field.setObjectName(object_name)
        field.setAccessibleName(label)
        fields[object_name] = field
        form.addRow(label, field)

    current = QDate.currentDate()
    semester_dates: dict[str, QDateEdit] = {}
    for object_name, label, value in (
        ("semester_start_date", "学期开始日期", QDate(current.year(), 1, 1)),
        ("semester_end_date", "学期结束日期", QDate(current.year(), 12, 31)),
    ):
        field = QDateEdit(value)
        field.setObjectName(object_name)
        field.setAccessibleName(label)
        field.setCalendarPopup(True)
        field.setDisplayFormat("yyyy年M月d日")
        semester_dates[object_name] = field
        form.addRow(label, field)
    layout.addLayout(form)

    status = QLabel("")
    status.setObjectName("setup_status")

    def complete() -> None:
        values = {name: field.text() for name, field in fields.items()}
        values.update(
            {name: field.date().toString("yyyy-MM-dd") for name, field in semester_dates.items()}
        )
        try:
            on_complete(values)
        except Exception as error:
            status.setText(user_error_message(error, "设置保存失败，请检查输入后重试"))

    button = QPushButton("完成设置并创建教案")
    button.setObjectName("complete_setup")
    button.setProperty("kind", "primary")
    button.clicked.connect(complete)
    layout.addWidget(button)
    layout.addWidget(status)
    outer.addWidget(card, 1)
    outer.addStretch()
    return page


def build_first_run_daily_plan_window(*, services: DesktopServices) -> QWidget:
    from kindergarten_manager.ui.main_window import DesktopMainWindow

    return DesktopMainWindow(services)
