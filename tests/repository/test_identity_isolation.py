"""身份 Repository 园所隔离测试。"""

from collections.abc import Iterator
from uuid import uuid4

import pytest

from packages.backend.database import session as session_module
from packages.backend.identity.repository import IdentityRepository


@pytest.fixture
def repo(db_repo: IdentityRepository) -> IdentityRepository:
    """默认使用真实 PostgreSQL 隔离 schema 的 Repository。"""
    return db_repo


@pytest.fixture
def db_repo(migrated_database_url: str) -> Iterator[IdentityRepository]:
    """在真实 PostgreSQL 隔离 schema 上构造 Repository。"""
    session = session_module.SessionLocal()
    try:
        yield IdentityRepository(session)
    finally:
        session.close()


@pytest.fixture
def kg_a(repo: IdentityRepository) -> str:
    kg = repo.create_kindergarten(name="A园")
    return str(kg.id)


@pytest.fixture
def kg_b(repo: IdentityRepository) -> str:
    kg = repo.create_kindergarten(name="B园")
    return str(kg.id)


def test_create_and_retrieve_kindergarten(repo: IdentityRepository, kg_a: str) -> None:
    kg = repo.create_kindergarten(name="阳光幼儿园")
    assert kg is not None
    assert kg.name == "阳光幼儿园"


def test_kindergarten_isolation(repo: IdentityRepository) -> None:
    repo.create_kindergarten(name="A园")
    non_existent = str(uuid4())
    assert repo.get_kindergarten_by_id(non_existent) is None


