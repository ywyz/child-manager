"""只生成合成内容的确定性 DOCX/ZIP 上传样本。"""

from dataclasses import dataclass
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOCX_FILENAME = "synthetic-group-activity.docx"
SYNTHETIC_TEXT = "这是用于安全测试的合成集体活动文本。"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ARCHIVE_LIMIT_BYTES = 10 * 1024 * 1024
EXPANDED_LIMIT_BYTES = 50 * 1024 * 1024
ZIP_ENTRY_LIMIT = 1000
TEXT_LIMIT = 200_000


@dataclass(frozen=True, slots=True)
class DocxUpload:
    """T112 以后可直接交给上传边界的固定元数据与字节。"""

    payload: bytes
    filename: str = DOCX_FILENAME
    content_type: str = DOCX_MIME


def make_valid_docx(*, text: str = SYNTHETIC_TEXT) -> DocxUpload:
    """构造可由 ``python-docx`` 读取的最小 OOXML 文档。"""

    return DocxUpload(payload=_write_zip(_base_members(text)))


def make_archive_over_limit_docx() -> DocxUpload:
    return _with_extra_member(
        "word/media/archive-over-limit.bin", bytes(ARCHIVE_LIMIT_BYTES + 1), stored=True
    )


def make_expanded_over_limit_docx() -> DocxUpload:
    return _with_extra_member("word/media/expanded-over-limit.bin", bytes(EXPANDED_LIMIT_BYTES + 1))


def make_entry_count_over_limit_docx() -> DocxUpload:
    members = _base_members(SYNTHETIC_TEXT)
    extras = tuple(
        (f"word/customXml/item-{index:04d}.xml", b"<x/>")
        for index in range(ZIP_ENTRY_LIMIT + 1 - len(members))
    )
    return DocxUpload(payload=_write_zip(members + extras))


def make_text_over_limit_docx() -> DocxUpload:
    return make_valid_docx(text="合" * (TEXT_LIMIT + 1))


def make_macro_docx() -> DocxUpload:
    members = list(_base_members(SYNTHETIC_TEXT))
    members[0] = ("[Content_Types].xml", _content_types_with_macro())
    members[-1] = ("word/_rels/document.xml.rels", _MACRO_DOCUMENT_RELATIONSHIPS)
    members.append(("word/vbaProject.bin", b"synthetic macro marker"))
    return DocxUpload(payload=_write_zip(tuple(members)))


def make_external_relationship_docx() -> DocxUpload:
    members = list(_base_members(SYNTHETIC_TEXT))
    members[-1] = ("word/_rels/document.xml.rels", _EXTERNAL_DOCUMENT_RELATIONSHIPS)
    return DocxUpload(payload=_write_zip(tuple(members)))


def make_path_traversal_docx() -> DocxUpload:
    return _with_extra_member("../synthetic-traversal.txt", b"synthetic traversal marker")


def make_nested_archive_docx() -> DocxUpload:
    nested = _write_zip((("synthetic-nested.txt", b"synthetic nested content"),))
    return _with_extra_member("word/embeddings/synthetic-nested.zip", nested)


def make_masquerading_docx() -> DocxUpload:
    return DocxUpload(payload=b"synthetic payload that is not a ZIP archive")


def make_non_ooxml_zip_docx() -> DocxUpload:
    return DocxUpload(payload=_write_zip((("synthetic.txt", b"not an OOXML package"),)))


def make_corrupt_docx() -> DocxUpload:
    payload = bytearray(
        _write_zip(
            _base_members(SYNTHETIC_TEXT),
            stored_members=frozenset({"word/document.xml"}),
        )
    )
    payload[payload.index(b"<w:document")] ^= 1
    return DocxUpload(payload=bytes(payload))


def _base_members(text: str) -> tuple[tuple[str, bytes], ...]:
    return (
        ("[Content_Types].xml", _CONTENT_TYPES),
        ("_rels/.rels", _ROOT_RELATIONSHIPS),
        ("word/document.xml", _document_xml(text)),
        ("word/_rels/document.xml.rels", _EMPTY_DOCUMENT_RELATIONSHIPS),
    )


def _with_extra_member(name: str, content: bytes, *, stored: bool = False) -> DocxUpload:
    members = (*_base_members(SYNTHETIC_TEXT), (name, content))
    return DocxUpload(
        payload=_write_zip(members, stored_members=frozenset({name}) if stored else frozenset())
    )


def _document_xml(text: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>"
        f"{escape(text)}"
        '</w:t></w:r></w:p><w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'
    ).encode()


def _write_zip(
    members: tuple[tuple[str, bytes], ...],
    *,
    stored_members: frozenset[str] = frozenset(),
) -> bytes:
    output = BytesIO()
    with ZipFile(
        output, "w", compression=ZIP_DEFLATED, compresslevel=9, strict_timestamps=True
    ) as archive:
        archive.comment = b""
        for name, content in members:
            entry = ZipInfo(name, date_time=ZIP_TIMESTAMP)
            entry.create_system = 3
            entry.external_attr = 0o600 << 16
            compression = ZIP_STORED if name in stored_members else ZIP_DEFLATED
            archive.writestr(entry, content, compress_type=compression, compresslevel=9)
    return output.getvalue()


_CONTENT_TYPES = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
    b'  <Default Extension="rels" '
    b'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
    b'  <Default Extension="xml" ContentType="application/xml"/>\n'
    b'  <Override PartName="/word/document.xml" '
    b'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
    b"</Types>"
)
_ROOT_RELATIONSHIPS = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    b'  <Relationship Id="rId1" '
    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    b'Target="word/document.xml"/>\n'
    b"</Relationships>"
)
_EMPTY_DOCUMENT_RELATIONSHIPS = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
)


def _content_types_with_macro() -> bytes:
    return _CONTENT_TYPES.replace(
        b"</Types>",
        b'  <Override PartName="/word/vbaProject.bin" '
        b'ContentType="application/vnd.ms-office.vbaProject"/>\n</Types>',
    )


_MACRO_DOCUMENT_RELATIONSHIPS = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    b'  <Relationship Id="rIdMacro" '
    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/vbaProject" '
    b'Target="vbaProject.bin"/>\n'
    b"</Relationships>"
)
_EXTERNAL_DOCUMENT_RELATIONSHIPS = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    b'  <Relationship Id="rIdExternal" '
    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
    b'Target="https://example.invalid/synthetic" '
    b'TargetMode="External"/>\n'
    b"</Relationships>"
)
