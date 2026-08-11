"""单一 AI 模型、OS 凭据与提示词覆盖的应用服务。"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Protocol

from kindergarten_manager.infrastructure.ai.client import validate_base_url
from kindergarten_manager.infrastructure.ai.prompts import load_default_prompt

_CREDENTIAL_ACCOUNT = "ai.current"
_PROMPT_CODES = (
    "morning_activity",
    "morning_talk",
    "indoor_area_game",
    "afternoon_outdoor_game",
    "daily_reflection",
)


class AiSettingsError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.code = error_code


class AiSettingsRepository(Protocol):
    def get_configuration(self) -> Any: ...

    def settings_transaction(
        self,
        now_utc_ms: int,
    ) -> AbstractContextManager[AiSettingsTransaction]: ...

    def get_prompt_override(self, prompt_code: str) -> str | None: ...

    def delete_prompt_override(self, prompt_code: str) -> None: ...


class AiSettingsTransaction(Protocol):
    def save_configuration(
        self,
        *,
        base_url: str | None,
        model_name: str | None,
        credential_configured: bool,
        enabled: bool,
    ) -> None: ...

    def set_prompt_override(self, prompt_code: str, content: str) -> None: ...

    def delete_prompt_override(self, prompt_code: str) -> None: ...


class CredentialPort(Protocol):
    def write(self, account: str, secret: str) -> None: ...

    def read(self, account: str) -> str | None: ...

    def delete(self, account: str) -> None: ...


@dataclass(frozen=True, slots=True)
class AiSettingsView:
    base_url: str | None
    model_name: str | None
    credential_configured: bool
    enabled: bool
    prompts: dict[str, str]


class AiSettingsService:
    def __init__(
        self,
        repository: AiSettingsRepository,
        credential_store: CredentialPort | None,
        *,
        now_utc_ms: Callable[[], int],
    ) -> None:
        self._repository = repository
        self._credential_store = credential_store
        self._now_utc_ms = now_utc_ms

    def load(self) -> AiSettingsView:
        configuration = self._repository.get_configuration()
        credential_configured = bool(
            configuration is not None
            and configuration.credential_configured
            and self._credential_store is not None
            and self._credential_store.read(_CREDENTIAL_ACCOUNT) is not None
        )
        return AiSettingsView(
            base_url=configuration.base_url if configuration is not None else None,
            model_name=configuration.model_name if configuration is not None else None,
            credential_configured=credential_configured,
            enabled=bool(
                configuration is not None and configuration.enabled and credential_configured
            ),
            prompts={
                code: self._repository.get_prompt_override(code) or load_default_prompt(code)
                for code in _PROMPT_CODES
            },
        )

    def save(self, values: Mapping[str, object]) -> AiSettingsView:
        base_url = str(values.get("base_url", "")).strip() or None
        model_name = str(values.get("model_name", "")).strip() or None
        enabled = values.get("enabled") is True
        api_key = str(values.get("api_key", ""))
        prompts = values.get("prompts")
        if not isinstance(prompts, Mapping):
            raise AiSettingsError("ai.prompts_invalid", "提示词设置无效")
        if base_url is not None:
            try:
                base_url = validate_base_url(base_url)
            except ValueError as error:
                raise AiSettingsError("ai.base_url_invalid", "AI 服务地址无效") from error
        if model_name is not None and len(model_name) > 200:
            raise AiSettingsError("ai.model_name_invalid", "模型名过长")
        normalized_prompts: dict[str, str] = {}
        for code in _PROMPT_CODES:
            content = prompts.get(code)
            if not isinstance(content, str) or not content.strip():
                raise AiSettingsError("ai.prompt_invalid", "提示词不能为空")
            normalized_prompts[code] = content

        previous_secret = (
            self._credential_store.read(_CREDENTIAL_ACCOUNT)
            if self._credential_store is not None
            else None
        )
        credential_configured = previous_secret is not None or bool(api_key)
        if enabled and (base_url is None or model_name is None or not credential_configured):
            raise AiSettingsError(
                "ai.configuration_incomplete",
                "启用 AI 前必须填写地址、模型名并安全保存 API Key",
            )
        if api_key:
            if self._credential_store is None:
                raise AiSettingsError(
                    "credential.backend_unsupported",
                    "当前环境没有可用的 Windows 本机凭据存储",
                )
            self._credential_store.write(_CREDENTIAL_ACCOUNT, api_key)

        now_utc_ms = int(self._now_utc_ms())
        try:
            with self._repository.settings_transaction(now_utc_ms) as transaction:
                transaction.save_configuration(
                    base_url=base_url,
                    model_name=model_name,
                    credential_configured=credential_configured,
                    enabled=enabled,
                )
                for code in _PROMPT_CODES:
                    content = normalized_prompts[code]
                    if content == load_default_prompt(code):
                        transaction.delete_prompt_override(code)
                    else:
                        transaction.set_prompt_override(code, content)
        except Exception:
            if api_key and self._credential_store is not None:
                if previous_secret is None:
                    self._credential_store.delete(_CREDENTIAL_ACCOUNT)
                else:
                    self._credential_store.write(_CREDENTIAL_ACCOUNT, previous_secret)
            raise
        return self.load()

    def reset_prompt(self, prompt_code: str) -> str:
        default = load_default_prompt(prompt_code)
        self._repository.delete_prompt_override(prompt_code)
        return default
