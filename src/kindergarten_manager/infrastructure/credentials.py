from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Protocol, cast

_SERVICE_NAME = "cn.kindergartenmanager.desktop"
_DEFAULT_BACKEND = object()


class CredentialError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class CredentialBackend(Protocol):
    name: str

    def set_password(self, service: str, account: str, secret: str) -> None: ...

    def get_password(self, service: str, account: str) -> str | None: ...

    def delete_password(self, service: str, account: str) -> None: ...


@dataclass(repr=False)
class CredentialStore:
    _backend: CredentialBackend
    backend_name: str
    persistence: str = "local-machine"

    def __repr__(self) -> str:
        return (
            f"CredentialStore(backend_name={self.backend_name!r}, persistence={self.persistence!r})"
        )

    def write(self, account: str, secret: str) -> None:
        try:
            self._backend.set_password(_SERVICE_NAME, account, secret)
        except Exception:
            raise CredentialError("credential.access_failed", "操作系统凭据访问失败") from None

    def read(self, account: str) -> str | None:
        try:
            return self._backend.get_password(_SERVICE_NAME, account)
        except Exception:
            raise CredentialError("credential.access_failed", "操作系统凭据访问失败") from None

    def require(self, account: str) -> str:
        secret = self.read(account)
        if secret is None:
            raise CredentialError("credential.missing", "未找到所需的本机凭据")
        return secret

    def delete(self, account: str) -> None:
        try:
            self._backend.delete_password(_SERVICE_NAME, account)
        except Exception:
            raise CredentialError("credential.access_failed", "操作系统凭据访问失败") from None


def create_credential_store(
    *,
    platform: str | None = None,
    backend: object = _DEFAULT_BACKEND,
) -> CredentialStore:
    actual_platform = sys.platform if platform is None else platform
    if backend is _DEFAULT_BACKEND:
        import keyring

        backend = keyring.get_keyring()

    name = getattr(backend, "name", "")
    backend_type = type(backend)
    is_secret_service = (
        backend_type.__module__ == "keyring.backends.SecretService"
        and backend_type.__qualname__ == "Keyring"
        and name == "SecretService Keyring"
    )
    declared_scope = getattr(backend, "storage_scope", None)
    is_windows_vault = actual_platform == "win32" and name == "Windows WinVaultKeyring"
    if actual_platform == "linux" and is_secret_service:
        persistence = "local-user"
    elif is_windows_vault:
        persistence = declared_scope or "local-machine"
    else:
        raise CredentialError(
            "credential.backend_unsupported",
            "当前操作系统凭据后端不受支持",
        )
    if is_windows_vault and persistence != "local-machine":
        raise CredentialError(
            "credential.backend_unsupported",
            "当前操作系统凭据后端不受支持",
        )
    if is_windows_vault and declared_scope is None:
        try:
            cast(Any, backend).persist = "local machine"
        except (AttributeError, TypeError) as error:
            raise CredentialError(
                "credential.backend_unsupported",
                "Windows 凭据后端无法固定为本机持久化",
            ) from error

    return CredentialStore(
        _backend=cast(CredentialBackend, backend),
        backend_name=name,
        persistence=persistence,
    )
