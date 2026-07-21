from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.dependencies import HealthDependencies, build_health_dependencies
from apps.api.middleware import request_context_middleware
from apps.api.routers import auth, users
from packages.backend.identity.csrf import CsrfError
from packages.backend.identity.exceptions import IdentityError
from packages.backend.observability import configure_logging
from packages.contracts.common import ErrorResponse, HealthResponse

configure_logging()


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    field_errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    from apps.api.middleware import request_id

    request_id_value = request_id(request)
    payload: dict[str, object] = {
        "code": code,
        "message": message,
        "request_id": request_id_value,
        "field_errors": field_errors or [],
    }
    response = JSONResponse(status_code=status_code, content=payload)
    response.headers["X-Request-ID"] = request_id_value
    return response


def _align_current_user(schemas: dict[str, object]) -> None:
    """对齐 CurrentUser：username 去除 anyOf/null，role_codes/capabilities 补 uniqueItems。"""
    current_user = schemas.get("CurrentUser")
    if not isinstance(current_user, dict):
        return
    props = current_user.get("properties", {})
    if not isinstance(props, dict):
        return
    username = props.get("username")
    if isinstance(username, dict):
        props["username"] = {
            "type": "string",
            "maxLength": 120,
            "description": "用户名",
        }
    role_codes = props.get("role_codes")
    if isinstance(role_codes, dict):
        role_codes["uniqueItems"] = True
        items = role_codes.get("items")
        if isinstance(items, dict):
            items["enum"] = ["admin", "teacher"]
    capabilities = props.get("capabilities")
    if isinstance(capabilities, dict):
        capabilities["uniqueItems"] = True


def _align_kindergarten_snapshot(schemas: dict[str, object]) -> None:
    """对齐 KindergartenSnapshot：timezone 必须 required + const Asia/Shanghai。"""
    kg = schemas.get("KindergartenSnapshot")
    if not isinstance(kg, dict):
        return
    props = kg.get("properties", {})
    if isinstance(props, dict) and "timezone" in props:
        props["timezone"] = {"type": "string", "const": "Asia/Shanghai"}
    required = kg.setdefault("required", [])
    if isinstance(required, list) and "timezone" not in required:
        required.append("timezone")


def _align_user_patch(schemas: dict[str, object]) -> None:
    """对齐 UserPatch：minProperties: 1，username/display_name 去除 anyOf/null。"""
    user_patch = schemas.get("UserPatch")
    if not isinstance(user_patch, dict):
        return
    user_patch["minProperties"] = 1
    props = user_patch.get("properties", {})
    if not isinstance(props, dict):
        return
    for field_name in ("username", "display_name"):
        field = props.get(field_name)
        if not isinstance(field, dict) or "anyOf" not in field:
            continue
        string_clause = next(
            (c for c in field["anyOf"] if isinstance(c, dict) and c.get("type") == "string"),
            None,
        )
        if string_clause is not None:
            props[field_name] = {
                "type": "string",
                "minLength": string_clause.get("minLength", 1),
                "maxLength": string_clause.get("maxLength", 120),
                "description": field.get("description", ""),
            }


def _align_password_fields(schemas: dict[str, object]) -> None:
    """对齐请求体密码字段：writeOnly + $ref Password（按冻结契约）。"""
    login_request = schemas.get("LoginRequest")
    if isinstance(login_request, dict):
        props = login_request.get("properties", {})
        if isinstance(props, dict) and isinstance(props.get("password"), dict):
            props["password"]["writeOnly"] = True

    change_password = schemas.get("ChangePasswordRequest")
    if isinstance(change_password, dict):
        props = change_password.get("properties", {})
        if isinstance(props, dict):
            current_pw = props.get("current_password")
            if isinstance(current_pw, dict):
                current_pw["writeOnly"] = True
            if "new_password" in props:
                props["new_password"] = {"$ref": "#/components/schemas/Password"}

    create_user = schemas.get("CreateUserRequest")
    if isinstance(create_user, dict):
        props = create_user.get("properties", {})
        if isinstance(props, dict) and "password" in props:
            props["password"] = {"$ref": "#/components/schemas/Password"}


