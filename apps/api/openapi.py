"""M2 运行时 OpenAPI 的集中契约装配。"""

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

OperationKey = tuple[str, str]

_SECURITY_SCHEMES = {
    "accessCookie": {
        "type": "apiKey",
        "in": "cookie",
        "name": "child_manager_access",
        "description": "15 分钟 HS256 JWT；Secure、HttpOnly、SameSite=Lax、Path=/",
    },
    "refreshCookie": {
        "type": "apiKey",
        "in": "cookie",
        "name": "child_manager_refresh",
        "description": "7 天绝对期限的随机 opaque token；只保存强哈希并每次轮换",
    },
}

_HEADERS = {
    "CsrfSetCookie": {
        "description": (
            "单独一条 child_manager_csrf Set-Cookie；Secure（回环开发例外）、SameSite=Lax、Path=/"
        ),
        "schema": {"type": "string"},
    },
    "AuthSetCookies": {
        "description": (
            "两条独立 Set-Cookie 字段，依次设置 child_manager_access 与 "
            "child_manager_refresh；raw HTTP/BFF 不得用逗号折叠"
        ),
        "schema": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {"type": "string"},
        },
    },
    "ClearAuthCookies": {
        "description": (
            "两条独立 Set-Cookie 字段，分别以 Max-Age=0/过期时间清除 access 与 "
            "refresh；raw HTTP/BFF 不得用逗号折叠"
        ),
        "schema": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {"type": "string"},
        },
    },
}

_PARAMETERS = {
    "CsrfHeader": {
        "in": "header",
        "name": "X-CSRF-Token",
        "required": True,
        "description": "必须与签名 child_manager_csrf Cookie 匹配；同时校验 Origin/Referer",
        "schema": {"type": "string", "minLength": 32, "maxLength": 512},
    }
}

_SCHEMAS = {
    "ErrorField": {
        "type": "object",
        "additionalProperties": False,
        "required": ["field", "code", "message"],
        "properties": {
            "field": {"type": "string"},
            "code": {"type": "string"},
            "message": {"type": "string"},
        },
    },
    "Error": {
        "type": "object",
        "additionalProperties": False,
        "required": ["code", "message", "request_id", "field_errors"],
        "properties": {
            "code": {"type": "string", "pattern": "^[a-z][a-z0-9_.-]+$"},
            "message": {"type": "string"},
            "request_id": {"type": "string", "format": "uuid"},
            "field_errors": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/ErrorField"},
            },
        },
    },
    "UnavailableError": {
        "type": "object",
        "additionalProperties": False,
        "required": ["code", "message", "request_id", "field_errors"],
        "properties": {
            "code": {
                "type": "string",
                "enum": ["database.unavailable", "configuration.unavailable"],
            },
            "message": {"type": "string"},
            "request_id": {"type": "string", "format": "uuid"},
            "field_errors": {
                "type": "array",
                "maxItems": 0,
                "items": {"$ref": "#/components/schemas/ErrorField"},
            },
        },
    },
    "Health": {
        "type": "object",
        "additionalProperties": False,
        "required": ["status", "checks"],
        "properties": {
            "status": {"type": "string", "enum": ["ok", "degraded", "unavailable"]},
            "checks": {
                "type": "object",
                "additionalProperties": {
                    "type": "string",
                    "enum": ["ok", "degraded", "unavailable", "not_required"],
                },
            },
        },
    },
    "UserPatch": {
        "type": "object",
        "additionalProperties": False,
        "minProperties": 1,
        "properties": {
            "username": {"type": "string", "minLength": 1, "maxLength": 120},
            "phone_e164": {"type": ["string", "null"], "maxLength": 32},
            "display_name": {"type": "string", "minLength": 1, "maxLength": 120},
        },
    },
}


def _response(description: str, schema_name: str) -> dict[str, object]:
    return {
        "description": description,
        "content": {
            "application/json": {
                "schema": {"$ref": f"#/components/schemas/{schema_name}"},
            }
        },
    }


