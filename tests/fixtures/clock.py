from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import patch

import pytest


@pytest.fixture
def fixed_datetime() -> Iterator[None]:
    fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.utcnow.return_value = fixed_time
        mock_datetime.side_effect = datetime
        yield None
