from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot.schemas.scan import ScanResult

LANGUAGE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ", callback_data="lang:km"),
        ]
    ]
)


_VIEW_ANALYZE = {"en": "🔍 View Analysis on VirusTotal", "km": "🔍 មើលការវិភាគនៅលើ VirusTotal"}
_REPORT_URL = {"en": "🚩 Report this URL", "km": "🚩 រាយការណ៍តំណភ្ជាប់នេះ"}


def virustotal_keyboard(result: ScanResult, language: str) -> InlineKeyboardMarkup | None:
    buttons = []
    if result.vt_file is not None and result.vt_file.permalink:
        buttons.append(InlineKeyboardButton(_VIEW_ANALYZE[language], url=result.vt_file.permalink))
    if result.vt_url is not None and result.vt_url.permalink:
        buttons.append(InlineKeyboardButton(_VIEW_ANALYZE[language], url=result.vt_url.permalink))
    if result.vt_url is not None and result.scan_record_id is not None:
        buttons.append(
            InlineKeyboardButton(_REPORT_URL[language], callback_data=f"report:{result.scan_record_id}")
        )
    if not buttons:
        return None
    return InlineKeyboardMarkup([[button] for button in buttons])


_MENU_LABELS = {
    "use": {"en": "📖 How to Use", "km": "📖 របៀបប្រើប្រាស់"},
    "secure": {"en": "🔒 Secure Account", "km": "🔒 សុវត្ថិភាពគណនី"},
    "password": {"en": "🔑 Password", "km": "🔑 ពាក្យសម្ងាត់"},
    "add_to_group": {"en": "👥 Add to Group", "km": "👥 បន្ថែមទៅក្រុម"},
    "donate": {"en": "❤️ Donate", "km": "❤️ ឧបត្ថម្ភ"},
    "help": {"en": "❓ Help", "km": "❓ ជំនួយ"},
    "language": {"en": "🌐 Change Language", "km": "🌐 ប្តូរភាសា"},
}

_MENU_ROWS = [["use", "secure"], ["password", "add_to_group"], ["donate", "help"], ["language"]]

_TEXT_TO_TOPIC = {label: topic for topic, labels in _MENU_LABELS.items() for label in labels.values()}


def main_menu_keyboard(language: str) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(_MENU_LABELS[topic][language]) for topic in row] for row in _MENU_ROWS
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def resolve_menu_topic(text: str) -> str | None:
    return _TEXT_TO_TOPIC.get(text)


_LANGUAGE_BUTTONS = {
    "en": InlineKeyboardButton("🇬🇧 Switch to English", callback_data="lang:en"),
    "km": InlineKeyboardButton("🇰🇭 ប្តូរទៅភាសាខ្មែរ", callback_data="lang:km"),
}


def other_language_keyboard(current_language: str | None) -> InlineKeyboardMarkup:
    if current_language is None:
        return LANGUAGE_KEYBOARD
    other = "km" if current_language == "en" else "en"
    return InlineKeyboardMarkup([[_LANGUAGE_BUTTONS[other]]])
