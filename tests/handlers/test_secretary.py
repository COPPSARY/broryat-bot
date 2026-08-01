from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from telegram.constants import ParseMode
from telegram.error import BadRequest

from bot.handlers.secretary import (
    _delete_action_prompt,
    handle_business_connection,
    handle_secretary_action,
    handle_secretary_message,
)
from bot.schemas.enums import RiskLevel
from bot.schemas.scan import ScanResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict


def _result(*, file_status=None, url_status=None):
    return ScanResult(
        risk_level=RiskLevel.HIGH if "malicious" in (file_status, url_status) else RiskLevel.SAFE,
        vt_file=(
            VTFileVerdict(sha256="a" * 64, status=file_status, total_engines=70)
            if file_status
            else None
        ),
        vt_url=(
            VTUrlVerdict(url="https://example.com", status=url_status, total_engines=70)
            if url_status
            else None
        ),
    )


def _update(*, text=None, document=None, animation=None, sticker=None):
    update = MagicMock()
    message = update.business_message
    message.business_connection_id = "conn-1"
    message.chat_id = 111
    message.message_id = 555
    message.from_user.id = 222
    message.text = text
    message.document = document
    message.animation = animation
    message.sticker = sticker
    return update


def _repos(*, found=True, language=None):
    secretary_repo = AsyncMock()
    secretary_repo.get_by_connection.return_value = (
        MagicMock(user_id=999) if found else None
    )
    user_repo = AsyncMock()
    user_repo.get_language.return_value = language
    return secretary_repo, user_repo


def _context():
    context = MagicMock()
    context.bot.delete_business_messages = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.job_queue.run_once = MagicMock()
    context.bot.get_business_connection = AsyncMock(
        side_effect=BadRequest("connection unavailable")
    )
    context.bot.get_file = AsyncMock(
        return_value=AsyncMock(download_to_drive=AsyncMock())
    )
    return context


def _callback_update(action, *, user_id=999):
    update = MagicMock()
    query = update.callback_query
    query.data = f"secretary:{action}:555"
    query.from_user.id = user_id
    query.message.business_connection_id = "conn-1"
    query.message.message_id = 777
    query.message.text = "Malware warning"
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    return update


def _callback_context(*, can_delete_all_messages=True):
    context = _context()
    context.bot.get_business_connection.side_effect = None
    context.bot.get_business_connection.return_value = MagicMock(
        is_enabled=True,
        user=MagicMock(id=999),
        rights=MagicMock(
            can_delete_all_messages=can_delete_all_messages
        ),
    )
    return context


async def _handle(update, pipeline, *, found=True, language=None, context=None, **kwargs):
    secretary_repo, user_repo = _repos(found=found, language=language)
    context = context or _context()
    await handle_secretary_message(
        update, context, pipeline, secretary_repo, user_repo, **kwargs
    )
    return context, secretary_repo, user_repo


async def test_business_connection_update_tracks_active_connection():
    update = MagicMock()
    update.business_connection.user.id = 999
    update.business_connection.id = "conn-1"
    update.business_connection.is_enabled = True
    repo = AsyncMock()

    await handle_business_connection(update, MagicMock(), repo)

    repo.set_business_connection.assert_awaited_once_with(999, "conn-1")


async def test_business_connection_update_stores_owner_in_user_preferences():
    update = MagicMock()
    update.business_connection.user.id = 999
    update.business_connection.user.username = "owner1"
    update.business_connection.user.first_name = "Owen"
    update.business_connection.user.last_name = "Owner"
    update.business_connection.id = "conn-1"
    update.business_connection.is_enabled = True
    repo = AsyncMock()
    user_repo = AsyncMock()

    await handle_business_connection(update, MagicMock(), repo, user_pref_repo=user_repo)

    user_repo.set_username.assert_awaited_once_with(999, "owner1")
    user_repo.set_name.assert_awaited_once_with(999, "Owen", "Owner")


async def test_business_connection_update_without_user_pref_repo_does_not_crash():
    update = MagicMock()
    update.business_connection.user.id = 999
    update.business_connection.id = "conn-1"
    update.business_connection.is_enabled = True
    repo = AsyncMock()

    await handle_business_connection(update, MagicMock(), repo)


