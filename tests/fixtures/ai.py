from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest


class MockAiClient:
    def __init__(self) -> None:
        self.generate = AsyncMock(return_value={"content": "mock response"})


@pytest.fixture
def mock_ai_client() -> Iterator[MockAiClient]:
    yield MockAiClient()
