"""AI 模型档案生命周期与调用配置 revision 事务。"""

from __future__ import annotations

import json
import os
import socket
import unicodedata
from pathlib import Path
from uuid import UUID, uuid7

import psycopg
from cryptography.exceptions import InvalidTag

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.service import IdentityError, IdentityService, SessionUser
from packages.backend.integrations.ai.url_policy import (
    AiUrlPolicyError,
    Resolver,
    validate_ai_base_url,
)
from packages.backend.integrations.crypto.ai_keys import (
    AiKeyEnvelope,
    FileAiKeyProvider,
    StaticAiKeyProvider,
    decrypt_api_key_with_provider,
    encrypt_api_key_with_provider,
)
from packages.backend.settings.repository import (
    AiModelProfileRecord,
    AiModelProfileRepository,
)
from packages.contracts.audit import IdentityAuditEventCode
from packages.contracts.settings import AiModelProfileWrite

AiKeyProvider = StaticAiKeyProvider | FileAiKeyProvider


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _display(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def _key(value: str) -> str:
    return _display(value).casefold()


class AiModelService:
    def __init__(
        self,
        *,
        database_url: str,
        key_provider: AiKeyProvider,
        resolver: Resolver | None = None,
        allowed_hosts: set[str] | frozenset[str],
    ) -> None:
        self.database_url = database_url
        self.key_provider = key_provider
        self.resolver: Resolver = resolver or socket.getaddrinfo
        self.allowed_hosts = frozenset(allowed_hosts)

    @classmethod
    def from_environment(cls) -> AiModelService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        keyring_value = os.environ.get("CHILD_MANAGER_AI_KEYRING")
        key_id = os.environ.get("CHILD_MANAGER_AI_ACTIVE_KEY_ID")
        hosts = {
            value.strip()
            for value in os.environ.get("CHILD_MANAGER_AI_ALLOWED_HOSTS", "").split(",")
            if value.strip()
        }
        if not database_url or not keyring_value or not key_id or not hosts:
            raise IdentityError(503, "configuration.unavailable", "AI 模型安全配置不可用。")
        try:
            keyring = {
                str(item_key): Path(str(item_path))
                for item_key, item_path in json.loads(keyring_value).items()
            }
        except (AttributeError, TypeError, ValueError) as exc:
            raise IdentityError(
                503, "configuration.unavailable", "AI 主密钥 keyring 配置无效。"
            ) from exc
        provider = FileAiKeyProvider(
            keyring,
            active_key_id=key_id,
            repository_root=Path(__file__).resolve().parents[3],
        )
        return cls(
            database_url=database_url,
            key_provider=provider,
            allowed_hosts=hosts,
        )

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _scope(session: SessionUser) -> UUID:
        IdentityService.require_admin(session)
        if session.user.kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return session.user.kindergarten_id

    def _validate_url(self, value: str) -> str:
        try:
            return validate_ai_base_url(
                value,
                resolver=self.resolver,
                allowed_hosts=self.allowed_hosts,
            ).value
        except AiUrlPolicyError as exc:
            raise IdentityError(422, "ai_model.invalid_url", str(exc)) from exc

    @staticmethod
    def _envelope(record: AiModelProfileRecord) -> AiKeyEnvelope | None:
        if (
            record.api_key_ciphertext is None
            or record.api_key_nonce is None
            or record.api_key_key_id is None
            or record.api_key_encryption_version is None
        ):
            return None
        return AiKeyEnvelope(
            ciphertext=record.api_key_ciphertext,
            nonce=record.api_key_nonce,
            key_id=record.api_key_key_id,
            envelope_version=record.api_key_encryption_version,
            last_four=record.api_key_last_four or "",
        )

    def list(
        self, session: SessionUser, *, page: int, page_size: int
    ) -> tuple[list[AiModelProfileRecord], int]:
        kindergarten_id = self._scope(session)
        with self._connect() as connection:
            return AiModelProfileRepository(connection).list(
                kindergarten_id, page=page, page_size=page_size
            )

    def get(self, session: SessionUser, profile_id: UUID) -> AiModelProfileRecord:
        kindergarten_id = self._scope(session)
        with self._connect() as connection:
            record = AiModelProfileRepository(connection).get(kindergarten_id, profile_id)
        if record is None:
            raise IdentityError(404, "resource.not_found", "模型档案不存在。")
        return record

    def create(
        self,
        session: SessionUser,
        body: AiModelProfileWrite,
    ) -> AiModelProfileRecord:
        kindergarten_id = self._scope(session)
        name = _display(body.name)
        model_name = _display(body.model_name)
        if not name or not model_name:
            raise IdentityError(422, "ai_model.invalid_profile", "名称和模型名不能为空。")
        base_url = self._validate_url(body.api_base_url)
        profile_id = uuid7()
        envelope = (
            encrypt_api_key_with_provider(
                body.api_key,
                key_provider=self.key_provider,
                kindergarten_id=kindergarten_id,
                profile_id=profile_id,
            )
            if body.api_key is not None
            else None
        )
        try:
            with self._connect() as connection, connection.transaction():
                record = AiModelProfileRepository(connection).create(
                    kindergarten_id,
                    profile_id=profile_id,
                    name=name,
                    name_normalized=_key(name),
                    api_base_url=base_url,
                    model_name=model_name,
                    envelope=envelope,
                    capability_codes=sorted(body.capability_codes),
                    max_concurrency=body.max_concurrency,
                    rate_limit_per_minute=body.rate_limit_per_minute,
                    is_default=body.is_default,
                    actor_id=session.user.id,
                )
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.AI_MODEL_CREATED,
                    actor_user_id=session.user.id,
                    actor_role_codes=list(session.role_codes),
                    resource_type="ai_model_profile",
                    resource_id=profile_id,
                    outcome="success",
                )
                return record
        except psycopg.IntegrityError as exc:
            raise IdentityError(409, "ai_model.conflict", "模型档案与现有记录冲突。") from exc

    def update(
        self,
        session: SessionUser,
        profile_id: UUID,
        body: AiModelProfileWrite,
    ) -> AiModelProfileRecord:
        kindergarten_id = self._scope(session)
        name = _display(body.name)
        model_name = _display(body.model_name)
        base_url = self._validate_url(body.api_base_url)
        try:
            with self._connect() as connection, connection.transaction():
                repository = AiModelProfileRepository(connection)
                current = repository.get(kindergarten_id, profile_id, for_update=True)
                if current is None:
                    raise IdentityError(404, "resource.not_found", "模型档案不存在。")
                replace_key = body.api_key is not None
                envelope: AiKeyEnvelope | None = None
                key_changed = False
                if body.api_key is not None:
                    old_envelope = self._envelope(current)
                    if old_envelope is None:
                        key_changed = True
                    else:
                        try:
                            previous = decrypt_api_key_with_provider(
                                old_envelope,
                                key_provider=self.key_provider,
                                kindergarten_id=kindergarten_id,
                                profile_id=profile_id,
                            )
                        except (InvalidTag, LookupError, UnicodeDecodeError) as exc:
                            raise IdentityError(
                                503,
                                "configuration.unavailable",
                                "模型密钥暂不可用。",
                            ) from exc
                        key_changed = previous != body.api_key
                    envelope = encrypt_api_key_with_provider(
                        body.api_key,
                        key_provider=self.key_provider,
                        kindergarten_id=kindergarten_id,
                        profile_id=profile_id,
                    )
                changed = (
                    current.api_base_url != base_url
                    or current.model_name != model_name
                    or set(current.capability_codes) != set(body.capability_codes)
                    or key_changed
                )
                record = repository.update(
                    kindergarten_id,
                    profile_id,
                    name=name,
                    name_normalized=_key(name),
                    api_base_url=base_url,
                    model_name=model_name,
                    envelope=envelope,
                    replace_key=replace_key,
                    capability_codes=sorted(body.capability_codes),
                    max_concurrency=body.max_concurrency,
                    rate_limit_per_minute=body.rate_limit_per_minute,
                    is_default=body.is_default,
                    increment_revision=changed,
                    actor_id=session.user.id,
                )
                assert record is not None
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.AI_MODEL_UPDATED,
                    actor_user_id=session.user.id,
                    actor_role_codes=list(session.role_codes),
                    resource_type="ai_model_profile",
                    resource_id=profile_id,
                    outcome="success",
                )
                return record
        except psycopg.IntegrityError as exc:
            raise IdentityError(409, "ai_model.conflict", "模型档案与现有记录冲突。") from exc

    def set_enabled(
        self,
        session: SessionUser,
        profile_id: UUID,
        *,
        enabled: bool,
    ) -> AiModelProfileRecord:
        kindergarten_id = self._scope(session)
        with self._connect() as connection, connection.transaction():
            repository = AiModelProfileRepository(connection)
            current = repository.get(kindergarten_id, profile_id, for_update=True)
            if current is None:
                raise IdentityError(404, "resource.not_found", "模型档案不存在。")
            if enabled and (
                current.api_key_ciphertext is None
                or not {"text", "structured_output"} <= set(current.capability_codes)
            ):
                raise IdentityError(
                    422,
                    "ai_model.not_ready",
                    "启用前必须配置 API Key 及文本、结构化输出能力。",
                )
            record = repository.set_enabled(
                kindergarten_id,
                profile_id,
                enabled=enabled,
                actor_id=session.user.id,
            )
            assert record is not None
            AuditRepository(connection, kindergarten_id).append(
                event_code=(
                    IdentityAuditEventCode.AI_MODEL_ENABLED
                    if enabled
                    else IdentityAuditEventCode.AI_MODEL_DISABLED
                ),
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                resource_type="ai_model_profile",
                resource_id=profile_id,
                outcome="success",
            )
            return record
