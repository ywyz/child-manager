from __future__ import annotations

import socket
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from tests.desktop.conftest import FictionalBusinessData, FixedClock


def test_desktop_fixtures_are_isolated_and_fictional(
    data_root: Path,
    fixed_clock: FixedClock,
    fictional_business_data: FictionalBusinessData,
    teacherplan_template_path: Path,
) -> None:
    assert data_root.is_dir()
    assert fixed_clock.now() == datetime(2026, 9, 7, 1, 2, 3, tzinfo=UTC)
    assert fictional_business_data.teacher_name == "测试教师"
    assert teacherplan_template_path.is_file()


def test_qt_runs_offscreen(qt_offscreen: QApplication) -> None:
    assert qt_offscreen.instance() is qt_offscreen


def test_real_network_is_blocked() -> None:
    with pytest.raises(AssertionError, match="禁止真实网络"):
        socket.create_connection(("127.0.0.1", 9))
