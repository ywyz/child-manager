"""固定时钟替身。"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value
