import os


def require_test_database_url() -> str:
    value = os.environ.get("CHILD_MANAGER_TEST_DATABASE_URL")
    if value:
        return value
    return "sqlite+aiosqlite:///:memory:"
