"""桌面启动公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from dataclasses import dataclass

from kindergarten_manager.infrastructure.paths import DesktopPaths


class StartupError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass(frozen=True, slots=True)
class StartupState:
    data_root: str
    schema_revision: str
    first_run: bool
    setup_complete: bool
    daily_backup: str
    warnings: tuple[str, ...] = ()


class BootstrapService:
    def __init__(self, paths: DesktopPaths) -> None:
        self.paths = paths

    def start(self) -> StartupState:
        raise NotImplementedError("T024 尚未实现桌面启动检查")
