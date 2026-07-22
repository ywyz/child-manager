"""身份阶段的稳定审计事件代码与最小资源引用。"""

from enum import StrEnum

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

    # 通用登录审计名称保留为认证 ceremony 的兼容别名, 不代表密码登录。
    INITIALIZED = "identity.bootstrap_started"
    LOGIN_SUCCEEDED = "identity.authentication_succeeded"
    LOGIN_FAILED = "identity.authentication_failed"
    LOGIN_RATE_LIMITED = "identity.authentication_rate_limited"


class AuditEventReference(ContractModel):
    event_code: IdentityAuditEventCode
    resource: ResourceReference | None = None
