import hashlib
import json
from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class FieldError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(..., description="字段路径")
    code: str = Field(..., description="稳定机器码")
    message: str = Field(..., description="字段错误消息")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        ...,
        description="稳定英文机器码",
        pattern=r"^[a-z][a-z0-9_.-]+$",
    )
    message: str = Field(..., description="中文错误消息")
    request_id: UUID = Field(..., description="请求 ID (UUID)")
    field_errors: list[FieldError] = Field(..., description="字段级错误")


class PaginatedResponse[T](BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[T] = Field(..., description="数据列表")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=100, description="每页大小")
    total: int = Field(..., ge=0, description="总记录数")


class IdempotencyKey(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="幂等键")
    scope: str = Field(..., description="作用域")


class RequestContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID = Field(..., description="请求ID")
    trace_id: UUID | None = Field(None, description="追踪ID")
    kindergarten_id: UUID | None = Field(None, description="园所ID")
    user_id: UUID | None = Field(None, description="用户ID")


class HealthCheckResult(BaseModel):
    name: str = Field(..., description="检查项名称")
    status: str = Field(..., description="状态: healthy/degraded/unhealthy")
    message: str | None = Field(None, description="消息")


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="整体状态")
    checks: dict[str, str] = Field(..., description="检查项列表")


def canonical_fingerprint(
    *,
    path: str,
    method: str,
    query_params: dict[str, Any] | None = None,
    body: Any = None,
    scope: str | None = None,
) -> str:
    components = {
        "method": method.upper(),
        "path": path,
        "scope": scope or "",
    }

    if query_params:
        components["query"] = json.dumps(
            dict(sorted(query_params.items())),
            sort_keys=True,
            separators=(",", ":"),
        )

    if body is not None:
        if isinstance(body, (dict, list)):
            components["body"] = json.dumps(body, sort_keys=True, separators=(",", ":"))
        else:
            components["body"] = str(body)

    fingerprint_input = json.dumps(components, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(fingerprint_input.encode("utf-8")).hexdigest()


def idempotency_key_from_fingerprint(fingerprint: str, scope: str) -> IdempotencyKey:
    return IdempotencyKey(key=fingerprint, scope=scope)