def _align_runtime_schemas(schemas: dict[str, object]) -> None:
    """将 Pydantic 生成的运行时 schema 与冻结 OpenAPI 深层语义对齐。

    覆盖范围按 Codex M2 Final Contract Freeze `97251dc` P0/P1 清单：
    - CurrentUser.username：去掉 anyOf/null，改为 type: string
    - CurrentUser.role_codes：补 uniqueItems 与 items.enum
    - CurrentUser.capabilities：补 uniqueItems
    - KindergartenSnapshot.timezone：补 required 并改 const: Asia/Shanghai
    - UserPatch：补 minProperties: 1，username/display_name 改 type: string
    - LoginRequest.password：补 writeOnly: true
    - ChangePasswordRequest.current_password：补 writeOnly: true
    - ChangePasswordRequest.new_password：改 $ref Password
    - CreateUserRequest.password：改 $ref Password
    """
    _align_current_user(schemas)
    _align_kindergarten_snapshot(schemas)
    _align_user_patch(schemas)
    _align_password_fields(schemas)


def custom_openapi(application: FastAPI) -> dict[str, object]:
    if application.openapi_schema:
        return application.openapi_schema

    openapi_schema = get_openapi(
        title=application.title,
        version=application.version,
        routes=application.routes,
    )

    components = openapi_schema.setdefault("components", {})
    schemas: dict[str, object] = dict(components.setdefault("schemas", {}))

    # 从公共模型生成 schema，提取 $defs 合并到顶层
    error_schema = ErrorResponse.model_json_schema(ref_template="#/components/schemas/{model}")
    schemas.update(error_schema.pop("$defs", {}))
    schemas["Error"] = error_schema

    health_schema = HealthResponse.model_json_schema(ref_template="#/components/schemas/{model}")
    schemas.update(health_schema.pop("$defs", {}))
    schemas.setdefault("Health", health_schema)
    schemas["HealthResponse"] = health_schema

    unavailable_schema: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["code", "message", "request_id", "field_errors"],
        "properties": {
            "code": {
                "type": "string",
                "enum": [
                    "database.unavailable",
                    "configuration.unavailable",
                ],
            },
            "message": {"type": "string"},
            "request_id": {"type": "string", "format": "uuid"},
            "field_errors": {
                "type": "array",
                "maxItems": 0,
                "items": {"$ref": "#/components/schemas/ErrorField"},
            },
        },
    }
    schemas["UnavailableError"] = unavailable_schema

    # M2-F01：添加冻结契约中的 Uuid/Password 可复用组件，并将 User/CurrentUser.id
    # 替换为 $ref，使运行时 schema 与冻结 OpenAPI 严格对齐。
    schemas["Uuid"] = {"type": "string", "format": "uuid"}
    schemas["Password"] = {
        "type": "string",
        "minLength": 15,
        "maxLength": 128,
        "writeOnly": True,
        "description": "允许 Unicode、空格与粘贴；无字符组合规则；不得在日志或响应出现",
    }
    for schema_name in ("User", "CurrentUser"):
        schema_obj = schemas.get(schema_name)
        if isinstance(schema_obj, dict):
            props = schema_obj.get("properties", {})
            id_prop = props.get("id")
            if isinstance(id_prop, dict) and id_prop.get("type") == "string":
                props["id"] = {"$ref": "#/components/schemas/Uuid"}

    # M2-F01：补齐冻结契约深层语义（Codex M2 Final Contract Freeze P0/P1）。
    # Pydantic 默认 schema 与冻结 OpenAPI 在 nullable/enum/uniqueItems/writeOnly/
    # minProperties/const 等结构上仍有差异；此处统一覆写为冻结语义。
    _align_runtime_schemas(schemas)

    components["schemas"] = schemas
    # 安全方案与全局 security（与冻结契约 components/securitySchemes 对齐）。
    components["securitySchemes"] = {
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
    openapi_schema["security"] = [{"accessCookie": []}]

    # M2-F01：将 roles/reset-password 请求体替换为与冻结契约一致的 inline schema，
    # 并从 components/schemas 中移除对应的命名组件。
    paths = openapi_schema.get("paths", {})
    roles_op = paths.get("/api/v1/users/{user_id}/roles", {}).get("put", {})
    roles_body = roles_op.get("requestBody", {})
    if roles_body:
        roles_body["content"]["application/json"]["schema"] = {
            "type": "object",
            "additionalProperties": False,
            "required": ["role_codes"],
            "properties": {
                "role_codes": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "string", "enum": ["admin", "teacher"]},
                }
            },
        }
    reset_op = paths.get("/api/v1/users/{user_id}/reset-password", {}).get("post", {})
    reset_body = reset_op.get("requestBody", {})
    if reset_body:
        reset_body["content"]["application/json"]["schema"] = {
            "type": "object",
            "additionalProperties": False,
            "required": ["new_password"],
            "properties": {
                "new_password": {"$ref": "#/components/schemas/Password"},
            },
        }
    for stale in ("UserRolesUpdateRequest", "ResetPasswordRequest"):
        schemas.pop(stale, None)

    components["responses"] = {
        "ErrorResponse": {
            "description": "错误响应",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/Error"}},
            },
        },
        "HealthOk": {
            "description": "健康状态",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/Health"}},
            },
        },
        "Unavailable": {
            "description": "服务不可用",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/UnavailableError"}},
            },
        },
    }
    application.openapi_schema = openapi_schema
    return openapi_schema


