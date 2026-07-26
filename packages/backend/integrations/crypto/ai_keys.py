"""AI API Key 的 AES-256-GCM envelope 与数据库外 keyring。"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass(frozen=True, slots=True)
class AiKeyEnvelope:
    ciphertext: bytes
    nonce: bytes
    key_id: str
    envelope_version: int
    last_four: str


def _validate_key(key: bytes) -> None:
    if len(key) != 32:
        raise ValueError("AI 主密钥必须恰好为 32 字节")


def _aad(kindergarten_id: UUID, profile_id: UUID, envelope_version: int) -> bytes:
    if not 1 <= envelope_version <= 65_535:
        raise ValueError("AI Key envelope 版本无效")
    return b"".join(
        (
            b"child-manager:ai-key-envelope\x00",
            envelope_version.to_bytes(2, "big"),
            kindergarten_id.bytes,
            profile_id.bytes,
        )
    )


def encrypt_api_key(
    api_key: str,
    *,
    key: bytes,
    key_id: str,
    kindergarten_id: UUID,
    profile_id: UUID,
    envelope_version: int = 1,
) -> AiKeyEnvelope:
    _validate_key(key)
    if not api_key or len(api_key) > 4000:
        raise ValueError("AI API Key 长度无效")
    if not key_id or len(key_id) > 64:
        raise ValueError("AI 主密钥标识无效")
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(
        nonce,
        api_key.encode(),
        _aad(kindergarten_id, profile_id, envelope_version),
    )
    return AiKeyEnvelope(ciphertext, nonce, key_id, envelope_version, api_key[-4:])


def decrypt_api_key(
    envelope: AiKeyEnvelope,
    *,
    key: bytes,
    kindergarten_id: UUID,
    profile_id: UUID,
    envelope_version: int,
) -> str:
    _validate_key(key)
    if len(envelope.nonce) != 12:
        raise ValueError("AI Key nonce 长度无效")
    if envelope.envelope_version != envelope_version:
        raise ValueError("AI Key envelope 版本不匹配")
    return (
        AESGCM(key)
        .decrypt(
            envelope.nonce,
            envelope.ciphertext,
            _aad(kindergarten_id, profile_id, envelope_version),
        )
        .decode()
    )


def encrypt_api_key_with_provider(
    api_key: str,
    *,
    key_provider: StaticAiKeyProvider | FileAiKeyProvider,
    kindergarten_id: UUID,
    profile_id: UUID,
    envelope_version: int = 1,
) -> AiKeyEnvelope:
    key_id, key = key_provider.active_key()
    return encrypt_api_key(
        api_key,
        key=key,
        key_id=key_id,
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=envelope_version,
    )


def decrypt_api_key_with_provider(
    envelope: AiKeyEnvelope,
    *,
    key_provider: StaticAiKeyProvider | FileAiKeyProvider,
    kindergarten_id: UUID,
    profile_id: UUID,
) -> str:
    return decrypt_api_key(
        envelope,
        key=key_provider.get_key(envelope.key_id),
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=envelope.envelope_version,
    )


class StaticAiKeyProvider:
    def __init__(self, keys: Mapping[str, bytes], *, active_key_id: str) -> None:
        self._keys = dict(keys)
        self._active_key_id = active_key_id
        for key in self._keys.values():
            _validate_key(key)
        if active_key_id not in self._keys:
            raise ValueError("当前 AI 主密钥不存在")

    def active_key(self) -> tuple[str, bytes]:
        return self._active_key_id, self._keys[self._active_key_id]

    def get_key(self, key_id: str) -> bytes:
        try:
            return self._keys[key_id]
        except KeyError:
            raise LookupError("AI 主密钥不可用") from None


class FileAiKeyProvider:
    def __init__(
        self,
        key_paths: Mapping[str, Path],
        *,
        active_key_id: str,
        repository_root: Path,
    ) -> None:
        self._paths = dict(key_paths)
        self._active_key_id = active_key_id
        root = repository_root.resolve()
        if any(path.resolve(strict=False).is_relative_to(root) for path in self._paths.values()):
            raise ValueError("AI 主密钥文件必须位于代码库之外")
        if active_key_id not in self._paths:
            raise ValueError("当前 AI 主密钥文件未配置")

    @staticmethod
    def _read(path: Path) -> bytes:
        if path.is_symlink() or not path.is_file():
            raise ValueError("AI 主密钥路径必须是普通文件")
        metadata = path.stat()
        if metadata.st_uid != os.getuid():
            raise PermissionError("AI 主密钥文件必须属于当前进程用户")
        if metadata.st_mode & 0o077:
            raise PermissionError("AI 主密钥文件只能由属主访问")
        key = path.read_bytes()
        _validate_key(key)
        return key

    def active_key(self) -> tuple[str, bytes]:
        return self._active_key_id, self.get_key(self._active_key_id)

    def get_key(self, key_id: str) -> bytes:
        try:
            return self._read(self._paths[key_id])
        except KeyError:
            raise LookupError("AI 主密钥不可用") from None
