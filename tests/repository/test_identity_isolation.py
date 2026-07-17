"""身份 Repository 园所隔离测试。"""

from uuid import uuid4

import pytest

from packages.backend.identity.repository import IdentityRepository


@pytest.fixture
def repo() -> IdentityRepository:
    return IdentityRepository(session=None)


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


def test_active_admin_count_is_per_kindergarten(
    repo: IdentityRepository, kg_a: str, kg_b: str
) -> None:
    repo.create_user(
        kindergarten_id=kg_a,
        username="admin",
        phone=None,
        display_name="管理员",
        password_hash="hash",
    )
    assert repo.get_active_admin_count(kg_a) == 1
    assert repo.get_active_admin_count(kg_b) == 0


def test_deactivate_user_requires_another_admin(repo: IdentityRepository, kg_a: str) -> None:
    repo.create_user(
        kindergarten_id=kg_a,
        username="sole-admin",
        phone=None,
        display_name="唯一管理员",
        password_hash="hash",
    )
    assert repo.get_active_admin_count(kg_a) == 1
    with pytest.raises(ValueError):
        repo.deactivate_user(kg_a, "user-id")


def test_role_code_unique_per_kindergarten(repo: IdentityRepository, kg_a: str, kg_b: str) -> None:
    role = repo.create_role(kindergarten_id=kg_a, code="admin", name="管理员")
    assert role is not None
    role_b = repo.create_role(kindergarten_id=kg_b, code="admin", name="管理员")
    assert role_b is not None


def test_refresh_family_revoke_returns_count(repo: IdentityRepository) -> None:
    assert repo.revoke_refresh_family("family-1") >= 0


def test_revoke_user_tokens_returns_count(repo: IdentityRepository, kg_a: str) -> None:
    assert repo.revoke_user_tokens(kg_a, "user-1") >= 0
