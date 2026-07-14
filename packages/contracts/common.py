"""跨服务使用的公共 Schema 与规范化函数。"""

import json
from collections.abc import Mapping, Sequence
from hashlib import sha256
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

RequestId = Annotated[str, Field(min_length=1, max_length=128)]
IdempotencyKey = Annotated[str, Field(min_length=1, max_length=200)]
ResourceId = UUID


class ContractModel(BaseModel):
    """共享契约的统一 Pydantic 基类。"""

    model_config = {"extra": "forbid"}


class ResourceReference(ContractModel):
    """审计与任务契约使用的最小资源引用。"""

    resource_type: str
    resource_id: ResourceId


class FieldError(ContractModel):
    field: str
    code: str
    message: str


class ErrorResponse(ContractModel):
    code: str
    message: str
    request_id: UUID
    field_errors: list[FieldError] = []


class Pagination(ContractModel):
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 20


class Page(ContractModel):
    """可增长列表的中性分页骨架。"""

    items: list[str] = []
    page: int = 1
    page_size: int = 20
    total: int = 0


DATABASE_UNAVAILABLE = "database.unavailable"
CONFIGURATION_UNAVAILABLE = "configuration.unavailable"


def _normalize_scalar(value: object) -> object:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, str):
        try:
            return str(UUID(value))
        except ValueError:
            return value
    return value


def canonical_request_fingerprint(
    *,
    method: str,
    route_template: str,
    path_params: Mapping[str, object],
    query_params: Sequence[tuple[str, str]],
    body: object,
) -> str:
    """计算覆盖路由、实际资源与语义输入的 canonical SHA-256。"""

    canonical_payload = {
        "method": method.upper(),
        "route_template": route_template,
        "path_params": {
            key: _normalize_scalar(value) for key, value in sorted(path_params.items())
        },
        "query_params": sorted((key, value) for key, value in query_params),
        "body": body,
    }
    serialized = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return sha256(serialized).hexdigest()
