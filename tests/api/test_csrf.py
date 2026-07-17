# ruff: noqa: F811

from fastapi.testclient import TestClient

from tests.api.identity_helpers import csrf_headers, identity_client  # noqa: F401


def test_csrf_cookie_is_signed_readable_and_not_httponly(identity_client: TestClient) -> None:
    response = identity_client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    cookie = response.headers.get_list("set-cookie")[0]
    assert cookie.startswith("child_manager_csrf=")
    assert "SameSite=lax" in cookie
    assert "HttpOnly" not in cookie


def test_state_change_rejects_missing_csrf_and_wrong_origin(identity_client: TestClient) -> None:
    missing = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
    )
    assert missing.status_code == 403
    headers = csrf_headers(identity_client)
    headers["Origin"] = "https://evil.example"
    wrong_origin = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    assert wrong_origin.status_code == 403
    assert wrong_origin.json()["code"] == "auth.csrf_invalid"


def test_state_change_rejects_malformed_csrf_token(identity_client: TestClient) -> None:
    identity_client.cookies.set("child_manager_csrf", "a.a")
    response = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers={"Origin": "http://testserver", "X-CSRF-Token": "a.a"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "auth.csrf_invalid"
