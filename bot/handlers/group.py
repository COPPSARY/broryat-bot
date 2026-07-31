import asyncio
import tempfile
from pathlib import Path

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config.settings import DEFAULT_MAX_FILE_SIZE_BYTES
from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.handlers.formatting import format_response
from bot.handlers.keyboards import virustotal_keyboard
from bot.handlers.progress import run_with_progress
from bot.handlers.reply import edit_with_markdown, reply_with_markdown
from bot.schemas.scan import ScanRequest, ScanResult
from bot.services.pipeline import ScanPipeline
from bot.utils.images import is_image_document
from bot.utils.trusted_domains import is_own_domain, is_trusted_domain
from bot.utils.url_extraction import extract_urls, is_message_only_urls

_MALWARE_REMOVED = {
    "en": "⚠️ A message was removed — it contained a malicious link or file.",
    "km": "⚠️ សារមួយត្រូវបានលុបចេញ ដោយសារវាមានផ្ទុកលីងបោកប្រាស់ ឬឯកសារមានមេរោគ។",
}

_OWN_WEBSITE = {
    "en": "🤖 This is our own official website. No need to worry, and no scan needed!",
    "km": "🤖 នេះជាគេហទំព័រផ្លូវការរបស់ពួកយើងផ្ទាល់។ មិនចាំបាច់បារម្ភទេ ហើយក៏មិនចាំបាច់ស្កេនដែរ!",
}


def _is_vt_malicious(result: ScanResult) -> bool:
    return (result.vt_file is not None and result.vt_file.status == "malicious") or (
        result.vt_url is not None and result.vt_url.status == "malicious"
    )


def _is_lone_link(text: str, urls: list[str]) -> bool:
    return len(urls) == 1 and is_message_only_urls(text, urls)


def _is_lone_trusted_link(text: str, urls: list[str]) -> bool:
    return _is_lone_link(text, urls) and is_trusted_domain(urls[0])


def _is_lone_own_website_link(text: str, urls: list[str]) -> bool:
    return _is_lone_link(text, urls) and is_own_domain(urls[0])


_DAILY_LIMIT = 2

_LIMIT_REACHED = {
    "en": "🚦 Your group has used its 2 free scans for today. Please try again in 24 hours.",
    "km": "🚦 ក្រុមរបស់អ្នកបានប្រើប្រាស់ការស្កេនចំនួន ២ ដងសម្រាប់ថ្ងៃនេះអស់ហើយ។ សូមព្យាយាមម្តងទៀតក្នុងរយៈពេល ២៤ម៉ោង។",
}

_MAX_SIZE_REACHED = {
    "en": "🚦 The file you sent is too large to scan. Please send a smaller file.",
    "km": "🚦 ឯកសារដែលអ្នកផ្ញើមកមានទំហំធំពេក ដើម្បីស្កេន។ សូមផ្ញើឯកសារតូចជាងនេះ។",
}

_LIMIT_NOTIFIED: set[int] = set()


async def handle_group_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline: ScanPipeline,
    group_pref_repo: GroupPreferenceRepository,
    group_scan_enabled: bool,
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> None:
    if not group_scan_enabled:
        return

    message = update.message

    # GIFs arrive as an animation (Telegram converts them to MP4); never scan them.
    if message.animation is not None:
        return

    document = message.document
    text = message.text or ""
    urls = extract_urls(text) if document is None else []

    if document is None and not urls:
        return

    # OCR is private-only; in groups we don't scan images at all.
    if document is not None and is_image_document(document.file_name, document.mime_type):
        return

    stored_language = await group_pref_repo.get_language(message.chat_id)
    language = stored_language or "km"
    await group_pref_repo.set_group_name(message.chat_id, message.chat.title)

    if document is None and _is_lone_own_website_link(text, urls):
        await reply_with_markdown(message, _OWN_WEBSITE[language])
        return

    if document is None and _is_lone_trusted_link(text, urls):
        return

    if document is not None:
        if document.file_size > max_file_size_bytes:
            await reply_with_markdown(message, _MAX_SIZE_REACHED[language])
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

    if not await pipeline.was_recently_scanned(request) and (
        await pipeline.count_recent_scans("group", message.chat_id) >= _DAILY_LIMIT
    ):
        if message.chat_id not in _LIMIT_NOTIFIED:
            _LIMIT_NOTIFIED.add(message.chat_id)
            placeholder = await reply_with_markdown(message, _LIMIT_REACHED[language])
            await asyncio.sleep(3)
            await placeholder.delete()
        return

    _LIMIT_NOTIFIED.discard(message.chat_id)
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
