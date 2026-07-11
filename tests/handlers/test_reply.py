from unittest.mock import AsyncMock

import pytest
from telegram.constants import ParseMode
from telegram.error import BadRequest

from bot.handlers.reply import reply_with_markdown


async def test_sends_with_markdown_parse_mode():
    message = AsyncMock()

    await reply_with_markdown(message, "*bold* text")

    message.reply_text.assert_awaited_once_with("*bold* text", parse_mode=ParseMode.MARKDOWN)


async def test_returns_the_sent_message():
    message = AsyncMock()
    sent = object()
    message.reply_text.return_value = sent

    result = await reply_with_markdown(message, "text")

    assert result is sent


async def test_returns_the_sent_message_on_fallback():
    message = AsyncMock()
    sent = object()
    message.reply_text.side_effect = [BadRequest("Can't parse entities"), sent]

    result = await reply_with_markdown(message, "*unclosed")

    assert result is sent


async def test_falls_back_to_plain_text_when_markdown_parsing_fails():
    message = AsyncMock()
    message.reply_text.side_effect = [BadRequest("Can't parse entities"), None]

    await reply_with_markdown(message, "*unclosed bold")

    assert message.reply_text.await_count == 2
    first_call, second_call = message.reply_text.await_args_list
    assert first_call.kwargs.get("parse_mode") == ParseMode.MARKDOWN
    assert "parse_mode" not in second_call.kwargs
    assert second_call.args[0] == "*unclosed bold"


async def test_propagates_non_parsing_errors():
    message = AsyncMock()
    message.reply_text.side_effect = BadRequest("Message is too long")

    with pytest.raises(BadRequest):
        await reply_with_markdown(message, "x" * 5000)


async def test_passes_reply_markup_through_to_the_primary_send():
    message = AsyncMock()
    markup = object()

    await reply_with_markdown(message, "text", reply_markup=markup)

    message.reply_text.assert_awaited_once_with("text", parse_mode=ParseMode.MARKDOWN, reply_markup=markup)


async def test_passes_reply_markup_through_to_the_fallback_send():
    message = AsyncMock()
    message.reply_text.side_effect = [BadRequest("Can't parse entities"), None]
    markup = object()

    await reply_with_markdown(message, "*unclosed", reply_markup=markup)

    second_call = message.reply_text.await_args_list[1]
    assert second_call.kwargs.get("reply_markup") is markup
