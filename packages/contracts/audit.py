from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AuditEventType(StrEnum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    ROLE_ASSIGN = "role_assign"
    ROLE_REVOKE = "role_revoke"
    KINDERGARTEN_UPDATE = "kindergarten_update"
    SEMESTER_CREATE = "semester_create"
    SEMESTER_UPDATE = "semester_update"
    CLASS_CREATE = "class_create"
    CLASS_UPDATE = "class_update"
    TEACHER_ASSIGN = "teacher_assign"
    TEACHER_REVOKE = "teacher_revoke"
    AREA_CREATE = "area_create"
    AREA_UPDATE = "area_update"
    PLAN_CREATE = "plan_create"
    PLAN_SAVE = "plan_save"
    PLAN_AUTOSAVE = "plan_autosave"
    PLAN_ARCHIVE = "plan_archive"
    PLAN_UNARCHIVE = "plan_unarchive"
    PLAN_RESTORE = "plan_restore"
    MODEL_PROFILE_CREATE = "model_profile_create"
    MODEL_PROFILE_UPDATE = "model_profile_update"
    MODEL_PROFILE_ENABLE = "model_profile_enable"
    MODEL_PROFILE_DISABLE = "model_profile_disable"
    PROMPT_CREATE = "prompt_create"
    PROMPT_PUBLISH = "prompt_publish"
    PROMPT_ROLLBACK = "prompt_rollback"
    AI_GENERATE = "ai_generate"
    AI_ADOPT = "ai_adopt"
    AI_RETRY = "ai_retry"
    EXPORT_CREATE = "export_create"
    EXPORT_DOWNLOAD = "export_download"


class AuditEvent(BaseModel):
    id: str = Field(..., description="事件ID")
    event_type: AuditEventType = Field(..., description="事件类型")
    user_id: str = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户名")
    kindergarten_id: str = Field(..., description="园所ID")
    resource_type: str | None = Field(None, description="资源类型")
    resource_id: str | None = Field(None, description="资源ID")
    details: dict[str, object] = Field(..., description="详情(脱敏)")
    result: str = Field(..., description="结果: success/failed")
    ip_address: str | None = Field(None, description="IP地址")
    created_at: datetime = Field(..., description="创建时间")


class AuditListResponse(BaseModel):
    events: list[AuditEvent] = Field(..., description="事件列表")
    total: int = Field(..., description="总数")


class AuditQueryRequest(BaseModel):
    event_type: AuditEventType | None = Field(None, description="事件类型")
    user_id: str | None = Field(None, description="用户ID")
    resource_type: str | None = Field(None, description="资源类型")
    resource_id: str | None = Field(None, description="资源ID")
    start_time: datetime | None = Field(None, description="开始时间")
    end_time: datetime | None = Field(None, description="结束时间")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页大小")
