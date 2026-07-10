import asyncio
import tempfile
from pathlib import Path

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.handlers.formatting import format_response
from bot.handlers.keyboards import virustotal_keyboard
from bot.handlers.progress import run_with_progress
from bot.handlers.reply import edit_with_markdown
from bot.schemas.scan import ScanRequest, ScanResult
from bot.services.pipeline import ScanPipeline
from bot.utils.file_types import MAX_FILE_SIZE_BYTES
from bot.utils.trusted_domains import is_trusted_domain
from bot.utils.url_extraction import extract_urls, is_message_only_urls

_MALWARE_REMOVED = {
    "en": "⚠️ A message was removed — it contained a malicious link or file.",
    "km": "⚠️ សារមួយត្រូវបានលុបចេញ ដោយសារវាមានផ្ទុកលីងបោកប្រាស់ ឬឯកសារមានមេរោគ។",
}


def _is_vt_malicious(result: ScanResult) -> bool:
    return (result.vt_file is not None and result.vt_file.status == "malicious") or (
        result.vt_url is not None and result.vt_url.status == "malicious"
    )


def _is_lone_trusted_link(text: str, urls: list[str]) -> bool:
    return len(urls) == 1 and is_message_only_urls(text, urls) and is_trusted_domain(urls[0])


_DAILY_LIMIT = 2

_LIMIT_REACHED = {
    "en": "🚦 This group has used its 2 free scans for today. Please try again in 24 hours.",
    "km": "🚦 ក្រុមនេះបានប្រើប្រាស់ការស្កេនចំនួន ២ ដងសម្រាប់ថ្ងៃនេះអស់ហើយ។ សូមព្យាយាមម្តងទៀតក្នុងរយៈពេល ២៤ម៉ោង។",
}


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
    document = message.document
    text = message.text or ""
    urls = extract_urls(text) if document is None else []

    if document is None and not urls:
        return

    if document is None and _is_lone_trusted_link(text, urls):
        return

    stored_language = await group_pref_repo.get_language(message.chat_id)
    language = stored_language or "km"

    if document is not None:
        if document.file_size > MAX_FILE_SIZE_BYTES:
            await message.reply_text("Sorry, this file is too large to scan.")
            return

        tg_file = await context.bot.get_file(document.file_id)
        tmp_dir = tempfile.mkdtemp()
        file_path = str(Path(tmp_dir) / document.file_name)
        await tg_file.download_to_drive(file_path)

        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="group",
            input_type="file",
            text=message.caption,
            file_path=file_path,
            file_name=document.file_name,
            language=language,
        )
    else:
        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="group",
            input_type="url",
            text=text,
            urls=urls,
            language=language,
        )

    if await pipeline.count_recent_scans("group", message.chat_id) >= _DAILY_LIMIT:
        await message.reply_text(_LIMIT_REACHED[language])
        return

    await run_group_scan(message, context, pipeline, language, request)


async def run_group_scan(
    message,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline: ScanPipeline,
    language: str,
    request: ScanRequest,
) -> None:
    placeholder, result = await run_with_progress(message, pipeline.run(request), language)

    if _is_vt_malicious(result):
        await asyncio.sleep(5)
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        except TelegramError:
            await edit_with_markdown(
                placeholder, format_response(result), reply_markup=virustotal_keyboard(result, language)
            )
            return
        await placeholder.edit_text(_MALWARE_REMOVED[language])
        return

    await edit_with_markdown(
        placeholder, format_response(result), reply_markup=virustotal_keyboard(result, language)
    )
    await asyncio.sleep(5)
    await placeholder.delete()
