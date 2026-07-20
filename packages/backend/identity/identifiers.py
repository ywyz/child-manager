"""用户名、手机号等身份标识规范化。"""

import re
import unicodedata

_USERNAME_MAX_LENGTH = 120


def normalize_username(value: str) -> str:
    """返回规范化用户名：NFKC、去首尾空白、小写。

    在统一边界校验 NFKC 规范化后非空与长度 <=120，避免组合字符
    （如 U+FB03 ``ﬃ`` 经 NFKC 展开为 ``ffi``）把原长 <=120 的合法契约输入
    扩长为 >120 的值，写入 ``VARCHAR(120)`` 列时被数据库拒绝并把 DataError
    外泄为 500。create/update/init/login 均经过此边界，行为一致。

    冻结 Schema（``data-model.md`` §5.2）只要求 NFKC+trim+lower 和长度边界；
    不限制字符集，以保证 0006 迁移保留的 Unicode 旧用户名（如 ``教师``）
    升级后仍能登录（T029）。
    """
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    if not normalized:
        msg = "用户名不能为空"
        raise ValueError(msg)
    if len(normalized) > _USERNAME_MAX_LENGTH:
        msg = f"用户名长度不能超过 {_USERNAME_MAX_LENGTH} 字符"
        raise ValueError(msg)
    return normalized


def normalize_phone(value: str | None) -> str | None:
    """返回 E.164 手机号或空值；当前只接受中国大陆手机号。"""
    if value is None:
        return None
    cleaned = value.strip().replace(" ", "").replace("-", "")
    if cleaned == "":
        return None

    if cleaned.startswith("+"):
        digits = cleaned
    else:
        digits = "+86" + cleaned

    if not re.fullmatch(r"\+86[1-9]\d{10}", digits):
        msg = "手机号格式无效"
        raise ValueError(msg)
    return digits
