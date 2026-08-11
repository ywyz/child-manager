"""桌面切片使用的确定性、离线测试夹具。"""

from __future__ import annotations

import os
import socket
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@dataclass(frozen=True, slots=True)
class FictionalBusinessData:
    teacher_name: str = "测试教师"
    kindergarten_name: str = "星河幼儿园"
    semester_name: str = "2026 年秋季学期"
    class_name: str = "向日葵班"
    indoor_areas: tuple[str, ...] = ("建构区", "阅读区")
    outdoor_areas: tuple[str, ...] = ("沙水区", "种植区")


@dataclass(frozen=True, slots=True)
class FixedClock:
    value: datetime = datetime(2026, 9, 7, 1, 2, 3, tzinfo=UTC)

    def now(self) -> datetime:
        return self.value

    def now_utc_ms(self) -> int:
        return int(self.value.timestamp() * 1000)


@pytest.fixture
def data_root(tmp_path: Path) -> Path:
    root = tmp_path / "desktop-data"
    root.mkdir()
    return root


@pytest.fixture
def fixed_clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def fictional_business_data() -> FictionalBusinessData:
    return FictionalBusinessData()


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def teacherplan_template_path(project_root: Path) -> Path:
    return project_root / "templates" / "teacherplan" / "teacherplan.docx"


@pytest.fixture
def qt_offscreen(qapp: QApplication) -> QApplication:
    assert QApplication.platformName().lower() == "offscreen"
    return qapp


@pytest.fixture(autouse=True)
def forbid_desktop_network(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """桌面常规测试连回环网络也不允许，必须使用显式替身。"""

    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("桌面测试禁止真实网络连接")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    yield
