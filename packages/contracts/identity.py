"""身份与认证公共 Schema。"""

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_UUID_RE = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class KindergartenSnapshot(BaseModel):
    """当前登录用户所属园所快照。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., pattern=_UUID_RE, description="园所ID")
    name: str = Field(..., min_length=1, max_length=200, description="园所名称")
    timezone: str = Field(
        default="Asia/Shanghai",
        max_length=64,
        description="园所时区",
    )

    @field_validator("timezone")
    @classmethod
    def _timezone_fixed(cls, value: str) -> str:
        if value != "Asia/Shanghai":
            raise ValueError("时区必须为 Asia/Shanghai")
        return value


class CurrentUser(BaseModel):
    """当前登录用户。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., pattern=_UUID_RE, description="用户ID")
    username: str = Field(..., min_length=1, max_length=120, description="用户名")
    display_name: str = Field(..., min_length=1, max_length=120, description="显示名称")
    kindergarten: KindergartenSnapshot = Field(..., description="所属园所快照")
    role_codes: list[str] = Field(default_factory=list, description="角色代码列表")
    capabilities: list[str] = Field(default_factory=list, description="能力标签列表")

    @field_validator("role_codes")
    @classmethod
    def _validate_role_codes(cls, value: list[str]) -> list[str]:
        return _validate_response_role_codes(value)

    @field_validator("capabilities")
    @classmethod
    def _validate_capabilities(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("能力标签不能重复")
        return value

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

    csrf_token: str = Field(..., min_length=32, max_length=512, description="CSRF 令牌")


class LoginRequest(BaseModel):
    """登录请求。"""

    model_config = ConfigDict(extra="forbid")

    login: str = Field(..., min_length=1, max_length=120, description="用户名或手机号")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求。"""

    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(..., min_length=1, max_length=128, description="原密码")
    new_password: str = Field(..., min_length=15, max_length=128, description="新密码")


RoleCode = Literal["admin", "teacher"]
_ALLOWED_ROLE_CODES = set(RoleCode.__args__)  # type: ignore[attr-defined]


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


def _validate_response_role_codes(value: list[str]) -> list[str]:
    """校验响应角色列表：唯一、仅允许 admin/teacher（允许空）。"""
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

    username: str = Field(..., min_length=1, max_length=120, description="用户名")
    display_name: str = Field(..., min_length=1, max_length=120, description="显示名称")
    phone_e164: str | None = Field(None, max_length=32, description="手机号(E.164)")
    role_codes: list[RoleCode] = Field(
        ...,
        min_length=1,
        description="角色代码列表",
        json_schema_extra={"uniqueItems": True},
    )
    password: str = Field(..., min_length=15, max_length=128, description="初始密码")

    @field_validator("role_codes")
    @classmethod
    def _validate_roles(cls, value: list[str]) -> list[str]:
        return _validate_role_codes(value)


class UserPatch(BaseModel):
    """修改账号非凭证字段请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str | None = Field(default=None, min_length=1, max_length=120, description="用户名")
    display_name: str | None = Field(
        default=None, min_length=1, max_length=120, description="显示名称"
    )
    phone_e164: str | None = Field(default=None, max_length=32, description="手机号(E.164)")

    @field_validator("username", "display_name")
    @classmethod
    def _reject_null_strings(cls, value: str | None) -> str | None:
        """username/display_name 只能作为有效字符串提交，不允许显式设为 null。"""
        if value is None:
            raise ValueError("字段不能为 null")
        return value

    @model_validator(mode="after")
    def _require_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("PATCH 请求必须提供至少一个要修改的字段")
        return self

    @property
    def phone_e164_is_set(self) -> bool:
        """phone_e164 是否在请求中被显式提供（包括设为 null）。"""
        return "phone_e164" in self.model_fields_set


class User(BaseModel):
    """用户响应。

    Schema 名称与字段约束按冻结 OpenAPI 契约 `#/components/schemas/User` 收敛：
    id 为 UUID 格式、role_codes 唯一且枚举 admin/teacher、items 必填。
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., json_schema_extra={"format": "uuid"}, description="用户ID")
    username: str = Field(..., min_length=1, max_length=120, description="用户名")
    display_name: str = Field(..., min_length=1, max_length=120, description="显示名称")
    phone_e164: str | None = Field(default=None, max_length=32, description="手机号(E.164)")
    role_codes: list[RoleCode] = Field(
        ...,
        json_schema_extra={"uniqueItems": True},
        description="角色代码列表",
    )
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    @field_validator("role_codes")
    @classmethod
    def _validate_role_codes(cls, value: list[str]) -> list[str]:
        return _validate_response_role_codes(value)


class UserPage(BaseModel):
    """用户分页响应。"""

    model_config = ConfigDict(extra="forbid")

    items: list[User] = Field(..., description="账号列表")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=100, description="每页大小")
    total: int = Field(..., ge=0, description="总记录数")


class ResetPasswordRequest(BaseModel):
    """重置密码请求。"""

    model_config = ConfigDict(extra="forbid")

    new_password: str = Field(..., min_length=15, max_length=128, description="新密码")


class UserRolesUpdateRequest(BaseModel):
    """设置账号角色请求。"""

    model_config = ConfigDict(extra="forbid")

    role_codes: list[RoleCode] = Field(
        ...,
        min_length=1,
        description="角色代码列表",
        json_schema_extra={"uniqueItems": True},
    )

    @field_validator("role_codes")
    @classmethod
    def _validate_roles(cls, value: list[str]) -> list[str]:
        return _validate_role_codes(value)
