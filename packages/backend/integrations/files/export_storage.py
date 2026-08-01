"""Word 导出受控文件名与原子本地存储。"""

from __future__ import annotations

import os
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

_ILLEGAL_FILENAME_CHARACTERS = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]+')
_UNDERSCORES = re.compile(r"_+")


def build_display_filename(class_name: str, plan_date: str) -> str:
    """生成不包含内部存储 key 的确定性 Word 下载文件名。"""

    normalized = unicodedata.normalize("NFKC", class_name).strip()
    normalized = _ILLEGAL_FILENAME_CHARACTERS.sub("_", normalized)
    normalized = _UNDERSCORES.sub("_", normalized).strip(" ._")
    safe_class_name = normalized or "班级"
    return f"一日活动计划_{safe_class_name}_{plan_date}.docx"


@dataclass(frozen=True, slots=True)
class StoredExport:
    file_size: int
    file_sha256: str


def new_storage_key(export_id: UUID) -> str:
    """内部 key 只使用不可猜目录外的 UUID 文件名。"""

    return f"{export_id}.docx"


class ExportStorage:
    """在受控临时目录写完、同步并原子落位后才暴露文件。"""

    def __init__(self, root: Path, *, temporary_root: Path) -> None:
        self._root = Path(root).resolve()
        self._temporary_root = Path(temporary_root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self._temporary_root.mkdir(parents=True, exist_ok=True)

    def write_atomic(self, storage_key: str, chunks: Iterable[bytes]) -> StoredExport:
        destination = self._path(storage_key)
        if destination.exists():
            raise FileExistsError("导出文件已存在")
        temporary_path: Path | None = None
        digest = sha256()
        file_size = 0
        try:
            with NamedTemporaryFile(
                mode="xb",
                dir=self._temporary_root,
                prefix="word-export-",
                suffix=".partial",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                for chunk in chunks:
                    if not isinstance(chunk, bytes):
                        raise TypeError("导出数据块必须是 bytes")
                    temporary.write(chunk)
                    digest.update(chunk)
                    file_size += len(chunk)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, destination)
            temporary_path = None
            return StoredExport(file_size=file_size, file_sha256=digest.hexdigest())
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def open_for_read(self, storage_key: str) -> Path:
        path = self._path(storage_key)
        if not path.is_file():
            raise FileNotFoundError("导出文件不存在")
        return path

    def delete(self, storage_key: str) -> None:
        self._path(storage_key).unlink(missing_ok=True)

    def _path(self, storage_key: str) -> Path:
        if (
            not storage_key
            or storage_key in {".", ".."}
            or "/" in storage_key
            or "\\" in storage_key
            or Path(storage_key).name != storage_key
        ):
            raise ValueError("非法导出存储 key")
        path = (self._root / storage_key).resolve()
        if path.parent != self._root:
            raise ValueError("非法导出存储 key")
        return path
