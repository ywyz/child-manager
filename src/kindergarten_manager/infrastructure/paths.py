"""桌面数据路径公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

APPLICATION_ID = "cn.kindergartenmanager.desktop"


@dataclass(frozen=True, slots=True)
class DesktopPaths:
    root: Path
    data: Path
    database: Path
    backups: Path
    daily_backups: Path
    pre_migration_backups: Path
    pre_restore_backups: Path
    recovery: Path
    staging: Path
    cache: Path
    logs: Path


def resolve_desktop_paths(
    *,
    generic_data_location: Path | None = None,
    install_directory: Path | None = None,
) -> DesktopPaths:
    raise NotImplementedError("T019 尚未实现桌面数据路径解析")
