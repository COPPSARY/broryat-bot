import asyncio
import logging
import time
from collections import deque
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

_MINUTE = 60.0
_DAY = 86400.0
_MONTH = 2678400.0

_WAIT_WARNING_THRESHOLD_SECONDS = 2.0


class VTRateLimiter:
    def __init__(
        self,
        rpm_limit: int,
        daily_limit: int,
        monthly_limit: int,
        time_func: Callable[[], float] = time.monotonic,
        sleep_func: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self._rpm_limit = rpm_limit
        self._daily_limit = daily_limit
        self._monthly_limit = monthly_limit
        self._time = time_func
        self._sleep = sleep_func
        self._lock = asyncio.Lock()
        self._minute_window: deque[float] = deque()
        self._day_window: deque[float] = deque()
        self._month_window: deque[float] = deque()

    def _prune(self, now: float) -> None:
        while self._minute_window and self._minute_window[0] <= now - _MINUTE:
            self._minute_window.popleft()
        while self._day_window and self._day_window[0] <= now - _DAY:
            self._day_window.popleft()
        while self._month_window and self._month_window[0] <= now - _MONTH:
            self._month_window.popleft()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = self._time()
                self._prune(now)

                wait_candidates = []
                if len(self._minute_window) >= self._rpm_limit:
                    wait_candidates.append(self._minute_window[0] + _MINUTE - now)
                if len(self._day_window) >= self._daily_limit:
                    wait_candidates.append(self._day_window[0] + _DAY - now)
                if len(self._month_window) >= self._monthly_limit:
                    wait_candidates.append(self._month_window[0] + _MONTH - now)

                if not wait_candidates:
                    break

                wait_seconds = max(wait_candidates)
                if wait_seconds > _WAIT_WARNING_THRESHOLD_SECONDS:
                    logger.warning("VirusTotal rate limit reached; waiting %.1fs", wait_seconds)
                await self._sleep(wait_seconds)

            now = self._time()
            self._minute_window.append(now)
            self._day_window.append(now)
            self._month_window.append(now)

    def stats(self) -> dict[str, int]:
        now = self._time()
        self._prune(now)
        return {
            "minute": len(self._minute_window),
            "day": len(self._day_window),
            "month": len(self._month_window),
        }
