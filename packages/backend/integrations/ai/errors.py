"""供应商中立、稳定且脱敏的 AI 错误。"""


class AiClientError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
