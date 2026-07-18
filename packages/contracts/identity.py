"""身份与认证公共 Schema。"""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class KindergartenSnapshot(BaseModel):
    """当前登录用户所属园所快照。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="园所ID")
    name: str = Field(..., description="园所名称")
    timezone: str = Field(default="Asia/Shanghai", description="园所时区")


class CurrentUser(BaseModel):
    """当前登录用户。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    kindergarten: KindergartenSnapshot = Field(..., description="所属园所快照")
    role_codes: list[str] = Field(default_factory=list, description="角色代码列表")
    capabilities: list[str] = Field(default_factory=list, description="能力标签列表")

    @property
    def kindergarten_id(self) -> str:
        """内部兼容：返回所属园所ID。"""
        return self.kindergarten.id

    @property
    def roles(self) -> list[str]:
        """内部兼容：返回角色代码列表。"""
        return self.role_codes


class CsrfResponse(BaseModel):
    """CSRF 令牌响应。"""

    model_config = ConfigDict(extra="forbid")

    csrf_token: str = Field(..., description="CSRF 令牌")


class LoginRequest(BaseModel):
    """登录请求。"""

    model_config = ConfigDict(extra="forbid")

    login: str = Field(..., description="用户名或手机号")
    password: str = Field(..., description="密码")


class RefreshRequest(BaseModel):
    """刷新请求。"""

    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(..., description="Refresh 令牌")


class ChangePasswordRequest(BaseModel):
    """修改密码请求。"""

    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(..., description="原密码")
    new_password: str = Field(..., description="新密码")


_ALLOWED_ROLE_CODES = {"admin", "teacher"}


def _validate_role_codes(value: list[str]) -> list[str]:
    """校验角色列表：非空、唯一、仅允许 admin/teacher。"""
    if not value:
        raise ValueError("角色列表不能为空")
    codes = [code.strip().lower() for code in value]
    if len(set(codes)) != len(codes):
        raise ValueError("角色不能重复")
    unknown = set(codes) - _ALLOWED_ROLE_CODES
    if unknown:
        raise ValueError(f"未知角色: {', '.join(sorted(unknown))}")
    return codes


class UserCreateRequest(BaseModel):
    """创建用户请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    phone_e164: str | None = Field(None, description="手机号(E.164)")
    role_codes: list[str] = Field(default_factory=list, description="角色代码列表")
    password: str = Field(..., description="初始密码")

    @field_validator("role_codes")
    @classmethod
    def _validate_roles(cls, value: list[str]) -> list[str]:
        return _validate_role_codes(value)


class UserPatch(BaseModel):
    """修改账号非凭证字段请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str | None = Field(default=None, description="用户名")
    display_name: str | None = Field(default=None, description="显示名称")
    phone_e164: str | None = Field(default=None, description="手机号(E.164)")

    @model_validator(mode="after")
    def _require_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("PATCH 请求必须提供至少一个要修改的字段")
        return self

    @property
    def phone_e164_is_set(self) -> bool:
        """phone_e164 是否在请求中被显式提供（包括设为 null）。"""
        return "phone_e164" in self.model_fields_set


class UserResponse(BaseModel):
    """用户响应。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    phone_e164: str | None = Field(None, description="手机号(E.164)")
    role_codes: list[str] = Field(default_factory=list, description="角色代码列表")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserPage(BaseModel):
    """用户分页响应。"""

    model_config = ConfigDict(extra="forbid")

    items: list[UserResponse] = Field(default_factory=list, description="账号列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total: int = Field(..., description="总记录数")


class ResetPasswordRequest(BaseModel):
    """重置密码请求。"""

    model_config = ConfigDict(extra="forbid")

    new_password: str = Field(..., description="新密码")


class UserRolesUpdateRequest(BaseModel):
    """设置账号角色请求。"""

    model_config = ConfigDict(extra="forbid")

    role_codes: list[str] = Field(..., description="角色代码列表")

    @field_validator("role_codes")
    @classmethod
    def _validate_roles(cls, value: list[str]) -> list[str]:
        return _validate_role_codes(value)
