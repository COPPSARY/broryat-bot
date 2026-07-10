import asyncio
from typing import Any

from telegram import Message

THINKING = {"en": "🤔 Thinking...", "km": "🤔 កំពុងគិត..."}
ANALYZING = {"en": "🔍 Analyzing...", "km": "🔍 កំពុងវិភាគ..."}


async def run_with_progress(
    message: Message, coroutine, language: str, threshold: float = 3.0
) -> tuple[Message, Any]:
    placeholder = await message.reply_text(THINKING[language])
    task = asyncio.ensure_future(coroutine)

    done, _ = await asyncio.wait([task], timeout=threshold)
    if task not in done:
        await placeholder.edit_text(ANALYZING[language])
        await task

    return placeholder, task.result()
