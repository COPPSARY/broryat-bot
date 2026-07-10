from unittest.mock import AsyncMock, MagicMock

from bot.handlers.language import handle_language_choice


def _update(chat_type: str, callback_data: str, user_id: int = 111, chat_id: int = 222):
    update = MagicMock()
    update.callback_query.data = callback_data
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_reply_markup = AsyncMock()
    update.effective_chat.type = chat_type
    update.effective_chat.id = chat_id
    update.effective_user.id = user_id
    return update


def _context():
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    return context


async def test_private_chat_sets_user_language_preference():
    update = _update("private", "lang:km")
    user_pref_repo = AsyncMock()
    group_pref_repo = AsyncMock()

    await handle_language_choice(update, _context(), user_pref_repo, group_pref_repo)

    user_pref_repo.set_language.assert_awaited_once_with(111, "km")
    group_pref_repo.set_language.assert_not_awaited()
    update.callback_query.answer.assert_awaited_once()


async def test_group_chat_sets_group_language_preference():
    update = _update("group", "lang:en", chat_id=-100999)
    user_pref_repo = AsyncMock()
    group_pref_repo = AsyncMock()

    await handle_language_choice(update, _context(), user_pref_repo, group_pref_repo)

    group_pref_repo.set_language.assert_awaited_once_with(-100999, "en")
    user_pref_repo.set_language.assert_not_awaited()


async def test_supergroup_chat_sets_group_language_preference():
    update = _update("supergroup", "lang:km", chat_id=-100888)
    user_pref_repo = AsyncMock()
    group_pref_repo = AsyncMock()

    await handle_language_choice(update, _context(), user_pref_repo, group_pref_repo)

    group_pref_repo.set_language.assert_awaited_once_with(-100888, "km")


async def test_removes_the_language_buttons_from_the_original_message():
    update = _update("private", "lang:en")
    user_pref_repo = AsyncMock()
    group_pref_repo = AsyncMock()

    await handle_language_choice(update, _context(), user_pref_repo, group_pref_repo)

    update.callback_query.edit_message_reply_markup.assert_awaited_once_with(reply_markup=None)


async def test_sends_a_new_confirmation_message_in_the_chosen_language():
    update = _update("private", "lang:km", chat_id=555)
    user_pref_repo = AsyncMock()
    group_pref_repo = AsyncMock()
    context = _context()

    await handle_language_choice(update, context, user_pref_repo, group_pref_repo)

    context.bot.send_message.assert_awaited_once()
    kwargs = context.bot.send_message.call_args.kwargs
    assert kwargs["chat_id"] == 555
    assert "ខ្មែរ" in kwargs["text"]


async def test_sent_message_explains_how_to_use_the_bot_in_english():
    update = _update("private", "lang:en")
    context = _context()

    await handle_language_choice(update, context, AsyncMock(), AsyncMock())

    text = context.bot.send_message.call_args.kwargs["text"]
    assert "forward" in text.lower() or "file" in text.lower() or "url" in text.lower()


async def test_sent_message_explains_how_to_use_the_bot_in_khmer():
    update = _update("private", "lang:km")
    context = _context()

    await handle_language_choice(update, context, AsyncMock(), AsyncMock())

    text = context.bot.send_message.call_args.kwargs["text"]
    assert "ឯកសារ" in text or "URL" in text
