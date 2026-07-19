"""同源 Cookie 认证、Refresh 轮换与 CSRF 端点。"""

import asyncio
import inspect
import os
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Request, Response

from apps.api.dependencies import CurrentSessionDependency, IdentityServiceDependency
from packages.backend.identity.client_ip import resolve_client_ip
from packages.backend.identity.csrf import issue_csrf_token, verify_csrf_token
from packages.backend.identity.login_throttle import ThrottleDecision
from packages.backend.identity.service import (
    AuthResult,
    IdentityError,
    IdentityService,
    SessionUser,
)
from packages.contracts.identity import (
    ChangePasswordRequest,
    CsrfResponse,
    CurrentUser,
    LoginRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

ACCESS_COOKIE = "child_manager_access"
REFRESH_COOKIE = "child_manager_refresh"
CSRF_COOKIE = "child_manager_csrf"


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _cookie_secure() -> bool:
    return os.environ.get("CHILD_MANAGER_COOKIE_SECURE", "true").lower() == "true"


def _allowed_origins(request: Request) -> set[str]:
    configured = os.environ.get("CHILD_MANAGER_ALLOWED_ORIGINS")
    if configured:
        return {value.strip().rstrip("/") for value in configured.split(",") if value.strip()}
    environment = os.environ.get("CHILD_MANAGER_ENV", "production")
    if environment not in {"development", "test"}:
        return set()
    web_port = os.environ.get("CHILD_MANAGER_WEB_PORT", "18080")
    return {
        "http://testserver",
        f"http://127.0.0.1:{web_port}",
        f"http://localhost:{web_port}",
    }


def require_csrf(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is None:
        referer = request.headers.get("referer")
        if referer:
            parsed = urlsplit(referer)
            origin = f"{parsed.scheme}://{parsed.netloc}"
    token = request.headers.get("x-csrf-token")
    cookie = request.cookies.get(CSRF_COOKIE)
    signing_key = os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY", "")
    valid = (
        origin is not None
        and origin.rstrip("/") in _allowed_origins(request)
        and token is not None
        and cookie is not None
        and token == cookie
        and bool(signing_key)
        and verify_csrf_token(token, signing_key)
    )
    if not valid:
        raise IdentityError(403, "auth.csrf_invalid", "请求来源或 CSRF 校验失败。")


def _set_auth_cookies(response: Response, result: AuthResult) -> None:
    common = {"secure": _cookie_secure(), "httponly": True, "samesite": "lax", "path": "/"}
    response.set_cookie(ACCESS_COOKIE, result.access_token, max_age=15 * 60, **common)
    response.set_cookie(REFRESH_COOKIE, result.refresh_token, max_age=7 * 24 * 60 * 60, **common)


def _clear_auth_cookies(response: Response) -> None:
    common = {"secure": _cookie_secure(), "httponly": True, "samesite": "lax", "path": "/"}
    response.delete_cookie(ACCESS_COOKIE, **common)
    response.delete_cookie(REFRESH_COOKIE, **common)


def _payload(service: IdentityService, session: SessionUser) -> dict[str, object]:
    return {
        "id": session.user.id,
        "username": session.user.username,
        "display_name": session.user.display_name,
        "kindergarten": service.kindergarten_summary(session.user.kindergarten_id),
        "role_codes": session.role_codes,
        "capabilities": session.capabilities,
    }


async def _throttle_failure(request: Request, *, account: str, source: str) -> ThrottleDecision:
    throttle = request.app.state.login_throttle
    if throttle is None:
        raise IdentityError(503, "configuration.unavailable", "登录服务暂不可用，请稍后重试。")
    decision = throttle.record_failure(
        account=account, source=source, now=request.app.state.clock()
    )
    if inspect.isawaitable(decision):
        decision = await decision
    if decision.delay_seconds:
        await asyncio.sleep(decision.delay_seconds)
    return decision


async def _throttle_check(request: Request, *, account: str, source: str) -> ThrottleDecision:
    throttle = request.app.state.login_throttle
    if throttle is None:
        raise IdentityError(503, "configuration.unavailable", "登录服务暂不可用，请稍后重试。")
    decision = throttle.check(account=account, source=source, now=request.app.state.clock())
    if inspect.isawaitable(decision):
        decision = await decision
    return decision


@router.get("/csrf", response_model=CsrfResponse)
def csrf(response: Response) -> dict[str, str]:
    signing_key = os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY")
    if not signing_key:
        raise IdentityError(503, "configuration.unavailable", "服务端安全配置不可用。")
    token = issue_csrf_token(signing_key)
    response.set_cookie(
        CSRF_COOKIE,
        token,
        max_age=7 * 24 * 60 * 60,
        secure=_cookie_secure(),
        httponly=False,
        samesite="lax",
        path="/",
    )
    return {"csrf_token": token}


@router.post("/login", response_model=CurrentUser)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    socket_peer = request.client.host if request.client else "127.0.0.1"
    source = resolve_client_ip(
        socket_peer=socket_peer,
        internal_client_ip=request.headers.get("x-child-manager-client-ip"),
        trusted_bff_peers=request.app.state.trusted_bff_peers,
    )
    account_key = service.safe_login_key(body.login)
    initial_decision = await _throttle_check(request, account=account_key, source=source)
    if initial_decision.source_limited:
        service.record_login_rate_limited(
            login=body.login,
            source=source,
            request_id=_request_id(request),
        )
        raise IdentityError(429, "auth.login_rate_limited", "登录尝试过多，请稍后重试。")
    try:
        result = service.login(
            login=body.login,
            password=body.password,
            request_id=_request_id(request),
            source=source,
        )
    except IdentityError as exc:
        if exc.code != "auth.login_failed":
            raise
        decision = await _throttle_failure(request, account=account_key, source=source)
        if decision.source_limited:
            service.record_login_rate_limited(
                login=body.login,
                source=source,
                request_id=_request_id(request),
            )
            raise IdentityError(
                429, "auth.login_rate_limited", "登录尝试过多，请稍后重试。"
            ) from None
        raise
    throttle = request.app.state.login_throttle
    assert throttle is not None
    completed = throttle.record_success(
        account=account_key, source=source, now=request.app.state.clock()
    )
    if inspect.isawaitable(completed):
        await completed
    _set_auth_cookies(response, result)
    return _payload(service, result.session)


@router.post("/refresh", response_model=CurrentUser)
def refresh(
    request: Request,
    response: Response,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    raw = request.cookies.get(REFRESH_COOKIE)
    if not raw:
        raise IdentityError(401, "auth.unauthenticated", "刷新会话已失效，请重新登录。")
    result = service.refresh(raw, request_id=_request_id(request))
    _set_auth_cookies(response, result)
    return _payload(service, result.session)


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    service: IdentityServiceDependency,
) -> None:
    require_csrf(request)
    service.logout(
        request.cookies.get(REFRESH_COOKIE),
        request_id=_request_id(request),
        raw_access_token=request.cookies.get(ACCESS_COOKIE),
    )
    _clear_auth_cookies(response)


@router.get("/me", response_model=CurrentUser)
def me(
    session: CurrentSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    return _payload(service, session)


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    request: Request,
    service: IdentityServiceDependency,
    session: CurrentSessionDependency,
) -> None:
    require_csrf(request)
    service.change_password(
        session,
        current_password=body.current_password,
        new_password=body.new_password,
        request_id=_request_id(request),
    )
