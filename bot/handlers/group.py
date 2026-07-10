from telegram import Update
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.handlers.formatting import format_response
from bot.handlers.keyboards import virustotal_keyboard
from bot.handlers.progress import run_with_progress
from bot.handlers.reply import edit_with_markdown
from bot.schemas.enums import RiskLevel
from bot.schemas.scan import ScanRequest
from bot.services.pipeline import ScanPipeline
from bot.utils.language import detect_language
from bot.utils.url_extraction import extract_urls

_NO_ISSUES = {"en": "✅ No issues found.", "km": "✅ រកមិនឃើញបញ្ហាទេ។"}


async def handle_group_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline: ScanPipeline,
    group_pref_repo: GroupPreferenceRepository,
    group_scan_enabled: bool,
) -> None:
    if not group_scan_enabled:
        return

    message = update.message
    text = message.text or ""
    urls = extract_urls(text)
    stored_language = await group_pref_repo.get_language(message.chat_id)

    request = ScanRequest(
        chat_id=message.chat_id,
        user_id=message.from_user.id,
        chat_type="group",
        input_type="url" if urls else "text",
        text=text,
        urls=urls,
        language=stored_language or detect_language(text),
    )

    placeholder, result = await run_with_progress(message, pipeline.run(request), request.language)

    if result.risk_level == RiskLevel.SAFE:
        await placeholder.edit_text(_NO_ISSUES[request.language])
    else:
        await edit_with_markdown(
            placeholder, format_response(result), reply_markup=virustotal_keyboard(result, request.language)
        )
