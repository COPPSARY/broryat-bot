import asyncio
import time
from collections.abc import Awaitable, Callable, Coroutine
from typing import TypeVar

from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict

_Verdict = TypeVar("_Verdict", VTFileVerdict, VTUrlVerdict)


async def poll_until_complete(
    fetch: Callable[[], Coroutine[None, None, _Verdict]],
    interval: float = 15,
    timeout: float = 180,
    time_func: Callable[[], float] = time.monotonic,
    sleep_func: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> _Verdict:
    start = time_func()
    verdict = await fetch()

    while verdict.status == "pending" and (time_func() - start) < timeout:
        await sleep_func(interval)
        verdict = await fetch()

    return verdict