_RESPONSES = {
    "HealthOk": _response("健康状态", "Health"),
    "UserOk": _response("脱敏账号", "User"),
    "UserCreated": _response("脱敏账号已创建", "User"),
    "UserPage": _response("分页账号", "UserPage"),
    "CurrentUserOk": _response("当前登录账号与实时权限", "CurrentUser"),
    "CurrentUserRefreshed": {
        **_response("轮换成功；旧 Refresh Token 已撤销", "CurrentUser"),
        "headers": {"Set-Cookie": {"$ref": "#/components/headers/AuthSetCookies"}},
    },
    "RegistrationOptionsOk": _response(
        "5 分钟单次 WebAuthn 注册 options；publicKey 可直接传给浏览器 API",
        "WebAuthnRegistrationOptions",
    ),
    "AuthenticationOptionsOk": _response(
        "5 分钟单次 WebAuthn 认证 options；publicKey 可直接传给浏览器 API",
        "WebAuthnAuthenticationOptions",
    ),
    "RegistrationPending": _response(
        "凭据登记完成，等待带外核验；未建立会话", "RegistrationPending"
    ),
    "Authenticated": {
        **_response(
            "通行密钥认证成功并设置 access/refresh Cookie；"
            "激活后首次成功认证只向用户返回一次恢复码",
            "AuthenticationResult",
        ),
        "headers": {"Set-Cookie": {"$ref": "#/components/headers/AuthSetCookies"}},
    },
    "StepUpOk": _response("当前会话的新近用户验证已更新", "StepUpResult"),
    "CredentialOk": _response("脱敏通行密钥凭据元数据", "Credential"),
    "CredentialCreated": _response("通行密钥凭据已登记", "Credential"),
    "CredentialListOk": _response(
        "当前目标账号的凭据元数据；不返回公钥、credential 原文或 assertion",
        "CredentialList",
    ),
    "InvitationIssued": _response(
        "邀请已签发；明文 token 仅在本响应展示一次，不返回含 token 的 URL",
        "InvitationIssued",
    ),
    "InvitationListOk": _response("邀请状态列表；不返回 token 或摘要", "InvitationList"),
    "AdminCredentialRevoked": _response(
        "凭据已撤销；若撤销教师最后凭据则同时撤销会话并返回一次性重新邀请",
        "AdminCredentialRevocationResult",
    ),
    "RecoveryRequestAccepted": _response(
        "统一恢复申请响应；不确认账号或恢复码是否存在",
        "RecoveryRequestAccepted",
    ),
    "RecoveryRequestListOk": _response(
        "待核验恢复申请列表；不返回恢复码或摘要",
        "RecoveryRequestList",
    ),
    "RecoveryEnrollmentIssued": _response(
        "人工核验完成并签发短时恢复登记 token；明文只展示一次",
        "RecoveryEnrollmentIssued",
    ),
    "RecoveryCompleted": _response(
        "恢复完成；新恢复码只展示一次且未建立会话",
        "RecoveryCompleted",
    ),
    "RecoveryCodeIssued": _response("新离线恢复码只展示一次", "RecoveryCodeIssued"),
    "SessionListOk": _response("本人有效会话列表", "SessionList"),
    "AuthenticationFailed": _response(
        "通用认证失败，不暴露凭据、账号、停用或签名失败原因",
        "Error",
    ),
    "Unauthorized": _response("未认证或会话无效", "Error"),
    "Forbidden": _response("CSRF/来源错误或无权限", "Error"),
    "NotFound": _response("资源不存在或不应向当前用户暴露", "Error"),
    "Conflict": _response("版本、幂等、预览有效性或业务不变量冲突", "Error"),
    "LastAdminRecoveryRequiresCli": _response(
        "目标是最后一名有效管理员，Web/API 不得审批；必须改走部署控制台双人核验。",
        "Error",
    ),
    "CeremonyUnavailable": _response(
        "Ceremony 已过期、已消费、跨用途或上下文不匹配",
        "Error",
    ),
    "InvitationUnavailable": _response("邀请过期、撤销或已消费，不细分状态", "Error"),
    "RecoveryUnavailable": _response("恢复材料或登记授权过期、撤销或已消费，不细分状态", "Error"),
    "ValidationError": _response("请求字段或业务前置条件无效", "Error"),
    "TooManyRequests": {
        **_response(
            "公开身份端点按可信来源、账号或授权材料摘要及端点全局三层独立限流",
            "Error",
        ),
        "headers": {
            "Retry-After": {
                "schema": {"type": "integer", "minimum": 1, "maximum": 60},
            }
        },
    },
    "Unavailable": _response(
        "PostgreSQL 或必要服务端本地配置/固定资源在请求受理前不可用",
        "UnavailableError",
    ),
}