async def test_business_connection_update_clears_disabled_connection():
    update = MagicMock()
    update.business_connection.user.id = 999
    update.business_connection.id = "conn-1"
    update.business_connection.is_enabled = False
    repo = AsyncMock()

    await handle_business_connection(update, MagicMock(), repo)

    repo.set_business_connection.assert_awaited_once_with(999, None)


async def test_plain_conversation_is_never_scanned_or_looked_up():
    pipeline = AsyncMock()
    update = _update(text="Hello, is this available?")

    _, _, user_repo = await _handle(update, pipeline)

    pipeline.run.assert_not_awaited()
    user_repo.get_language.assert_not_awaited()


async def test_lone_trusted_url_is_not_scanned():
    pipeline = AsyncMock()

    context, _, user_repo = await _handle(
        _update(text="https://www.facebook.com/share/p/example"), pipeline
    )

    pipeline.run.assert_not_awaited()
    user_repo.get_language.assert_not_awaited()
    context.bot.send_message.assert_not_awaited()


async def test_trusted_url_with_other_text_is_still_scanned():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(url_status="clean")

    await _handle(
        _update(text="Log in urgently: https://chatgpt.com"), pipeline
    )

    pipeline.run.assert_awaited_once()


async def test_missing_connection_mapping_skips_scan():
    pipeline = AsyncMock()

    await _handle(_update(text="https://example.com"), pipeline, found=False)

    pipeline.run.assert_not_awaited()


async def test_missing_connection_mapping_is_recovered_from_telegram():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(url_status="clean")
    context = _context()
    context.bot.get_business_connection.side_effect = None
    context.bot.get_business_connection.return_value = MagicMock(
        id="conn-1",
        is_enabled=True,
        user=MagicMock(id=999),
    )

    _, secretary_repo, _ = await _handle(
        _update(text="https://example.com"),
        pipeline,
        found=False,
        context=context,
    )

    secretary_repo.set_business_connection.assert_awaited_once_with(999, "conn-1")
    pipeline.run.assert_awaited_once()


async def test_outgoing_business_owner_message_is_not_scanned():
    pipeline = AsyncMock()
    update = _update(text="https://example.com")
    update.business_message.from_user.id = 999

    await _handle(update, pipeline)

    pipeline.run.assert_not_awaited()


async def test_edited_incoming_url_is_scanned():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(url_status="clean")
    update = _update(text="https://example.com")
    update.edited_business_message = update.business_message
    update.business_message = None

    await _handle(update, pipeline)

    pipeline.run.assert_awaited_once()


async def test_safe_url_passes_silently_and_user_ids_are_not_recorded():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(url_status="clean")

    context, _, _ = await _handle(_update(text="see https://example.com"), pipeline)

    request = pipeline.run.await_args.args[0]
    assert request.chat_id == request.user_id == 0
    assert request.text is None
    assert request.urls == ["https://example.com"]
    assert request.language == "km"
    context.bot.delete_business_messages.assert_not_awaited()
    context.bot.send_message.assert_not_awaited()


async def test_saved_owner_language_is_used():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(url_status="clean")

    await _handle(_update(text="https://example.com"), pipeline, language="en")

    assert pipeline.run.await_args.args[0].language == "en"


async def test_malicious_url_asks_owner_to_delete_or_keep():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(url_status="malicious")

    context, _, _ = await _handle(_update(text="https://example.com"), pipeline)

    context.bot.delete_business_messages.assert_not_awaited()
    sent = context.bot.send_message.await_args.kwargs
    assert sent["chat_id"] == 111
    assert sent["business_connection_id"] == "conn-1"
    assert sent["parse_mode"] == ParseMode.HTML
    assert "មានមេរោគ" in sent["text"]
    assert "Broryat" in sent["text"]
    callbacks = [
        button.callback_data for button in sent["reply_markup"].inline_keyboard[0]
    ]
    assert callbacks == ["secretary:delete:555", "secretary:keep:555"]


async def test_malware_prompt_includes_virustotal_details_and_disclaimer():
    pipeline = AsyncMock()
    result = _result(url_status="malicious")
    result.analysis_failed = True
    result.vt_url.malicious_count = 9
    result.vt_url.detection_names = ["Phishing.Generic"]
    pipeline.run.return_value = result

    context, _, _ = await _handle(
        _update(text="https://example.com"), pipeline, language="en"
    )

    warning = context.bot.send_message.await_args.kwargs["text"]
    assert warning.startswith(
        "This response is generated by Broryat Bot.\n\n"
    )
    assert "9/70" in warning
    assert "Phishing.Generic" in warning
    assert "Broryat may make mistakes" in warning


