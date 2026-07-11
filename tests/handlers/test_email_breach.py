from unittest.mock import AsyncMock, MagicMock

from bot.handlers.email_breach import _format_breach_report, _is_valid_email, email_command
from bot.schemas.breach import BreachCheckResult, BreachRecord
from bot.services.breach_check.client import BreachCheckError


def test_is_valid_email_accepts_simple_address():
    assert _is_valid_email("user@example.com") is True


def test_is_valid_email_rejects_missing_at_sign():
    assert _is_valid_email("userexample.com") is False


def test_is_valid_email_rejects_missing_domain_dot():
    assert _is_valid_email("user@examplecom") is False


def test_format_report_no_breaches_english():
    result = BreachCheckResult(email="test@example.com", found=False)

    text = _format_breach_report(result, "en")

    assert "didn't find" in text.lower() or "did not find" in text.lower()
    assert "⚠️" not in text


def test_format_report_no_breaches_khmer():
    result = BreachCheckResult(email="test@example.com", found=False)

    text = _format_breach_report(result, "km")

    assert "✅" in text


def test_format_report_with_breach_english_includes_details():
    record = BreachRecord(
        breach="Zomato", domain="zomato.com", xposed_date="2016",
        xposed_data=["Email addresses", "Passwords"], password_risk="easytocrack",
    )
    result = BreachCheckResult(email="test@example.com", found=True, records=[record])

    text = _format_breach_report(result, "en")

    assert "Zomato" in text
    assert "2016" in text
    assert "Email addresses" in text
    assert "Passwords" in text
    assert "please change it" in text.lower()


def test_format_report_omits_password_note_when_risk_unknown():
    record = BreachRecord(
        breach="Sysco", domain="sysco.com", xposed_date="2023",
        xposed_data=["Names"], password_risk="unknown",
    )
    result = BreachCheckResult(email="test@example.com", found=True, records=[record])

    text = _format_breach_report(result, "en")

    assert "please change it" not in text.lower()


def test_format_report_no_language_preference_is_bilingual():
    result = BreachCheckResult(email="test@example.com", found=False)

    text = _format_breach_report(result, None)

    assert "didn't find" in text.lower() or "did not find" in text.lower()
    assert "✅" in text


def _many_records(count):
    return [
        BreachRecord(
            breach=f"Breach{i}", domain=f"breach{i}.com", xposed_date="2020",
            xposed_data=["Email addresses"], password_risk="unknown",
        )
        for i in range(count)
    ]


def test_format_report_caps_breach_list_and_notes_remaining_count():
    result = BreachCheckResult(email="test@example.com", found=True, records=_many_records(20))

    text = _format_breach_report(result, "en")

    assert "Breach0" in text
    assert "Breach7" in text
    assert "Breach8" not in text
    assert "12 more" in text.lower()


def test_format_report_bilingual_stays_under_telegram_message_limit():
    result = BreachCheckResult(email="test@example.com", found=True, records=_many_records(50))

    text = _format_breach_report(result, None)

    assert len(text) <= 4096


def _update(chat_type="private"):
    update = MagicMock()
    update.effective_chat.type = chat_type
    update.effective_chat.id = 999
    update.effective_user.id = 42
    placeholder = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=placeholder)
    return update


def _context(args):
    context = MagicMock()
    context.args = args
    return context


def _breach_client():
    return AsyncMock()


def _user_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


def _group_pref_repo(language=None):
    repo = AsyncMock()
    repo.get_language.return_value = language
    return repo


async def test_missing_argument_shows_usage_hint():
    update = _update()
    context = _context([])
    breach_client = _breach_client()

    await email_command(update, context, breach_client, _user_pref_repo(), _group_pref_repo())

    breach_client.check.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()
    text = update.message.reply_text.call_args[0][0]
    assert "/email" in text


async def test_invalid_email_shows_validation_message():
    update = _update()
    context = _context(["not-an-email"])
    breach_client = _breach_client()

    await email_command(update, context, breach_client, _user_pref_repo(), _group_pref_repo())

    breach_client.check.assert_not_awaited()
    update.message.reply_text.assert_awaited_once()


async def test_valid_email_shows_progress_then_edits_with_report():
    update = _update()
    context = _context(["test@example.com"])
    breach_client = _breach_client()
    breach_client.check.return_value = BreachCheckResult(email="test@example.com", found=False)

    await email_command(update, context, breach_client, _user_pref_repo(language="en"), _group_pref_repo())

    breach_client.check.assert_awaited_once_with("test@example.com")
    update.message.reply_text.assert_awaited_once()
    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited_once()
    text = placeholder.edit_text.call_args[0][0]
    assert "didn't find" in text.lower() or "did not find" in text.lower()


async def test_api_failure_shows_apology_and_does_not_raise():
    update = _update()
    context = _context(["test@example.com"])
    breach_client = _breach_client()
    breach_client.check.side_effect = BreachCheckError("boom")

    await email_command(update, context, breach_client, _user_pref_repo(), _group_pref_repo())

    placeholder = update.message.reply_text.return_value
    placeholder.edit_text.assert_awaited_once()
    text = placeholder.edit_text.call_args[0][0]
    assert "boom" not in text


async def test_works_in_group_chat_using_group_language_preference():
    update = _update(chat_type="group")
    context = _context(["test@example.com"])
    breach_client = _breach_client()
    breach_client.check.return_value = BreachCheckResult(email="test@example.com", found=False)

    await email_command(update, context, breach_client, _user_pref_repo(), _group_pref_repo(language="km"))

    breach_client.check.assert_awaited_once_with("test@example.com")
    placeholder = update.message.reply_text.return_value
    text = placeholder.edit_text.call_args[0][0]
    assert "✅" in text
