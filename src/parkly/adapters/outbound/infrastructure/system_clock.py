from datetime import UTC, datetime

from parkly.domain.port.clock import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)
