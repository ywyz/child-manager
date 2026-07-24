from pathlib import Path
from typing import Any, cast

from argon2 import PasswordHasher
from argon2.low_level import Type

from packages.backend.identity.passwords import (
    hash_password,
    password_needs_rehash,
    password_violations,
    verify_password,
)


def test_backup_password_policy_accepts_eight_unicode_characters_and_spaces() -> None:
    assert password_violations("八个字符 的密码") == []
    assert "length" in password_violations("不足七位")
    assert "length" in password_violations("长" * 129)


def test_backup_password_policy_blocks_local_and_contextual_terms(tmp_path: Path) -> None:
    weak_passwords = tmp_path / "weak-passwords.txt"
    weak_passwords.write_text("已泄露的密码\n", encoding="utf-8")
    policy = cast(Any, password_violations)

    assert "weak" in policy(
        "已泄露的密码",
        weak_password_path=weak_passwords,
    )
    assert "context" in policy(
        "Child Manager admin 2026",
        weak_password_path=weak_passwords,
        forbidden_terms=("child manager", "admin"),
    )


def test_backup_password_hash_uses_auditable_argon2id_floor_and_rehashes() -> None:
    password_hash = hash_password("合格的备用登录密码 2026")

    assert password_hash.startswith("$argon2id$")
    assert "m=65536" in password_hash
    assert "t=3" in password_hash
    assert verify_password("合格的备用登录密码 2026", password_hash) is True
    assert verify_password("错误密码", password_hash) is False

    legacy_hash = PasswordHasher(
        time_cost=2,
        memory_cost=19_456,
        parallelism=1,
        type=Type.ID,
    ).hash("合格的备用登录密码 2026")
    assert password_needs_rehash(legacy_hash) is True
