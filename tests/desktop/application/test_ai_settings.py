from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest

from kindergarten_manager.application.ai_settings import (
    AiSettingsService,
    AiSettingsTransaction,
)
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
            "group_activity",
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
            "vision_enabled": True,
            "vision_base_url": "https://vision.example.test/v1",
            "vision_model_name": "fixture-vision-model",
            "vision_api_key": "fixture-vision-api-key",
            "prompts": _prompts(),
        }
    )

    assert credentials.values == {
        "ai.current": "fixture-api-key",
        "ai.vision": "fixture-vision-api-key",
    }
    assert view.enabled is True
    assert view.credential_configured is True
    assert view.vision_enabled is True
    assert view.vision_credential_configured is True
    assert "fixture-api-key" not in repr(view)
    assert "fixture-api-key" not in database.read_bytes().decode("utf-8", errors="ignore")
    assert "fixture-vision-api-key" not in database.read_bytes().decode("utf-8", errors="ignore")


def test_builtin_prompts_keep_mature_teaching_constraints_and_closed_json_schema() -> None:
    prompts = _prompts()

    assert all("schema_version" in content for content in prompts.values())
    assert all("Markdown" in content for content in prompts.values())
    assert '"physical_cycle"' in prompts["morning_activity"]
    assert "户外体育活动" in prompts["morning_activity"]
    assert "集体体育游戏" in prompts["morning_activity"]
    assert "自主体育游戏" in prompts["morning_activity"]
    assert '"questions"' in prompts["morning_talk"]
    assert '"support_strategies"' in prompts["indoor_area_game"]
    assert "从可用户外区域中选择" in prompts["afternoon_outdoor_game"]
    assert '"highlights"' in prompts["daily_reflection"]
    assert '"process"' in prompts["group_activity"]


@pytest.mark.parametrize(
    "legacy_prompt",
    [
        (
            "请根据教师提供的最小上下文生成晨间活动。"
            "只返回符合 morning_activity Schema 的 JSON，不得补充幼儿身份信息。"
        ),
        """你是一名熟悉幼儿年龄特点和幼儿园一日活动组织的教师。请根据教师提供的日期、年龄段、主题和已有内容，设计可直接执行的晨间活动。

要求：
1. 体能大循环、集体游戏和自主游戏要相互衔接，运动强度由低到高再平稳过渡。
2. 目标和指导要点必须具体、可观察、适合该年龄段，避免空泛表述。
3. 不得补充幼儿姓名、教师账号等身份信息，不得虚构输入中没有的设施。
4. 只输出一个合法 JSON 对象，不要输出 Markdown、代码围栏、解释或额外字段。

严格使用以下结构，schema_version 固定为 1：
{"schema_version":1,"physical_cycle":"体能大循环安排","group_game":"集体游戏","free_game":"自主游戏","focus_guidance":"重点指导","objectives":["目标1","目标2"],"guidance_points":["指导要点1","指导要点2"]}""",
    ],
)
def test_published_legacy_morning_prompt_upgrades_to_current_default(
    legacy_prompt: str,
) -> None:
    repository = TransactionalSettingsRepository(prompts={"morning_activity": legacy_prompt})
    service = AiSettingsService(repository, MemoryCredentialStore(), now_utc_ms=lambda: 10)

    prompt = service.load().prompts["morning_activity"]

    assert prompt == load_default_prompt("morning_activity")
    assert "户外体育活动" in prompt
    assert "集体体育游戏" in prompt
    assert "自主体育游戏" in prompt


def test_custom_morning_prompt_is_not_replaced_by_builtin_upgrade() -> None:
    custom = "本园自定义晨间体育提示词：只使用操场和沙池。"
    repository = TransactionalSettingsRepository(prompts={"morning_activity": custom})
    service = AiSettingsService(repository, MemoryCredentialStore(), now_utc_ms=lambda: 10)

    assert service.load().prompts["morning_activity"] == custom


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


@dataclass
class TransactionalSettingsRepository:
    events: list[str] = field(default_factory=list)
    configuration: object | None = None
    prompts: dict[str, str] = field(default_factory=dict)

    def get_configuration(self) -> object | None:
        return self.configuration

    def get_prompt_override(self, prompt_code: str) -> str | None:
        return self.prompts.get(prompt_code)

    @contextmanager
    def settings_transaction(self, now_utc_ms: int) -> Iterator[AiSettingsTransaction]:
        assert now_utc_ms == 10
        self.events.append("begin")
        transaction = FakeSettingsTransaction(self)
        try:
            yield transaction
        except Exception:
            self.events.append("rollback")
            raise
        else:
            self.events.append("commit")

    def _save_configuration(self, **values: object) -> None:
        self.events.append("configuration")
        self.configuration = SimpleNamespace(**values)

    def _set_prompt_override(self, prompt_code: str, content: str) -> None:
        self.events.append(f"set:{prompt_code}")
        self.prompts[prompt_code] = content

    def _delete_prompt_override(self, prompt_code: str) -> None:
        self.events.append(f"delete:{prompt_code}")
        self.prompts.pop(prompt_code, None)


@dataclass
class FakeSettingsTransaction:
    repository: TransactionalSettingsRepository

    def save_configuration(
        self,
        *,
        base_url: str | None,
        model_name: str | None,
        credential_configured: bool,
        enabled: bool,
    ) -> None:
        self.repository._save_configuration(
            base_url=base_url,
            model_name=model_name,
            credential_configured=credential_configured,
            enabled=enabled,
        )

    def save_vision_configuration(
        self,
        *,
        base_url: str | None,
        model_name: str | None,
        credential_configured: bool,
        enabled: bool,
    ) -> None:
        self.repository.events.append("vision_configuration")

    def set_prompt_override(self, prompt_code: str, content: str) -> None:
        self.repository._set_prompt_override(prompt_code, content)

    def delete_prompt_override(self, prompt_code: str) -> None:
        self.repository._delete_prompt_override(prompt_code)


def test_application_service_owns_ai_settings_transaction_scope() -> None:
    repository = TransactionalSettingsRepository()
    service = AiSettingsService(repository, MemoryCredentialStore(), now_utc_ms=lambda: 10)

    service.save(
        {
            "enabled": False,
            "base_url": "https://ai.example.test/v1",
            "model_name": "fixture-model",
            "api_key": "",
            "prompts": _prompts(),
        }
    )

    assert repository.events == [
        "begin",
        "configuration",
        "delete:morning_activity",
        "delete:morning_talk",
        "delete:indoor_area_game",
        "delete:afternoon_outdoor_game",
        "delete:daily_reflection",
        "delete:group_activity",
        "commit",
    ]


def test_application_service_owns_prompt_reset_transaction_scope() -> None:
    repository = TransactionalSettingsRepository(prompts={"morning_talk": "自定义提示词"})
    service = AiSettingsService(repository, MemoryCredentialStore(), now_utc_ms=lambda: 10)

    default = service.reset_prompt("morning_talk")

    assert default == load_default_prompt("morning_talk")
    assert repository.prompts == {}
    assert repository.events == ["begin", "delete:morning_talk", "commit"]
