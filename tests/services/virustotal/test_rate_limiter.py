import asyncio

import pytest

from bot.services.virustotal.rate_limiter import VTRateLimiter


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def time(self) -> float:
        return self.t

    async def sleep(self, seconds: float) -> None:
        self.t += seconds


@pytest.fixture
def clock():
    return FakeClock()


async def test_allows_calls_up_to_rpm_limit_without_waiting(clock):
    limiter = VTRateLimiter(
        rpm_limit=4, daily_limit=500, monthly_limit=15500, time_func=clock.time, sleep_func=clock.sleep
    )
    for _ in range(4):
        await limiter.acquire()
    assert clock.t == 0.0


async def test_fifth_call_within_minute_waits_for_window_to_free_up(clock):
    limiter = VTRateLimiter(
        rpm_limit=4, daily_limit=500, monthly_limit=15500, time_func=clock.time, sleep_func=clock.sleep
    )
    for _ in range(4):
        await limiter.acquire()

    await limiter.acquire()

    assert clock.t >= 60.0


async def test_never_exceeds_rpm_limit_in_any_rolling_60s_window(clock):
    limiter = VTRateLimiter(
        rpm_limit=4, daily_limit=500, monthly_limit=15500, time_func=clock.time, sleep_func=clock.sleep
    )
    call_times: list[float] = []
    for _ in range(12):
        await limiter.acquire()
        call_times.append(clock.t)

    for i in range(len(call_times)):
        window_start = call_times[i]
        count_in_window = sum(1 for t in call_times if window_start <= t < window_start + 60)
        assert count_in_window <= 4


async def test_daily_limit_forces_a_wait_once_exhausted(clock):
    limiter = VTRateLimiter(
        rpm_limit=1000, daily_limit=2, monthly_limit=15500, time_func=clock.time, sleep_func=clock.sleep
    )
    await limiter.acquire()
    await limiter.acquire()

    await limiter.acquire()

    assert clock.t >= 86400.0


async def test_acquire_is_safe_under_concurrent_callers(clock):
    limiter = VTRateLimiter(
        rpm_limit=4, daily_limit=500, monthly_limit=15500, time_func=clock.time, sleep_func=clock.sleep
    )
    await asyncio.gather(*(limiter.acquire() for _ in range(8)))
    assert clock.t >= 60.0


def test_stats_reports_current_window_usage(clock):
    limiter = VTRateLimiter(
        rpm_limit=4, daily_limit=500, monthly_limit=15500, time_func=clock.time, sleep_func=clock.sleep
    )
    stats = limiter.stats()
    assert stats == {"minute": 0, "day": 0, "month": 0}
