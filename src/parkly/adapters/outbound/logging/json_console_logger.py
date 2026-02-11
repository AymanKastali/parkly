import logging
from typing import Any

from loggerizer import LoggerBuilder, LogLevel, handlers
from loggerizer.enums import LogField
from loggerizer.formatters import JsonFormatter

from parkly.adapters.context import request_context
from parkly.application.port.logger import Logger


class JsonConsoleLogger(Logger):
    def __init__(self, name: str = "parkly", level: LogLevel = LogLevel.DEBUG) -> None:
        self._logger: logging.Logger = (
            LoggerBuilder()
            .name(name)
            .level(level)
            .handler(handlers.stream())
            .formatter(
                JsonFormatter(
                    fields=[
                        LogField.ASC_TIME,
                        LogField.LEVEL_NAME,
                        LogField.NAME,
                        LogField.MESSAGE,
                        LogField.FILE_NAME,
                        LogField.FUNC_NAME,
                        LogField.LINE_NO,
                    ]
                )
            )
            .build()
        )

    def _enrich(self, extra: dict[str, Any] | None) -> dict[str, Any]:
        enriched: dict[str, Any] = dict(request_context.get())
        if extra:
            enriched.update(extra)
        return enriched

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.debug(message, extra=self._enrich(extra))

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.info(message, extra=self._enrich(extra))

    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.warning(message, extra=self._enrich(extra))

    def error(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.error(message, extra=self._enrich(extra))
