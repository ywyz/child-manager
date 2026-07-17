import pytest

from packages.backend.identity.identifiers import normalize_phone, normalize_username


def test_username_is_nfkc_trimmed_and_lowercase() -> None:
    assert normalize_username(" Ｔｅａｃｈｅｒ ") == "teacher"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("13800138000", "+8613800138000"),
        ("+86 138-0013-8000", "+8613800138000"),
        (None, None),
        ("  ", None),
    ],
)
def test_phone_is_mainland_e164_or_empty(raw: str | None, expected: str | None) -> None:
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["123", "+12025550123", "1380013800x"])
def test_invalid_phone_is_rejected(raw: str) -> None:
    with pytest.raises(ValueError, match="手机号"):
        normalize_phone(raw)
