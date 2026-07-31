from unittest.mock import AsyncMock, MagicMock

from bot.handlers.private import handle_private_message
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult


def _scan_result(risk_level=RiskLevel.SAFE, message="No action needed."):
    return ScanResult(
        risk_level=risk_level,
        ai=IntentResult(risk_level=risk_level, message=message, language="en"),
    )


def _update(text=None, document=None, forward_origin=None, username="johndoe", animation=None):
    update = MagicMock()
    update.message.text = text
    update.message.caption = None
    update.message.document = document
    update.message.animation = animation
    update.message.forward_origin = forward_origin
    update.message.chat_id = 111
    update.message.from_user.id = 222
    update.message.from_user.username = username
    update.effective_chat.type = "private"
    update.effective_chat.id = 111
    update.effective_user.id = 222
    placeholder = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=placeholder)
    update.message.reply_photo = AsyncMock()
    return update


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
    return pipeline


def _extractor(text="extracted text"):
    extractor = AsyncMock()
    extractor.extract_text.return_value = text
    return extractor


async def test_forwarded_text_message_builds_forwarded_request_and_replies():
    update = _update(text="Hello, is this app legit?", forward_origin=MagicMock())
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), _extractor())

    request = pipeline.run.call_args[0][0]
    assert request.input_type == "forwarded"
    assert request.chat_id == 111
    assert request.user_id == 222
    assert request.chat_type == "private"
    update.message.reply_text.return_value.edit_text.assert_awaited()


async def test_records_the_sender_username_in_user_preferences():
    update = _update(text="Hello, is this app legit?", forward_origin=MagicMock(), username="janedoe")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()
    user_pref_repo = _user_pref_repo()

    await handle_private_message(update, MagicMock(), pipeline, user_pref_repo, _group_pref_repo(), _extractor())

    user_pref_repo.set_username.assert_awaited_once_with(222, "janedoe")


async def test_message_that_is_only_a_url_sets_input_type_url():
    update = _update(text="https://example.com/promo")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), _extractor())

    request = pipeline.run.call_args[0][0]
    assert request.input_type == "url"
    assert request.urls == ["https://example.com/promo"]


async def test_forwarded_message_sets_input_type_forwarded():
    update = _update(text="check this out", forward_origin=MagicMock())
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), _extractor())

    request = pipeline.run.call_args[0][0]
    assert request.input_type == "forwarded"


async def test_image_document_is_routed_to_ocr_not_file_scan():
    document = MagicMock()
    document.file_name = "screenshot.png"
    document.mime_type = "image/png"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(document=document)
    context = MagicMock()
    tg_file = MagicMock()
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"img-bytes"))
    context.bot.get_file = AsyncMock(return_value=tg_file)
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()
    extractor = _extractor("Your OTP is 123, verify at http://evil-site.com")

    await handle_private_message(
        update, context, pipeline, _user_pref_repo(), _group_pref_repo(), extractor
    )

    extractor.extract_text.assert_awaited_once()
    request = pipeline.run.call_args[0][0]
    assert request.text == "Your OTP is 123, verify at http://evil-site.com"
    assert request.input_type == "url"
    assert request.urls == ["http://evil-site.com"]
    assert request.file_name is None


async def test_non_image_document_is_still_file_scanned():
    document = MagicMock()
    document.file_name = "report.pdf"
    document.mime_type = "application/pdf"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(document=document)
    context = MagicMock()
    context.bot.get_file = AsyncMock(return_value=AsyncMock(download_to_drive=AsyncMock()))
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()
    extractor = _extractor()

    await handle_private_message(
        update, context, pipeline, _user_pref_repo(), _group_pref_repo(), extractor
    )

    extractor.extract_text.assert_not_awaited()
    pipeline.run.assert_awaited_once()
    request = pipeline.run.call_args[0][0]
    assert request.input_type == "file"
    assert request.file_name == "report.pdf"


