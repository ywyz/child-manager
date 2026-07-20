"""可复用的 OpenAPI 响应与参数声明。

按冻结 OpenAPI 契约 `specs/001-daily-activity-plan/contracts/openapi.yaml` 收敛
Auth/Users 运行时文档：统一 Error body、Set-Cookie/Retry-After headers、
CSRF header 参数与 cookie 安全方案。路由声明引用此处常量，避免散落重复。
"""

from typing import Any

# 统一错误 body：所有 4xx/5xx 稳定状态码指向 #/components/schemas/Error。
_ERROR_BODY: dict[str, Any] = {
    "application/json": {"schema": {"$ref": "#/components/schemas/Error"}},
}


def _error_response(description: str, *, headers: dict[str, Any] | None = None) -> dict[str, Any]:
    resp: dict[str, Any] = {"description": description, "content": _ERROR_BODY}
    if headers:
        resp["headers"] = headers
    return resp


# 稳定错误响应（与 components/responses/* 对齐）。
UNAUTHORIZED = _error_response("未认证或会话无效")
LOGIN_FAILED = _error_response("通用登录失败,不暴露账号是否存在或停用")
FORBIDDEN = _error_response("CSRF/来源错误或无权限")
NOT_FOUND = _error_response("资源不存在或不应向当前用户暴露")
CONFLICT = _error_response("版本、幂等、预览有效性或业务不变量冲突")
VALIDATION_ERROR = _error_response("请求字段或业务前置条件无效")

# 429 限流：额外声明 Retry-After header（1-60 秒整数）。
TOO_MANY_REQUESTS = _error_response(
    "登录来源限流",
    headers={
        "Retry-After": {
            "schema": {"type": "integer", "minimum": 1, "maximum": 60},
            "description": "建议重试等待秒数",
        }
    },
)

# Set-Cookie header schema（数组形式，避免逗号折叠）。
_AUTH_SET_COOKIE_SCHEMA = {
    "type": "array",
    "minItems": 2,
    "maxItems": 2,
    "items": {"type": "string"},
}
_CLEAR_SET_COOKIE_SCHEMA = {
    "type": "array",
    "minItems": 2,
    "maxItems": 2,
    "items": {"type": "string"},
}
_CSRF_SET_COOKIE_SCHEMA = {
    "type": "string",
}


def auth_cookies_response(description: str) -> dict[str, Any]:
    """成功设置 access+refresh Cookie 的响应（2 条独立 Set-Cookie）。"""
    return {
        "description": description,
        "headers": {"Set-Cookie": {"schema": _AUTH_SET_COOKIE_SCHEMA}},
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CurrentUser"}}},
    }


def csrf_cookie_response(description: str) -> dict[str, Any]:
    """签发 CSRF Cookie 的响应。"""
    return {
        "description": description,
        "headers": {"Set-Cookie": {"schema": _CSRF_SET_COOKIE_SCHEMA}},
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CsrfResponse"}}},
    }


def clear_cookies_response(description: str) -> dict[str, Any]:
    """清除 access+refresh Cookie 的响应（2 条独立 Set-Cookie）。"""
    return {
        "description": description,
        "headers": {"Set-Cookie": {"schema": _CLEAR_SET_COOKIE_SCHEMA}},
    }


# CSRF header 参数声明（与 components/parameters/CsrfHeader 对齐）。
CSRF_HEADER_PARAM: dict[str, Any] = {
    "in": "header",
    "name": "X-CSRF-Token",
    "required": True,
    "description": "必须与签名 child_manager_csrf Cookie 匹配;同时校验 Origin/Referer",
    "schema": {"type": "string", "minLength": 32, "maxLength": 512},
}
