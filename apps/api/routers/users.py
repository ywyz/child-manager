"""用户管理路由。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from apps.api.dependencies import check_csrf, get_db, require_admin
from apps.api.openapi_responses import (
    CONFLICT,
    CSRF_HEADER_PARAM,
    FORBIDDEN,
    NOT_FOUND,
    VALIDATION_ERROR,
)
from packages.backend.identity.exceptions import UserNotFoundError
from packages.backend.identity.service import IdentityService
from packages.contracts.identity import (
    CurrentUser,
    ResetPasswordRequest,
    User,
    UserCreateRequest,
    UserPage,
    UserPatch,
    UserRolesUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["users"])

# 成功响应 body（指向统一 User schema）。
_USER_OK = {
    "description": "脱敏账号",
    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
}
_USER_CREATED = {
    "description": "脱敏账号已创建",
    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
}
_USER_PAGE = {
    "description": "分页账号",
    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserPage"}}},
}


@router.post(
    "",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: _USER_CREATED,
        403: FORBIDDEN,
        409: CONFLICT,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def create_user(
    request: Request,
    body: UserCreateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    check_csrf(request)

    service = IdentityService(session)
    return service.create_user(
        kindergarten_id=current_user.kindergarten_id,
        creator=current_user,
        request=body,
    )


@router.get(
    "",
    response_model=UserPage,
    responses={
        200: _USER_PAGE,
        403: FORBIDDEN,
        422: VALIDATION_ERROR,
    },
)
async def list_users(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserPage:
    service = IdentityService(session)
    items, total = service.list_users(current_user.kindergarten_id, page=page, page_size=page_size)
    return UserPage(items=items, page=page, page_size=page_size, total=total)


@router.get(
    "/{user_id}",
    response_model=User,
    responses={
        200: _USER_OK,
        403: FORBIDDEN,
        404: NOT_FOUND,
        422: VALIDATION_ERROR,
    },
)
async def get_user(
    user_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    service = IdentityService(session)
    user = service.get_user(current_user.kindergarten_id, str(user_id))
    if user is None:
        raise UserNotFoundError()
    return user


@router.patch(
    "/{user_id}",
    response_model=User,
    responses={
        200: _USER_OK,
        403: FORBIDDEN,
        404: NOT_FOUND,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def update_user(
    request: Request,
    user_id: UUID,
    body: UserPatch,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    check_csrf(request)

    service = IdentityService(session)
    user = service.update_user(
        kindergarten_id=current_user.kindergarten_id,
        admin_user=current_user,
        user_id=str(user_id),
        patch=body,
    )
    if user is None:
        raise UserNotFoundError()
    return user


@router.put(
    "/{user_id}/roles",
    response_model=User,
    responses={
        200: _USER_OK,
        403: FORBIDDEN,
        404: NOT_FOUND,
        409: CONFLICT,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def set_user_roles(
    request: Request,
    user_id: UUID,
    body: UserRolesUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    check_csrf(request)

    service = IdentityService(session)
    user = service.set_user_roles(
        kindergarten_id=current_user.kindergarten_id,
        admin_user=current_user,
        user_id=str(user_id),
        role_codes=body.role_codes,
    )
    if user is None:
        raise UserNotFoundError()
    return user


@router.post(
    "/{user_id}/activate",
    response_model=User,
    responses={
        200: _USER_OK,
        403: FORBIDDEN,
        404: NOT_FOUND,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def activate_user(
    request: Request,
    user_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    check_csrf(request)

    service = IdentityService(session)
    user = service.activate_user(
        kindergarten_id=current_user.kindergarten_id,
        admin_user=current_user,
        user_id=str(user_id),
    )
    if user is None:
        raise UserNotFoundError()
    return user


@router.post(
    "/{user_id}/deactivate",
    response_model=User,
    responses={
        200: _USER_OK,
        403: FORBIDDEN,
        404: NOT_FOUND,
        409: CONFLICT,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def deactivate_user(
    request: Request,
    user_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    check_csrf(request)

    service = IdentityService(session)
    return service.deactivate_user(
        kindergarten_id=current_user.kindergarten_id,
        admin_user=current_user,
        user_id=str(user_id),
    )


@router.post(
    "/{user_id}/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "已重置"},
        403: FORBIDDEN,
        404: NOT_FOUND,
        409: CONFLICT,
        422: VALIDATION_ERROR,
    },
    openapi_extra={"parameters": [CSRF_HEADER_PARAM]},
)
async def reset_password(
    request: Request,
    response: Response,
    user_id: UUID,
    body: ResetPasswordRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    check_csrf(request)

    service = IdentityService(session)
    if not service.reset_password(
        kindergarten_id=current_user.kindergarten_id,
        admin_user=current_user,
        target_user_id=str(user_id),
        new_password=body.new_password,
    ):
        raise UserNotFoundError()

    response.status_code = status.HTTP_204_NO_CONTENT
    return response
