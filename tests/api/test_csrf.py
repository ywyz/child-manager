# ruff: noqa: F811

from fastapi.testclient import TestClient

from tests.api.passkey_helpers import csrf_headers, passkey_client  # noqa: F401


def test_csrf_cookie_is_signed_readable_and_not_httponly(passkey_client: TestClient) -> None:
    response = passkey_client.get("/api/v1/auth/csrf")

    assert response.status_code == 200
    cookie = response.headers.get_list("set-cookie")[0]
    assert cookie.startswith("child_manager_csrf=")
    assert "SameSite=lax" in cookie
    assert "HttpOnly" not in cookie


def test_passkey_state_change_rejects_missing_csrf_and_wrong_origin(
    passkey_client: TestClient,
) -> None:
    missing = passkey_client.post("/api/v1/auth/authentication/options")
    assert missing.status_code == 403

    headers = csrf_headers(passkey_client)
    headers["Origin"] = "https://evil.example"
    wrong_origin = passkey_client.post(
        "/api/v1/auth/authentication/options",
        headers=headers,
    )
    assert wrong_origin.status_code == 403
    assert wrong_origin.json()["code"] == "auth.csrf_invalid"


def test_recovery_rejects_malformed_signed_double_submit_token(passkey_client: TestClient) -> None:
    passkey_client.cookies.set("child_manager_csrf", "a.a")
    response = passkey_client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": "teacher", "recovery_code": "not-a-real-code"},
        headers={"Origin": "http://testserver", "X-CSRF-Token": "a.a"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "auth.csrf_invalid"
