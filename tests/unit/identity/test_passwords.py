"""密码政策与 Argon2id 哈希测试。"""

import pytest
from argon2 import PasswordHasher

from packages.backend.identity.passwords import (
    hash_password,
    needs_rehash,
    validate_password,
    verify_password,
)


@pytest.mark.parametrize(
    "password",
    [
        "a" * 15,
        "A" * 128,
        "Short!2024#LongEnough",
    ],
)
def test_valid_password_length(password: str) -> None:
    validate_password(password)


@pytest.mark.parametrize(
    "password",
    [
        "a" * 14,
        "A" * 129,
        "short",
    ],
)
def test_invalid_password_length(password: str) -> None:
    with pytest.raises(ValueError):
        validate_password(password)


def test_hash_and_verify_roundtrip() -> None:
    password = "ValidPassword2024!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_hash_is_argon2id_format() -> None:
    hashed = hash_password("ValidPassword2024!")
    assert hashed.startswith("$argon2id$")


def test_weak_password_is_rejected() -> None:
    with pytest.raises(ValueError):
        validate_password("password")


def test_non_common_password_is_accepted() -> None:
    validate_password("ValidPassword2024!")


def test_hash_uses_frozen_argon2id_parameters() -> None:
    """RED 回归：哈希必须使用冻结参数 m=19456,t=2,p=1。

    Codex 第十九轮审阅 P0：旧版使用 m=65536,t=3,p=1 与冻结值不符。
    冻结需求（data-model.md §75）：参数为 m=19456 KiB,t=2,p=1。
    """
    hashed = hash_password("ValidPassword2024!")
    # Argon2id 编码前缀：$argon2id$v=19$m=<memory>,t=<time>,p=<parallelism>$...
    assert "$argon2id$v=19$m=19456,t=2,p=1$" in hashed, (
        f"哈希参数与冻结值 m=19456,t=2,p=1 不符: {hashed}"
    )


def test_needs_rehash_returns_false_for_current_parameters() -> None:
    """当前冻结参数哈希不需要 rehash。"""
    hashed = hash_password("ValidPassword2024!")
    assert needs_rehash(hashed) is False


def test_needs_rehash_returns_true_for_legacy_parameters() -> None:
    """RED 回归：旧参数哈希（m=65536,t=3,p=1）必须被识别为需要 rehash。

    Codex 第十九轮审阅 P0：旧版全仓无 check_needs_rehash 或登录后重哈希路径。
    旧参数哈希永远不会被升级。needs_rehash 必须对旧参数返回 True。
    """
    legacy_hasher = PasswordHasher(
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        salt_len=16,
    )
    legacy_hash = legacy_hasher.hash("ValidPassword2024!")
    assert legacy_hash.startswith("$argon2id$v=19$m=65536,t=3,p=1$")
    assert needs_rehash(legacy_hash) is True


def test_verify_accepts_legacy_parameter_hash() -> None:
    """verify_password 必须兼容旧参数哈希。

    升级 Argon2id 参数后，已存在的旧参数哈希仍需能验证通过，
    否则用户无法登录触发 rehash。argon2-cffi 的 verify 不关心参数。
    """
    legacy_hasher = PasswordHasher(
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        salt_len=16,
    )
    legacy_hash = legacy_hasher.hash("ValidPassword2024!")
    assert verify_password("ValidPassword2024!", legacy_hash) is True
    assert verify_password("wrong", legacy_hash) is False
