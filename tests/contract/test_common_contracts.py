"""统一错误、分页和 Request ID 契约。"""

from uuid import UUID

import pytest
from pydantic import ValidationError

from packages.contracts.common import (
    CONFIGURATION_UNAVAILABLE,
    DATABASE_UNAVAILABLE,
    ErrorResponse,
    Pagination,
)


def test_error_response_has_stable_shape_and_empty_field_errors() -> None:
    response = ErrorResponse(
        code="lesson_plan.version_conflict",
        message="教案已被其他教师修改，请刷新后重试。",
        request_id=UUID("01900000-0000-7000-8000-000000000001"),
    )

    assert response.model_dump(mode="json") == {
        "code": "lesson_plan.version_conflict",
        "message": "教案已被其他教师修改，请刷新后重试。",
        "request_id": "01900000-0000-7000-8000-000000000001",
        "field_errors": [],
    }


@pytest.mark.parametrize(("page", "page_size"), [(0, 20), (1, 0), (1, 101)])
def test_pagination_rejects_values_outside_contract(page: int, page_size: int) -> None:
    with pytest.raises(ValidationError):
        Pagination(page=page, page_size=page_size)


def test_unavailable_error_codes_are_stable() -> None:
    assert DATABASE_UNAVAILABLE == "database.unavailable"
    assert CONFIGURATION_UNAVAILABLE == "configuration.unavailable"