async def test_clean_vt_result_is_not_deleted_even_if_other_analysis_is_high():
    pipeline = AsyncMock()
    result = _result(url_status="clean")
    result.risk_level = RiskLevel.HIGH
    pipeline.run.return_value = result

    context, _, _ = await _handle(_update(text="https://example.com"), pipeline)

    context.bot.delete_business_messages.assert_not_awaited()


async def test_owner_can_delete_flagged_message():
    context = _callback_context()
    _, user_repo = _repos(language="en")
    update = _callback_update("delete")

    await handle_secretary_action(update, context, user_repo)

    context.bot.delete_business_messages.assert_awaited_once_with("conn-1", [555])
    update.callback_query.edit_message_text.assert_awaited_once()
    assert "Deleted by the account owner" in (
        update.callback_query.edit_message_text.await_args.args[0]
    )


async def test_owner_can_keep_flagged_message():
    context = _callback_context()
    _, user_repo = _repos(language="en")
    update = _callback_update("keep")

    await handle_secretary_action(update, context, user_repo)

    context.bot.delete_business_messages.assert_not_awaited()
    assert "Kept by the account owner" in (
        update.callback_query.edit_message_text.await_args.args[0]
    )
    scheduled = context.job_queue.run_once.call_args
    assert scheduled.args[0] is _delete_action_prompt
    assert scheduled.kwargs == {
        "when": 5,
        "data": ("conn-1", 777),
    }


async def test_chat_participant_cannot_choose_for_owner():
    context = _callback_context()
    _, user_repo = _repos(language="en")
    update = _callback_update("delete", user_id=222)

    await handle_secretary_action(update, context, user_repo)

    context.bot.delete_business_messages.assert_not_awaited()
    update.callback_query.edit_message_text.assert_not_awaited()
    assert update.callback_query.answer.await_args.kwargs["show_alert"] is True


async def test_missing_delete_permission_is_explained_without_api_call():
    context = _callback_context(can_delete_all_messages=False)
    _, user_repo = _repos(language="en")
    update = _callback_update("delete")

    await handle_secretary_action(update, context, user_repo)

    context.bot.delete_business_messages.assert_not_awaited()
    assert "Delete received messages" in update.callback_query.answer.await_args.args[0]
    assert update.callback_query.answer.await_args.kwargs["show_alert"] is True


async def test_failed_delete_keeps_buttons_available():
    context = _callback_context()
    context.bot.delete_business_messages.side_effect = BadRequest("not enough rights")
    _, user_repo = _repos(language="en")
    update = _callback_update("delete")

    await handle_secretary_action(update, context, user_repo)

    update.callback_query.edit_message_text.assert_not_awaited()
    context.job_queue.run_once.assert_not_called()
    assert update.callback_query.answer.await_args.kwargs["show_alert"] is True


async def test_action_prompt_cleanup_deletes_business_message():
    context = MagicMock()
    context.bot.delete_business_messages = AsyncMock()
    context.job.data = ("conn-1", 777)

    await _delete_action_prompt(context)

    context.bot.delete_business_messages.assert_awaited_once_with("conn-1", [777])


async def test_file_scan_uses_safe_name_and_removes_temporary_download():
    pipeline = AsyncMock()
    pipeline.run.return_value = _result(file_status="clean")
    document = MagicMock(
        file_name="../../report.pdf",
        mime_type="application/pdf",
        file_size=10,
        file_id="file-id",
    )

    await _handle(_update(document=document), pipeline)

    request = pipeline.run.await_args.args[0]
    assert request.file_name == "report.pdf"
    assert not Path(request.file_path).parent.exists()


async def test_image_and_oversized_documents_are_skipped():
    pipeline = AsyncMock()
    image = MagicMock(file_name="screen.png", mime_type="image/png", file_size=10)
    oversized = MagicMock(
        file_name="big.exe", mime_type=None, file_size=21 * 1024 * 1024
    )

    await _handle(_update(document=image), pipeline)
    await _handle(
        _update(document=oversized),
        pipeline,
        max_file_size_bytes=20 * 1024 * 1024,
    )

    pipeline.run.assert_not_awaited()
