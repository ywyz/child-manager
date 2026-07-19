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
    "raw",
    [
        "",
        "   ",
        "\t\n",
    ],
)
def test_normalize_username_rejects_empty(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_username(raw)


def test_normalize_username_rejects_nfkc_expanded_over_length() -> None:
    """NFKC 组合字符扩长后超过 120 必须在边界拒绝，不让 DataError 外泄。

    U+FB03 ``ﬃ`` 经 NFKC 展开为 ``ffi``（1->3 字符）。50 个 ``ﬃ`` 原长 50
    （<= 120，契约合法），规范化后长 150（> 120），写入 ``VARCHAR(120)``
    会被数据库拒绝。normalize_username 必须在边界拦截。
    """
    raw = "\ufb03" * 50
    assert len(raw) == 50
    assert len(unicodedata.normalize("NFKC", raw)) == 150
    with pytest.raises(ValueError, match="120"):
        normalize_username(raw)


def test_normalize_username_allows_max_length_after_nfkc() -> None:
    """NFKC 后恰好 120 字符的用户名必须被接受。"""
    raw = "a" * 120
    assert normalize_username(raw) == raw


@pytest.mark.parametrize(
    "raw",
    [
        "user name",  # 空格不在允许字符集
        "user/name",
        "user#name",
        "user+name",  # + 不在允许字符集（与 E.164 手机号区分）
        "用户名",
    ],
)
def test_normalize_username_rejects_disallowed_characters(raw: str) -> None:
    with pytest.raises(ValueError, match="不允许的字符"):
        normalize_username(raw)


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
