from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from tests.desktop.helpers import pending_module, pending_symbol


@dataclass
class MemoryWindowsBackend:
    name: str = "Windows WinVaultKeyring"
    storage_scope: str = "local-machine"
    values: dict[tuple[str, str], str] = field(default_factory=dict)

    def set_password(self, service: str, account: str, secret: str) -> None:
        self.values[(service, account)] = secret

    def get_password(self, service: str, account: str) -> str | None:
        return self.values.get((service, account))

    def delete_password(self, service: str, account: str) -> None:
        self.values.pop((service, account), None)


def _module():
    return pending_module("kindergarten_manager.infrastructure.credentials")


def test_windows_backend_is_selected_only_for_local_machine_persistence() -> None:
    module = _module()
    create_store = pending_symbol(module, "create_credential_store")
    backend = MemoryWindowsBackend()

    store = create_store(platform="win32", backend=backend)

    assert store.backend_name == "Windows WinVaultKeyring"
    assert store.persistence == "local-machine"


def test_credential_round_trip_and_delete_use_stable_application_key() -> None:
    module = _module()
    create_store = pending_symbol(module, "create_credential_store")
    backend = MemoryWindowsBackend()
    store = create_store(platform="win32", backend=backend)

    store.write("ai.current", "fixture-api-key")
    assert store.read("ai.current") == "fixture-api-key"
    assert list(backend.values) == [("cn.kindergartenmanager.desktop", "ai.current")]
    store.delete("ai.current")
    assert store.read("ai.current") is None


def test_realistic_windows_backend_is_pinned_to_local_machine_persistence() -> None:
    module = _module()
    create_store = pending_symbol(module, "create_credential_store")
    backend_type = type(
        "RealisticWindowsBackend",
        (),
        {
            "name": "Windows WinVaultKeyring",
            "persist": "enterprise",
            "set_password": lambda *_args: None,
            "get_password": lambda *_args: None,
            "delete_password": lambda *_args: None,
        },
    )
    backend = backend_type()

    store = create_store(platform="win32", backend=backend)

    assert store.persistence == "local-machine"
    assert getattr(backend, "persist", None) == "local machine"


def test_secret_never_appears_in_store_repr_or_missing_error() -> None:
    module = _module()
    create_store = pending_symbol(module, "create_credential_store")
    store = create_store(platform="win32", backend=MemoryWindowsBackend())
    store.write("ai.current", "fixture-api-key")

    assert "fixture-api-key" not in repr(store)
    store.delete("ai.current")
    with pytest.raises(Exception) as captured:
        store.require("ai.current")
    assert "fixture-api-key" not in str(captured.value)
    assert getattr(captured.value, "code", None) == "credential.missing"


@pytest.mark.parametrize(
    "backend",
    [
        None,
        type("NullKeyring", (), {"name": "keyring.backends.null.Keyring"})(),
        type("FileKeyring", (), {"name": "keyrings.alt.file.PlaintextKeyring"})(),
        type("UnknownKeyring", (), {"name": "unknown.Backend"})(),
    ],
)
def test_null_file_and_unknown_backends_fail_closed(backend: object | None) -> None:
    module = _module()
    create_store = pending_symbol(module, "create_credential_store")

    with pytest.raises(Exception) as captured:
        create_store(platform="win32", backend=backend)
    assert getattr(captured.value, "code", None) == "credential.backend_unsupported"
