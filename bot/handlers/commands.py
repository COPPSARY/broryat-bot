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
            "*របៀបប្រើប្រាស់ Bot នេះ*\n\n"
            "លោកអ្នកអាចផ្ញើរបស់ទាំងនេះមកឱ្យខ្ញុំពិនិត្យបាន៖\n"
            "• **Forward សារ៖** ចុចបញ្ជូនបន្តសារដែលអ្នកសង្ស័យមកឱ្យខ្ញុំ។\n"
            "• **ផ្ញើឯកសារ៖** ផ្ញើជាឯកសារ ដែលអ្នកចង់ពិនិត្យ។\n"
            "• **ផ្ញើលីង (URL)៖** ចម្លងលីងគេហទំព័រយកមកផ្ញើទីនេះ។\n"
            "• **វាយអក្សរផ្ទាល់៖** សរសេររៀបរាប់ ឬចម្លងអត្ថបទណាមួយមកដាក់។\n\n"
            "ខ្ញុំនឹងផ្ញើសារប្រាប់វិញភ្លាមៗ អំពីកម្រិតគ្រោះថ្នាក់ ការពន្យល់ និងដំបូន្មានថាអ្នកគួរធ្វើដូចម្តេចបន្ត។"
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
            "🔒 *របៀបការពារគណនីរបស់អ្នក*\n\n"
            "• **បើកប្រព័ន្ធការពារពីរជាន់ (2FA)៖** ត្រូវបើកវាទាំងនៅលើ Telegram និងកម្មវិធីសំខាន់ៗផ្សេងទៀត។\n"
            "• **ហាមប្រាប់លេខកូដសម្ងាត់ (OTP)៖** ដាច់ខាតកុំប្រាប់លេខកូដផ្ទៀងផ្ទាត់ដែលផ្ញើចូលទូរសព្ទទៅឱ្យអ្នកដទៃ សូម្បីតែអ្នកដែលអះអាងថាជាបុគ្គលិកក្រុមហ៊ុនក៏ដោយ។\n"
            "• **កុំអាលចុចលីង (Link)៖** ត្រូវពិនិត្យមើលឈ្មោះអ្នកផ្ញើ និងមើលប្រភពលីងឱ្យបានច្បាស់លាស់ មុននឹងចុចលើវា។\n"
            "• **ពិនិត្យមើលឧបករណ៍ប្លែកៗ៖** ចូលទៅកាន់ Settings → Devices បើសិនជាឃើញមានទូរសព្ទ ឬកុំព្យូទ័រប្លែកៗកំពុងលួចប្រើ Telegram របស់អ្នក ត្រូវចុចលុប (Log out) ចេញភ្លាម។\n"
            "• **ប្រយ័ត្នការបោកប្រាស់៖** ត្រូវប្រុងប្រយ័ត្នខ្ពស់ចំពោះសារផ្ញើមកក្លែងបន្លំធ្វើជា ធនាគារ ភ្នាក់ងាររដ្ឋាភិបាល ឬក្លែងធ្វើជាក្រុមហ៊ុន Telegram ផ្ទាល់។"
        ),
    },
    "password": {
        "en": (
            "🔑 *Simple tips for a safe password*\n\n"
            "• **Make it long:** Use a long phrase (at least 16 letters/numbers). Long passwords are much safer.\n"
            "• **One password per account:** Never use the same password for different apps or accounts.\n"
            "• **No personal info:** Do not use your name, birthday, or phone number as a password.\n"
            "• **Write it safely:** Use a secure Password Manager app, or write it down in a safe notebook at home."
        ),
        "km": (
            "🔑 *គន្លឹះងាយៗដើម្បីសុវត្ថិភាពពាក្យសម្ងាត់*\n\n"
            "• **ដាក់ឱ្យវែង៖** គួរប្រើពាក្យសម្ងាត់ឱ្យបានវែង (យ៉ាងតិច ១៦តួ) ព្រោះពាក្យសម្ងាត់កាន់តែវែង គឺកាន់តែមានសុវត្ថិភាព។\n"
            "• **កុំប្រើជាន់គ្នា៖** គណនី ឬកម្មវិធីមួយ ត្រូវប្រើពាក្យសម្ងាត់មួយផ្សេងៗគ្នា ហាមប្រើពាក្យសម្ងាត់ដូចគ្នាទាំងអស់។\n"
            "• **កុំប្រើប្រវត្តិផ្ទាល់ខ្លួន៖** ហាមយកឈ្មោះ ថ្ងៃខែឆ្នាំកំណើត ឬលេខទូរសព្ទ មកធ្វើជាពាក្យសម្ងាត់ ព្រោះគេងាយស្រួលទាយដឹង។\n"
            "• **កត់ត្រាទុកឱ្យមានសុវត្ថិភាព៖** កុំព្យាយាមចាំមាត់ទទេ គួរប្រើកម្មវិធីរក្សាទុកពាក្យសម្ងាត់ (Password Manager) ឬកត់ចូលសៀវភៅទុកនៅផ្ទះឱ្យមានរបៀប។"
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
            "👥 *របៀបផ្ទេរខ្ញុំចូលក្នុងក្រុម*\n\n"
            "១. បើកចូលទៅក្នុងក្រុម រួចចុចមើលព័ត៌មានក្រុម (Group Info)។\n"
            "២. ចុចពាក្យថា *បន្ថែមសមាជិក (Add Member)*។\n"
            "៣. វាយស្វែងរកឈ្មោះរបស់ខ្ញុំ (Bot) រួចចុចជ្រើសរើសយក។\n"
            "៤. ខ្ញុំនឹងជួយពិនិត្យមើលរាល់សារក្នុងក្រុម ដើម្បីស្វែងរកការបោកប្រាស់ ឬមេរោគផ្សេងៗ។ ខ្ញុំគ្រាន់តែជួយប្រកាសអាសន្ន ឬផ្ដល់ដំណឹងប្រាប់ប៉ុណ្ណោះ គឺមិនមានសិទ្ធិចាត់ការ ឬលុបនរណាចេញឡើយ។"
        ),
    },
    "donate": {
        "en": (
            "❤️ *Support this project*\n\n"
            "Your contribution helps cover running and AI maintenance costs so this bot can keep continuing to operate."
        ),
        "km": (
            "❤️ *គាំទ្រគម្រោងនេះ*\n\n"
            "ការចូលរួមឧបត្ថម្ភរបស់លោកអ្នក គឺដើម្បីជួយសម្រាលរាល់ការចំណាយលើការដំណើរការ និងការថែទាំប្រព័ន្ធ AI ដើម្បីឱ្យ Bot នេះអាចបន្តដំណើរការតទៅទៀត។"
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
