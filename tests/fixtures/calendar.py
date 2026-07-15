from unittest.mock import MagicMock

import pytest


class MockCalendar:
    def __init__(self) -> None:
        self.is_workday = MagicMock(return_value=True)


@pytest.fixture
def mock_calendar() -> MockCalendar:
    return MockCalendar()