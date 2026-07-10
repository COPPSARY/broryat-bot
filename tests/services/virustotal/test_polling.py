from unittest.mock import AsyncMock

import pytest

from bot.schemas.virustotal import VTFileVerdict
from bot.services.virustotal.polling import poll_until_complete


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def time(self) -> float:
        return self.t

    async def sleep(self, seconds: float) -> None:
        self.t += seconds


async def test_returns_immediately_when_first_check_is_complete():
    clock = FakeClock()
    client_get = AsyncMock(return_value=VTFileVerdict(sha256="a" * 64, status="malicious", malicious_count=1))

    result = await poll_until_complete(
        client_get, interval=15, timeout=180, time_func=clock.time, sleep_func=clock.sleep
    )

    assert result.status == "malicious"
    client_get.assert_awaited_once()


async def test_polls_until_status_is_no_longer_pending():
    clock = FakeClock()
    responses = [
        VTFileVerdict(sha256="a" * 64, status="pending"),
        VTFileVerdict(sha256="a" * 64, status="pending"),
        VTFileVerdict(sha256="a" * 64, status="clean", total_engines=70),
    ]
    client_get = AsyncMock(side_effect=responses)

    result = await poll_until_complete(
        client_get, interval=15, timeout=180, time_func=clock.time, sleep_func=clock.sleep
    )

    assert result.status == "clean"
    assert client_get.await_count == 3
    assert clock.t == 30.0


async def test_returns_pending_verdict_on_timeout():
    clock = FakeClock()
    client_get = AsyncMock(return_value=VTFileVerdict(sha256="a" * 64, status="pending"))

    result = await poll_until_complete(
        client_get, interval=15, timeout=40, time_func=clock.time, sleep_func=clock.sleep
    )

    assert result.status == "pending"
