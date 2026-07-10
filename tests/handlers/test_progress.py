import asyncio
from unittest.mock import AsyncMock

from bot.handlers.progress import ANALYZING, THINKING, run_with_progress


def _message(placeholder):
    message = AsyncMock()
    message.reply_text.return_value = placeholder
    return message


async def test_sends_thinking_placeholder_in_the_given_language():
    placeholder = AsyncMock()
    message = _message(placeholder)

    async def fast_coroutine():
        return "done"

    await run_with_progress(message, fast_coroutine(), "km", threshold=1.0)

    message.reply_text.assert_awaited_once_with(THINKING["km"])


async def test_returns_the_placeholder_and_the_coroutine_result():
    placeholder = AsyncMock()
    message = _message(placeholder)

    async def fast_coroutine():
        return "the-result"

    returned_placeholder, result = await run_with_progress(message, fast_coroutine(), "en", threshold=1.0)

    assert returned_placeholder is placeholder
    assert result == "the-result"


async def test_does_not_edit_to_analyzing_when_coroutine_finishes_before_threshold():
    placeholder = AsyncMock()
    message = _message(placeholder)

    async def fast_coroutine():
        return "done"

    await run_with_progress(message, fast_coroutine(), "en", threshold=10.0)

    placeholder.edit_text.assert_not_awaited()


async def test_edits_to_analyzing_when_coroutine_is_still_running_after_threshold():
    placeholder = AsyncMock()
    message = _message(placeholder)
    release = asyncio.Event()

    async def slow_coroutine():
        await release.wait()
        return "done"

    task = asyncio.create_task(run_with_progress(message, slow_coroutine(), "en", threshold=0.0))
    for _ in range(10):
        if placeholder.edit_text.await_count:
            break
        await asyncio.sleep(0)
    release.set()
    await task

    placeholder.edit_text.assert_awaited_once_with(ANALYZING["en"])
