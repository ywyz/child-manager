from unittest.mock import AsyncMock

import pytest


class MockRedisClient:
    def __init__(self) -> None:
        self.ping = AsyncMock(return_value=True)
        self.get = AsyncMock(return_value=b"mock")
        self.set = AsyncMock(return_value=True)
        self.delete = AsyncMock(return_value=1)


@pytest.fixture
def mock_redis_client() -> MockRedisClient:
    return MockRedisClient()
