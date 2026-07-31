from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram.error import BadRequest

from bot.handlers import group as group_module
from bot.handlers.group import handle_group_message
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict


@pytest.fixture(autouse=True)
def mock_sleep():
    with patch("bot.handlers.group.asyncio.sleep", new=AsyncMock()) as sleep_mock:
        yield sleep_mock


@pytest.fixture(autouse=True)
def reset_limit_notified():
    group_module._LIMIT_NOTIFIED.clear()
    yield
    group_module._LIMIT_NOTIFIED.clear()


def _scan_result(risk_level=RiskLevel.SAFE, message="No action needed.", vt_file=None, vt_url=None):
    return ScanResult(
        risk_level=risk_level,
        ai=IntentResult(risk_level=risk_level, message=message, language="en"),
        vt_file=vt_file,
        vt_url=vt_url,
    )


def _update(text="check this https://example.com", document=None, chat_title="Scam Watch", animation=None, sticker=None):
    update = MagicMock()
    update.message.text = text
    update.message.caption = None
    update.message.document = document
    update.message.animation = animation
    update.message.sticker = sticker
    update.message.forward_origin = None
    update.message.chat_id = 999
    update.message.message_id = 555
    update.message.from_user.id = 42
    update.message.chat.title = chat_title
    placeholder = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=placeholder)
    return update


def _context():
    context = MagicMock()
    context.bot.delete_message = AsyncMock()
    context.bot.get_file = AsyncMock(return_value=AsyncMock(download_to_drive=AsyncMock()))
    return context


def _group_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


def _pipeline():
    pipeline = AsyncMock()
    pipeline.count_recent_scans = AsyncMock(return_value=0)
    pipeline.was_recently_scanned = AsyncMock(return_value=False)
    return pipeline


async def test_does_nothing_when_group_scan_disabled():
    update = _update()
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=False)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_records_the_group_name_in_group_preferences():
    update = _update(chat_title="Scam Watch")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()
    group_pref_repo = _group_pref_repo()

    await handle_group_message(update, _context(), pipeline, group_pref_repo, group_scan_enabled=True)

    group_pref_repo.set_group_name.assert_awaited_once_with(999, "Scam Watch")


async def test_image_document_is_ignored_silently():
    document = MagicMock()
    document.file_name = "screenshot.png"
    document.mime_type = "image/png"
    document.file_size = 1000
    update = _update(text=None, document=document)
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_animation_gif_is_ignored_silently():
    document = MagicMock()
    document.file_name = "giphy.mp4"
    document.mime_type = "video/mp4"
    document.file_size = 1000
    update = _update(text=None, document=document, animation=MagicMock())
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_sticker_is_ignored_silently():
    update = _update(text=None, sticker=MagicMock())
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_none_message_is_ignored_silently():
    update = _update()
    update.message = None
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()


async def test_gif_document_is_ignored_silently():
    document = MagicMock()
    document.file_name = "funny.gif"
    document.mime_type = "image/gif"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(text=None, document=document)
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_plain_text_without_link_is_skipped_entirely():
    update = _update(text="hey everyone, how's it going?")
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_text_with_link_is_scanned_and_defaults_to_khmer():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(language=None), group_scan_enabled=True)

    request = pipeline.run.call_args[0][0]
    assert request.language == "km"
    assert request.chat_type == "group"
    assert request.urls == ["https://example.com"]


async def test_stored_language_preference_overrides_khmer_default():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(language="en"), group_scan_enabled=True)

    request = pipeline.run.call_args[0][0]
    assert request.language == "en"


async def test_lone_trusted_domain_link_skips_scan_entirely():
    update = _update(text="https://google.com")
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_own_website_link_skips_scan_with_own_site_message():
    update = _update(text="https://broryat.tech")
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()


async def test_trusted_domain_link_with_other_text_still_scanned():
    update = _update(text="You won a prize, claim it at https://google.com now!")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_awaited_once()


async def test_daily_limit_reached_blocks_scan_with_message():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "២" in text


