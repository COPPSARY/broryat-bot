from unittest.mock import AsyncMock, MagicMock

from telegram.constants import ParseMode

from bot.handlers.commands import help_command, language_command, start_command


def _repos(user_language=None, group_language=None):
    user_pref_repo = AsyncMock()
    user_pref_repo.get_language.return_value = user_language
    group_pref_repo = AsyncMock()
    group_pref_repo.get_language.return_value = group_language
    return user_pref_repo, group_pref_repo


def _update():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_chat.type = "private"
    update.effective_user.id = 222
    return update


async def test_start_command_replies_with_welcome_text():
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await start_command(update, MagicMock())

    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Broryat AI" in text


async def test_start_command_welcome_is_short_and_bilingual():
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await start_command(update, MagicMock())

    text = update.message.reply_text.call_args[0][0]
    assert len(text) <= 200
    khmer_chars = [ch for ch in text if "ក" <= ch <= "៿"]
    assert khmer_chars


async def test_start_command_includes_language_choice_buttons():
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await start_command(update, MagicMock())

    kwargs = update.message.reply_text.call_args.kwargs
    markup = kwargs["reply_markup"]
    buttons = [button for row in markup.inline_keyboard for button in row]
    callback_data = {button.callback_data for button in buttons}
    assert callback_data == {"lang:en", "lang:km"}


async def test_language_buttons_show_flag_emojis():
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await start_command(update, MagicMock())

    kwargs = update.message.reply_text.call_args.kwargs
    markup = kwargs["reply_markup"]
    labels_by_callback = {
        button.callback_data: button.text for row in markup.inline_keyboard for button in row
    }
    assert "🇬🇧" in labels_by_callback["lang:en"]
    assert "🇰🇭" in labels_by_callback["lang:km"]


async def test_help_command_replies_with_command_list():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language="en")

    await help_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "/start" in text
    assert "/help" in text


async def test_help_command_mentions_the_topic_commands():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language="en")

    await help_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    text = update.message.reply_text.call_args[0][0]
    assert "/use" in text
    assert "/secure" in text
    assert "/password" in text
    assert "/addgroup" in text
    assert "/donate" in text


async def test_help_command_sends_with_markdown_formatting():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language="en")

    await help_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    kwargs = update.message.reply_text.call_args.kwargs
    assert kwargs.get("parse_mode") == ParseMode.MARKDOWN
    text = update.message.reply_text.call_args[0][0]
    assert "*/secure*" in text
    assert "*/password*" in text
    assert "*/addgroup*" in text
    assert "*/donate*" in text


async def test_help_command_uses_khmer_when_stored():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language="km")

    await help_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    text = update.message.reply_text.call_args[0][0]
    assert "ពាក្យបញ្ជា" in text


async def test_help_command_shows_bilingual_when_no_preference():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language=None)

    await help_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    text = update.message.reply_text.call_args[0][0]
    assert "Commands" in text
    assert "ពាក្យបញ្ជា" in text


async def test_language_command_offers_english_when_current_is_khmer():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language="km")

    await language_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    kwargs = update.message.reply_text.call_args.kwargs
    markup = kwargs["reply_markup"]
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert buttons[0].callback_data == "lang:en"


async def test_language_command_offers_khmer_when_current_is_english():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language="en")

    await language_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    kwargs = update.message.reply_text.call_args.kwargs
    markup = kwargs["reply_markup"]
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert buttons[0].callback_data == "lang:km"


async def test_language_command_shows_both_options_when_no_preference():
    update = _update()
    user_pref_repo, group_pref_repo = _repos(user_language=None)

    await language_command(update, MagicMock(), user_pref_repo, group_pref_repo)

    kwargs = update.message.reply_text.call_args.kwargs
    markup = kwargs["reply_markup"]
    buttons = [b for row in markup.inline_keyboard for b in row]
    callback_data = {b.callback_data for b in buttons}
    assert callback_data == {"lang:en", "lang:km"}