_OPERATION_RESPONSES: dict[OperationKey, dict[str, str]] = {
    ("/health/live", "get"): {"200": "HealthOk"},
    ("/health/ready", "get"): {"200": "HealthOk", "503": "Unavailable"},
    ("/api/v1/auth/csrf", "get"): {"200": ""},
    ("/api/v1/auth/bootstrap/registration/options", "post"): {
        "200": "RegistrationOptionsOk",
        "403": "Forbidden",
        "410": "CeremonyUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/bootstrap/registration/verify", "post"): {
        "200": "RegistrationPending",
        "403": "Forbidden",
        "410": "CeremonyUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/invitation/registration/options", "post"): {
        "200": "RegistrationOptionsOk",
        "403": "Forbidden",
        "410": "InvitationUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/invitation/registration/verify", "post"): {
        "200": "RegistrationPending",
        "403": "Forbidden",
        "410": "CeremonyUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/authentication/options", "post"): {
        "200": "AuthenticationOptionsOk",
        "403": "Forbidden",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/authentication/verify", "post"): {
        "200": "Authenticated",
        "401": "AuthenticationFailed",
        "403": "Forbidden",
        "409": "Conflict",
        "410": "CeremonyUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/step-up/options", "post"): {
        "200": "AuthenticationOptionsOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/step-up/verify", "post"): {
        "200": "StepUpOk",
        "401": "AuthenticationFailed",
        "403": "Forbidden",
        "409": "Conflict",
        "410": "CeremonyUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/refresh", "post"): {
        "200": "CurrentUserRefreshed",
        "401": "Unauthorized",
        "403": "Forbidden",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/logout", "post"): {"204": "", "403": "Forbidden"},
    ("/api/v1/auth/me", "get"): {"200": "CurrentUserOk", "401": "Unauthorized"},
    ("/api/v1/auth/credentials", "get"): {
        "200": "CredentialListOk",
        "401": "Unauthorized",
    },
    ("/api/v1/auth/credentials/registration/options", "post"): {
        "200": "RegistrationOptionsOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/credentials/registration/verify", "post"): {
        "201": "CredentialCreated",
        "401": "Unauthorized",
        "403": "Forbidden",
        "409": "Conflict",
        "410": "CeremonyUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/credentials/{credential_id}", "patch"): {
        "200": "CredentialOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "422": "ValidationError",
    },
    ("/api/v1/auth/credentials/{credential_id}", "delete"): {
        "204": "",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "Conflict",
    },
    ("/api/v1/auth/recovery/requests", "post"): {
        "202": "RecoveryRequestAccepted",
        "403": "Forbidden",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/recovery/registration/options", "post"): {
        "200": "RegistrationOptionsOk",
        "403": "Forbidden",
        "410": "RecoveryUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/recovery/registration/verify", "post"): {
        "200": "RecoveryCompleted",
        "403": "Forbidden",
        "410": "RecoveryUnavailable",
        "422": "ValidationError",
        "429": "TooManyRequests",
    },
    ("/api/v1/auth/recovery-code/rotate", "post"): {
        "200": "RecoveryCodeIssued",
        "401": "Unauthorized",
        "403": "Forbidden",
    },
    ("/api/v1/auth/sessions", "get"): {
        "200": "SessionListOk",
        "401": "Unauthorized",
    },
    ("/api/v1/auth/sessions/{session_id}", "delete"): {
        "204": "",
        "401": "Unauthorized",
        "404": "NotFound",
    },
    ("/api/v1/users", "get"): {
        "200": "UserPage",
        "401": "Unauthorized",
        "403": "Forbidden",
        "422": "ValidationError",
    },
    ("/api/v1/users", "post"): {
        "201": "UserCreated",
        "401": "Unauthorized",
        "403": "Forbidden",
        "409": "Conflict",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}", "get"): {
        "200": "UserOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}", "patch"): {
        "200": "UserOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}/roles", "put"): {
        "200": "UserOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "Conflict",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}/activate", "post"): {
        "200": "UserOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "Conflict",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}/deactivate", "post"): {
        "200": "UserOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "Conflict",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}/invitations", "get"): {
        "200": "InvitationListOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
    },
    ("/api/v1/users/{user_id}/invitations", "post"): {
        "201": "InvitationIssued",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "Conflict",
        "422": "ValidationError",
    },
    ("/api/v1/users/{user_id}/invitations/{invitation_id}/revoke", "post"): {
        "204": "",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
    },
    ("/api/v1/users/{user_id}/credentials", "get"): {
        "200": "CredentialListOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
    },
    ("/api/v1/users/{user_id}/credentials/{credential_id}", "delete"): {
        "200": "AdminCredentialRevoked",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "Conflict",
    },
    ("/api/v1/users/{user_id}/sessions/revoke", "post"): {
        "204": "",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
    },
    ("/api/v1/users/{user_id}/recovery-requests", "get"): {
        "200": "RecoveryRequestListOk",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
    },
    (
        "/api/v1/users/{user_id}/recovery-requests/{recovery_request_id}/approve",
        "post",
    ): {
        "200": "RecoveryEnrollmentIssued",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "NotFound",
        "409": "LastAdminRecoveryRequiresCli",
        "422": "ValidationError",
    },
}

