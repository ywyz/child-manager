"""密码政策与 Argon2id。"""

import unicodedata
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from argon2.low_level import Type

_DEFAULT_WEAK_PASSWORD_PATH = Path(__file__).parent / "data/10k-most-common.txt"
_HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1, type=Type.ID)


def _weak_passwords(path: Path) -> set[str]:
    return {
        unicodedata.normalize("NFKC", line.rstrip("\r\n")).casefold()
        for line in path.read_text(encoding="utf-8", errors="strict").splitlines()
    }


def password_violations(password: str, *, weak_password_path: Path | None = None) -> list[str]:
    violations: list[str] = []
    if not 15 <= len(password) <= 128:
        violations.append("length")
    path = weak_password_path or _DEFAULT_WEAK_PASSWORD_PATH
    if path.is_file() and unicodedata.normalize("NFKC", password).casefold() in _weak_passwords(
        path
    ):
        violations.append("weak")
    return violations


def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _HASHER.verify(password_hash, password)
    except InvalidHashError, VerifyMismatchError:
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return _HASHER.check_needs_rehash(password_hash)
