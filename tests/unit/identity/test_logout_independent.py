"""注销独立解析 access 与 refresh 的负向回归测试。

Codex 第十二轮 P0-3：refresh 无效/查无/错配时不得阻断 access 回退；
二者 family 不一致时至少撤销 access 所代表的当前会话。
"""

from collections.abc import Iterator

import pytest

from packages.backend.database import session as session_module
from packages.backend.identity.service import IdentityService
from packages.backend.identity.tokens import (
    decode_access_token,
    generate_refresh_value,
    hash_refresh_value,
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


@pytest.fixture
def service(migrated_database_url: str) -> Iterator[IdentityService]:
    session = session_module.SessionLocal()
    try:
        yield IdentityService(session)
    finally:
        session.close()


@pytest.fixture
def kindergarten(service: IdentityService):
    result = service.init_admin(
        kg_name="注销负向测试园", admin_username="admin", password="ValidPassword2024!"
    )
    service._session.commit()
    return result["kindergarten_id"]


def _login_family(service: IdentityService, kindergarten: str) -> tuple[str, str, str]:
    """登录并返回 (access_token, refresh_value, family_id)。"""
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    token_row = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login.refresh_value)
    )
    assert token_row is not None
    return login.access_token, login.refresh_value, token_row.token_family_id


def _is_access_family_active(
    service: IdentityService, kindergarten: str, access_token: str
) -> bool:
    from packages.backend.config import settings

    payload = decode_access_token(access_token, settings.jwt_signing_key)
    assert payload is not None
    family_id = payload["family_id"]
    return service.is_token_family_active(kindergarten, family_id)


def test_logout_with_malformed_refresh_still_revokes_access(
    service: IdentityService, kindergarten: str
) -> None:
    """畸形 refresh cookie + 合法 access 注销后，access family 必须被撤销。"""
    access_token, _refresh_value, _family_id = _login_family(service, kindergarten)

    service.logout(access_token=access_token, refresh_cookie="not-a-valid-refresh")
    service._session.commit()

    assert _is_access_family_active(service, kindergarten, access_token) is False


def test_logout_with_unknown_refresh_still_revokes_access(
    service: IdentityService, kindergarten: str
) -> None:
    """查无记录的 refresh + 合法 access 注销后，access family 必须被撤销。"""
    access_token, _refresh_value, _family_id = _login_family(service, kindergarten)

    # 构造格式合法但数据库中不存在的 refresh cookie。
    unknown_refresh = generate_refresh_value(kindergarten_id=kindergarten)
    service.logout(access_token=access_token, refresh_cookie=unknown_refresh)
    service._session.commit()

    assert _is_access_family_active(service, kindergarten, access_token) is False


def test_logout_with_mismatched_refresh_revokes_access_family(
    service: IdentityService, kindergarten: str
) -> None:
    """错配 refresh（family B）+ 合法 access（family A）注销后，access family A 必须撤销。"""
    # family A：第一次登录
    access_a, _refresh_a, family_a = _login_family(service, kindergarten)

    # family B：第二次登录（新 family）
    login_b = service.login(username="admin", password="ValidPassword2024!")
    assert login_b is not None
    service._session.commit()
    token_b = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login_b.refresh_value)
    )
    assert token_b is not None
    family_b = token_b.token_family_id
    assert family_b != family_a

    # 用 family B 的 refresh + family A 的 access 注销。
    service.logout(access_token=access_a, refresh_cookie=login_b.refresh_value)
    service._session.commit()

    # family A（access 所在）必须被撤销。
    assert service.is_token_family_active(kindergarten, family_a) is False
    # family B（refresh 所在）也必须被撤销，避免遗留会话。
    assert service.is_token_family_active(kindergarten, family_b) is False


def test_logout_with_only_access_revokes_access_family(
    service: IdentityService, kindergarten: str
) -> None:
    """仅携带 access（无 refresh）注销后，access family 必须被撤销。"""
    access_token, _refresh_value, family_id = _login_family(service, kindergarten)

    service.logout(access_token=access_token, refresh_cookie=None)
    service._session.commit()

    assert service.is_token_family_active(kindergarten, family_id) is False
