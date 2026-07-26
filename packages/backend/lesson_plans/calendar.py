"""不依赖框架、数据库或网络的教案日期规则。"""

from datetime import date, timedelta

_WEEKDAYS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
_CHINESE_DIGITS = "零一二三四五六七八九"


def _chinese_number(value: int) -> str:
    if value < 10:
        return _CHINESE_DIGITS[value]
    if value < 20:
        return "十" + (_CHINESE_DIGITS[value % 10] if value % 10 else "")
    tens, ones = divmod(value, 10)
    return _CHINESE_DIGITS[tens] + "十" + (_CHINESE_DIGITS[ones] if ones else "")


def teaching_week(
    plan_date: date,
    semester_start: date,
    semester_end: date,
) -> tuple[int | None, str | None]:
    if not semester_start <= plan_date <= semester_end:
        return None, None
    first_monday = semester_start - timedelta(days=semester_start.weekday())
    number = ((plan_date - first_monday).days // 7) + 1
    return number, f"第（{_chinese_number(number)}）周"


def activity_date_text(value: date) -> str:
    weekday = _WEEKDAYS[value.weekday()].removeprefix("星期")
    return f"周（{weekday}）{value.month}月{value.day}日"


def season_for(value: date) -> str:
    if value.month in (3, 4, 5):
        return "spring"
    if value.month in (6, 7, 8):
        return "summer"
    if value.month in (9, 10, 11):
        return "autumn"
    return "winter"
