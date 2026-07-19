"""认证 API 测试。"""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.app import create_app
from apps.api.dependencies import HealthDependencies


@pytest.fixture
def client(migrated_database_url: str) -> TestClient:
    async def _true() -> bool:
        return True

    return TestClient(
        create_app(
            dependencies=HealthDependencies(
                database=_true,
                redis=_true,
                ai=_true,
                calendar=_true,
                template=_true,
                export_storage=_true,
                security_ready=True,
            )
        )
    )


@pytest.fixture(autouse=True)
def _set_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from packages.backend.config import settings

    monkeypatch.setattr(
        settings,
        "jwt_signing_key",
        "test-jwt-signing-key-32bytes-long-12345",
        raising=False,
    )
    monkeypatch.setattr(
        settings,
        "csrf_signing_key",
        "test-csrf-signing-key-32bytes-long-1234",
        raising=False,
    )


@pytest.fixture(autouse=True)
def _reset_login_throttle() -> Iterator[None]:
    """每个认证测试前清空内存限流状态，避免顺序运行导致误拦截。"""
    from apps.api.routers import auth as auth_router

    backend = getattr(auth_router._throttle, "_backend", None)
    if backend is not None and hasattr(backend, "storage"):
        backend.storage.clear()
    yield


@pytest.fixture
def csrf_token(monkeypatch: pytest.MonkeyPatch) -> str:
    from packages.backend.config import settings
    from packages.backend.identity.csrf import generate_csrf_token

    key = "test-csrf-signing-key-32bytes-long-1234"
    monkeypatch.setattr(settings, "csrf_signing_key", key, raising=False)
    return generate_csrf_token(key)


@pytest.fixture
def csrf_cookie(csrf_token: str) -> dict[str, str]:
    return {"child_manager_csrf": csrf_token}


@pytest.fixture
def csrf_headers(csrf_token: str) -> dict[str, str]:
    return {
        "origin": "http://127.0.0.1:28080",
        "x-csrf-token": csrf_token,
    }


def _cookies(response: Any) -> list[str]:
    return response.headers.get_list("set-cookie")


def _auth_cookies(response: Any) -> list[str]:
    return [c for c in _cookies(response) if "HttpOnly" in c]


