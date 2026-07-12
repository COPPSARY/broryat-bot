from unittest.mock import AsyncMock, MagicMock, patch

from bot.handlers.media import handle_unsupported_media
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult


def _scan_result(risk_level=RiskLevel.SAFE, message="No action needed."):
    return ScanResult(
        risk_level=risk_level,
        ai=IntentResult(
            risk_level=risk_level, confidence=0.5, categories=[], explanation="x",
            message=message, language="en",
        ),
    )


def _update(caption=None, chat_type="private"):
    update = MagicMock()
    update.message.caption = caption
    update.message.chat_id = 111
    update.message.message_id = 555
    update.message.from_user.id = 222
    update.effective_chat.type = chat_type
    update.effective_chat.id = 111
    update.effective_user.id = 222
    placeholder = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=placeholder)
    return update


def _user_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


def _group_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


def _pipeline():
    pipeline = AsyncMock()
    pipeline.count_recent_scans = AsyncMock(return_value=0)
    pipeline.was_recently_scanned = AsyncMock(return_value=False)
    return pipeline


async def test_private_photo_without_caption_url_gets_gentle_note():
    update = _update(caption=None, chat_type="private")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "photos or videos" in text


async def test_private_photo_gentle_note_in_khmer():
    update = _update(caption=None, chat_type="private")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="km"), _group_pref_repo()
    )

    text = update.message.reply_text.call_args[0][0]
    assert "រូបភាព" in text


async def test_private_photo_with_caption_url_is_scanned():
    update = _update(caption="check this out https://example.com", chat_type="private")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo()
    )

    pipeline.run.assert_awaited_once()
    request = pipeline.run.call_args[0][0]
    assert request.input_type == "url"
    assert request.urls == ["https://example.com"]
    assert request.chat_type == "private"


async def test_group_photo_without_caption_url_gets_gentle_note_in_khmer_by_default():
    update = _update(caption=None, chat_type="group")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(language=None)
    )

    pipeline.run.assert_not_awaited()
    text = update.message.reply_text.call_args[0][0]
    assert "រូបភាព" in text


async def test_private_photo_with_trusted_caption_url_skips_scan_entirely():
    update = _update(caption="https://google.com", chat_type="private")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    text = update.message.reply_text.call_args[0][0]
    assert "trusted" in text.lower()


async def test_group_photo_with_trusted_caption_url_skips_scan_entirely():
    update = _update(caption="https://google.com", chat_type="group")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(language=None)
    )

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_private_photo_with_own_website_caption_url_gets_own_site_message():
    update = _update(caption="https://broryat.tech", chat_type="private")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    text = update.message.reply_text.call_args[0][0]
    assert "our" in text.lower() and "website" in text.lower()


async def test_group_photo_with_own_website_caption_url_gets_own_site_message():
    update = _update(caption="https://broryat.tech", chat_type="group")
    pipeline = _pipeline()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(language="en")
    )

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "our" in text.lower() and "website" in text.lower()


async def test_private_daily_limit_reached_blocks_scan():
    update = _update(caption="check this out https://example.com", chat_type="private")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    text = update.message.reply_text.call_args[0][0]
    assert "2" in text


async def test_group_daily_limit_reached_blocks_scan():
    update = _update(caption="check this out https://example.com", chat_type="group")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(language=None)
    )

    pipeline.run.assert_not_awaited()
    text = update.message.reply_text.call_args[0][0]
    assert "២" in text


async def test_private_cached_repeat_bypasses_daily_limit():
    update = _update(caption="check this out https://example.com", chat_type="private")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)
    pipeline.was_recently_scanned = AsyncMock(return_value=True)
    pipeline.run.return_value = _scan_result()

    await handle_unsupported_media(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo()
    )

    pipeline.run.assert_awaited_once()


async def test_group_photo_with_caption_url_is_scanned():
    update = _update(caption="check this out https://example.com", chat_type="group")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()
    context = MagicMock()
    context.bot.delete_message = AsyncMock()

    with patch("bot.handlers.group.asyncio.sleep", new=AsyncMock()):
        await handle_unsupported_media(
            update, context, pipeline, _user_pref_repo(), _group_pref_repo(language=None)
        )

    pipeline.run.assert_awaited_once()
    request = pipeline.run.call_args[0][0]
    assert request.input_type == "url"
    assert request.chat_type == "group"
    assert request.language == "km"
