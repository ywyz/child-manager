from hashlib import sha256
from pathlib import Path

import pytest

from packages.backend.identity.passwords import hash_password, password_violations, verify_password

RESOURCE = Path(__file__).parents[3] / "packages/backend/identity/data/10k-most-common.txt"
NOTICE = RESOURCE.with_name("NOTICE.md")


@pytest.mark.parametrize("password", ["短密码", "a" * 14, "x" * 129])
def test_password_length_is_15_to_128_unicode_characters(password: str) -> None:
    assert "length" in password_violations(password)


def test_unicode_spaces_and_paste_are_allowed() -> None:
    assert password_violations("可以 粘贴的足够长安全密码 2026") == []


def test_weak_password_file_is_checked_without_network(tmp_path: Path) -> None:
    weak = tmp_path / "weak.txt"
    weak.write_text("verycommonpassword\n", encoding="utf-8")
    assert "weak" in password_violations("verycommonpassword", weak_password_path=weak)


def test_password_is_argon2id_hashed_and_verified() -> None:
    encoded = hash_password("足够长的安全密码 2026")
    assert encoded.startswith("$argon2id$")
    assert verify_password("足够长的安全密码 2026", encoded)
    assert not verify_password("错误但同样足够长的密码", encoded)


def test_invalid_password_hash_is_rejected() -> None:
    assert verify_password("足够长的安全密码 2026", "not-an-argon2-hash") is False


def test_seclists_resource_is_exactly_pinned_and_attributed() -> None:
    content = RESOURCE.read_bytes()
    notice = NOTICE.read_text(encoding="utf-8")
    assert sha256(content).hexdigest() == (
        "4adb3f0afb4a10cf19ebe48d8c69a46f934bbc8d77c694c210564f9583e7f4ba"
    )
    assert len(content) == 73017
    assert len(content.splitlines()) == 10000
    assert "2026.1" in notice
    assert "190c6f7bd58c847ceadfe57d9853592737f059e8" in notice
    assert "MIT License" in notice
