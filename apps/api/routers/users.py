"""用户管理路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db, require_admin
from packages.backend.identity.csrf import validate_csrf_request
from packages.backend.identity.service import IdentityService
from packages.contracts.identity import (
    CurrentUser,
    ResetPasswordRequest,
    UserCreateRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])
CSRF_COOKIE_NAME = "child_manager_csrf"


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


@router.post("", response_model=UserResponse)
async def create_user(
    request: Request,
    body: UserCreateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    _require_csrf(request)

    service = IdentityService(session)
    user = service.create_user(creator=current_user, request=body)
    session.commit()
    return UserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        phone=user.phone,
        roles=service._repo.list_user_roles(user.kindergarten_id, user.id),
        is_active=user.is_active,
    )


@router.get("")
async def list_users(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> list[UserResponse]:
    return IdentityService(session).list_users()


@router.post("/{user_id}/reset-password")
async def reset_password(
    request: Request,
    user_id: str,
    body: ResetPasswordRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    _require_csrf(request)

    service = IdentityService(session)
    if not service.reset_password(
        admin_user_id=current_user.id,
        target_user_id=user_id,
        new_password=body.new_password,
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    session.commit()
    return {"message": "密码已重置"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    request: Request,
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    _require_csrf(request)

    service = IdentityService(session)
    service.deactivate_user(admin_user_id=current_user.id, user_id=user_id)
    session.commit()
    return {"message": "账号已停用"}