def test_user_isolation(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    repo.create_user(
        kindergarten_id=kg_a,
        username="admin",
        username_normalized="admin",
        phone_e164=None,
        display_name="管理员",
        password_hash="hash",
    )
    assert repo.get_user_by_username(kg_b, "admin") is None
    assert repo.list_users(kg_b) == []


def test_phone_isolation(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    repo.create_user(
        kindergarten_id=kg_a,
        username="teacher",
        username_normalized="teacher",
        phone_e164="+8613800000000",
        display_name="教师",
        password_hash="hash",
    )
    assert repo.get_user_by_phone(kg_b, "+8613800000000") is None
    found = repo.get_user_by_phone(kg_a, "+8613800000000")
    assert found is not None
    assert found.username == "teacher"


def test_active_admin_count_is_per_kindergarten(
    repo: IdentityRepository, kg_a: str, kg_b: str
) -> None:
    role = repo.get_role_by_code("admin")
    assert role is not None
    user = repo.create_user(
        kindergarten_id=kg_a,
        username="admin",
        username_normalized="admin",
        phone_e164=None,
        display_name="管理员",
        password_hash="hash",
    )
    repo.assign_role(
        kindergarten_id=kg_a,
        user_id=user.id,
        role_id=role.id,
        assigned_by=user.id,
    )
    assert repo.get_active_admin_count(kg_a) == 1
    assert repo.get_active_admin_count(kg_b) == 0


def test_deactivate_user_sets_is_active_false(repo: IdentityRepository, kg_a: str) -> None:
    user = repo.create_user(
        kindergarten_id=kg_a,
        username="teacher",
        username_normalized="teacher",
        phone_e164=None,
        display_name="教师",
        password_hash="hash",
    )
    repo.deactivate_user(kg_a, user.id)
    deactivated = repo.get_user_by_id(kg_a, user.id)
    assert deactivated is not None
    assert deactivated.is_active is False


def test_role_code_is_globally_unique(repo: IdentityRepository) -> None:
    from sqlalchemy.exc import IntegrityError

    unique_code = f"role-{uuid4().hex[:8]}"
    role = repo.create_role(code=unique_code, name="唯一角色")
    assert role is not None
    with pytest.raises(IntegrityError):
        repo.create_role(code=unique_code, name="重复角色")


def test_refresh_family_revoke_returns_count(repo: IdentityRepository, kg_a: str) -> None:
    assert repo.revoke_refresh_family(kg_a, str(uuid4())) >= 0


def test_revoke_user_tokens_returns_count(repo: IdentityRepository, kg_a: str) -> None:
    assert repo.revoke_user_tokens(kg_a, str(uuid4())) >= 0


def _make_user(repo: IdentityRepository, kindergarten_id: str, username: str) -> str:
    user = repo.create_user(
        kindergarten_id=kindergarten_id,
        username=username,
        username_normalized=username,
        phone_e164=None,
        display_name=username,
        password_hash="hash",
    )
    return user.id


def test_refresh_token_crud_with_family_expires_at(db_repo: IdentityRepository) -> None:
    from datetime import UTC, datetime, timedelta

    kg = db_repo.create_kindergarten(name="Refresh测试园")
    kg_id = str(kg.id)
    user_id = _make_user(db_repo, kg_id, "user1")
    family_id = str(uuid4())
    token_hash = "hash-1"
    expires = datetime.now(UTC) + timedelta(days=7)

    token = db_repo.create_refresh_token(
        kindergarten_id=kg_id,
        user_id=user_id,
        token_family_id=family_id,
        token_hash=token_hash,
        expires_at=expires,
        family_expires_at=expires,
    )
    assert token.family_expires_at == expires

    found = db_repo.find_refresh_token_by_hash(kg_id, token_hash)
    assert found is not None
    assert found.token_family_id == family_id

    count = db_repo.revoke_refresh_family(kg_id, family_id)
    assert count == 1

    revoked = db_repo.find_refresh_token_by_hash(kg_id, token_hash)
    assert revoked is not None
    assert revoked.revoked_at is not None


def test_find_refresh_token_by_hash_for_update(db_repo: IdentityRepository) -> None:
    from datetime import UTC, datetime, timedelta

    kg = db_repo.create_kindergarten(name="Refresh测试园2")
    kg_id = str(kg.id)
    user_id = _make_user(db_repo, kg_id, "user2")
    family_id = str(uuid4())
    token_hash = "hash-2"
    expires = datetime.now(UTC) + timedelta(days=7)

    db_repo.create_refresh_token(
        kindergarten_id=kg_id,
        user_id=user_id,
        token_family_id=family_id,
        token_hash=token_hash,
        expires_at=expires,
        family_expires_at=expires,
    )

    found = db_repo.find_refresh_token_by_hash_for_update(kg_id, token_hash)
    assert found is not None
    assert found.token_hash == token_hash


def test_refresh_token_revoke_respects_kindergarten_id(
    db_repo: IdentityRepository, kg_a: str, kg_b: str
) -> None:
    from datetime import UTC, datetime, timedelta

    user_id = _make_user(db_repo, kg_a, "user3")
    family_id = str(uuid4())
    token_hash = "hash-3"
    expires = datetime.now(UTC) + timedelta(days=7)

    db_repo.create_refresh_token(
        kindergarten_id=kg_a,
        user_id=user_id,
        token_family_id=family_id,
        token_hash=token_hash,
        expires_at=expires,
        family_expires_at=expires,
    )

    assert db_repo.revoke_refresh_family(kg_b, family_id) == 0
    assert db_repo.revoke_user_tokens(kg_b, user_id) == 0
    assert db_repo.find_refresh_token_by_hash(kg_b, token_hash) is None

    token = db_repo.find_refresh_token_by_hash(kg_a, token_hash)
    assert token is not None
    assert token.revoked_at is None


def test_refresh_token_rejects_cross_kindergarten_user(
    db_repo: IdentityRepository, kg_a: str, kg_b: str
) -> None:
    """Refresh token 的组合外键拒绝 (其他园 kindergarten_id, 本园 user_id) 的孤儿行。"""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy.exc import IntegrityError

    user = db_repo.create_user(
        kindergarten_id=kg_a,
        username="orphan_user",
        username_normalized="orphan_user",
        phone_e164=None,
        display_name="孤儿用户",
        password_hash="hash",
    )
    family_id = str(uuid4())
    token_hash = "hash-orphan"
    expires = datetime.now(UTC) + timedelta(days=7)

    with pytest.raises(IntegrityError):
        db_repo.create_refresh_token(
            kindergarten_id=kg_b,
            user_id=user.id,
            token_family_id=family_id,
            token_hash=token_hash,
            expires_at=expires,
            family_expires_at=expires,
        )
