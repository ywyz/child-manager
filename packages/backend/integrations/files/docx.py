"""受限 DOCX 输入的安全 OOXML 文本提取。"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from time import monotonic
from typing import Protocol
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
ARCHIVE_LIMIT_BYTES = 10 * 1024 * 1024
EXPANDED_LIMIT_BYTES = 50 * 1024 * 1024
ZIP_ENTRY_LIMIT = 1000
TEXT_LIMIT = 200_000
_CHUNK_SIZE = 64 * 1024
_REQUIRED_MEMBERS = frozenset(
    {"[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/_rels/document.xml.rels"}
)
_WORD_TEXT_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


class DocxExtractionError(ValueError):
    """不安全、损坏或超限的 DOCX 输入。"""


class _ByteWriter(Protocol):
    def write(self, data: bytes, /) -> int: ...


def extract_docx_text(
    *,
    payload: bytes,
    filename: str,
    content_type: str,
    temporary_directory: Path,
    timeout_seconds: float | None = None,
) -> str:
    """验证 DOCX 包后仅提取 word/document.xml 文本，始终清理本次暂存文件。"""

    temporary_path: Path | None = None
    deadline = _deadline(timeout_seconds)
    try:
        _validate_metadata(filename=filename, content_type=content_type, payload=payload)
        temporary_directory.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="wb",
            dir=temporary_directory,
            prefix="docx-",
            suffix=".upload",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            _write_limited(temporary_file, payload, deadline=deadline)

        _check_deadline(deadline)
        with ZipFile(temporary_path) as archive:
            _validate_package(archive, deadline=deadline)
            return _extract_document_text(archive, deadline=deadline)
    except DocxExtractionError:
        raise
    except (BadZipFile, ElementTree.ParseError, OSError, ValueError) as error:
        raise DocxExtractionError("DOCX 文件无效或不安全") from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _deadline(timeout_seconds: float | None) -> float | None:
    if timeout_seconds is None:
        return None
    if timeout_seconds < 0:
        raise DocxExtractionError("DOCX 提取超时")
    return monotonic() + timeout_seconds


def _check_deadline(deadline: float | None) -> None:
    if deadline is not None and monotonic() >= deadline:
        raise DocxExtractionError("DOCX 提取超时")


def _validate_metadata(*, filename: str, content_type: str, payload: bytes) -> None:
    if not filename.casefold().endswith(".docx"):
        raise DocxExtractionError("只接受 DOCX 文件")
    if content_type != DOCX_MIME:
        raise DocxExtractionError("DOCX MIME 类型不匹配")
    if len(payload) > ARCHIVE_LIMIT_BYTES:
        raise DocxExtractionError("DOCX 压缩包超过大小限制")
    if not payload.startswith(b"PK\x03\x04"):
        raise DocxExtractionError("DOCX ZIP 签名无效")


def _write_limited(
    destination: _ByteWriter,
    payload: bytes,
    *,
    deadline: float | None,
) -> None:
    written = 0
    for offset in range(0, len(payload), _CHUNK_SIZE):
        _check_deadline(deadline)
        chunk = payload[offset : offset + _CHUNK_SIZE]
        written += len(chunk)
        if written > ARCHIVE_LIMIT_BYTES:
            raise DocxExtractionError("DOCX 压缩包超过大小限制")
        destination.write(chunk)


def _validate_package(archive: ZipFile, *, deadline: float | None) -> None:
    entries = archive.infolist()
    if not entries or len(entries) > ZIP_ENTRY_LIMIT:
        raise DocxExtractionError("DOCX 条目数量超过限制")

    total_expanded = 0
    member_names: set[str] = set()
    for entry in entries:
        _check_deadline(deadline)
        member_name = entry.filename
        _validate_member_name(member_name)
        if entry.flag_bits & 0x1:
            raise DocxExtractionError("DOCX 不支持加密条目")
        if member_name.casefold().endswith((".zip", ".docx", ".jar")):
            raise DocxExtractionError("DOCX 不允许嵌套压缩包")
        if member_name.casefold().endswith("vbaproject.bin"):
            raise DocxExtractionError("DOCX 不允许宏")
        total_expanded += entry.file_size
        if total_expanded > EXPANDED_LIMIT_BYTES:
            raise DocxExtractionError("DOCX 展开后超过大小限制")
        member_names.add(member_name)

    if not member_names >= _REQUIRED_MEMBERS:
        raise DocxExtractionError("DOCX 缺少必要的 OOXML 结构")
    if archive.testzip() is not None:
        raise DocxExtractionError("DOCX ZIP 条目损坏")

    content_types = _read_xml_member(archive, "[Content_Types].xml", deadline=deadline)
    if b"vba" in content_types.lower():
        raise DocxExtractionError("DOCX 不允许宏")
    for member_name in member_names:
        if member_name.casefold().endswith(".rels"):
            _reject_external_relationships(
                _read_xml_member(archive, member_name, deadline=deadline)
            )


def _validate_member_name(member_name: str) -> None:
    path = PurePosixPath(member_name)
    if (
        not member_name
        or member_name.startswith("/")
        or "\\" in member_name
        or "\x00" in member_name
        or ".." in path.parts
    ):
        raise DocxExtractionError("DOCX 包含非法路径")


def _read_xml_member(archive: ZipFile, member_name: str, *, deadline: float | None) -> bytes:
    _check_deadline(deadline)
    data = archive.read(member_name)
    _check_deadline(deadline)
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise DocxExtractionError("DOCX XML 不允许实体声明")
    return data


def _reject_external_relationships(xml_data: bytes) -> None:
    root = ElementTree.fromstring(xml_data)
    if any(
        name.casefold().endswith("targetmode") and value.casefold() == "external"
        for element in root.iter()
        for name, value in element.attrib.items()
    ):
        raise DocxExtractionError("DOCX 不允许外部关系")


def _extract_document_text(archive: ZipFile, *, deadline: float | None) -> str:
    document_xml = _read_xml_member(archive, "word/document.xml", deadline=deadline)
    text_parts: list[str] = []
    character_count = 0
    for _event, element in ElementTree.iterparse(BytesIO(document_xml), events=("end",)):
        _check_deadline(deadline)
        if element.tag == _WORD_TEXT_TAG:
            value = element.text or ""
            character_count += len(value)
            if character_count > TEXT_LIMIT:
                raise DocxExtractionError("DOCX 提取文本超过长度限制")
            text_parts.append(value)
        element.clear()
    if not text_parts:
        raise DocxExtractionError("DOCX 未包含可提取文本")
    return "".join(text_parts)
