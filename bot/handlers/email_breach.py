import logging
import re

from telegram import Update
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers.commands import _resolve_language
from bot.schemas.breach import BreachCheckResult
from bot.services.breach_check.client import BreachCheckClient, BreachCheckError

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_DATA_TYPE_KM = {
    "Email addresses": "អាសយដ្ឋានអ៊ីមែល",
    "Passwords": "ពាក្យសម្ងាត់",
    "Names": "ឈ្មោះ",
    "Phone numbers": "លេខទូរស័ព្ទ",
    "Usernames": "ឈ្មោះអ្នកប្រើប្រាស់",
    "IP addresses": "អាសយដ្ឋាន IP",
    "Physical addresses": "អាសយដ្ឋានលំនៅដ្ឋាន",
    "Dates of birth": "ថ្ងៃខែឆ្នាំកំណើត",
}

_RISKY_PASSWORD_LEVELS = {"easytocrack", "plaintext"}

_NOT_FOUND = {
    "en": (
        "✅ Good news — we didn't find your email in any known data breaches.\n"
        "This doesn't guarantee total safety, but it's a good sign. Stay cautious with links and passwords."
    ),
    "km": (
        "✅ ដំណឹងល្អ — ខ្ញុំមិនឃើញអ៊ីមែលរបស់អ្នកនៅក្នុងព័ត៌មានលេចធ្លាយដែលគេស្គាល់ទេ។\n"
        "ទោះជាយ៉ាងណា វានៅតែមិនអាចធានាបានពេញលេញនោះទេ សូមប្រុងប្រយ័ត្នចំពោះលីង និងពាក្យសម្ងាត់ជានិច្ច។"
    ),
}

_ADVICE = {
    "en": (
        "✅ What to do:\n"
        "• Change your password on any site where you reused it.\n"
        "• Turn on two-factor authentication (2FA) if you haven't already.\n"
        "• Never share OTP/verification codes with anyone."
    ),
    "km": (
        "✅ អ្វីដែលអ្នកគួរធ្វើ៖\n"
        "• ប្តូរពាក្យសម្ងាត់នៅគេហទំព័រណាមួយ ដែលអ្នកធ្លាប់ប្រើពាក្យសម្ងាត់ដដែល។\n"
        "• បើកប្រព័ន្ធការពារពីរជាន់ (2FA) ប្រសិនបើមិនទាន់បាន។\n"
        "• កុំប្រាប់លេខកូដ OTP ដល់អ្នកណាម្នាក់ឡើយ។"
    ),
}


def _is_valid_email(value: str) -> bool:
    return bool(_EMAIL_RE.match(value))


def _translate_data_type(data_type: str, language: str) -> str:
    if language == "km":
        return _DATA_TYPE_KM.get(data_type, data_type)
    return data_type


def _password_note(password_risk: str, language: str) -> str | None:
    if password_risk not in _RISKY_PASSWORD_LEVELS:
        return None
    if language == "km":
        return "⚠️ ពាក្យសម្ងាត់របស់អ្នកពីព័ត៌មានលេចធ្លាយនេះ អាចត្រូវបានទាយងាយ សូមប្តូរវាបើអ្នកនៅតែប្រើនៅកន្លែងណាមួយ។"
    return "⚠️ Your password from this breach could be easily guessed — please change it if you still use it anywhere."


def _format_found_single(result: BreachCheckResult, language: str) -> str:
    count = len(result.records)
    header = {
        "en": f"⚠️ Your email was found in {count} data breach{'es' if count != 1 else ''}.",
        "km": f"⚠️ អ៊ីមែលរបស់អ្នកត្រូវបានរកឃើញនៅក្នុងព័ត៌មានលេចធ្លាយចំនួន {count}។",
    }[language]

    lines = [header, ""]
    for record in result.records:
        data_types = ", ".join(_translate_data_type(d, language) for d in record.xposed_data)
        exposed_label = "Exposed" if language == "en" else "ព័ត៌មានលេចធ្លាយ"
        lines.append(f"📍 {record.breach} ({record.xposed_date})")
        lines.append(f"   {exposed_label}: {data_types}")
        note = _password_note(record.password_risk, language)
        if note:
            lines.append(f"   {note}")
        lines.append("")

    lines.append(_ADVICE[language])
    return "\n".join(lines)


def _format_breach_report(result: BreachCheckResult, language: str | None) -> str:
    if language:
        if result.found:
            return _format_found_single(result, language)
        return _NOT_FOUND[language]

    if result.found:
        return f"{_format_found_single(result, 'en')}\n\n{_format_found_single(result, 'km')}"
    return f"{_NOT_FOUND['en']}\n\n{_NOT_FOUND['km']}"


_USAGE_HINT = {
    "en": "Please include an email address, like this: /email you@example.com",
    "km": "សូមវាយអាសយដ្ឋានអ៊ីមែលភ្ជាប់ជាមួយ ដូចនេះ៖ /email you@example.com",
}

_INVALID_EMAIL = {
    "en": "That doesn't look like a valid email address. Please try again, like: /email you@example.com",
    "km": "អាសយដ្ឋាននេះមើលទៅមិនត្រឹមត្រូវទេ។ សូមព្យាយាមម្តងទៀត ដូចនេះ៖ /email you@example.com",
}

_CHECK_FAILED = {
    "en": "Sorry, I couldn't check that email right now. Please try again in a little while.",
    "km": "សូមអភ័យទោស ខ្ញុំមិនអាចពិនិត្យអ៊ីមែលនេះបានទេពេលនេះ។ សូមព្យាយាមម្តងទៀតក្នុងពេលបន្តិចទៀត។",
}


def _bilingual(mapping: dict[str, str], language: str | None) -> str:
    if language:
        return mapping[language]
    return f"{mapping['en']}\n\n{mapping['km']}"


async def email_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    breach_client: BreachCheckClient,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)

    if not context.args:
        await update.message.reply_text(_bilingual(_USAGE_HINT, language))
        return

    email = context.args[0]
    if not _is_valid_email(email):
        await update.message.reply_text(_bilingual(_INVALID_EMAIL, language))
        return

    try:
        result = await breach_client.check(email)
    except BreachCheckError:
        logger.exception("Email breach check failed for %s", email)
        await update.message.reply_text(_bilingual(_CHECK_FAILED, language))
        return

    await update.message.reply_text(_format_breach_report(result, language))
