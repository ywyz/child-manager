"""身份域异常。

这些异常不依赖任何 HTTP 传输类型，由 API 层捕获后转换为 HTTP 响应。
"""


class IdentityError(Exception):
    """身份域错误基类，携带稳定错误码、中文消息与 HTTP 状态码。"""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class LastAdminError(IdentityError):
    """操作会移除最后一个有效管理员时抛出。"""

    def __init__(self, message: str = "不能移除最后一个有效管理员") -> None:
        super().__init__("auth.last_admin_protected", message, status_code=409)


class UserNotFoundError(IdentityError):
    """目标用户不存在时抛出。"""

    def __init__(self, message: str = "用户不存在") -> None:
        super().__init__("resource.not_found", message, status_code=404)


class LoginFailedError(IdentityError):
    """用户名/密码或手机号/密码不匹配时抛出。"""

    def __init__(self, message: str = "账号或密码错误") -> None:
        super().__init__("auth.login_failed", message, status_code=401)


class ChangePasswordFailedError(IdentityError):
    """修改密码时原密码校验失败。"""

    def __init__(self, message: str = "原密码错误") -> None:
        super().__init__("auth.login_failed", message, status_code=401)


class UnauthenticatedError(IdentityError):
    """请求缺少有效身份凭证时抛出。"""

    def __init__(self, message: str = "会话已失效") -> None:
        super().__init__("auth.unauthenticated", message, status_code=401)


class ForbiddenError(IdentityError):
    """已认证但无权限时抛出。"""

    def __init__(self, message: str = "没有访问权限") -> None:
        super().__init__("auth.forbidden", message, status_code=403)


class LoginRateLimitedError(IdentityError):
    """登录请求被限流时抛出。"""

    def __init__(self, message: str = "登录尝试过于频繁") -> None:
        super().__init__("auth.login_rate_limited", message, status_code=429)


class ConflictError(IdentityError):
    """资源唯一性冲突时抛出。"""

    def __init__(self, message: str = "资源已存在") -> None:
        super().__init__("resource.conflict", message, status_code=409)
