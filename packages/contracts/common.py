from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="中文错误消息")
    detail: str | None = Field(None, description="技术细节")
    request_id: str | None = Field(None, description="请求ID")


class FieldError(BaseModel):
    field: str = Field(..., description="字段名")
    message: str = Field(..., description="字段错误消息")


class PaginatedResponse[T](BaseModel):
    items: list[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class IdempotencyKey(BaseModel):
    key: str = Field(..., description="幂等键")
    scope: str = Field(..., description="作用域")


class RequestContext(BaseModel):
    request_id: str = Field(..., description="请求ID")
    trace_id: str | None = Field(None, description="追踪ID")
    kindergarten_id: str | None = Field(None, description="园所ID")
    user_id: str | None = Field(None, description="用户ID")


class HealthCheckResult(BaseModel):
    name: str = Field(..., description="检查项名称")
    status: str = Field(..., description="状态: healthy/degraded/unhealthy")
    message: str | None = Field(None, description="消息")


class HealthResponse(BaseModel):
    status: str = Field(..., description="整体状态")
    checks: list[HealthCheckResult] = Field(..., description="检查项列表")
    timestamp: str = Field(..., description="时间戳")