async def test_daily_limit_message_shown_briefly_then_deleted(mock_sleep):
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)
    placeholder = update.message.reply_text.return_value

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    mock_sleep.assert_awaited_once_with(3)
    placeholder.delete.assert_awaited_once()


async def test_daily_limit_message_not_sent_again_for_same_chat():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)
    update.message.reply_text.reset_mock()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_below_daily_limit_still_scans():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=1)
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_awaited_once()


async def test_cached_repeat_bypasses_daily_limit():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)
    pipeline.was_recently_scanned = AsyncMock(return_value=True)
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_awaited_once()


async def test_document_without_link_is_scanned():
    document = MagicMock()
    document.file_name = "invoice.pdf"
    document.mime_type = "application/pdf"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(text=None, document=document)
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_awaited_once()
    request = pipeline.run.call_args[0][0]
    assert request.input_type == "file"
    assert request.file_name == "invoice.pdf"


async def test_document_caption_is_included_as_text():
    document = MagicMock()
    document.file_name = "invoice.pdf"
    document.mime_type = "application/pdf"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(text=None, document=document)
    update.message.caption = "please review this"
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    request = pipeline.run.call_args[0][0]
    assert request.text == "please review this"


async def test_oversized_document_is_rejected_without_calling_pipeline():
    document = MagicMock()
    document.file_name = "big.exe"
    document.mime_type = "application/octet-stream"
    document.file_size = 25 * 1024 * 1024
    update = _update(text=None, document=document)
    pipeline = _pipeline()

    await handle_group_message(update, _context(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()


async def test_vt_malicious_url_deletes_message_and_warns():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result(
        vt_url=VTUrlVerdict(url="https://example.com", status="malicious", malicious_count=5, total_engines=10)
    )
    context = _context()

    await handle_group_message(update, context, pipeline, _group_pref_repo(), group_scan_enabled=True)

    context.bot.delete_message.assert_awaited_once_with(chat_id=999, message_id=555)
    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited_once()
    assert "លុបចេញ" in placeholder.edit_text.await_args.args[0]


async def test_waits_five_seconds_before_deleting_malicious_message(mock_sleep):
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result(
        vt_url=VTUrlVerdict(url="https://example.com", status="malicious", malicious_count=5, total_engines=10)
    )
    context = _context()

    await handle_group_message(update, context, pipeline, _group_pref_repo(), group_scan_enabled=True)

    mock_sleep.assert_awaited_once_with(5)
    assert context.bot.delete_message.await_count == 1


async def test_vt_malicious_file_deletes_message_and_warns():
    document = MagicMock()
    document.file_name = "malware.exe"
    document.mime_type = "application/octet-stream"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(text=None, document=document)
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result(
        vt_file=VTFileVerdict(sha256="a" * 64, status="malicious", malicious_count=5, total_engines=10)
    )
    context = _context()

    await handle_group_message(update, context, pipeline, _group_pref_repo(), group_scan_enabled=True)

    context.bot.delete_message.assert_awaited_once_with(chat_id=999, message_id=555)


async def test_delete_failure_falls_back_to_full_risk_report():
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result(
        message="Do not click the link.",
        vt_url=VTUrlVerdict(url="https://example.com", status="malicious", malicious_count=5, total_engines=10),
    )
    context = _context()
    context.bot.delete_message.side_effect = BadRequest("Message can't be deleted")

    await handle_group_message(update, context, pipeline, _group_pref_repo(), group_scan_enabled=True)

    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited()
    assert "Do not click the link." in placeholder.edit_text.await_args.args[0]


async def test_non_malicious_result_shows_response_then_deletes_after_five_seconds(mock_sleep):
    update = _update(text="check this out https://example.com")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result(risk_level=RiskLevel.HIGH, message="Do not click the link.")
    context = _context()

    await handle_group_message(update, context, pipeline, _group_pref_repo(), group_scan_enabled=True)

    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited_once()
    assert "Do not click the link." in placeholder.edit_text.await_args.args[0]
    mock_sleep.assert_awaited_once_with(5)
    placeholder.delete.assert_awaited_once()
    context.bot.delete_message.assert_not_awaited()
