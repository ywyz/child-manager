"""身份与认证公共 Schema 骨架。"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from packages.contracts.common import ContractModel

Password = Annotated[str, Field(min_length=15, max_length=128)]
RoleCode = Annotated[str, Field(pattern="^(admin|teacher)$")]
LoginIdentifier = Annotated[str, Field(min_length=1, max_length=120)]
Credential = Annotated[str, Field(min_length=1, max_length=128)]
UserText = Annotated[str, Field(min_length=1, max_length=120)]


def _unique_role_codes(value: list[str]) -> list[str]:
    if len(value) != len(set(value)):
        raise ValueError("角色不能重复")
    return value


def _unique_strings(value: list[str]) -> list[str]:
    if len(value) != len(set(value)):
        raise ValueError("列表项不能重复")
    return value


class LoginRequest(ContractModel):
    login: LoginIdentifier
    password: Credential


class ChangePasswordRequest(ContractModel):
    current_password: Credential
    new_password: Password


class CsrfResponse(ContractModel):
    csrf_token: Annotated[str, Field(min_length=32, max_length=512)]


class KindergartenSummary(ContractModel):
    id: UUID
    name: str
    timezone: Literal["Asia/Shanghai"]


class CurrentUser(ContractModel):
    id: UUID
    username: str
    display_name: str
    kindergarten: KindergartenSummary
    role_codes: list[RoleCode]
    capabilities: list[str]

    _roles_are_unique = field_validator("role_codes")(_unique_role_codes)
    _capabilities_are_unique = field_validator("capabilities")(_unique_strings)


class CreateUserRequest(ContractModel):
    username: UserText
    phone_e164: str | None = None
    display_name: UserText
    password: Password
    role_codes: Annotated[list[RoleCode], Field(min_length=1)]

    _roles_are_unique = field_validator("role_codes")(_unique_role_codes)


class UserPatch(ContractModel):
    username: UserText | None = None
    phone_e164: str | None = None
    display_name: UserText | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> UserPatch:
        if not self.model_fields_set:
            raise ValueError("至少提供一个待修改字段")
        return self


class RoleUpdate(ContractModel):
    role_codes: Annotated[list[RoleCode], Field(min_length=1)]

    _roles_are_unique = field_validator("role_codes")(_unique_role_codes)


class PasswordResetRequest(ContractModel):
    new_password: Password


class UserResponse(ContractModel):
    id: UUID
    username: str
    phone_e164: str | None
    display_name: str
    role_codes: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserPage(ContractModel):
    items: list[UserResponse]
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total: Annotated[int, Field(ge=0)]
