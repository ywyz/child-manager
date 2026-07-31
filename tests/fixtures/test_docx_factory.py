"""确定性 DOCX/ZIP 测试工厂的自测。"""

from collections.abc import Callable
from io import BytesIO
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile, is_zipfile

import pytest
from docx import Document

from tests.fixtures.docx_factory import (
    ARCHIVE_LIMIT_BYTES,
    EXPANDED_LIMIT_BYTES,
    SYNTHETIC_TEXT,
    TEXT_LIMIT,
    ZIP_ENTRY_LIMIT,
    ZIP_TIMESTAMP,
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


def test_valid_docx_is_reproducible_and_readable() -> None:
    first = make_valid_docx()
    second = make_valid_docx()

    assert first == second
    assert first.filename == "synthetic-group-activity.docx"
    assert (
        first.content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    with ZipFile(BytesIO(first.payload)) as archive:
        assert archive.namelist() == [
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/_rels/document.xml.rels",
        ]
        assert [entry.date_time for entry in archive.infolist()] == [ZIP_TIMESTAMP] * 4

    document = Document(BytesIO(first.payload))
    assert "\n".join(paragraph.text for paragraph in document.paragraphs) == SYNTHETIC_TEXT


@pytest.mark.parametrize(
    "factory",
    [
        make_archive_over_limit_docx,
        make_expanded_over_limit_docx,
        make_entry_count_over_limit_docx,
        make_text_over_limit_docx,
        make_macro_docx,
        make_external_relationship_docx,
        make_path_traversal_docx,
        make_nested_archive_docx,
        make_masquerading_docx,
        make_non_ooxml_zip_docx,
        make_corrupt_docx,
    ],
)
def test_adversarial_samples_are_reproducible(factory: Callable[[], DocxUpload]) -> None:
    sample = factory()
    assert sample == factory()
    if is_zipfile(BytesIO(sample.payload)):
        with ZipFile(BytesIO(sample.payload)) as archive:
            assert all(entry.date_time == ZIP_TIMESTAMP for entry in archive.infolist())


def test_limit_samples_exceed_each_documented_boundary() -> None:
    archive = make_archive_over_limit_docx()
    expanded = make_expanded_over_limit_docx()
    entry_count = make_entry_count_over_limit_docx()
    text = make_text_over_limit_docx()

    assert len(archive.payload) > ARCHIVE_LIMIT_BYTES
    with ZipFile(BytesIO(expanded.payload)) as source:
        assert sum(entry.file_size for entry in source.infolist()) > EXPANDED_LIMIT_BYTES
    with ZipFile(BytesIO(entry_count.payload)) as source:
        assert len(source.infolist()) == ZIP_ENTRY_LIMIT + 1
    with ZipFile(BytesIO(text.payload)) as source:
        document = ElementTree.fromstring(source.read("word/document.xml"))
    values = document.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
    assert len("".join(value.text or "" for value in values)) == TEXT_LIMIT + 1


def test_macro_external_traversal_and_nested_samples_have_inert_markers() -> None:
    with ZipFile(BytesIO(make_macro_docx().payload)) as source:
        assert "word/vbaProject.bin" in source.namelist()
    with ZipFile(BytesIO(make_external_relationship_docx().payload)) as source:
        relationships = source.read("word/_rels/document.xml.rels")
        assert b'TargetMode="External"' in relationships
    with ZipFile(BytesIO(make_path_traversal_docx().payload)) as source:
        assert "../synthetic-traversal.txt" in source.namelist()
    with ZipFile(BytesIO(make_nested_archive_docx().payload)) as source:
        nested = source.read("word/embeddings/synthetic-nested.zip")
        assert is_zipfile(BytesIO(nested))


def test_masquerading_samples_cover_signature_and_ooxml_structure() -> None:
    non_zip = make_masquerading_docx()
    non_ooxml_zip = make_non_ooxml_zip_docx()

    assert non_zip.filename.endswith(".docx")
    assert not is_zipfile(BytesIO(non_zip.payload))
    assert is_zipfile(BytesIO(non_ooxml_zip.payload))
    with ZipFile(BytesIO(non_ooxml_zip.payload)) as source:
        assert "[Content_Types].xml" not in source.namelist()


def test_corrupt_sample_has_readable_directory_but_bad_member_crc() -> None:
    with ZipFile(BytesIO(make_corrupt_docx().payload)) as source:
        assert "word/document.xml" in source.namelist()
        with pytest.raises(BadZipFile, match="CRC"):
            source.read("word/document.xml")
