from abc import ABC, abstractmethod
from datetime import datetime


class DatabaseSessionPort(ABC):
    @abstractmethod
    def begin(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def close(self):
        pass


class ClockPort(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def utc_now(self) -> datetime:
        pass


class CalendarPort(ABC):
    @abstractmethod
    def is_workday(self, date: str, kindergarten_id: str) -> bool:
        pass


class AIClientPort(ABC):
    @abstractmethod
    def generate(
        self, prompt: str, variables: dict[str, object], model_name: str
    ) -> dict[str, object]:
        pass


class RedisPort(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    def set(self, key: str, value: str, expire_seconds: int | None = None):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass


class AuditPort(ABC):
    @abstractmethod
    def record(
        self, event_type: str, user_id: str, user_name: str, kindergarten_id: str, **kwargs: object
    ):
        pass


class CryptoPort(ABC):
    @abstractmethod
    def encrypt(self, plaintext: bytes, associated_data: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes, associated_data: bytes) -> bytes:
        pass
