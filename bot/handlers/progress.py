import asyncio
from typing import Any

from telegram import Message
from telegram.error import BadRequest

THINKING = {"en": "🤔 Thinking...", "km": "🤔 កំពុងគិត..."}
ANALYZING = {"en": "🔍 Analyzing...", "km": "🔍 កំពុងវិភាគ..."}


async def send_placeholder(message: Message, language: str) -> Message:
    return await message.reply_text(THINKING[language])


async def track_progress(
    placeholder: Message, coroutine, language: str, threshold: float = 3.0
) -> Any:
    task = asyncio.ensure_future(coroutine)

    labels = (ANALYZING[language], THINKING[language])
    i = 0
    while True:
        done, _ = await asyncio.wait([task], timeout=threshold)
        if task in done:
            break
        try:
            await placeholder.edit_text(labels[i % 2])
        except BadRequest:
            pass
        i += 1

    return task.result()


async def run_with_progress(
    message: Message, coroutine, language: str, threshold: float = 3.0
) -> tuple[Message, Any]:
    placeholder = await send_placeholder(message, language)
    result = await track_progress(placeholder, coroutine, language, threshold)
    return placeholder, result
