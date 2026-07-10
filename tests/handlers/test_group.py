from unittest.mock import AsyncMock, MagicMock

from bot.handlers.group import handle_group_message
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


def _update(text="check this https://example.com"):
    update = MagicMock()
    update.message.text = text
    update.message.caption = None
    update.message.document = None
    update.message.forward_origin = None
    update.message.chat_id = 999
    update.message.from_user.id = 42
    placeholder = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=placeholder)
    return update


def _group_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


async def test_replies_when_risk_is_above_safe():
    update = _update()
    pipeline = AsyncMock()
    pipeline.run.return_value = _scan_result(risk_level=RiskLevel.HIGH, message="Do not click the link.")

    await handle_group_message(update, MagicMock(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited()
    assert "Do not click the link." in placeholder.edit_text.await_args.args[0]


async def test_stays_silent_when_risk_is_safe():
    update = _update()
    pipeline = AsyncMock()
    pipeline.run.return_value = _scan_result()

    await handle_group_message(update, MagicMock(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited_once_with("✅ No issues found.")


async def test_does_nothing_when_group_scan_disabled():
    update = _update()
    pipeline = AsyncMock()

    await handle_group_message(update, MagicMock(), pipeline, _group_pref_repo(), group_scan_enabled=False)

    pipeline.run.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_scan_request_uses_group_chat_type():
    update = _update()
    pipeline = AsyncMock()
    pipeline.run.return_value = _scan_result(risk_level=RiskLevel.HIGH, message="Do not click the link.")

    await handle_group_message(update, MagicMock(), pipeline, _group_pref_repo(), group_scan_enabled=True)

    request = pipeline.run.call_args[0][0]
    assert request.chat_type == "group"


async def test_no_stored_preference_falls_back_to_auto_detected_language():
    update = _update(text="សួស្តី តើនេះជាការពិតទេ")
    pipeline = AsyncMock()
    pipeline.run.return_value = _scan_result(risk_level=RiskLevel.HIGH)

    await handle_group_message(update, MagicMock(), pipeline, _group_pref_repo(language=None), group_scan_enabled=True)

    request = pipeline.run.call_args[0][0]
    assert request.language == "km"


async def test_stored_preference_overrides_auto_detected_language():
    update = _update(text="សួស្តី តើនេះជាការពិតទេ")
    pipeline = AsyncMock()
    pipeline.run.return_value = _scan_result(risk_level=RiskLevel.HIGH)

    await handle_group_message(update, MagicMock(), pipeline, _group_pref_repo(language="en"), group_scan_enabled=True)

    request = pipeline.run.call_args[0][0]
    assert request.language == "en"
