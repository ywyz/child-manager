import inspect

from apps.web.pages import auth


def test_backup_auth_pages_expose_required_admin_and_optional_teacher_flows() -> None:
    text = set(auth.login_page_text())

    assert {
        "密码与 TOTP 备用登录",
        "设置备用登录",
        "稍后设置",
        "重新验证后新增通行密钥",
        "本人安全事件",
    } <= text


def test_backup_auth_web_source_keeps_secrets_out_of_urls_and_storage() -> None:
    source = inspect.getsource(auth).lower()

    assert "/api/v1/auth/backup" in source
    assert "localstorage" not in source
    assert "sessionstorage" not in source
