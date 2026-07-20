"""用户管理 API 测试。"""

import pytest
from fastapi.testclient import TestClient

from apps.api.app import create_app
from apps.api.dependencies import HealthDependencies
from packages.backend.identity.csrf import generate_csrf_token


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


_CSRF_TOKEN = generate_csrf_token("test-csrf-signing-key-32bytes-long-1234")
_CSRF_HEADERS = {
    "origin": "http://127.0.0.1:28080",
    "x-csrf-token": _CSRF_TOKEN,
}
_CSRF_COOKIE = {"child_manager_csrf": _CSRF_TOKEN}


def _admin_session(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert login.status_code == 200
    access = login.cookies.get("child_manager_access")
    assert access is not None
    return {"child_manager_access": access, **_CSRF_COOKIE}


def test_create_user_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "username": "teacher",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401


def test_create_user_returns_201_and_user(client: TestClient) -> None:
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "teacher1",
            "display_name": "教师一",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "teacher1"
    assert data["role_codes"] == ["teacher"]
    assert "created_at" in data


def test_create_user_rejects_nfkc_expanded_username_with_422(client: TestClient) -> None:
    """NFKC 扩长用户名必须在统一边界返回 422，不得让 DataError 外泄为 500。

    U+FB03 ``ﬃ`` 经 NFKC 展开为 ``ffi``。50 个 ``ﬃ`` 原长 50（<=120，契约
    合法），规范化后 150（>120），写入 ``VARCHAR(120)`` 会被数据库拒绝。
    Codex 第十六轮探针复现：PostgreSQL 实测报 ``value too long``。
    """
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "\ufb03" * 50,
            "display_name": "扩长用户名",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "auth.invalid_username"


def test_create_user_allows_unicode_username(client: TestClient) -> None:
    """冻结 Schema 只要求 NFKC+trim+lower，Unicode 用户名必须被接受。

    Codex 第十八轮审阅 P1-4：0006 迁移保留的 Unicode 旧用户名（如 ``教师``）
    升级后必须仍能创建与登录，否则应用层静默锁死既有账号（T029 回归）。
    """
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "教师",
            "display_name": "Unicode 教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 201
    assert response.json()["username"] == "教师"


def test_create_user_invalid_phone_returns_422(client: TestClient) -> None:
    """RED 回归：非法手机号必须返回 422，不得外泄为 500。

    Codex 第十九轮审阅 P0：旧版 normalize_phone 的 ValueError 在 create 路径
    未被捕获，外泄为 500。冻结 OpenAPI 要求 422 ValidationError。
    """
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "bad_phone_user",
            "display_name": "非法手机号",
            "phone_e164": "abc",
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "auth.invalid_phone"


def test_create_user_weak_password_returns_422(client: TestClient) -> None:
    """RED 回归：SecLists 弱密码必须返回 422，不得外泄为 500。

    Codex 第十九轮审阅 P0：旧版 validate_password 的 ValueError 在 create 路径
    未被捕获，外泄为 500。使用合法长度但出现在常见弱密码列表中的密码。
    """
    cookies = _admin_session(client)
    # "films+pic+galeries" 是 Codex 报告中提到的 SecLists 弱密码样本，
    # 长度 17 满足 >=15 但在 10k-most-common 列表中。
    response = client.post(
        "/api/v1/users",
        json={
            "username": "weak_pw_user",
            "display_name": "弱密码",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "films+pic+galeries",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "auth.invalid_password"


def test_create_user_short_password_returns_422(client: TestClient) -> None:
    """RED 回归：长度不足的密码必须返回 422。

    短密码（<15）由契约层 minLength 校验拦截，返回 422
    ``request.validation_failed``；服务层 ``validate_password`` 不会到达。
    此测试验证短密码不外泄为 500。
    """
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "short_pw_user",
            "display_name": "短密码",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "short",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422


def test_create_user_invalid_phone_no_side_effects(client: TestClient) -> None:
    """非法手机号 422 后事务无副作用：用户未被创建。

    Codex 第十九轮审阅 P0：确认 422 失败后不会留下半写入的用户记录。
    """
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "no_side_effect_user",
            "display_name": "事务无副作用",
            "phone_e164": "invalid",
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    # 用户列表中不应出现该用户名。
    listing = client.get("/api/v1/users", headers=_CSRF_HEADERS, cookies=cookies)
    usernames = [u["username"] for u in listing.json()["items"]]
    assert "no_side_effect_user" not in usernames


def test_list_users_returns_pagination(client: TestClient) -> None:
    cookies = _admin_session(client)
    response = client.get("/api/v1/users", headers=_CSRF_HEADERS, cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data


def test_get_user_by_id(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher2",
            "display_name": "教师二",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}", headers=_CSRF_HEADERS, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_update_user(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher3",
            "display_name": "教师三",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"display_name": "更新后的名称"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "更新后的名称"


def test_update_user_username(client: TestClient) -> None:
    """PATCH 用户名应能正常更新。"""
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_username",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"username": "teacher_new_name"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["username"] == "teacher_new_name"


def test_update_user_rejects_nfkc_expanded_username_with_422(client: TestClient) -> None:
    """PATCH NFKC 扩长用户名必须在统一边界返回 422，不得外泄 DataError。"""
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_nfkc_patch",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"username": "\ufb03" * 50},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "auth.invalid_username"


def test_update_user_phone_to_null_clears_phone(client: TestClient) -> None:
    """PATCH phone_e164 为 null 应显式清空手机号。"""
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_phone",
            "display_name": "有手机教师",
            "phone_e164": "13800000001",
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    assert create.json()["phone_e164"] == "+8613800000001"

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"phone_e164": None},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["phone_e164"] is None

    get_response = client.get(
        f"/api/v1/users/{user_id}",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert get_response.status_code == 200
    assert get_response.json()["phone_e164"] is None


def test_update_user_invalid_phone_returns_422(client: TestClient) -> None:
    """RED 回归：PATCH 非法手机号必须返回 422，不得外泄为 500。

    Codex 第十九轮审阅 P0：旧版 normalize_phone 的 ValueError 在 update 路径
    未被捕获，外泄为 500。冻结 OpenAPI 要求 422 ValidationError。
    """
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_bad_phone_update",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"phone_e164": "not-a-phone"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "auth.invalid_phone"


def test_reset_password_weak_password_returns_422(client: TestClient) -> None:
    """RED 回归：reset-password 弱密码必须返回 422，不得外泄为 500。

    Codex 第十九轮审阅 P0：旧版 validate_password 的 ValueError 在 reset 路径
    未被捕获，外泄为 500。冻结 OpenAPI 要求 422 ValidationError。
    """
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_reset_weak",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "films+pic+galeries"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "auth.invalid_password"


def test_reset_password_short_password_returns_422(client: TestClient) -> None:
    """RED 回归：reset-password 长度不足的密码必须返回 422。

    短密码（<15）由契约层 minLength 校验拦截，返回 422。
    """
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_reset_short",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "short"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422


def test_set_user_roles(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher4",
            "display_name": "教师四",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.put(
        f"/api/v1/users/{user_id}/roles",
        json={"role_codes": ["teacher", "admin"]},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert set(response.json()["role_codes"]) == {"teacher", "admin"}


def test_deactivate_and_activate_user(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher5",
            "display_name": "教师五",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    deactivate = client.post(
        f"/api/v1/users/{user_id}/deactivate",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    get_response = client.get(f"/api/v1/users/{user_id}", headers=_CSRF_HEADERS, cookies=cookies)
    assert get_response.json()["is_active"] is False

    activate = client.post(
        f"/api/v1/users/{user_id}/activate",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert activate.status_code == 200
    assert activate.json()["is_active"] is True


def test_reset_password_returns_204(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher6",
            "display_name": "教师六",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 204


def test_reset_password_revokes_target_access_token_on_next_request(client: TestClient) -> None:
    """管理员重置密码后，目标用户旧 Access Token 下一请求必须返回 401。"""
    admin_cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_reset_target",
            "display_name": "重置目标教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=admin_cookies,
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    teacher_login = client.post(
        "/api/v1/auth/login",
        json={"login": "teacher_reset_target", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert teacher_login.status_code == 200
    teacher_access = teacher_login.cookies.get("child_manager_access")
    assert teacher_access is not None

    me_before = client.get(
        "/api/v1/auth/me",
        headers=_CSRF_HEADERS,
        cookies={"child_manager_access": teacher_access, **_CSRF_COOKIE},
    )
    assert me_before.status_code == 200

    reset = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=admin_cookies,
    )
    assert reset.status_code == 204

    me_after = client.get(
        "/api/v1/auth/me",
        headers=_CSRF_HEADERS,
        cookies={"child_manager_access": teacher_access, **_CSRF_COOKIE},
    )
    assert me_after.status_code == 401
    assert me_after.json()["code"] == "auth.unauthenticated"


def test_deactivate_last_admin_is_rejected(client: TestClient) -> None:
    cookies = _admin_session(client)
    me = client.get("/api/v1/auth/me", headers=_CSRF_HEADERS, cookies=cookies)
    admin_id = me.json()["id"]

    response = client.post(
        f"/api/v1/users/{admin_id}/deactivate",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 409


def test_reset_password_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/user-1/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401


# --- OpenAPI 与 Runtime 一致性（Issue #6 M2 Final Fix Area 1）---
# 验证 403（CSRF/权限）/422（参数校验）/404（不存在）与冻结 OpenAPI 声明一致。


def test_create_user_missing_required_fields_returns_422(client: TestClient) -> None:
    """OpenAPI 声明 POST /users 422；缺少必填字段必须返回 422，不得 500。"""
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={"username": "only_username"},  # 缺少 display_name/password/role_codes
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "request.validation_failed"


def test_get_nonexistent_user_returns_404(client: TestClient) -> None:
    """OpenAPI 声明 GET /users/{user_id} 404；不存在必须返回 404。"""
    cookies = _admin_session(client)
    response = client.get(
        "/api/v1/users/00000000-0000-7000-8000-000000000000",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 404
    assert response.json()["code"] == "resource.not_found"


def test_create_user_without_csrf_returns_403(client: TestClient) -> None:
    """OpenAPI 声明 POST /users 403；已认证但无 CSRF 必须返回 403。

    Users 端点的 403 覆盖 CSRF 失败与权限不足两种情况。此处验证已认证
    管理员缺少 CSRF 头时返回 403（auth.csrf_invalid），而非 401 或 500。
    """
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "no_csrf_user",
            "display_name": "无CSRF",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        cookies=cookies,  # 有 access cookie 但故意不传 CSRF 头/origin
    )
    assert response.status_code == 403
    assert response.json()["code"] == "auth.csrf_invalid"


def test_update_user_empty_body_returns_422(client: TestClient) -> None:
    """OpenAPI 声明 PATCH /users/{user_id} 422；空 body 必须返回 422。

    UserPatch 要求 minProperties: 1，空对象不得通过。
    """
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "patch_empty",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "request.validation_failed"


def test_reset_password_nonexistent_user_returns_404(client: TestClient) -> None:
    """OpenAPI 声明 POST /users/{user_id}/reset-password 404；不存在必须 404。"""
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users/00000000-0000-7000-8000-000000000000/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 404
    assert response.json()["code"] == "resource.not_found"
