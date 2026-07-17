from pathlib import Path

import pytest
import yaml

from packages.contracts.identity import ChangePasswordRequest, LoginRequest

OPENAPI = yaml.safe_load(
    Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
)


def test_auth_contract_has_no_public_registration_or_http_initialization() -> None:
    paths = OPENAPI["paths"]
    assert "/api/v1/register" not in paths
    assert "/api/v1/auth/init-admin" not in paths


def test_auth_contract_locks_two_raw_auth_cookie_headers() -> None:
    headers = OPENAPI["components"]["headers"]
    assert headers["AuthSetCookies"]["schema"]["minItems"] == 2
    assert headers["AuthSetCookies"]["schema"]["maxItems"] == 2
    assert headers["ClearAuthCookies"]["schema"]["minItems"] == 2
    assert "逗号折叠" in headers["AuthSetCookies"]["description"]


def test_auth_request_models_reject_extra_fields_and_short_new_password() -> None:
    assert LoginRequest(login="teacher", password="secret").model_dump() == {
        "login": "teacher",
        "password": "secret",
    }
    try:
        ChangePasswordRequest.model_validate(
            {"current_password": "old", "new_password": "too-short", "role": "admin"}
        )
    except ValueError:
        pass
    else:
        raise AssertionError("短密码或额外角色字段必须被契约拒绝")


@pytest.mark.parametrize(
    "payload",
    [
        {"login": "", "password": "secret"},
        {"login": "teacher", "password": ""},
        {"login": "x" * 121, "password": "secret"},
        {"login": "teacher", "password": "x" * 129},
    ],
)
def test_login_request_matches_openapi_length_bounds(payload: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        LoginRequest.model_validate(payload)
