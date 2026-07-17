"""认证路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from apps.api.dependencies import get_current_user, get_db
from packages.backend.config import settings
from packages.backend.identity.client_ip import get_client_ip
from packages.backend.identity.csrf import generate_csrf_token, validate_csrf_request
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
    LoginResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_TRUSTED_BFF_PEERS = {"127.0.0.1", "::1", "localhost"}


def _build_throttle() -> LoginThrottle:
    if settings.environment == "test":
        return LoginThrottle(InMemoryThrottleBackend())
    if settings.redis_url:
        from redis.asyncio import Redis

        return LoginThrottle(RedisThrottleBackend(Redis.from_url(settings.redis_url)))
    return LoginThrottle(InMemoryThrottleBackend())


_throttle = _build_throttle()

ACCESS_COOKIE_NAME = "child_manager_access"
REFRESH_COOKIE_NAME = "child_manager_refresh"
CSRF_COOKIE_NAME = "child_manager_csrf"


def _set_csrf_cookie(response: Response, csrf_token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",
        max_age=7 * 24 * 60 * 60,
    )


def _set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",
    )
    _set_csrf_cookie(response, csrf_token)


def _clear_auth_cookies(response: Response) -> None:
    for name in (ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME):
        response.set_cookie(
            key=name,
            value="",
            max_age=0,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            path="/",
        )
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value="",
        max_age=0,
        httponly=False,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",
    )


def _require_csrf(request: Request) -> None:
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    cookie = request.cookies.get(CSRF_COOKIE_NAME)
    header = request.headers.get("x-csrf-token")
    if not validate_csrf_request(
        cookie_value=cookie,
        header_value=header,
        origin=origin,
        referer=referer,
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF 校验失败")


def _build_current_user(
    service: IdentityService, user_id: str, kindergarten_id: str
) -> CurrentUser:
    user = service.get_user_by_id(kindergarten_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="会话已失效")
    return service.build_current_user(user)


@router.get("/csrf", response_model=CsrfResponse)
async def csrf(response: Response) -> CsrfResponse:
    """签发签名双提交 CSRF Cookie。"""
    token = generate_csrf_token(settings.csrf_signing_key)
    _set_csrf_cookie(response, token)
    return CsrfResponse(csrf_token=token)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    session: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    _require_csrf(request)

    source_ip = get_client_ip(request, trusted_peers=_TRUSTED_BFF_PEERS)
    account_key = normalize_username(body.username)

    if await _throttle.is_blocked(account_key=account_key, source_ip=source_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="登录尝试过于频繁"
        )

    service = IdentityService(session)
    result = service.login(username=account_key, password=body.password, source_ip=source_ip)
    if result is None:
        await _throttle.record_failure(account_key=account_key, source_ip=source_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    await _throttle.record_success(account_key=account_key, source_ip=source_ip)

    _set_auth_cookies(
        response,
        access_token=result["access_token"],
        refresh_token=result["refresh_value"],
        csrf_token=result["csrf_token"],
    )
    session.commit()
    return LoginResponse(
        user=_build_current_user(service, result["user"].id, result["kindergarten_id"])
    )


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="会话已失效")

    service = IdentityService(session)
    result = service.refresh(refresh_cookie=refresh_cookie)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="会话已失效")

    _set_auth_cookies(
        response,
        access_token=result["access_token"],
        refresh_token=result["refresh_value"],
        csrf_token=result["csrf_token"],
    )
    session.commit()
    return {"user": {"id": result["user_id"], "roles": result["roles"]}}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    _require_csrf(request)

    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    source_ip = get_client_ip(request, trusted_peers=_TRUSTED_BFF_PEERS)
    service = IdentityService(session)
    service.logout(refresh_cookie=refresh_cookie, source_ip=source_ip)
    if refresh_cookie:
        session.commit()

    _clear_auth_cookies(response)
    return {"message": "已退出登录"}


@router.get("/me", response_model=CurrentUser)
async def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    """返回当前登录用户信息。"""
    return current_user


@router.post("/change-password")
async def change_password(
    request: Request,
    response: Response,
    body: ChangePasswordRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    _require_csrf(request)

    service = IdentityService(session)
    if not service.change_password(
        user_id=current_user.id,
        old_password=body.old_password,
        new_password=body.new_password,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")

    session.commit()
    _clear_auth_cookies(response)
    return {"message": "密码已修改，请重新登录"}
