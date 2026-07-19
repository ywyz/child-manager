"""Refresh Token family 语义测试。"""

from collections.abc import Iterator

import pytest

from packages.backend.database import session as session_module
from packages.backend.identity.service import IdentityService
from packages.backend.identity.tokens import hash_refresh_value


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
    """在已迁移的隔离 schema 上构造 IdentityService。"""
    session = session_module.SessionLocal()
    try:
        yield IdentityService(session)
    finally:
        session.close()


@pytest.fixture
def kindergarten(service: IdentityService):
    result = service.init_admin(
        kg_name="Refresh 测试园", admin_username="admin", password="ValidPassword2024!"
    )
    service._session.commit()
    return result["kindergarten_id"]


def test_login_creates_independent_family(service: IdentityService, kindergarten: str) -> None:
    result = service.login(username="admin", password="ValidPassword2024!")
    assert result is not None
    service._session.commit()

    token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(result.refresh_value)
    )
    assert token is not None
    assert token.token_family_id != result.user.id
    assert token.expires_at is not None


def test_refresh_preserves_family_id_with_sliding_expiration(
    service: IdentityService, kindergarten: str
) -> None:
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    original_family = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login.refresh_value)
    )
    assert original_family is not None
    family_id = original_family.token_family_id

    refreshed = service.refresh(refresh_cookie=login.refresh_value)
    assert refreshed is not None
    service._session.commit()

    new_token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(refreshed.refresh_value)
    )
    assert new_token is not None
    assert new_token.token_family_id == family_id
    # 冻结 Schema §5.5 未定义 family 级过期；滑动续期每条 token 自带 7 天 expires_at。
    assert new_token.expires_at is not None
