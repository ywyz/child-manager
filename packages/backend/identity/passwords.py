"""密码政策与 Argon2id 哈希。"""

from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def _load_common_passwords() -> frozenset[str]:
    data_path = Path(__file__).with_suffix("").parent / "data" / "10k-most-common.txt"
    if not data_path.exists():
        return frozenset()
    with data_path.open("r", encoding="utf-8") as handle:
        return frozenset(line.strip() for line in handle if line.strip())


_COMMON_PASSWORDS = _load_common_passwords()


def validate_password(password: str) -> None:
    """校验密码复杂度：长度 15–128 字符且不在常见弱密码列表中。"""
    if not isinstance(password, str):
        msg = "密码必须是字符串"
        raise ValueError(msg)
    if len(password) < 15 or len(password) > 128:
        msg = "密码长度必须在 15 到 128 个字符之间"
        raise ValueError(msg)
    if password in _COMMON_PASSWORDS:
        msg = "密码过于常见，请更换"
        raise ValueError(msg)


def is_common_password(password: str) -> bool:
    """判断密码是否在常见弱密码列表中。"""
    return password in _COMMON_PASSWORDS


def hash_password(password: str) -> str:
    """返回 Argon2id 密码哈希。"""
    validate_password(password)
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码与哈希是否匹配。"""
    try:
        _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    return True
