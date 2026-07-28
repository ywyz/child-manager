"""测试数据库的显式档位配置。"""

import os


class SensitiveDatabaseUrl(str):
    """保留连接字符串行为，但禁止失败报告通过 ``repr`` 展开凭据。"""

    def __repr__(self) -> str:
        return "'<redacted test database URL>'"


def require_test_database_url() -> SensitiveDatabaseUrl:
    """返回测试数据库 URL；禁止静默回退到共享数据库。"""

    value = os.environ.get("CHILD_MANAGER_TEST_DATABASE_URL")
    if not value:
        raise RuntimeError("必须设置 CHILD_MANAGER_TEST_DATABASE_URL 并指向隔离测试数据库")
    return SensitiveDatabaseUrl(value)
