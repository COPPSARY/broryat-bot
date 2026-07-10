from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers.keyboards import LANGUAGE_KEYBOARD, other_language_keyboard

_DONATE_QR_PATH = Path(__file__).resolve().parent.parent / "assets" / "donate_qr.jpg"

_WELCOME = (
    "🛡️ *Broryat AI*\n\n"
    "Protect yourself from scams, phishing & malware.\n"
    "ការពារខ្លួនអ្នកពីការបោកប្រាស់ ការវាយប្រហារតាមអ៊ីនធឺណិត។\n\n"
    "👇 *Choose your language / សូមជ្រើសរើសភាសា:*"
)

_TOPIC_CONTENT = {
    "help": {
        "en": (
            "*Commands*\n"
            "*/start* — welcome & choose your language\n"
            "*/help* — this command list\n"
            "*/use* — how to use this bot\n"
            "*/secure* — how to secure your account\n"
            "*/password* — password tips\n"
            "*/addgroup* — how to add me to a group\n"
            "*/donate* — support this project"
        ),
        "km": (
            "*ពាក្យបញ្ជា*\n"
            "*/start* — សារស្វាគមន៍ & ជ្រើសរើសភាសា\n"
            "*/help* — បញ្ជីពាក្យបញ្ជានេះ\n"
            "*/use* — របៀបប្រើប្រាស់ bot នេះ\n"
            "*/secure* — របៀបការពារគណនីរបស់អ្នក\n"
            "*/password* — គន្លឹះពាក្យសម្ងាត់\n"
            "*/addgroup* — របៀបបន្ថែមខ្ញុំទៅក្រុម\n"
            "*/donate* — គាំទ្រគម្រោងនេះ"
        ),
    },
    "use": {
        "en": (
            "*How to use this bot*\n\n"
            "Send me any of the following to scan it:\n"
            "• A forwarded message\n"
            "• An uploaded file\n"
            "• A pasted URL\n"
            "• Plain text\n\n"
            "I'll reply with a risk level, explanation, and recommended action."
        ),
        "km": (
            "*របៀបប្រើប្រាស់ bot នេះ*\n\n"
            "សូមផ្ញើមកខ្ញុំមួយក្នុងចំណោមខាងក្រោមដើម្បីស្កេន៖\n"
            "• បញ្ជូនបន្តសារសង្ស័យ\n"
            "• ផ្ញើឯកសារ\n"
            "• តំណភ្ជាប់ (URL)\n"
            "• ឬវាយសរសេរដោយផ្ទាល់\n\n"
            "ខ្ញុំនឹងឆ្លើយតបជាមួយកម្រិតហានិភ័យ ការពន្យល់ និងការណែនាំ។"
        ),
    },
    "secure_account": {
        "en": (
            "🔒 *Secure your account*\n\n"
            "• Enable two-factor authentication (2FA) on Telegram and other important accounts.\n"
            "• Never share OTP codes or verification codes with anyone, even someone claiming to be support.\n"
            "• Verify the sender and the real link before clicking anything.\n"
            "• Check Telegram Settings → Devices and log out of sessions you don't recognize.\n"
            "• Be cautious of messages impersonating banks, government agencies, or Telegram itself."
        ),
        "km": (
            "🔒 *ការពារគណនីអ្នក*\n\n"
            "• បើកការផ្ទៀងផ្ទាត់ពីរជាន់ (2FA) នៅលើ Telegram និងគណនីសំខាន់ៗផ្សេងទៀត។\n"
            "• កុំចែករំលែកលេខកូដ OTP ឬលេខកូដផ្ទៀងផ្ទាត់ជាមួយអ្នកណាម្នាក់ឡើយ សូម្បីតែអ្នកអះអាងថាជាផ្នែកជំនួយ។\n"
            "• ត្រួតពិនិត្យអ្នកផ្ញើ និងតំណភ្ជាប់ពិតមុននឹងចុច។\n"
            "• ចូលទៅ Settings → Devices ហើយចាកចេញពីសម័យដែលអ្នកមិនស្គាល់។\n"
            "• ប្រយ័ត្នចំពោះសារក្លែងបន្លំពីធនាគារ ភ្នាក់ងាររដ្ឋាភិបាល ឬ Telegram ខ្លួនឯង។"
        ),
    },
    "password": {
        "en": (
            "🔑 *Password tips*\n\n"
            "• Use a unique password for every account or app.\n"
            "• Consider using a password manager to generate and store strong passwords.\n"
            "• Prefer long passphrases (e.g. P@assword1234) over short complex strings.\n"
            "• Avoid personal info like birthdays or names in your passwords."
        ),
        "km": (
            "🔑 *គន្លឹះពាក្យសម្ងាត់*\n\n"
            "• ប្រើពាក្យសម្ងាត់តែមួយគត់សម្រាប់គណនី ឬកម្មវិធីនីមួយៗ។\n"
            "• ពិចារណាប្រើកម្មវិធីគ្រប់គ្រងពាក្យសម្ងាត់ដើម្បីបង្កើត និងរក្សាទុកពាក្យសម្ងាត់រឹងមាំ។\n"
            "• គួរប្រើឃ្លាវែង (ឧទាហរណ៍ P@assword1234) ជាជាងខ្សែអក្សរខ្លីស្មុគស្មាញ។\n"
            "• ជៀសវាងព័ត៌មានផ្ទាល់ខ្លួនដូចជាថ្ងៃខែឆ្នាំកំណើត ឬឈ្មោះក្នុងពាក្យសម្ងាត់របស់អ្នក។"
        ),
    },
    "add_to_group": {
        "en": (
            "👥 *Add me to a group*\n\n"
            "1. Open the group and go to group info.\n"
            "2. Tap *Add Member*.\n"
            "3. Search for this bot's username and select it.\n"
            "4. I'll scan messages for scams/malware in scan-only mode — no moderation, just alerts."
        ),
        "km": (
            "👥 *បន្ថែមខ្ញុំទៅក្រុម*\n\n"
            "១. បើកក្រុម ហើយចូលទៅព័ត៌មានក្រុម។\n"
            "២. ចុច *Add Member*។\n"
            "៣. ស្វែងរកឈ្មោះអ្នកប្រើរបស់ bot នេះ ហើយជ្រើសរើសវា។\n"
            "៤. ខ្ញុំនឹងស្កេនសារដើម្បីរកការបោកប្រាស់/មេរោគ ជាមុខងារស្កេនតែប៉ុណ្ណោះ — មិនមានសកម្មភាពគ្រប់គ្រងទេ គ្រាន់តែជូនដំណឹង។"
        ),
    },
    "donate": {
        "en": (
            "❤️ *Support this project*\n\n"
            "Your contribution helps cover AI and VirusTotal API costs so this bot can keep protecting the community."
        ),
        "km": (
            "❤️ *គាំទ្រគម្រោងនេះ*\n\n"
            "ការចូលរួមចំណែករបស់អ្នកជួយគ្របដណ្តប់ចំណាយលើ AI និង VirusTotal API ដើម្បីឱ្យ bot នេះបន្តការពារសហគមន៍។"
        ),
    },
}