_CSRF_OPERATIONS = {
    key
    for key in _OPERATION_RESPONSES
    if key[1] in {"post", "put", "patch", "delete"} and key[0] not in {"/health/live"}
}
_CSRF_OPERATIONS.discard(("/health/ready", "get"))

_PUBLIC_OPERATIONS = {
    ("/health/live", "get"),
    ("/health/ready", "get"),
    ("/api/v1/auth/csrf", "get"),
    ("/api/v1/auth/bootstrap/registration/options", "post"),
    ("/api/v1/auth/bootstrap/registration/verify", "post"),
    ("/api/v1/auth/invitation/registration/options", "post"),
    ("/api/v1/auth/invitation/registration/verify", "post"),
    ("/api/v1/auth/authentication/options", "post"),
    ("/api/v1/auth/authentication/verify", "post"),
    ("/api/v1/auth/recovery/requests", "post"),
    ("/api/v1/auth/recovery/registration/options", "post"),
    ("/api/v1/auth/recovery/registration/verify", "post"),
}


def _operation(document: dict[str, Any], key: OperationKey) -> dict[str, Any]:
    path, method = key
    return document["paths"][path][method]


def _no_content_response() -> dict[str, str]:
    return {"description": "操作成功，无响应正文"}


def _apply_operation_contract(document: dict[str, Any], key: OperationKey) -> None:
    operation = _operation(document, key)
    operation["responses"] = {
        status: (
            {"$ref": f"#/components/responses/{component}"} if component else _no_content_response()
        )
        for status, component in _OPERATION_RESPONSES[key].items()
    }
    parameters = [
        parameter
        for parameter in operation.get("parameters", [])
        if str(parameter.get("name", "")).lower()
        not in {"child_manager_access", "child_manager_refresh"}
    ]
    if key in _CSRF_OPERATIONS:
        parameters.append({"$ref": "#/components/parameters/CsrfHeader"})
    if parameters:
        operation["parameters"] = parameters
    else:
        operation.pop("parameters", None)
    if key in _PUBLIC_OPERATIONS:
        operation["security"] = []
    elif key in {
        ("/api/v1/auth/refresh", "post"),
    }:
        operation["security"] = [{"refreshCookie": []}]
    elif key == ("/api/v1/auth/logout", "post"):
        operation["security"] = [{"refreshCookie": []}, {}]
    else:
        operation.pop("security", None)


def configure_openapi(application: FastAPI) -> Callable[[], dict[str, Any]]:
    """返回缓存后的 M2 运行时 OpenAPI 生成器。"""

    def custom_openapi() -> dict[str, Any]:
        if application.openapi_schema is not None:
            return application.openapi_schema
        document = get_openapi(
            title=application.title,
            version=application.version,
            routes=application.routes,
        )
        document["openapi"] = "3.1.0"
        document["security"] = [{"accessCookie": []}]
        components = document.setdefault("components", {})
        components.setdefault("securitySchemes", {}).update(_SECURITY_SCHEMES)
        components.setdefault("headers", {}).update(_HEADERS)
        components.setdefault("parameters", {}).update(_PARAMETERS)
        schemas = components.setdefault("schemas", {})
        schemas.update(_SCHEMAS)
        schemas["RegistrationPublicKey"]["properties"]["extensions"] = {
            "$ref": "#/components/schemas/RegistrationExtensions"
        }
        components.setdefault("responses", {}).update(_RESPONSES)
        for key in _OPERATION_RESPONSES:
            _apply_operation_contract(document, key)

        csrf_operation = _operation(document, ("/api/v1/auth/csrf", "get"))
        csrf_operation["responses"] = {
            "200": {
                "description": "签发双提交 CSRF Cookie",
                "headers": {
                    "Set-Cookie": {"$ref": "#/components/headers/CsrfSetCookie"},
                },
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/CsrfResponse"},
                    }
                },
            }
        }
        logout_operation = _operation(document, ("/api/v1/auth/logout", "post"))
        logout_operation["responses"] = {
            "204": {
                **_no_content_response(),
                "headers": {
                    "Set-Cookie": {"$ref": "#/components/headers/ClearAuthCookies"},
                },
            },
            "403": {"$ref": "#/components/responses/Forbidden"},
        }
        session_revoke = _operation(document, ("/api/v1/auth/sessions/{session_id}", "delete"))
        session_revoke["responses"]["204"]["headers"] = {
            "Set-Cookie": {"$ref": "#/components/headers/ClearAuthCookies"},
        }
        application.openapi_schema = document
        return document

    return custom_openapi
