"""测试数据库的显式档位配置。"""

import os
import stat
from pathlib import Path
from urllib.parse import unquote, urlsplit

TEST_DATABASE_URL_ENV = "CHILD_MANAGER_TEST_DATABASE_URL"
TEST_DATABASE_URL_FILE_ENV = "CHILD_MANAGER_TEST_DATABASE_URL_FILE"
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SensitiveDatabaseUrl(str):
    """保留连接字符串行为，但禁止失败报告通过 ``repr`` 展开凭据。"""

    def __repr__(self) -> str:
        return "'<redacted test database URL>'"


def _default_profile_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    root = Path(config_home) if config_home else Path.home() / ".config"
    return root / "child-manager" / "test-database-url"


def _load_profile(path: Path) -> str:
    try:
        metadata = path.lstat()
    except FileNotFoundError as error:
        raise RuntimeError(
            f"必须设置 {TEST_DATABASE_URL_ENV}，或由 "
            f"{TEST_DATABASE_URL_FILE_ENV} 指向权限为 0600 的仓库外档位文件"
        ) from error

    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError("测试数据库档位必须是普通文件，且不得使用符号链接")
    if path.resolve().is_relative_to(_REPOSITORY_ROOT):
        raise RuntimeError("测试数据库档位文件必须位于仓库外")
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise RuntimeError("测试数据库档位文件权限必须为 0600")
    if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
        raise RuntimeError("测试数据库档位文件必须属于当前用户")

    value = path.read_text(encoding="utf-8").strip()
    if not value or "\n" in value or "\r" in value:
        raise RuntimeError("测试数据库档位文件必须只包含一行非空连接字符串")
    return value


def _validate_isolated_postgresql_url(value: str) -> None:
    parsed = urlsplit(value)
    database_name = unquote(parsed.path).removeprefix("/")
    if (
        parsed.scheme not in {"postgresql", "postgresql+psycopg"}
        or not database_name
        or "/" in database_name
        or not database_name.endswith(("_test", "_ci"))
    ):
        raise RuntimeError("测试数据库 URL 必须指向隔离的 PostgreSQL 测试数据库")


def require_test_database_url() -> SensitiveDatabaseUrl:
    """返回测试数据库 URL；禁止静默回退到共享数据库。"""

    value = os.environ.get(TEST_DATABASE_URL_ENV)
    if not value:
        profile_path = Path(
            os.environ.get(TEST_DATABASE_URL_FILE_ENV, str(_default_profile_path()))
        ).expanduser()
        value = _load_profile(profile_path)
    _validate_isolated_postgresql_url(value)
    return SensitiveDatabaseUrl(value)
