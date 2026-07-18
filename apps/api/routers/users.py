"""用户管理路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from apps.api.dependencies import check_csrf, get_db, require_admin
from packages.backend.identity.exceptions import UserNotFoundError
from packages.backend.identity.service import IdentityService
from packages.contracts.identity import (
    CurrentUser,
    ResetPasswordRequest,
    UserCreateRequest,
    UserPage,
    UserPatch,
    UserResponse,
    UserRolesUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    body: UserCreateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    check_csrf(request)

    service = IdentityService(session)
    return service.create_user(
        kindergarten_id=current_user.kindergarten_id, creator=current_user, request=body
    )


@router.get("", response_model=UserPage)
async def list_users(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserPage:
    service = IdentityService(session)
    items, total = service.list_users(current_user.kindergarten_id, page=page, page_size=page_size)
    return UserPage(items=items, page=page, page_size=page_size, total=total)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    service = IdentityService(session)
    user = service.get_user(current_user.kindergarten_id, user_id)
    if user is None:
        raise UserNotFoundError()
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: str,
    body: UserPatch,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    check_csrf(request)

    service = IdentityService(session)
    user = service.update_user(
        kindergarten_id=current_user.kindergarten_id,
        admin_user_id=current_user.id,
        user_id=user_id,
        patch=body,
    )
    if user is None:
        raise UserNotFoundError()
    return user


@router.put("/{user_id}/roles", response_model=UserResponse)
async def set_user_roles(
    request: Request,
    user_id: str,
    body: UserRolesUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    check_csrf(request)

    service = IdentityService(session)
    user = service.set_user_roles(
        kindergarten_id=current_user.kindergarten_id,
        admin_user_id=current_user.id,
        user_id=user_id,
        role_codes=body.role_codes,
    )
    if user is None:
        raise UserNotFoundError()
    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    request: Request,
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    check_csrf(request)

    service = IdentityService(session)
    user = service.activate_user(
        kindergarten_id=current_user.kindergarten_id,
        admin_user_id=current_user.id,
        user_id=user_id,
    )
    if user is None:
        raise UserNotFoundError()
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    request: Request,
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    check_csrf(request)

    service = IdentityService(session)
    return service.deactivate_user(
        kindergarten_id=current_user.kindergarten_id,
        admin_user_id=current_user.id,
        user_id=user_id,
    )


@router.post("/{user_id}/reset-password")
async def reset_password(
    request: Request,
    response: Response,
    user_id: str,
    body: ResetPasswordRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    check_csrf(request)

    service = IdentityService(session)
    if not service.reset_password(
        kindergarten_id=current_user.kindergarten_id,
        admin_user_id=current_user.id,
        target_user_id=user_id,
        new_password=body.new_password,
    ):
        raise UserNotFoundError()

    response.status_code = status.HTTP_204_NO_CONTENT
    return response
