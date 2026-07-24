"""TOTP 种子的 AES-256-GCM 信封与数据库外密钥适配器。"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from packages.backend.ports import IdentitySecretKeyProvider

SubjectKind = Literal["enrollment", "credential"]


@dataclass(frozen=True, slots=True)
class TotpSecretEnvelope:
    ciphertext: bytes
    nonce: bytes
    key_id: str
    envelope_version: int


def _validate_key(key: bytes) -> None:
    if len(key) != 32:
        raise ValueError("身份主密钥必须恰好为 32 字节")


def _aad(
    *,
    kindergarten_id: UUID,
    user_id: UUID,
    subject_id: UUID,
    subject_kind: SubjectKind,
    envelope_version: int,
) -> bytes:
    if subject_kind not in {"enrollment", "credential"}:
        raise ValueError("不支持的 TOTP 信封主体类型")
    if not 1 <= envelope_version <= 65_535:
        raise ValueError("TOTP 信封版本无效")
    return b"".join(
        (
            b"child-manager:totp-envelope\x00",
            envelope_version.to_bytes(2, "big"),
            kindergarten_id.bytes,
            user_id.bytes,
            subject_kind.encode("ascii"),
            b"\x00",
            subject_id.bytes,
        )
    )


def encrypt_totp_secret(
    secret: bytes,
    *,
    key: bytes,
    key_id: str,
    kindergarten_id: UUID,
    user_id: UUID,
    subject_id: UUID,
    subject_kind: SubjectKind,
    envelope_version: int,
) -> TotpSecretEnvelope:
    """用随机 96 位 nonce 加密 TOTP 种子并绑定园所、账号和主体。"""

    _validate_key(key)
    if len(secret) != 20:
        raise ValueError("TOTP 种子必须恰好为 20 字节")
    if not key_id or len(key_id) > 64:
        raise ValueError("身份主密钥标识无效")
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(
        nonce,
        secret,
        _aad(
            kindergarten_id=kindergarten_id,
            user_id=user_id,
            subject_id=subject_id,
            subject_kind=subject_kind,
            envelope_version=envelope_version,
        ),
    )
    return TotpSecretEnvelope(ciphertext, nonce, key_id, envelope_version)


def decrypt_totp_secret(
    envelope: TotpSecretEnvelope,
    *,
    key: bytes,
    kindergarten_id: UUID,
    user_id: UUID,
    subject_id: UUID,
    subject_kind: SubjectKind,
    envelope_version: int,
) -> bytes:
    """验证信封及 AAD 后返回种子；认证标签失败由 ``AESGCM`` 原样拒绝。"""

    _validate_key(key)
    if len(envelope.nonce) != 12:
        raise ValueError("TOTP 信封 nonce 长度无效")
    if envelope.envelope_version != envelope_version:
        raise ValueError("TOTP 信封版本不匹配")
    return AESGCM(key).decrypt(
        envelope.nonce,
        envelope.ciphertext,
        _aad(
            kindergarten_id=kindergarten_id,
            user_id=user_id,
            subject_id=subject_id,
            subject_kind=subject_kind,
            envelope_version=envelope_version,
        ),
    )


def encrypt_totp_secret_with_provider(
    secret: bytes,
    *,
    key_provider: IdentitySecretKeyProvider,
    kindergarten_id: UUID,
    user_id: UUID,
    subject_id: UUID,
    subject_kind: SubjectKind,
    envelope_version: int = 1,
) -> TotpSecretEnvelope:
    key_id, key = key_provider.active_key()
    return encrypt_totp_secret(
        secret,
        key=key,
        key_id=key_id,
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        subject_id=subject_id,
        subject_kind=subject_kind,
        envelope_version=envelope_version,
    )


def decrypt_totp_secret_with_provider(
    envelope: TotpSecretEnvelope,
    *,
    key_provider: IdentitySecretKeyProvider,
    kindergarten_id: UUID,
    user_id: UUID,
    subject_id: UUID,
    subject_kind: SubjectKind,
) -> bytes:
    return decrypt_totp_secret(
        envelope,
        key=key_provider.get_key(envelope.key_id),
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        subject_id=subject_id,
        subject_kind=subject_kind,
        envelope_version=envelope.envelope_version,
    )


def rebind_totp_secret_with_provider(
    envelope: TotpSecretEnvelope,
    *,
    key_provider: IdentitySecretKeyProvider,
    kindergarten_id: UUID,
    user_id: UUID,
    enrollment_id: UUID,
    credential_id: UUID,
) -> TotpSecretEnvelope:
    """将 enrollment 信封解密后以新 nonce 和 credential AAD 重新加密。"""

    secret = decrypt_totp_secret_with_provider(
        envelope,
        key_provider=key_provider,
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        subject_id=enrollment_id,
        subject_kind="enrollment",
    )
    return encrypt_totp_secret_with_provider(
        secret,
        key_provider=key_provider,
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        subject_id=credential_id,
        subject_kind="credential",
        envelope_version=envelope.envelope_version,
    )


class StaticIdentitySecretKeyProvider:
    """自动化测试使用的显式固定密钥适配器。"""

    def __init__(self, keys: Mapping[str, bytes], *, active_key_id: str) -> None:
        self._keys = dict(keys)
        self._active_key_id = active_key_id
        for key in self._keys.values():
            _validate_key(key)
        if active_key_id not in self._keys:
            raise ValueError("当前身份主密钥不存在")

    def active_key(self) -> tuple[str, bytes]:
        return self._active_key_id, self._keys[self._active_key_id]

    def get_key(self, key_id: str) -> bytes:
        try:
            return self._keys[key_id]
        except KeyError:
            raise LookupError("身份主密钥不可用") from None


class FileIdentitySecretKeyProvider:
    """开发环境读取仓库外、仅属主可读的 32 字节二进制密钥文件。"""

    def __init__(
        self,
        key_paths: Mapping[str, Path],
        *,
        active_key_id: str,
        repository_root: Path,
    ) -> None:
        self._key_paths = dict(key_paths)
        self._active_key_id = active_key_id
        repository_root = repository_root.resolve()
        if any(
            path.resolve(strict=False).is_relative_to(repository_root)
            for path in self._key_paths.values()
        ):
            raise ValueError("身份主密钥文件必须位于代码库之外")
        if active_key_id not in self._key_paths:
            raise ValueError("当前身份主密钥文件未配置")

    @staticmethod
    def _read_key(path: Path) -> bytes:
        if path.is_symlink() or not path.is_file():
            raise ValueError("身份主密钥路径必须是普通文件")
        metadata = path.stat()
        if metadata.st_uid != os.getuid():
            raise PermissionError("身份主密钥文件必须属于当前进程用户")
        if metadata.st_mode & 0o077:
            raise PermissionError("身份主密钥文件只能由属主访问")
        key = path.read_bytes()
        _validate_key(key)
        return key

    def active_key(self) -> tuple[str, bytes]:
        return self._active_key_id, self.get_key(self._active_key_id)

    def get_key(self, key_id: str) -> bytes:
        try:
            path = self._key_paths[key_id]
        except KeyError:
            raise LookupError("身份主密钥不可用") from None
        return self._read_key(path)
