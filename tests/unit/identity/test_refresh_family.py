"""Refresh Token family 语义测试。"""

from collections.abc import Iterator

import pytest
from sqlalchemy import select

from packages.backend.database import session as session_module
from packages.backend.identity.models import RefreshToken
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


def test_refresh_writes_replaced_by_id_pointer(service: IdentityService, kindergarten: str) -> None:
    """Codex 第十九轮 P0-4：轮换后旧行 replaced_by_id 必须指向新行 id。

    权威数据模型要求"每次刷新撤销旧 token 并指向新 token"。旧行 revoked_at
    非空、revoke_reason="rotation"、replaced_by_id 等于新行 id；新行 revoked_at
    为空。CHECK ck_refresh_tokens_replaced_implies_revoked 要求 replaced_by_id 与
    revoked_at 在同一 UPDATE 中写入，因此 service 先创建新行 flush 再原子撤销旧行。
    """
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    old_token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login.refresh_value)
    )
    assert old_token is not None
    old_id = old_token.id
    assert old_token.replaced_by_id is None

    refreshed = service.refresh(refresh_cookie=login.refresh_value)
    assert refreshed is not None
    service._session.commit()

    # 重新查询旧行以读取 UPDATE 后的状态。
    old_row = service._session.get(RefreshToken, old_id)
    assert old_row is not None
    assert old_row.revoked_at is not None
    assert old_row.revoke_reason == "rotation"
    assert old_row.replaced_by_id is not None

    new_row = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(refreshed.refresh_value)
    )
    assert new_row is not None
    assert new_row.revoked_at is None
    assert new_row.replaced_by_id is None
    # 关键断言：旧行的 replaced_by_id 指向新行 id。
    assert old_row.replaced_by_id == new_row.id


def test_refresh_replay_after_rotation_revokes_family(
    service: IdentityService, kindergarten: str
) -> None:
    """重放已轮换的旧 cookie：返回 None 并以 replay 撤销整个 family。

    Codex 第十九轮 P0-4：补重放测试，确保 replaced_by_id 指针写入后，重放仍能
    正确触发 family 级撤销。轮换产生的新 token 在重放后必须被撤销并标记 replay。
    """
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    first_refresh = service.refresh(refresh_cookie=login.refresh_value)
    assert first_refresh is not None
    service._session.commit()

    # 用已轮换掉的旧 cookie 再次调用 refresh，触发重放。
    replay = service.refresh(refresh_cookie=login.refresh_value)
    assert replay is None
    service._session.commit()

    # 新 token（第一次轮换产生）必须被 family 级撤销覆盖，revoke_reason 标记为 replay。
    new_token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(first_refresh.refresh_value)
    )
    assert new_token is not None
    assert new_token.revoked_at is not None
    assert new_token.revoke_reason == "replay"

    # family 内所有 token 都必须被撤销。
    stmt = select(RefreshToken).where(RefreshToken.kindergarten_id == kindergarten)
    all_tokens = list(service._session.execute(stmt).scalars().all())
    assert len(all_tokens) >= 2
    for token in all_tokens:
        assert token.revoked_at is not None


def test_refresh_exception_rolls_back_old_token_not_revoked(
    service: IdentityService,
    kindergarten: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """轮换过程中抛异常时事务回滚，旧 token 不被撤销，replaced_by_id 保持 NULL。

    Codex 第十九轮 P0-4：补回滚测试，确保 create 新行后、revoke 旧行前抛异常时
    不会留下"新行已建但旧行未撤销"的半成品状态。事务原子性要求两者同生共死。
    """
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    service._session.commit()

    old_token = service._repo.find_refresh_token_by_hash(
        kindergarten, hash_refresh_value(login.refresh_value)
    )
    assert old_token is not None
    old_id = old_token.id

    def _raise_on_revoke(*args: object, **kwargs: object) -> int:
        raise RuntimeError("simulated failure during rotation")

    monkeypatch.setattr(service._repo, "revoke_refresh_token", _raise_on_revoke)

    with pytest.raises(RuntimeError, match="simulated failure"):
        service.refresh(refresh_cookie=login.refresh_value)

    # 回滚事务，清除 pending 的新行（create_refresh_token 已 flush INSERT）。
    service._session.rollback()

    # 重新查询旧行以确认 DB 状态：未被撤销，replaced_by_id 保持 NULL。
    stmt = select(RefreshToken).where(
        RefreshToken.kindergarten_id == kindergarten,
        RefreshToken.token_hash == hash_refresh_value(login.refresh_value),
    )
    old_row = service._session.execute(stmt).scalar_one_or_none()
    assert old_row is not None
    assert old_row.id == old_id
    assert old_row.revoked_at is None
    assert old_row.replaced_by_id is None

    # 新行应已随回滚消失；family 内只剩原始登录 token，且未撤销。
    remaining = (
        service._session.execute(
            select(RefreshToken).where(RefreshToken.kindergarten_id == kindergarten)
        )
        .scalars()
        .all()
    )
    assert len(remaining) == 1
    assert remaining[0].id == old_id
    assert remaining[0].revoked_at is None