async def _resolve_language(
    update: Update,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> str | None:
    if update.effective_chat.type == "private":
        return await user_pref_repo.get_language(update.effective_user.id)
    return await group_pref_repo.get_language(update.effective_chat.id)


def _content_for(topic: str, language: str | None) -> str:
    content = _TOPIC_CONTENT[topic]
    if language:
        return content[language]
    return f"{content['en']}\n\n{content['km']}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        _WELCOME, reply_markup=LANGUAGE_KEYBOARD, parse_mode=ParseMode.MARKDOWN
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    await update.message.reply_text(_content_for("help", language), parse_mode=ParseMode.MARKDOWN)


async def use_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    await update.message.reply_text(_content_for("use", language), parse_mode=ParseMode.MARKDOWN)


async def secure_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    await update.message.reply_text(_content_for("secure_account", language), parse_mode=ParseMode.MARKDOWN)


async def password_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    await update.message.reply_text(_content_for("password", language), parse_mode=ParseMode.MARKDOWN)


async def addgroup_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    await update.message.reply_text(_content_for("add_to_group", language), parse_mode=ParseMode.MARKDOWN)


_LANGUAGE_PROMPT = {
    "en": "🌐 Current language: *English*",
    "km": "🌐 ភាសាបច្ចុប្បន្ន៖ *ខ្មែរ*",
}
_LANGUAGE_PROMPT_NO_PREFERENCE = "🌐 Choose your language / សូមជ្រើសរើសភាសា:"


async def language_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    text = _LANGUAGE_PROMPT[language] if language else _LANGUAGE_PROMPT_NO_PREFERENCE
    await update.message.reply_text(
        text, reply_markup=other_language_keyboard(language), parse_mode=ParseMode.MARKDOWN
    )


async def donate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    language = await _resolve_language(update, user_pref_repo, group_pref_repo)
    caption = _content_for("donate", language)

    if _DONATE_QR_PATH.exists():
        with open(_DONATE_QR_PATH, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode=ParseMode.MARKDOWN)
        return

    await update.message.reply_text(caption, parse_mode=ParseMode.MARKDOWN)
