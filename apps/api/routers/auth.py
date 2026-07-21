"""认证路由。"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from apps.api.dependencies import check_csrf, get_current_user, get_db
from apps.api.openapi_responses import (
    CSRF_HEADER_PARAM,
    FORBIDDEN,
    LOGIN_FAILED,
    TOO_MANY_REQUESTS,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    auth_cookies_response,
    clear_cookies_response,
    csrf_cookie_response,
)
from packages.backend.config import settings
from packages.backend.identity.client_ip import get_client_ip
from packages.backend.identity.csrf import generate_csrf_token
from packages.backend.identity.exceptions import (
    ChangePasswordFailedError,
    LoginFailedError,
    LoginRateLimitedError,
    UnauthenticatedError,
)
from packages.backend.identity.identifiers import normalize_username
from packages.backend.identity.login_throttle import (
    InMemoryThrottleBackend,
    LoginThrottle,
    RedisThrottleBackend,
)
from packages.backend.identity.service import IdentityService
from packages.contracts.identity import (
    ChangePasswordRequest,
    CsrfResponse,
    CurrentUser,
    LoginRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_throttle() -> LoginThrottle:
    if settings.environment == "test":
        return LoginThrottle(InMemoryThrottleBackend())
    if settings.redis_url:
        from redis.asyncio import Redis

        return LoginThrottle(RedisThrottleBackend(Redis.from_url(settings.redis_url)))
    return LoginThrottle(InMemoryThrottleBackend())


_throttle = _build_throttle()

# P1-3：可替换休眠器，用于账号退避阻塞；测试中替换为立即返回的替身以保持确定性。
_account_sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep

ACCESS_COOKIE_NAME = "child_manager_access"
REFRESH_COOKIE_NAME = "child_manager_refresh"
CSRF_COOKIE_NAME = "child_manager_csrf"


def _trusted_bff_peers() -> set[str]:
    """从配置读取可信 BFF peer 集合。

    Issue #6 M2 Final Fix：删除硬编码回环地址常量，改由 settings.trusted_bff_peers
    驱动。development/test 默认支持本地回环；production 必须显式配置。
    """
    return {peer.strip().lower() for peer in settings.trusted_bff_peers if peer.strip()}


def _set_csrf_cookie(response: Response, csrf_token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
        max_age=7 * 24 * 60 * 60,
    )


def _set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
) -> None:
    """设置 access + refresh 两条 Cookie。

    M2-F01：冻结契约 AuthSetCookies 要求恰好 2 条 Set-Cookie；
    CSRF Cookie 由独立的 /auth/csrf 端点签发，不在登录/刷新中重复设置。
    """
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    """清除 access + refresh 两条 Cookie。

    M2-F01：冻结契约 ClearAuthCookies 要求恰好 2 条 Set-Cookie；
    CSRF Cookie 不在退出中清除，由浏览器自然过期或由下次 /auth/csrf 覆盖。
    """
    for name in (ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME):
        response.set_cookie(
            key=name,
            value="",
            max_age=0,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            path="/",
        )


@router.get(
    "/csrf",
    response_model=CsrfResponse,
    responses={200: csrf_cookie_response("CSRF Cookie 已签发")},
    openapi_extra={"security": []},
)
async def csrf(response: Response) -> CsrfResponse:
    """签发签名双提交 CSRF Cookie。"""
    token = generate_csrf_token(settings.csrf_signing_key)
    _set_csrf_cookie(response, token)
    return CsrfResponse(csrf_token=token)


@router.post(
    "/login",
    response_model=CurrentUser,
    responses={
        200: auth_cookies_response("登录成功并设置 access/refresh Cookie"),
        401: LOGIN_FAILED,
        403: FORBIDDEN,
        422: VALIDATION_ERROR,
        429: TOO_MANY_REQUESTS,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM], "security": []},
)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    session: Annotated[Session, Depends(get_db)],
) -> CurrentUser:
    check_csrf(request)

    source_ip = get_client_ip(request, trusted_peers=_trusted_bff_peers())
    # 登录输入可能是用户名或手机号。normalize_username 在统一边界校验 NFKC 后
    # 非空与长度 <=120；输入不符合用户名格式（例如带 ``+`` 的 E.164
    # 手机号）时退化为原始输入的小写形式作为限流键，避免把有效登录请求变成 500。
    try:
        account_key = normalize_username(body.login)
    except ValueError:
        account_key = body.login.strip().lower() or body.login

    service = IdentityService(session)

    # P1-3：来源级硬频控（>= 30 次/15 分钟）返回 429 + Retry-After。
    if await _throttle.is_source_blocked(source_ip=source_ip):
        service.record_login_rate_limited(username=account_key, source_ip=source_ip)
        retry_after = await _throttle.source_retry_after_seconds()
        raise LoginRateLimitedError(retry_after=retry_after)

    # P1-3：账号级指数退避（>= 5 次/15 分钟）阻塞请求 1-60 秒，不返回 429。
    # 退避后继续认证流程，失败计数在认证失败时继续演进。
    backoff = await _throttle.account_backoff_seconds(account_key=account_key)
    if backoff > 0:
        await _account_sleeper(backoff)

    result = service.login(username=account_key, password=body.password, source_ip=source_ip)
    if result is None:
        await _throttle.record_failure(account_key=account_key, source_ip=source_ip)
        raise LoginFailedError()

    await _throttle.record_success(account_key=account_key, source_ip=source_ip)

    _set_auth_cookies(
        response,
        access_token=result.access_token,
        refresh_token=result.refresh_value,
    )
    return result.current_user


@router.post(
    "/refresh",
    response_model=CurrentUser,
    responses={
        200: auth_cookies_response("刷新成功并设置 access/refresh Cookie"),
        401: UNAUTHORIZED,
        403: FORBIDDEN,
    },
    openapi_extra={
        "parameters": [CSRF_HEADER_PARAM],
        "security": [{"refreshCookie": []}],
    },
)
async def refresh(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
) -> CurrentUser:
    check_csrf(request)

    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_cookie:
        raise UnauthenticatedError()

    service = IdentityService(session)
    result = service.refresh(refresh_cookie=refresh_cookie)
    if result is None:
        raise UnauthenticatedError()

    _set_auth_cookies(
        response,
        access_token=result.access_token,
        refresh_token=result.refresh_value,
    )
    return result.current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: clear_cookies_response("已退出并清除 access/refresh Cookie"),
        403: FORBIDDEN,
    },
    openapi_extra={
        "parameters": [CSRF_HEADER_PARAM],
        "security": [{"refreshCookie": []}],
    },
)
async def logout(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    check_csrf(request)

    access_cookie = request.cookies.get(ACCESS_COOKIE_NAME)
    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    source_ip = get_client_ip(request, trusted_peers=_trusted_bff_peers())
    service = IdentityService(session)
    service.logout(
        access_token=access_cookie,
        refresh_cookie=refresh_cookie,
        source_ip=source_ip,
    )

    # 安全注销：撤销当前会话 family（refresh 优先，否则通过 access token），并清除全部相关 Cookie。
    _clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get(
    "/me",
    response_model=CurrentUser,
    responses={401: UNAUTHORIZED},
)
async def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    """返回当前登录用户信息。"""
    return current_user


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: clear_cookies_response("密码已修改；全部会话已撤销；清除 access/refresh Cookie"),
        401: UNAUTHORIZED,
        403: FORBIDDEN,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def change_password(
    request: Request,
    response: Response,
    body: ChangePasswordRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    check_csrf(request)

    service = IdentityService(session)
    if not service.change_password(
        kindergarten_id=current_user.kindergarten_id,
        user_id=current_user.id,
        old_password=body.current_password,
        new_password=body.new_password,
    ):
        raise ChangePasswordFailedError()

    _clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