async def test_animation_gif_is_ignored_silently():
    # Telegram delivers GIFs as an animation (converted to MP4) with a document
    # also attached for backward-compat, so filename/MIME checks miss it.
    document = MagicMock()
    document.file_name = "giphy.mp4"
    document.mime_type = "video/mp4"
    document.file_size = 1000
    update = _update(document=document, animation=MagicMock())
    pipeline = _pipeline()
    extractor = _extractor()

    await handle_private_message(
        update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), extractor
    )

    extractor.extract_text.assert_not_awaited()
    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_gif_document_is_ignored_silently():
    document = MagicMock()
    document.file_name = "funny.gif"
    document.mime_type = "image/gif"
    document.file_size = 1000
    document.file_id = "file-id"
    update = _update(document=document)
    pipeline = _pipeline()
    extractor = _extractor()

    await handle_private_message(
        update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), extractor
    )

    extractor.extract_text.assert_not_awaited()
    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_oversized_file_is_rejected_without_calling_pipeline():
    document = MagicMock()
    document.file_name = "big.exe"
    document.file_size = 25 * 1024 * 1024
    update = _update(document=document)
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()


async def test_no_stored_preference_falls_back_to_auto_detected_language():
    update = _update(text="សួស្តី តើនេះជាការពិតទេ", forward_origin=MagicMock())
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(
        update, MagicMock(), pipeline, _user_pref_repo(language=None), _group_pref_repo(), _extractor()
    )

    request = pipeline.run.call_args[0][0]
    assert request.language == "km"


async def test_stored_preference_overrides_auto_detected_language():
    update = _update(text="សួស្តី តើនេះជាការពិតទេ", forward_origin=MagicMock())
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(
        update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor()
    )

    request = pipeline.run.call_args[0][0]
    assert request.language == "en"


async def test_final_answer_is_edited_onto_the_placeholder_message():
    update = _update(text="Hello, is this app legit?", forward_origin=MagicMock())
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result(message="No action needed.")

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(), _group_pref_repo(), _extractor())

    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited()
    assert "No action needed." in placeholder.edit_text.await_args.args[0]


async def test_menu_button_tap_dispatches_to_secure_command_without_scanning():
    update = _update(text="🔒 Secure Account")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Secure your account" in text


async def test_menu_button_tap_dispatches_to_donate_command_without_scanning():
    update = _update(text="❤️ Donate")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    assert update.message.reply_text.await_count + update.message.reply_photo.await_count == 1


async def test_plain_non_forwarded_text_gets_fallback_instead_of_scan():
    update = _update(text="hi how are you")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Forward" in text


async def test_plain_non_forwarded_text_fallback_in_khmer():
    update = _update(text="សួស្តី")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="km"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    text = update.message.reply_text.call_args[0][0]
    assert "បញ្ជូនបន្ត" in text


async def test_forwarded_plain_text_still_scanned():
    update = _update(text="hi how are you", forward_origin=MagicMock())
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_awaited_once()


async def test_non_forwarded_url_text_still_scanned():
    update = _update(text="https://example.com/promo")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_awaited_once()


async def test_daily_limit_reached_blocks_scan_with_message():
    update = _update(text="https://example.com/promo")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "2" in text


async def test_below_daily_limit_still_scans():
    update = _update(text="https://example.com/promo")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=1)
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_awaited_once()


async def test_cached_repeat_bypasses_daily_limit():
    update = _update(text="https://example.com/promo")
    pipeline = _pipeline()
    pipeline.count_recent_scans = AsyncMock(return_value=2)
    pipeline.was_recently_scanned = AsyncMock(return_value=True)
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_awaited_once()


async def test_lone_trusted_domain_link_skips_scan_entirely():
    update = _update(text="https://google.com")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "trusted" in text.lower()


async def test_trusted_domain_link_with_other_text_still_scanned():
    update = _update(text="You won a prize, claim it at https://google.com now!")
    pipeline = _pipeline()
    pipeline.run.return_value = _scan_result()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_awaited_once()


async def test_own_website_link_skips_scan_with_own_site_message():
    update = _update(text="https://broryat.tech")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="en"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "our" in text.lower() and "website" in text.lower()


async def test_menu_button_tap_in_khmer_dispatches_correctly():
    update = _update(text="🔑 ពាក្យសម្ងាត់")
    pipeline = _pipeline()

    await handle_private_message(update, MagicMock(), pipeline, _user_pref_repo(language="km"), _group_pref_repo(), _extractor())

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "គន្លឹះងាយៗដើម្បីសុវត្ថិភាពពាក្យសម្ងាត់" in text