def test_login_sets_two_http_only_cookies(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 200
    cookies = _auth_cookies(response)
    assert len(cookies) == 2
    assert all("HttpOnly" in c for c in cookies)
    assert any(c.startswith("child_manager_access=") for c in cookies)
    assert any(c.startswith("child_manager_refresh=") for c in cookies)


def test_login_failure_returns_generic_message(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "wrong-password"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 401
    data = response.json()
    assert "账号或密码错误" in data["message"]


def test_disabled_user_cannot_login(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "disabled", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 401


def test_refresh_returns_two_new_cookies(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    refresh_cookie = login.cookies.get("child_manager_refresh")
    assert refresh_cookie is not None
    response = client.post(
        "/api/v1/auth/refresh",
        headers=csrf_headers,
        cookies={"child_manager_refresh": refresh_cookie, **csrf_cookie},
    )
    assert response.status_code == 200
    cookies = _auth_cookies(response)
    assert len(cookies) == 2


def test_logout_clears_two_cookies(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/logout",
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 204
    cookies = _auth_cookies(response)
    assert len(cookies) == 2
    assert all("Max-Age=0" in c for c in cookies)


def test_logout_revokes_access_token_on_next_request(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """退出后，旧 Access Token 下一请求必须返回 401。"""
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    access_cookie = login.cookies.get("child_manager_access")
    refresh_cookie = login.cookies.get("child_manager_refresh")
    assert access_cookie is not None
    assert refresh_cookie is not None

    logout = client.post(
        "/api/v1/auth/logout",
        headers=csrf_headers,
        cookies={"child_manager_refresh": refresh_cookie, **csrf_cookie},
    )
    assert logout.status_code == 204

    me_after_logout = client.get(
        "/api/v1/auth/me",
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert me_after_logout.status_code == 401
    assert me_after_logout.json()["code"] == "auth.unauthenticated"


def test_login_rate_limit_after_repeated_source_failures(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """P1-3：来源 30 次/15 分钟失败后触发 429；账号退避不返回 429。"""
    # 替换休眠器为立即返回，避免账号退避阻塞测试。
    from apps.api.routers import auth as auth_router

    async def _no_sleep(_: float) -> None:
        return None

    original_sleeper = auth_router._account_sleeper
    auth_router._account_sleeper = _no_sleep
    try:
        # 30 次失败来自不同账号但同一来源 IP，触发来源硬频控。
        for i in range(30):
            client.post(
                "/api/v1/auth/login",
                json={"login": f"user-{i}", "password": "wrong"},
                headers=csrf_headers,
                cookies=csrf_cookie,
            )
        response = client.post(
            "/api/v1/auth/login",
            json={"login": "any-user", "password": "wrong"},
            headers=csrf_headers,
            cookies=csrf_cookie,
        )
        assert response.status_code == 429
    finally:
        auth_router._account_sleeper = original_sleeper


def test_refresh_replay_revokes_family(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    refresh_cookie = login.cookies.get("child_manager_refresh")
    assert refresh_cookie is not None

    first = client.post(
        "/api/v1/auth/refresh",
        headers=csrf_headers,
        cookies={"child_manager_refresh": refresh_cookie, **csrf_cookie},
    )
    assert first.status_code == 200
    new_access_cookie = first.cookies.get("child_manager_access")
    new_refresh_cookie = first.cookies.get("child_manager_refresh")
    assert new_access_cookie is not None
    assert new_refresh_cookie is not None

    replay = client.post(
        "/api/v1/auth/refresh",
        headers=csrf_headers,
        cookies={"child_manager_refresh": refresh_cookie, **csrf_cookie},
    )
    assert replay.status_code == 401

    # 重放后，第一次轮换得到的新 Access Token 也必须失效。
    access_after_replay = client.get(
        "/api/v1/auth/me",
        headers=csrf_headers,
        cookies={"child_manager_access": new_access_cookie, **csrf_cookie},
    )
    assert access_after_replay.status_code == 401
    assert access_after_replay.json()["code"] == "auth.unauthenticated"

    new_token_after_replay = client.post(
        "/api/v1/auth/refresh",
        headers=csrf_headers,
        cookies={"child_manager_refresh": new_refresh_cookie, **csrf_cookie},
    )
    assert new_token_after_replay.status_code == 401


def test_change_password_returns_204(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    access_cookie = login.cookies.get("child_manager_access")
    assert access_cookie is not None

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "ValidPassword2024!", "new_password": "NewPassword2024!"},
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert response.status_code == 204


def test_change_password_revokes_access_token_on_next_request(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """本人改密后，旧 Access Token 下一请求必须返回 401。"""
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    access_cookie = login.cookies.get("child_manager_access")
    assert access_cookie is not None

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "ValidPassword2024!", "new_password": "NewPassword2024!"},
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert response.status_code == 204

    me_after_change = client.get(
        "/api/v1/auth/me",
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert me_after_change.status_code == 401
    assert me_after_change.json()["code"] == "auth.unauthenticated"


def test_change_password_wrong_current_password_returns_auth_login_failed(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """原密码错误时返回 401 auth.login_failed，不使用 request.http_error。"""
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    access_cookie = login.cookies.get("child_manager_access")
    assert access_cookie is not None

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "WrongPassword2024!", "new_password": "NewPassword2024!"},
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "auth.login_failed"
    assert "原密码" in data["message"]


def test_login_with_phone_number(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert admin_login.status_code == 200
    access_cookie = admin_login.cookies.get("child_manager_access")
    assert access_cookie is not None

    create = client.post(
        "/api/v1/users",
        json={
            "username": "phoneuser",
            "display_name": "手机号用户",
            "phone_e164": "13800000000",
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert create.status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"login": "13800000000", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 200
    assert response.json()["username"] == "phoneuser"


def test_unknown_account_login_returns_generic_401(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """未知账号登录不得泄露是否存在，统一返回 401 auth.login_failed。"""
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "definitely-missing-user", "password": "AnyPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "auth.login_failed"


def test_deactivated_user_access_token_revoked_on_next_request(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """教师已登录 -> 管理员停用 -> 旧会话访问受保护资源返回 401。"""
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert admin_login.status_code == 200
    admin_access = admin_login.cookies.get("child_manager_access")
    assert admin_access is not None

    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_to_disable",
            "display_name": "待停用教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=csrf_headers,
        cookies={"child_manager_access": admin_access, **csrf_cookie},
    )
    assert create.status_code == 201
    teacher_id = create.json()["id"]

    teacher_login = client.post(
        "/api/v1/auth/login",
        json={"login": "teacher_to_disable", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert teacher_login.status_code == 200
    teacher_access = teacher_login.cookies.get("child_manager_access")
    assert teacher_access is not None

    # 教师会话有效
    me_before = client.get(
        "/api/v1/auth/me",
        headers=csrf_headers,
        cookies={"child_manager_access": teacher_access, **csrf_cookie},
    )
    assert me_before.status_code == 200

    # 管理员停用教师
    deactivate = client.post(
        f"/api/v1/users/{teacher_id}/deactivate",
        headers=csrf_headers,
        cookies={"child_manager_access": admin_access, **csrf_cookie},
    )
    assert deactivate.status_code == 200

    # 教师旧会话下一受保护请求失权
    me_after = client.get(
        "/api/v1/auth/me",
        headers=csrf_headers,
        cookies={"child_manager_access": teacher_access, **csrf_cookie},
    )
    assert me_after.status_code == 401
    assert me_after.json()["code"] == "auth.unauthenticated"


def test_logout_without_refresh_cookie_revokes_access_token(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """仅携带 Access Cookie 调用退出，也必须撤销该会话 family。"""
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=csrf_headers,
        cookies=csrf_cookie,
    )
    assert login.status_code == 200
    access_cookie = login.cookies.get("child_manager_access")
    assert access_cookie is not None

    logout = client.post(
        "/api/v1/auth/logout",
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert logout.status_code == 204

    me_after_logout = client.get(
        "/api/v1/auth/me",
        headers=csrf_headers,
        cookies={"child_manager_access": access_cookie, **csrf_cookie},
    )
    assert me_after_logout.status_code == 401
    assert me_after_logout.json()["code"] == "auth.unauthenticated"


def test_csrf_rejects_different_port_origin(
    client: TestClient, csrf_cookie: dict[str, str], csrf_token: str
) -> None:
    """同源校验必须比较 scheme + host + effective port，异端口 Origin 应被拒绝。"""
    headers = {
        "origin": "http://127.0.0.1:9999",
        "x-csrf-token": csrf_token,
    }
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 403
    assert response.json()["code"] == "auth.csrf_invalid"


def test_csrf_rejects_different_scheme_origin(
    client: TestClient, csrf_cookie: dict[str, str], csrf_token: str
) -> None:
    """异协议 Origin 即使端口相同也应被拒绝。"""
    headers = {
        "origin": "https://127.0.0.1:28080",
        "x-csrf-token": csrf_token,
    }
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=headers,
        cookies=csrf_cookie,
    )
    assert response.status_code == 403
    assert response.json()["code"] == "auth.csrf_invalid"


def test_login_rate_limit_returns_retry_after(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """P1-3：来源级限流触发 429 时必须返回 Retry-After 头（900 秒窗口）。"""
    from apps.api.routers import auth as auth_router

    async def _no_sleep(_: float) -> None:
        return None

    original_sleeper = auth_router._account_sleeper
    auth_router._account_sleeper = _no_sleep
    try:
        for i in range(30):
            client.post(
                "/api/v1/auth/login",
                json={"login": f"user-{i}", "password": "wrong"},
                headers=csrf_headers,
                cookies=csrf_cookie,
            )
        response = client.post(
            "/api/v1/auth/login",
            json={"login": "any-user", "password": "wrong"},
            headers=csrf_headers,
            cookies=csrf_cookie,
        )
        assert response.status_code == 429
        assert response.json()["code"] == "auth.login_rate_limited"
        retry_after = response.headers.get("retry-after")
        assert retry_after is not None
        # Issue #6：Retry-After 必须落在冻结 OpenAPI [1, 60] 区间内
        assert 1 <= int(retry_after) <= 60
    finally:
        auth_router._account_sleeper = original_sleeper


def test_refresh_with_non_uuid_kindergarten_prefix_returns_unauthenticated(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """带 kg: 前缀但园所 ID 非 UUID 的 Refresh 必须返回 401，不得 500。

    Codex 探针发现 `kg:not-a-uuid:*` 会让 PostgreSQL 抛 InvalidTextRepresentation，
    通过 API 时变成通用 500。父 Issue #4 要求对无效 Refresh 稳定拒绝为未认证结果。
    """
    response = client.post(
        "/api/v1/auth/refresh",
        headers=csrf_headers,
        cookies={"child_manager_refresh": "kg:not-a-uuid:anything", **csrf_cookie},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "auth.unauthenticated"


def test_refresh_with_malformed_values_returns_unauthenticated(
    client: TestClient, csrf_cookie: dict[str, str], csrf_headers: dict[str, str]
) -> None:
    """各类 malformed Refresh 值都必须稳定返回 401，不得进入数据库类型错误。"""
    malformed_values = [
        "not-a-refresh",
        "",
        "kg:",
        "kg:abc",
        "kg:abc:",
        "kgr:00000000-0000-7000-8000-000000000001:token",
    ]
    for value in malformed_values:
        response = client.post(
            "/api/v1/auth/refresh",
            headers=csrf_headers,
            cookies={"child_manager_refresh": value, **csrf_cookie},
        )
        assert response.status_code == 401, f"malformed value={value!r}"
        assert response.json()["code"] == "auth.unauthenticated"
