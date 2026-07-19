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


def test_refresh_preserves_family_id_with_fixed_absolute_expiration(
    service: IdentityService, kindergarten: str
) -> None:
    """冻结 Schema §5.5：同一 family 后续 token 必须复制首次签发的 expires_at。"""
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    original_family = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login.refresh_value)
    )
    assert original_family is not None
    family_id = original_family.token_family_id
    first_expires_at = original_family.expires_at

    refreshed = service.refresh(refresh_cookie=login.refresh_value)
    assert refreshed is not None
    service._session.commit()

    new_token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(refreshed.refresh_value)
    )
    assert new_token is not None
    assert new_token.token_family_id == family_id
    # 关键断言：新 token 必须复制首次签发的 expires_at，不得滑动延长。
    assert new_token.expires_at == first_expires_at


def test_refresh_twice_keeps_family_expires_at_constant(
    service: IdentityService, kindergarten: str
) -> None:
    """连续轮换两次，family 内所有 token 的 expires_at 必须完全一致。"""
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    first_token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login.refresh_value)
    )
    assert first_token is not None
    family_expires_at = first_token.expires_at

    first_refresh = service.refresh(refresh_cookie=login.refresh_value)
    assert first_refresh is not None
    service._session.commit()

    second_refresh = service.refresh(refresh_cookie=first_refresh.refresh_value)
    assert second_refresh is not None
    service._session.commit()

    # 查询 family 内所有未撤销 token，断言 expires_at 完全一致。
    from sqlalchemy import select

    from packages.backend.identity.models import RefreshToken

    stmt = (
        select(RefreshToken)
        .where(
            RefreshToken.kindergarten_id == kindergarten,
            RefreshToken.token_family_id == first_token.token_family_id,
        )
        .order_by(RefreshToken.issued_at)
    )
    tokens = list(service._session.execute(stmt).scalars().all())
    # 连续轮换两次后 family 内有 3 条记录：登录、第一次轮换、第二次轮换。
    assert len(tokens) == 3
    for token in tokens:
        assert token.expires_at == family_expires_at
