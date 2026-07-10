from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers.keyboards import main_menu_keyboard

_CONFIRMATION = {
    "en": (
        "✅ Language set to *English*.\n\n"
        "*How to use me:*\n"
        "• Forward a suspicious message\n"
        "• Send me a file\n"
        "• Paste a URL\n"
        "• Or just type it out\n\n"
        "I'll reply with a risk level, explanation, and recommended action."
    ),
    "km": (
        "✅ បានកំណត់ភាសាទៅជា *ភាសាខ្មែរ*។\n\n"
        "*របៀបប្រើប្រាស់៖*\n"
        "• បញ្ជូនបន្តសារសង្ស័យ\n"
        "• ផ្ញើឯកសារ\n"
        "• តំណភា្ជប់ (URL)\n"
        "• ឬវាយសរសេរដោយផ្ទាល់\n\n"
        "ខ្ញុំនឹងឆ្លើយតបជាមួយកម្រិតហានិភ័យ ការពន្យល់ និងការណែនាំ។"
    ),
}


async def handle_language_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    query = update.callback_query
    language = query.data.split(":", 1)[1]

    if update.effective_chat.type == "private":
        await user_pref_repo.set_language(update.effective_user.id, language)
    else:
        await group_pref_repo.set_language(update.effective_chat.id, language)

    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_CONFIRMATION[language],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(language),
    )
