"""固定工作日替身。"""

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class FakeCalendar:
    values: dict[date, bool | None] = field(default_factory=dict)

    def is_workday(self, value: date) -> bool | None:
        return self.values.get(value)
