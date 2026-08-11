from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from kindergarten_manager import __main__ as entrypoint
from kindergarten_manager.application.bootstrap import StartupError


def test_entrypoint_maps_path_resolution_failure_to_stable_startup_error(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert qapp is QApplication.instance()

    def fail_resolution() -> None:
        raise OSError("秘密本机路径")

    monkeypatch.setattr(entrypoint, "resolve_desktop_paths", fail_resolution)

    with pytest.raises(StartupError) as captured:
        entrypoint.main()

    assert captured.value.error_code == "startup.path_unavailable"
    assert "秘密本机路径" not in str(captured.value)
