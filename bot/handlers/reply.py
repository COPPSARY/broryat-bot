from telegram import InlineKeyboardMarkup, Message
from telegram.constants import ParseMode
from telegram.error import BadRequest


async def reply_with_markdown(
    message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> Message:
    kwargs = {"parse_mode": ParseMode.MARKDOWN}
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup

    try:
        return await message.reply_text(text, **kwargs)
    except BadRequest as exc:
        if "can't parse entities" not in str(exc).lower():
            raise
        kwargs.pop("parse_mode")
        return await message.reply_text(text, **kwargs)


async def edit_with_markdown(
    message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> None:
    kwargs = {"parse_mode": ParseMode.MARKDOWN}
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup

    try:
        await message.edit_text(text, **kwargs)
    except BadRequest as exc:
        if "can't parse entities" not in str(exc).lower():
            raise
        kwargs.pop("parse_mode")
        await message.edit_text(text, **kwargs)
