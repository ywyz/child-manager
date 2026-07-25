import inspect

import pytest

from apps.web import api_client
from apps.web.pages import auth


def test_backup_auth_pages_expose_required_admin_and_optional_teacher_flows() -> None:
    text = set(auth.login_page_text())

    assert {
        "密码与 TOTP 备用登录",
        "使用密码与 TOTP 登录",
        "设置备用登录",
        "稍后设置",
        "重新验证后新增通行密钥",
        "获取五分钟专用授权",
        "为此设备新增通行密钥",
        "本人安全事件",
    } <= text


def test_backup_auth_web_source_keeps_secrets_out_of_urls_and_storage() -> None:
    source = inspect.getsource(auth).lower()

    assert "/api/v1/auth/backup" in source
    assert "localstorage" not in source
    assert "sessionstorage" not in source


@pytest.mark.asyncio
async def test_backup_login_and_reauthentication_submit_secrets_only_in_post_bodies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        calls.append((path, method, payload))
        return {"ok": True, "status": 204, "body": {}}

    monkeypatch.setattr(api_client, "same_origin_api_request", fake_request)

    await api_client.backup_login_api_request(
        identifier="teacher",
        password="test-password",
        totp_code="123456",
    )
    await api_client.backup_reauthentication_api_request(
        password="test-password",
        totp_code="654321",
    )

    assert calls == [
        (
            "/api/v1/auth/backup/authentication",
            "POST",
            {
                "identifier": "teacher",
                "password": "test-password",
                "totp_code": "123456",
            },
        ),
        (
            "/api/v1/auth/backup/reauthentication",
            "POST",
            {"password": "test-password", "totp_code": "654321"},
        ),
    ]
    assert all("password" not in path and "totp_code" not in path for path, _, _ in calls)
