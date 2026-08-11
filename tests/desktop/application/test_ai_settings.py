from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from kindergarten_manager.application.ai_settings import AiSettingsService
from kindergarten_manager.infrastructure.ai.prompts import load_default_prompt
from kindergarten_manager.infrastructure.database.repositories import AiRepository
from kindergarten_manager.infrastructure.database.upgrade import upgrade_database


@dataclass
class MemoryCredentialStore:
    values: dict[str, str] = field(default_factory=dict)

    def write(self, account: str, secret: str) -> None:
        self.values[account] = secret

    def read(self, account: str) -> str | None:
        return self.values.get(account)

    def delete(self, account: str) -> None:
        self.values.pop(account, None)


def _prompts() -> dict[str, str]:
    return {
        code: load_default_prompt(code)
        for code in (
            "morning_activity",
            "morning_talk",
            "indoor_area_game",
            "afternoon_outdoor_game",
            "daily_reflection",
        )
    }


def test_ai_settings_put_secret_only_in_credential_store(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    upgrade_database(database)
    credentials = MemoryCredentialStore()
    service = AiSettingsService(
        AiRepository(database),
        credentials,
        now_utc_ms=lambda: 10,
    )

    view = service.save(
        {
            "enabled": True,
            "base_url": "https://ai.example.test/v1",
            "model_name": "fixture-model",
            "api_key": "fixture-api-key",
            "prompts": _prompts(),
        }
    )

    assert credentials.values == {"ai.current": "fixture-api-key"}
    assert view.enabled is True
    assert view.credential_configured is True
    assert "fixture-api-key" not in repr(view)
    assert "fixture-api-key" not in database.read_bytes().decode("utf-8", errors="ignore")


def test_enabling_without_supported_credential_backend_fails_before_database_write(
    tmp_path: Path,
) -> None:
    database = tmp_path / "desktop.sqlite3"
    upgrade_database(database)
    repository = AiRepository(database)
    service = AiSettingsService(repository, None, now_utc_ms=lambda: 10)

    with pytest.raises(Exception) as captured:
        service.save(
            {
                "enabled": True,
                "base_url": "https://ai.example.test/v1",
                "model_name": "fixture-model",
                "api_key": "fixture-api-key",
                "prompts": _prompts(),
            }
        )

    assert getattr(captured.value, "code", None) == "credential.backend_unsupported"
    assert repository.get_configuration() is None
    assert "fixture-api-key" not in database.read_bytes().decode("utf-8", errors="ignore")
