from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from kindergarten_manager import __main__ as entrypoint
from kindergarten_manager.application.bootstrap import StartupError

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_source_module_entrypoint_resolves_without_pytest_pythonpath() -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = ""
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "import runpy; "
                "runpy.run_module('kindergarten_manager', run_name='startup_probe'); "
                "print('source-entrypoint-imported')"
            ),
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "source-entrypoint-imported"


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