async def _live_handler() -> dict[str, object]:
    return {
        "status": "ok",
        "checks": {},
    }


async def _ready_handler(request: Request, health: HealthDependencies) -> JSONResponse:
    from apps.api.dependencies import _safe_check

    database_ready = await _safe_check("database", health.database)
    if not database_ready:
        return _error_response(
            request,
            status_code=503,
            code="database.unavailable",
            message="数据库暂不可用,请稍后重试。",
        )
    if not health.security_ready:
        return _error_response(
            request,
            status_code=503,
            code="configuration.unavailable",
            message="服务端安全配置不可用。",
        )

    checks: dict[str, str] = {
        "database": "ok",
        "security": "ok",
    }
    for name, check in [
        ("redis", health.redis),
        ("ai", health.ai),
        ("calendar", health.calendar),
        ("template", health.template),
        ("export_storage", health.export_storage),
    ]:
        checks[name] = "ok" if await _safe_check(name, check) else "degraded"

    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return JSONResponse(content={"status": status, "checks": checks})


async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    field_errors: list[dict[str, str]] = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"] if part != "body")
        field_errors.append(
            {
                "field": field,
                "code": str(error["type"]),
                "message": "请求字段无效。",
            }
        )
    return _error_response(
        request,
        status_code=422,
        code="request.validation_failed",
        message="请求参数无效,请检查后重试。",
        field_errors=field_errors,
    )


async def _csrf_error_handler(request: Request, exc: CsrfError) -> JSONResponse:
    return _error_response(
        request,
        status_code=exc.status_code,
        code=exc.code,
        message=str(exc.detail),
    )


async def _identity_error_handler(request: Request, exc: IdentityError) -> JSONResponse:
    response = _error_response(
        request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
    )
    retry_after = getattr(exc, "retry_after", 0)
    if exc.status_code == 429 and retry_after > 0:
        response.headers["Retry-After"] = str(retry_after)
    return response


async def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        code = "resource.not_found"
        message = "请求的资源不存在。"
    elif exc.status_code == 405:
        code = "request.method_not_allowed"
        message = "请求方法不被允许。"
    else:
        code = "request.http_error"
        message = str(exc.detail) if exc.detail else "请求处理失败。"
    return _error_response(
        request,
        status_code=exc.status_code,
        code=code,
        message=message,
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    import structlog

    logger = structlog.get_logger(__name__)
    logger.error(
        "unhandled_exception",
        path=str(request.url.path),
        error_type=type(exc).__name__,
    )
    return _error_response(
        request,
        status_code=500,
        code="server.internal_error",
        message="服务器内部错误,请稍后重试。",
    )


def create_app(dependencies: HealthDependencies | None = None) -> FastAPI:
    health = dependencies or build_health_dependencies()
    application = FastAPI(title="Child Manager API")
    application.openapi = lambda: custom_openapi(application)

    application.middleware("http")(request_context_middleware)

    application.get(
        "/health/live",
        response_model=HealthResponse,
        responses={},
    )(_live_handler)

    async def ready_endpoint(request: Request) -> JSONResponse:
        return await _ready_handler(request, health)

    application.get(
        "/health/ready",
        response_model=HealthResponse,
        responses={
            503: {"model": None, "description": "服务不可用"},
        },
    )(ready_endpoint)

    application.exception_handler(RequestValidationError)(_validation_error_handler)
    application.exception_handler(CsrfError)(_csrf_error_handler)
    application.exception_handler(IdentityError)(_identity_error_handler)
    application.exception_handler(StarletteHTTPException)(_http_exception_handler)
    application.exception_handler(Exception)(_unhandled_error_handler)

    application.include_router(auth.router, prefix="/api/v1")
    application.include_router(users.router, prefix="/api/v1")

    return application
