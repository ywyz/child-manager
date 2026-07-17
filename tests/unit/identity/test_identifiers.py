"""身份标识规范化测试。"""

import unicodedata

import pytest

from packages.backend.identity.identifiers import normalize_phone, normalize_username


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" Ｔｅａｃｈｅｒ ", "teacher"),
        ("Teacher", "teacher"),
        ("  teacher@example.com  ", "teacher@example.com"),
        ("　admin\u3000", "admin"),
        ("ＡＢＣ", "abc"),
    ],
)
def test_normalize_username_nfkc_trim_lower(raw: str, expected: str) -> None:
    actual = normalize_username(raw)
    assert actual == expected
    assert actual == unicodedata.normalize("NFKC", actual).strip().lower()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("13800138000", "+8613800138000"),
        ("+8613800138000", "+8613800138000"),
        (" 13800138000 ", "+8613800138000"),
        ("", None),
        ("   ", None),
        (None, None),
    ],
)
def test_normalize_phone_e164_or_empty(raw: str | None, expected: str | None) -> None:
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "abc",
        "123",
        "+1-555-0100",
        "008613800138000",
    ],
)
def test_normalize_phone_rejects_invalid(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_phone(raw)
