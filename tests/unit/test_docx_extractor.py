"""T112 安全 DOCX 提取与临时清理 RED 验收。"""

from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from tests.fixtures.docx_factory import (
    SYNTHETIC_TEXT,
    DocxUpload,
    make_archive_over_limit_docx,
    make_corrupt_docx,
    make_entry_count_over_limit_docx,
    make_expanded_over_limit_docx,
    make_external_relationship_docx,
    make_macro_docx,
    make_masquerading_docx,
    make_nested_archive_docx,
    make_non_ooxml_zip_docx,
    make_path_traversal_docx,
    make_text_over_limit_docx,
    make_valid_docx,
)

_MODULE_NAME = "packages.backend.integrations.files.docx"


def _docx_module() -> ModuleType:
    try:
        return import_module(_MODULE_NAME)
    except ModuleNotFoundError as error:
        if error.name and _MODULE_NAME.startswith(f"{error.name}."):
            pytest.fail("T120 安全 DOCX 提取器尚未实现", pytrace=False)
        raise


def _extractor(module: ModuleType) -> Callable[..., str]:
    value = getattr(module, "extract_docx_text", None)
    assert callable(value), f"T120 提取接口缺失: {module.__name__}.extract_docx_text"
    return cast(Callable[..., str], value)


def _rejection(module: ModuleType) -> type[Exception]:
    value: Any = getattr(module, "DocxExtractionError", None)
    assert isinstance(value, type) and issubclass(value, Exception), (
        f"T120 拒绝异常缺失: {module.__name__}.DocxExtractionError"
    )
    return value


def _caller_owned_temporary_directory(tmp_path: Path) -> Path:
    temporary_directory = tmp_path / "docx-extraction"
    temporary_directory.mkdir()
    (temporary_directory / ".caller-owned-sentinel").write_text("keep", encoding="utf-8")
    return temporary_directory


def _assert_temporary_directory_clean(temporary_directory: Path) -> None:
    assert sorted(path.name for path in temporary_directory.iterdir()) == [".caller-owned-sentinel"]


def _extract(
    upload: DocxUpload,
    temporary_directory: Path,
    *,
    timeout_seconds: float | None = None,
) -> str:
    module = _docx_module()
    return _extractor(module)(
        payload=upload.payload,
        filename=upload.filename,
        content_type=upload.content_type,
        temporary_directory=temporary_directory,
        timeout_seconds=timeout_seconds,
    )


def _assert_rejected_and_cleaned(upload: DocxUpload, tmp_path: Path) -> None:
    module = _docx_module()
    temporary_directory = _caller_owned_temporary_directory(tmp_path)

    with pytest.raises(_rejection(module)):
        _extract(upload, temporary_directory)

    _assert_temporary_directory_clean(temporary_directory)


def test_extracts_valid_ooxml_text_and_cleans_temporary_files(tmp_path: Path) -> None:
    temporary_directory = _caller_owned_temporary_directory(tmp_path)

    assert _extract(make_valid_docx(), temporary_directory) == SYNTHETIC_TEXT

    _assert_temporary_directory_clean(temporary_directory)


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(make_archive_over_limit_docx, id="archive-size"),
        pytest.param(make_expanded_over_limit_docx, id="expanded-size"),
        pytest.param(make_entry_count_over_limit_docx, id="entry-count"),
        pytest.param(make_text_over_limit_docx, id="text-size"),
    ],
)
def test_rejects_each_resource_limit_and_cleans_temporary_files(
    factory: Callable[[], DocxUpload], tmp_path: Path
) -> None:
    _assert_rejected_and_cleaned(factory(), tmp_path)


def test_timeout_cleans_temporary_files(tmp_path: Path) -> None:
    module = _docx_module()
    temporary_directory = _caller_owned_temporary_directory(tmp_path)

    with pytest.raises(_rejection(module)):
        _extract(make_valid_docx(), temporary_directory, timeout_seconds=0.0)

    _assert_temporary_directory_clean(temporary_directory)


@pytest.mark.parametrize(
    "upload",
    [
        pytest.param(
            DocxUpload(
                payload=make_valid_docx().payload,
                filename="synthetic-group-activity.txt",
            ),
            id="extension-mismatch",
        ),
        pytest.param(
            DocxUpload(
                payload=make_valid_docx().payload,
                content_type="application/zip",
            ),
            id="mime-mismatch",
        ),
        pytest.param(make_masquerading_docx(), id="zip-signature-mismatch"),
        pytest.param(make_non_ooxml_zip_docx(), id="ooxml-structure-mismatch"),
    ],
)
def test_rejects_metadata_signature_or_ooxml_mismatch_and_cleans_temporary_files(
    upload: DocxUpload, tmp_path: Path
) -> None:
    _assert_rejected_and_cleaned(upload, tmp_path)


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(make_macro_docx, id="macro"),
        pytest.param(make_external_relationship_docx, id="external-relationship"),
        pytest.param(make_path_traversal_docx, id="path-traversal"),
        pytest.param(make_nested_archive_docx, id="nested-archive"),
        pytest.param(make_corrupt_docx, id="corrupt-member"),
    ],
)
def test_rejects_active_or_malformed_ooxml_and_cleans_temporary_files(
    factory: Callable[[], DocxUpload], tmp_path: Path
) -> None:
    _assert_rejected_and_cleaned(factory(), tmp_path)
