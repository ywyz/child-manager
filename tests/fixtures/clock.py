from datetime import datetime, timezone
from unittest.mock import patch

import pytest


@pytest.fixture
def fixed_datetime() -> None:
    fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.utcnow.return_value = fixed_time
        mock_datetime.side_effect = datetime
        yield