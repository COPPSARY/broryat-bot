from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from bot.handlers.report import handle_report_callback
from bot.models.scan_record import ScanRecord


def _update(scan_id):
    update = MagicMock()
    update.callback_query.data = f"report:{scan_id}"
    update.callback_query.answer = AsyncMock()
    update.effective_chat.id = 111
    update.effective_user.id = 222
    return update


def _scan_record(scan_id, language="en", url="https://example.com/phish"):
    return ScanRecord(
        id=scan_id,
        chat_id=1,
        user_id=2,
        chat_type="private",
        input_type="url",
        url=url,
        language=language,
        final_risk_level="HIGH",
    )


async def test_inserts_a_report_row():
    scan_id = uuid4()
    update = _update(scan_id)
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    report_repo = AsyncMock()
    scan_repo = AsyncMock()
    scan_repo.get_by_id.return_value = _scan_record(scan_id)

    await handle_report_callback(update, context, report_repo, scan_repo, admin_chat_id=None)

    report_repo.insert_report.assert_awaited_once()
    inserted = report_repo.insert_report.call_args[0][0]
    assert inserted.scan_record_id == scan_id
    assert inserted.chat_id == 111
    assert inserted.user_id == 222
    assert inserted.url == "https://example.com/phish"


async def test_answers_the_callback_query_with_a_localized_confirmation():
    scan_id = uuid4()
    update = _update(scan_id)
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    report_repo = AsyncMock()
    scan_repo = AsyncMock()
    scan_repo.get_by_id.return_value = _scan_record(scan_id, language="km")

    await handle_report_callback(update, context, report_repo, scan_repo, admin_chat_id=None)

    update.callback_query.answer.assert_awaited_once()
    assert update.callback_query.answer.call_args[0][0] != ""


async def test_notifies_the_admin_chat_when_configured():
    scan_id = uuid4()
    update = _update(scan_id)
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    report_repo = AsyncMock()
    scan_repo = AsyncMock()
    scan_repo.get_by_id.return_value = _scan_record(scan_id)

    await handle_report_callback(update, context, report_repo, scan_repo, admin_chat_id=999)

    context.bot.send_message.assert_awaited_once()
    assert context.bot.send_message.call_args.kwargs["chat_id"] == 999
    assert "https://example.com/phish" in context.bot.send_message.call_args.kwargs["text"]


async def test_does_not_notify_admin_when_not_configured():
    scan_id = uuid4()
    update = _update(scan_id)
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    report_repo = AsyncMock()
    scan_repo = AsyncMock()
    scan_repo.get_by_id.return_value = _scan_record(scan_id)

    await handle_report_callback(update, context, report_repo, scan_repo, admin_chat_id=None)

    context.bot.send_message.assert_not_awaited()


async def test_handles_missing_scan_record_gracefully():
    scan_id = uuid4()
    update = _update(scan_id)
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    report_repo = AsyncMock()
    scan_repo = AsyncMock()
    scan_repo.get_by_id.return_value = None

    await handle_report_callback(update, context, report_repo, scan_repo, admin_chat_id=999)

    report_repo.insert_report.assert_not_awaited()
    context.bot.send_message.assert_not_awaited()
    update.callback_query.answer.assert_awaited_once()
