from abc import ABC, abstractmethod
from typing import Any


class Logger(ABC):
    @abstractmethod
    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None: ...

    @abstractmethod
    def info(self, message: str, extra: dict[str, Any] | None = None) -> None: ...

    @abstractmethod
    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None: ...

    @abstractmethod
    def error(self, message: str, extra: dict[str, Any] | None = None) -> None: ...
