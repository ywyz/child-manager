"""首次设置向导。"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

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
    layout = QVBoxLayout(page)
    form = QFormLayout()
    fields: dict[str, QLineEdit] = {}
    for object_name, label in SETUP_FIELDS.items():
        field = QLineEdit()
        field.setObjectName(object_name)
        field.setAccessibleName(label)
        fields[object_name] = field
        form.addRow(label, field)
    layout.addLayout(form)

    status = QLabel("")
    status.setObjectName("setup_status")

    def complete() -> None:
        values = {name: field.text() for name, field in fields.items()}
        try:
            on_complete(values)
        except Exception as error:
            status.setText(user_error_message(error, "设置保存失败，请检查输入后重试"))

    button = QPushButton("完成设置并创建教案")
    button.setObjectName("complete_setup")
    button.clicked.connect(complete)
    layout.addWidget(button)
    layout.addWidget(status)
    return page


def build_first_run_daily_plan_window(*, services: DesktopServices) -> QWidget:
    from kindergarten_manager.ui.main_window import DesktopMainWindow

    return DesktopMainWindow(services)
