"""桌面数据路径解析。"""

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

    @property
    def directories(self) -> tuple[Path, ...]:
        return (
            self.root,
            self.data,
            self.backups,
            self.daily_backups,
            self.pre_migration_backups,
            self.pre_restore_backups,
            self.recovery,
            self.staging,
            self.cache,
            self.logs,
        )

    def ensure_directories(self) -> None:
        for directory in self.directories:
            directory.mkdir(parents=True, exist_ok=True)


def resolve_desktop_paths(
    *,
    generic_data_location: Path | None = None,
    install_directory: Path | None = None,
) -> DesktopPaths:
    if generic_data_location is None:
        from PySide6.QtCore import QStandardPaths

        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.GenericDataLocation
        )
        if not location:
            raise OSError("无法确定桌面数据目录")
        generic_data_location = Path(location)

    root = Path(generic_data_location) / APPLICATION_ID
    backups = root / "backups"
    paths = DesktopPaths(
        root=root,
        data=root / "data",
        database=root / "data" / "child-manager.sqlite3",
        backups=backups,
        daily_backups=backups / "daily",
        pre_migration_backups=backups / "pre-migration",
        pre_restore_backups=backups / "pre-restore",
        recovery=root / "recovery",
        staging=root / "staging",
        cache=root / "cache",
        logs=root / "logs",
    )
    return paths
