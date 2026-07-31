from unittest.mock import AsyncMock, MagicMock

from bot.handlers.private import handle_private_photo
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult
from bot.services.ai.image_extractors.base import ImageExtractionError


def _scan_result(risk_level=RiskLevel.SAFE, message="No action needed."):
    return ScanResult(
        risk_level=risk_level,
        ai=IntentResult(risk_level=risk_level, message=message, language="en"),
    )


def _update(username="johndoe"):
    update = MagicMock()
    update.message.caption = None
    update.message.chat_id = 111
    update.message.from_user.id = 222
    update.message.from_user.username = username
    update.message.photo = [MagicMock(file_id="small"), MagicMock(file_id="large")]
    placeholder = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=placeholder)
    return update


def _context():
    context = MagicMock()
    tg_file = MagicMock()
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"image-bytes"))
    context.bot.get_file = AsyncMock(return_value=tg_file)
    return context


def _extractor(text="Your account is suspended http://evil-site.com"):
    extractor = AsyncMock()
    extractor.extract_text.return_value = text
    return extractor


def _user_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


def _group_pref_repo():
    return AsyncMock()


def _pipeline():
    pipeline = AsyncMock()
    pipeline.count_recent_scans = AsyncMock(return_value=0)
    pipeline.was_recently_scanned = AsyncMock(return_value=False)
    pipeline.run.return_value = _scan_result()
    return pipeline


async def test_downloads_the_largest_photo_size():
    update = _update()
    context = _context()

    await handle_private_photo(
        update, context, _pipeline(), _extractor(), _user_pref_repo(), _group_pref_repo()
    )

    context.bot.get_file.assert_awaited_once_with("large")


async def test_extracts_text_then_scans_with_urls_from_the_image():
    update = _update()
    pipeline = _pipeline()
    extractor = _extractor("Click http://evil-site.com to verify")

    await handle_private_photo(
        update, context := _context(), pipeline, extractor, _user_pref_repo(), _group_pref_repo()
    )

    extractor.extract_text.assert_awaited_once()
    request = pipeline.run.call_args[0][0]
    assert request.chat_type == "private"
    assert request.text == "Click http://evil-site.com to verify"
    assert request.urls == ["http://evil-site.com"]
    assert request.input_type == "url"


async def test_text_only_image_without_links_still_scans_as_text():
    update = _update()
    pipeline = _pipeline()
    extractor = _extractor("Send me 100 dollars to unlock your prize")

    await handle_private_photo(
        update, _context(), pipeline, extractor, _user_pref_repo(), _group_pref_repo()
    )

    request = pipeline.run.call_args[0][0]
    assert request.input_type == "text"
    assert request.urls == []
    assert request.text == "Send me 100 dollars to unlock your prize"


async def test_records_the_sender_username():
    update = _update(username="janedoe")
    user_pref_repo = _user_pref_repo()

    await handle_private_photo(
        update, _context(), _pipeline(), _extractor(), user_pref_repo, _group_pref_repo()
    )

    user_pref_repo.set_username.assert_awaited_once_with(222, "janedoe")


async def test_replies_friendly_when_no_text_found_and_does_not_scan():
    update = _update()
    pipeline = _pipeline()
    extractor = _extractor("   ")

    await handle_private_photo(
        update, _context(), pipeline, extractor, _user_pref_repo(), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited()


async def test_replies_gracefully_when_extraction_fails_and_does_not_scan():
    update = _update()
    pipeline = _pipeline()
    extractor = AsyncMock()
    extractor.extract_text.side_effect = ImageExtractionError("router down")

    await handle_private_photo(
        update, _context(), pipeline, extractor, _user_pref_repo(), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited()


async def test_enforces_the_daily_scan_limit():
    update = _update()
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=3)

    await handle_private_photo(
        update, _context(), pipeline, _extractor(), _user_pref_repo(), _group_pref_repo()
    )

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited()


async def test_cached_repeat_bypasses_daily_limit():
    update = _update()
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=3)
    pipeline.was_recently_scanned = AsyncMock(return_value=True)

    await handle_private_photo(
        update, _context(), pipeline, _extractor(), _user_pref_repo(), _group_pref_repo()
    )

    pipeline.run.assert_awaited_once()


async def test_uses_stored_language_preference_for_the_scan():
    update = _update()
    pipeline = _pipeline()

    await handle_private_photo(
        update, _context(), pipeline, _extractor(), _user_pref_repo(language="km"), _group_pref_repo()
    )

    request = pipeline.run.call_args[0][0]
    assert request.language == "km"
