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
def kg_a() -> str:
    return str(uuid4())


@pytest.fixture
def kg_b() -> str:
    return str(uuid4())


def test_create_and_retrieve_kindergarten(repo: IdentityRepository, kg_a: str) -> None:
    kg = repo.create_kindergarten(name="阳光幼儿园")
    assert kg is not None
    assert kg.name == "阳光幼儿园"


def test_kindergarten_isolation(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    repo.create_kindergarten(name="A园")
    assert repo.get_kindergarten_by_id(kg_b) is None


def test_user_isolation(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    repo.create_user(
        kindergarten_id=kg_a,
        username="admin",
        phone=None,
        display_name="管理员",
        password_hash="hash",
    )
    assert repo.get_user_by_username(kg_b, "admin") is None
    assert repo.list_users(kg_b) == []


def test_phone_isolation(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    repo.create_user(
        kindergarten_id=kg_a,
        username="teacher",
        phone="+8613800000000",
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
    role = repo.create_role(kindergarten_id=kg_a, code="admin", name="管理员")
    user = repo.create_user(
        kindergarten_id=kg_a,
        username="admin",
        phone=None,
        display_name="管理员",
        password_hash="hash",
    )
    repo.assign_role(kindergarten_id=kg_a, user_id=user.id, role_id=role.id)
    assert repo.get_active_admin_count(kg_a) == 1
    assert repo.get_active_admin_count(kg_b) == 0


def test_deactivate_user_sets_is_active_false(repo: IdentityRepository, kg_a: str) -> None:
    user = repo.create_user(
        kindergarten_id=kg_a,
        username="teacher",
        phone=None,
        display_name="教师",
        password_hash="hash",
    )
    repo.deactivate_user(kg_a, user.id)
    deactivated = repo.get_user_by_id(kg_a, user.id)
    assert deactivated is not None
    assert deactivated.is_active is False


def test_role_code_unique_per_kindergarten(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    role = repo.create_role(kindergarten_id=kg_a, code="admin", name="管理员")
    assert role is not None
    role_b = repo.create_role(kindergarten_id=kg_b, code="admin", name="管理员")
    assert role_b is not None


def test_refresh_family_revoke_returns_count(repo: IdentityRepository, kg_a: str) -> None:
    assert repo.revoke_refresh_family(kg_a, "family-1") >= 0


def test_revoke_user_tokens_returns_count(repo: IdentityRepository, kg_a: str) -> None:
    assert repo.revoke_user_tokens(kg_a, "user-1") >= 0


def test_refresh_token_crud_with_family_expires_at(db_repo: IdentityRepository) -> None:
    from datetime import UTC, datetime, timedelta

    kg_id = str(uuid4())
    user_id = str(uuid4())
    family_id = str(uuid4())
    token_hash = "hash-1"
    expires = datetime.now(UTC) + timedelta(days=7)

    token = db_repo.create_refresh_token(
        kindergarten_id=kg_id,
        user_id=user_id,
        family_id=family_id,
        token_hash=token_hash,
        expires_at=expires,
        family_expires_at=expires,
    )
    assert token.family_expires_at == expires

    found = db_repo.find_refresh_token_by_hash(kg_id, token_hash)
    assert found is not None
    assert found.family_id == family_id

    count = db_repo.revoke_refresh_family(kg_id, family_id)
    assert count == 1

    revoked = db_repo.find_refresh_token_by_hash(kg_id, token_hash)
    assert revoked is not None
    assert revoked.revoked_at is not None


def test_find_refresh_token_by_hash_for_update(db_repo: IdentityRepository) -> None:
    from datetime import UTC, datetime, timedelta

    kg_id = str(uuid4())
    user_id = str(uuid4())
    family_id = str(uuid4())
    token_hash = "hash-2"
    expires = datetime.now(UTC) + timedelta(days=7)

    db_repo.create_refresh_token(
        kindergarten_id=kg_id,
        user_id=user_id,
        family_id=family_id,
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

    user_id = str(uuid4())
    family_id = str(uuid4())
    token_hash = "hash-3"
    expires = datetime.now(UTC) + timedelta(days=7)

    db_repo.create_refresh_token(
        kindergarten_id=kg_a,
        user_id=user_id,
        family_id=family_id,
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
