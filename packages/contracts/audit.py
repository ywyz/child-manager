"""身份阶段需要的稳定审计事件代码。"""

from enum import StrEnum

from packages.contracts.common import ContractModel, ResourceReference


class IdentityAuditEventCode(StrEnum):
    INITIALIZED = "identity.initialized"
    LOGIN_SUCCEEDED = "identity.login_succeeded"
    LOGIN_FAILED = "identity.login_failed"
    LOGIN_RATE_LIMITED = "identity.login_rate_limited"
    TOKEN_REFRESHED = "identity.token_refreshed"
    REFRESH_REPLAYED = "identity.refresh_replayed"
    LOGGED_OUT = "identity.logged_out"
    PASSWORD_CHANGED = "identity.password_changed"
    USER_CREATED = "identity.user_created"
    USER_UPDATED = "identity.user_updated"
    USER_ACTIVATED = "identity.user_activated"
    USER_DEACTIVATED = "identity.user_deactivated"
    USER_ROLES_CHANGED = "identity.user_roles_changed"
    PASSWORD_RESET = "identity.password_reset"


class AuditEventReference(ContractModel):
    event_code: IdentityAuditEventCode
    resource: ResourceReference | None = None
