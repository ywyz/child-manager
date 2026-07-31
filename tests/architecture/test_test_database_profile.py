"""测试数据库档位的安全加载合同。"""

from pathlib import Path

import pytest

from tests import database_config
from tests.database_config import require_test_database_url

TEST_DATABASE_URL = (
    "postgresql+psycopg://child_manager:test-only@127.0.0.1:15432/child_manager_dev_test"
)
CI_DATABASE_URL = "postgresql+psycopg://child_manager:test-only@127.0.0.1:5432/child_manager_ci"


def _write_profile(path: Path, value: str, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{value}\n", encoding="utf-8")
    path.chmod(mode)


def test_test_database_url_uses_secure_repo_external_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "child-manager" / "test-database-url"
    _write_profile(profile_path, TEST_DATABASE_URL)
    monkeypatch.delenv("CHILD_MANAGER_TEST_DATABASE_URL", raising=False)
    monkeypatch.delenv("CHILD_MANAGER_TEST_DATABASE_URL_FILE", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    loaded = require_test_database_url()

    assert str(loaded) == TEST_DATABASE_URL
    assert "test-only" not in repr(loaded)


def test_environment_test_database_url_takes_precedence_over_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "test-database-url"
    _write_profile(profile_path, TEST_DATABASE_URL)
    monkeypatch.setenv("CHILD_MANAGER_TEST_DATABASE_URL_FILE", str(profile_path))
    monkeypatch.setenv("CHILD_MANAGER_TEST_DATABASE_URL", CI_DATABASE_URL)

    assert str(require_test_database_url()) == CI_DATABASE_URL


def test_test_database_profile_rejects_group_or_other_access(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "test-database-url"
    _write_profile(profile_path, TEST_DATABASE_URL, mode=0o644)
    monkeypatch.delenv("CHILD_MANAGER_TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("CHILD_MANAGER_TEST_DATABASE_URL_FILE", str(profile_path))

    with pytest.raises(RuntimeError, match="权限必须为 0600"):
        require_test_database_url()


def test_test_database_profile_must_stay_outside_the_repository(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repository_root = tmp_path / "repository"
    profile_path = repository_root / "test-database-url"
    _write_profile(profile_path, TEST_DATABASE_URL)
    monkeypatch.setattr(
        database_config,
        "_REPOSITORY_ROOT",
        repository_root,
        raising=False,
    )
    monkeypatch.delenv("CHILD_MANAGER_TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("CHILD_MANAGER_TEST_DATABASE_URL_FILE", str(profile_path))

    with pytest.raises(RuntimeError, match="仓库外"):
        require_test_database_url()


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg://child_manager:test-only@127.0.0.1:15432/child_manager_dev",
        "sqlite:///child_manager_dev_test.db",
    ],
)
def test_test_database_url_rejects_nonisolated_or_nonpostgresql_targets(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_TEST_DATABASE_URL", database_url)

    with pytest.raises(RuntimeError, match="隔离的 PostgreSQL 测试数据库"):
        require_test_database_url()


def test_test_database_url_reports_missing_environment_and_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing_profile = tmp_path / "missing-test-database-url"
    monkeypatch.delenv("CHILD_MANAGER_TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("CHILD_MANAGER_TEST_DATABASE_URL_FILE", str(missing_profile))

    with pytest.raises(
        RuntimeError,
        match=r"CHILD_MANAGER_TEST_DATABASE_URL.*CHILD_MANAGER_TEST_DATABASE_URL_FILE",
    ):
        require_test_database_url()
