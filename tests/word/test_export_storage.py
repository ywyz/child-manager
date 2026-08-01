"""T131 导出文件名、原子存储与清理 RED。"""

from importlib import import_module
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest


def _module() -> Any:
    try:
        return import_module("packages.backend.integrations.files.export_storage")
    except ModuleNotFoundError:
        pytest.fail("T131 ExportStorage 尚未实现")


@pytest.mark.parametrize(
    ("class_name", "expected"),
    [
        ("向日葵班", "一日活动计划_向日葵班_2026-03-02.docx"),
        ('  Ａ/\\:*?"<>|班..  ', "一日活动计划_A_班_2026-03-02.docx"),
        ('\x00/\\:*?"<>|...', "一日活动计划_班级_2026-03-02.docx"),
        ("星__河班", "一日活动计划_星_河班_2026-03-02.docx"),
    ],
)
def test_display_filename_nfkc_illegal_character_and_empty_fallback(
    class_name: str,
    expected: str,
) -> None:
    sanitize = getattr(_module(), "build_display_filename", None)
    if sanitize is None:
        pytest.fail("T131 显示文件名清理尚未实现")

    assert sanitize(class_name, "2026-03-02") == expected


def test_atomic_write_uses_unique_internal_key_and_streaming_hash(tmp_path: Path) -> None:
    module = _module()
    storage_type = getattr(module, "ExportStorage", None)
    key_factory = getattr(module, "new_storage_key", None)
    if storage_type is None or key_factory is None:
        pytest.fail("T131 原子导出存储尚未实现")
    storage = storage_type(tmp_path / "exports", temporary_root=tmp_path / "temporary")
    first_key = key_factory(uuid4())
    second_key = key_factory(uuid4())

    first = storage.write_atomic(first_key, [b"word-", b"one"])
    second = storage.write_atomic(second_key, [b"word-two"])

    assert first_key != second_key
    assert second.file_size == 8
    assert "/" not in first_key and "\\" not in first_key
    assert first.file_size == 8
    assert len(first.file_sha256) == 64
    assert storage.open_for_read(first_key).read_bytes() == b"word-one"
    assert storage.open_for_read(second_key).read_bytes() == b"word-two"
    assert list((tmp_path / "temporary").iterdir()) == []


def test_interrupted_write_exposes_no_half_file_and_cleans_temporary_file(
    tmp_path: Path,
) -> None:
    module = _module()
    storage_type = getattr(module, "ExportStorage", None)
    key_factory = getattr(module, "new_storage_key", None)
    if storage_type is None or key_factory is None:
        pytest.fail("T131 原子导出存储尚未实现")
    storage = storage_type(tmp_path / "exports", temporary_root=tmp_path / "temporary")
    storage_key = key_factory(uuid4())

    def interrupted() -> Any:
        yield b"partial"
        raise OSError("simulated write interruption")

    with pytest.raises(OSError, match="interruption"):
        storage.write_atomic(storage_key, interrupted())

    with pytest.raises(FileNotFoundError):
        storage.open_for_read(storage_key)
    assert list((tmp_path / "temporary").iterdir()) == []


def test_storage_rejects_paths_and_can_delete_orphan_after_database_failure(
    tmp_path: Path,
) -> None:
    module = _module()
    storage_type = getattr(module, "ExportStorage", None)
    key_factory = getattr(module, "new_storage_key", None)
    if storage_type is None or key_factory is None:
        pytest.fail("T131 原子导出存储尚未实现")
    storage = storage_type(tmp_path / "exports", temporary_root=tmp_path / "temporary")
    storage_key = key_factory(uuid4())
    storage.write_atomic(storage_key, [b"orphan"])

    storage.delete(storage_key)

    with pytest.raises(FileNotFoundError):
        storage.open_for_read(storage_key)
    with pytest.raises(ValueError):
        storage.open_for_read("../secret.docx")
