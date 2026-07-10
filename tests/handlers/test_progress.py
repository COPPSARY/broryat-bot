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

    task = asyncio.create_task(run_with_progress(message, slow_coroutine(), "en", threshold=0.01))
    for _ in range(50):
        if placeholder.edit_text.await_count:
            break
        await asyncio.sleep(0.01)
    release.set()
    await task

    assert placeholder.edit_text.await_args_list[0].args[0] == ANALYZING["en"]


async def test_loops_between_analyzing_and_thinking_while_still_running():
    placeholder = AsyncMock()
    message = _message(placeholder)
    release = asyncio.Event()

    async def slow_coroutine():
        await release.wait()
        return "done"

    task = asyncio.create_task(run_with_progress(message, slow_coroutine(), "en", threshold=0.01))
    for _ in range(200):
        if placeholder.edit_text.await_count >= 2:
            break
        await asyncio.sleep(0.01)
    release.set()
    await task

    calls = [c.args[0] for c in placeholder.edit_text.await_args_list]
    assert calls[0] == ANALYZING["en"]
    assert calls[1] == THINKING["en"]


async def test_stops_editing_once_coroutine_completes():
    placeholder = AsyncMock()
    message = _message(placeholder)
    release = asyncio.Event()

    async def slow_coroutine():
        await release.wait()
        return "done"

    task = asyncio.create_task(run_with_progress(message, slow_coroutine(), "en", threshold=0.01))
    for _ in range(50):
        if placeholder.edit_text.await_count:
            break
        await asyncio.sleep(0.01)
    release.set()
    await task

    count_after_completion = placeholder.edit_text.await_count
    await asyncio.sleep(0.05)
    assert placeholder.edit_text.await_count == count_after_completion
