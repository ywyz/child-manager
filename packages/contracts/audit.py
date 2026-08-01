"""身份阶段的稳定审计事件代码与最小资源引用。"""

from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import Field, StrictStr

from packages.contracts.common import ContractModel, ResourceReference


class IdentityAuditEventCode(StrEnum):
    BOOTSTRAP_STARTED = "identity.bootstrap_started"
    BOOTSTRAP_REGISTERED = "identity.bootstrap_registered"
    BOOTSTRAP_ACTIVATED = "identity.bootstrap_activated"
    AUTHENTICATION_SUCCEEDED = "identity.authentication_succeeded"
    AUTHENTICATION_FAILED = "identity.authentication_failed"
    AUTHENTICATION_RATE_LIMITED = "identity.authentication_rate_limited"
    TOKEN_REFRESHED = "identity.token_refreshed"
    REFRESH_REPLAYED = "identity.refresh_replayed"
    LOGGED_OUT = "identity.logged_out"
    USER_CREATED = "identity.user_created"
    USER_UPDATED = "identity.user_updated"
    USER_ACTIVATED = "identity.user_activated"
    USER_DEACTIVATED = "identity.user_deactivated"
    USER_ROLES_CHANGED = "identity.user_roles_changed"
    INVITATION_ISSUED = "identity.invitation_issued"
    INVITATION_REVOKED = "identity.invitation_revoked"
    CREDENTIAL_REGISTERED = "identity.credential_registered"
    CREDENTIAL_UPDATED = "identity.credential_updated"
    CREDENTIAL_REVOKED = "identity.credential_revoked"
    RECOVERY_REQUESTED = "identity.recovery_requested"
    RECOVERY_APPROVED = "identity.recovery_approved"
    RECOVERY_COMPLETED = "identity.recovery_completed"
    RECOVERY_CODE_ROTATED = "identity.recovery_code_rotated"
    SESSION_REVOKED = "identity.session_revoked"
    BACKUP_ENABLED = "auth.backup_enabled"
    BACKUP_CHANGED = "auth.backup_changed"
    BACKUP_DISABLED = "auth.backup_disabled"
    BACKUP_LOGIN_SUCCEEDED = "auth.backup_login_succeeded"
    PASSKEY_ADDED_FROM_BACKUP = "auth.passkey_added_from_backup"
    BACKUP_REVOKED_BY_RECOVERY = "auth.backup_revoked_by_recovery"
    PLAN_MANUALLY_SAVED = "lesson_plan.manually_saved"
    PLAN_ARCHIVED = "lesson_plan.archived"
    PLAN_UNARCHIVED = "lesson_plan.unarchived"
    PLAN_EXPORT_REQUESTED = "lesson_plan.export_requested"
    PLAN_EXPORT_DOWNLOADED = "lesson_plan.export_downloaded"
    PLAN_EXPORT_DOWNLOAD_FAILED = "lesson_plan.export_download_failed"
    PLAN_HISTORY_RESTORED = "lesson_plan.history_restored"
    AI_MODEL_CREATED = "ai_model.created"
    AI_MODEL_UPDATED = "ai_model.updated"
    AI_MODEL_ENABLED = "ai_model.enabled"
    AI_MODEL_DISABLED = "ai_model.disabled"
    PROMPT_PUBLISHED = "prompt.published"
    PROMPT_RESTORED = "prompt.restored"
    PROMPT_TEST_ATTEMPTED = "prompt.test_attempted"
    PROMPT_TESTS_CLEARED = "prompt.tests_cleared"
    AI_GENERATION_CREATED = "ai.generation_created"
    AI_AUTOMATIC_RETRY_SCHEDULED = "ai.automatic_retry_scheduled"
    AI_GENERATION_RETRIED = "ai.generation_retried"
    AI_GENERATION_SUCCEEDED = "ai.generation_succeeded"
    AI_GENERATION_FAILED = "ai.generation_failed"
    AI_PREVIEW_REJECTED = "ai.preview_rejected"
    AI_PREVIEW_ADOPTED = "ai.preview_adopted"

    # 通用登录审计名称保留为认证 ceremony 的兼容别名, 不代表密码登录。
    INITIALIZED = "identity.bootstrap_started"
    LOGIN_SUCCEEDED = "identity.authentication_succeeded"
    LOGIN_FAILED = "identity.authentication_failed"
    LOGIN_RATE_LIMITED = "identity.authentication_rate_limited"


class IdentityAuditMetadata(ContractModel):
    """身份审计只允许承载最小、严格类型化的非秘密元数据。"""

    reason: Annotated[StrictStr, Field(max_length=64)] | None = None
    source: Annotated[StrictStr, Field(max_length=160)] | None = None
    elapsed_ms: Annotated[int, Field(ge=0)] | None = None
    error_summary: Annotated[StrictStr, Field(max_length=1000)] | None = None
    target_role_codes: list[Annotated[StrictStr, Field(max_length=64)]] | None = None


class AiGenerationAuditMetadata(ContractModel):
    """AI 审计只保留任务谱系与脱敏执行摘要。"""

    job_id: UUID | None = None
    retry_of_job_id: UUID | None = None
    attempt_count: Annotated[int, Field(ge=0, le=3)] | None = None
    error_code: Annotated[StrictStr, Field(max_length=160)] | None = None
    target_section: Annotated[StrictStr, Field(max_length=160)] | None = None


class AuditEventReference(ContractModel):
    event_code: IdentityAuditEventCode
    resource: ResourceReference | None = None
