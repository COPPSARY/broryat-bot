import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers.commands import (
    addgroup_command,
    donate_command,
    help_command,
    language_command,
    password_command,
    secure_command,
    use_command,
)
from bot.handlers.formatting import format_response
from bot.handlers.keyboards import resolve_menu_topic, virustotal_keyboard
from bot.handlers.progress import run_with_progress
from bot.handlers.reply import edit_with_markdown, reply_with_markdown
from bot.schemas.scan import ScanRequest
from bot.services.ai.image_extractor import HuggingFaceImageExtractor, ImageExtractionError
from bot.services.pipeline import ScanPipeline
from bot.utils.file_types import MAX_FILE_SIZE_BYTES
from bot.utils.images import is_image_document, prepare_image_for_ocr
from bot.utils.language import detect_language
from bot.utils.trusted_domains import is_own_domain, is_trusted_domain
from bot.utils.url_extraction import extract_urls, is_message_only_urls

_FORWARD_ONLY_FALLBACK = {
    "en": (
        "Sorry, I can only check messages that someone else sent you. "
        "If you got a suspicious message, please press and hold it, tap "
        "*Forward*, and send it to me here — I'll check it for you right away."
    ),
    "km": (
        "សូមអភ័យទោស ខ្ញុំអាចត្រួតពិនិត្យបានតែសារដែលអ្នកដទៃផ្ញើមកអ្នកប៉ុណ្ណោះ។ "
        "ប្រសិនបើអ្នកទទួលបានសារគួរឱ្យសង្ស័យ សូមចុចសង្កត់លើសារនោះ ចុច "
        "*បញ្ជូនបន្ត (Forward)* រួចផ្ញើមកខ្ញុំ ខ្ញុំនឹងត្រួតពិនិត្យជូនភ្លាមៗ។"
    ),
}


def _forward_only_fallback(language: str | None) -> str:
    if language:
        return _FORWARD_ONLY_FALLBACK[language]
    return f"{_FORWARD_ONLY_FALLBACK['en']}\n\n{_FORWARD_ONLY_FALLBACK['km']}"


_TRUSTED_SITE = {
    "en": "✅ This is a well-known, trusted website. No scan needed.",
    "km": "✅ នេះជាគេហទំព័រផ្លូវការដែលគេស្គាល់ទូទៅ និងមានសុវត្ថិភាពខ្ពស់។ លោកអ្នកអាចទុកចិត្តបាន ដោយមិនបាច់ត្រូវការស្កេនឡើយបាទ/ចាស! ",
}


def _trusted_site_message(language: str | None) -> str:
    if language:
        return _TRUSTED_SITE[language]
    return f"{_TRUSTED_SITE['en']}\n\n{_TRUSTED_SITE['km']}"


_OWN_WEBSITE = {
    "en": "🤖 This is our official website. Please rest assured, there is no need to scan it!",
    "km": "🤖 នេះជាគេហទំព័រផ្លូវការរបស់ពួកយើងខ្ញុំផ្ទាល់។ សូមលោកអ្នកកុំបារម្ភអី បណ្តាញនេះមានសុវត្ថិភាពខ្ពស់ និងមិនបាច់ត្រូវការស្កេនឡើយបាទ/ចាស! ",
}


def _own_website_message(language: str | None) -> str:
    if language:
        return _OWN_WEBSITE[language]
    return f"{_OWN_WEBSITE['en']}\n\n{_OWN_WEBSITE['km']}"


def _is_lone_link(text: str, urls: list[str]) -> bool:
    return len(urls) == 1 and is_message_only_urls(text, urls)


def _is_lone_trusted_link(text: str, urls: list[str]) -> bool:
    return _is_lone_link(text, urls) and is_trusted_domain(urls[0])


def _is_lone_own_website_link(text: str, urls: list[str]) -> bool:
    return _is_lone_link(text, urls) and is_own_domain(urls[0])


_DAILY_LIMIT = 2

_LIMIT_REACHED = {
    "en": "🚦 You've used your 2 free scans for today. Please try again in 24 hours.",
    "km": "🚦 អ្នកបានប្រើប្រាស់ការស្កេនចំនួន ២ ដងសម្រាប់ថ្ងៃនេះអស់ហើយ។ សូមព្យាយាមម្តងទៀតក្នុងរយៈពេល ២៤ម៉ោង។",
}

_MAX_SIZE_REACHED = {
    "en": "🚦 The file you sent is too large to scan. Please send a smaller file.",
    "km": "🚦 ឯកសារដែលអ្នកផ្ញើមកមានទំហំធំពេក ដើម្បីស្កេន។ សូមផ្ញើឯកសារតូចជាងនេះ។",
}


def _limit_reached_message(language: str | None) -> str:
    if language:
        return _LIMIT_REACHED[language]
    return f"{_LIMIT_REACHED['en']}\n\n{_LIMIT_REACHED['km']}"


def _max_size_message(language: str | None) -> str:
    if language:
        return _MAX_SIZE_REACHED[language]
    return f"{_MAX_SIZE_REACHED['en']}\n\n{_MAX_SIZE_REACHED['km']}"


_NO_TEXT_IN_IMAGE = {
    "en": (
        "🖼️ I couldn't find any readable text in that image. If it's a suspicious "
        "message, try forwarding the original text to me instead."
    ),
    "km": (
        "🖼️ ខ្ញុំមិនអាចរកឃើញអក្សរនៅក្នុងរូបភាពនោះទេ។ ប្រសិនបើវាជាសារគួរឱ្យសង្ស័យ "
        "សូមព្យាយាមបញ្ជូនបន្តជាអក្សរដើមមកខ្ញុំវិញ។"
    ),
}

_IMAGE_READ_FAILED = {
    "en": "⚠️ Sorry, I couldn't read that image right now. Please try again in a moment.",
    "km": "⚠️ សូមអភ័យទោស ខ្ញុំមិនអាចអានរូបភាពនោះបានទេនៅពេលនេះ។ សូមព្យាយាមម្តងទៀត។",
}


def _no_text_in_image_message(language: str | None) -> str:
    if language:
        return _NO_TEXT_IN_IMAGE[language]
    return f"{_NO_TEXT_IN_IMAGE['en']}\n\n{_NO_TEXT_IN_IMAGE['km']}"


def _image_read_failed_message(language: str | None) -> str:
    if language:
        return _IMAGE_READ_FAILED[language]
    return f"{_IMAGE_READ_FAILED['en']}\n\n{_IMAGE_READ_FAILED['km']}"


_MENU_HANDLERS = {
    "use": use_command,
    "secure": secure_command,
    "password": password_command,
    "add_to_group": addgroup_command,
    "donate": donate_command,
    "help": help_command,
    "language": language_command,
}


def _input_type(text: str | None, urls: list[str], forwarded: bool) -> str:
    if forwarded:
        return "forwarded"
    if urls:
        stripped = text or ""
        for url in urls:
            stripped = stripped.replace(url, "")
        if not stripped.strip():
            return "url"
    return "text"


async def handle_private_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline: ScanPipeline,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
    image_extractor: HuggingFaceImageExtractor,
) -> None:
    message = update.message
    document = message.document

    if document is None:
        menu_topic = resolve_menu_topic(message.text or "")
        if menu_topic is not None:
            await _MENU_HANDLERS[menu_topic](update, context, user_pref_repo, group_pref_repo)
            return

    stored_language = await user_pref_repo.get_language(message.from_user.id)
    await user_pref_repo.set_username(message.from_user.id, message.from_user.username)

    if document is not None:
        if document.file_size > MAX_FILE_SIZE_BYTES:
            await reply_with_markdown(message, _max_size_message(stored_language))
            return

        if is_image_document(document.file_name, document.mime_type):
            tg_file = await context.bot.get_file(document.file_id)
            raw = bytes(await tg_file.download_as_bytearray())
            image_bytes, mime_type = prepare_image_for_ocr(raw, document.mime_type, document.file_name)
            await _run_image_scan(message, pipeline, image_extractor, stored_language, image_bytes, mime_type)
            return

        tg_file = await context.bot.get_file(document.file_id)
        tmp_dir = tempfile.mkdtemp()
        file_path = str(Path(tmp_dir) / document.file_name)
        await tg_file.download_to_drive(file_path)

        text = message.caption
        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="private",
            input_type="file",
            text=text,
            file_path=file_path,
            file_name=document.file_name,
            language=stored_language or (detect_language(text) if text else "en"),
        )
    else:
        text = message.text or ""
        urls = extract_urls(text)
        forwarded = getattr(message, "forward_origin", None) is not None

        if not urls and not forwarded:
            await reply_with_markdown(message, _forward_only_fallback(stored_language))
            return

        if _is_lone_own_website_link(text, urls):
            await reply_with_markdown(message, _own_website_message(stored_language))
            return

        if _is_lone_trusted_link(text, urls):
            await reply_with_markdown(message, _trusted_site_message(stored_language))
            return

        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="private",
            input_type=_input_type(text, urls, forwarded),
            text=text,
            urls=urls,
            language=stored_language or detect_language(text),
        )

    if not await pipeline.was_recently_scanned(request) and (
        await pipeline.count_recent_scans("private", message.from_user.id) >= _DAILY_LIMIT
    ):
        await reply_with_markdown(message, _limit_reached_message(request.language))
        return

    await run_private_scan(message, pipeline, request.language, request)


async def handle_private_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline: ScanPipeline,
    image_extractor: HuggingFaceImageExtractor,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    message = update.message
    stored_language = await user_pref_repo.get_language(message.from_user.id)
    await user_pref_repo.set_username(message.from_user.id, message.from_user.username)

    tg_file = await context.bot.get_file(message.photo[-1].file_id)
    image_bytes = bytes(await tg_file.download_as_bytearray())

    await _run_image_scan(message, pipeline, image_extractor, stored_language, image_bytes, "image/jpeg")


async def _run_image_scan(
    message,
    pipeline: ScanPipeline,
    image_extractor: HuggingFaceImageExtractor,
    stored_language: str | None,
    image_bytes: bytes,
    mime_type: str,
) -> None:
    try:
        text = await image_extractor.extract_text(image_bytes, mime_type)
    except ImageExtractionError:
        await reply_with_markdown(message, _image_read_failed_message(stored_language))
        return

    if not text.strip():
        await reply_with_markdown(message, _no_text_in_image_message(stored_language))
        return

    urls = extract_urls(text)
    language = stored_language or detect_language(text)

    request = ScanRequest(
        chat_id=message.chat_id,
        user_id=message.from_user.id,
        chat_type="private",
        input_type="url" if urls else "text",
        text=text,
        urls=urls,
        language=language,
    )

    if not await pipeline.was_recently_scanned(request) and (
        await pipeline.count_recent_scans("private", message.from_user.id) >= _DAILY_LIMIT
    ):
        await reply_with_markdown(message, _limit_reached_message(language))
        return

    await run_private_scan(message, pipeline, language, request)


async def run_private_scan(message, pipeline: ScanPipeline, language: str, request: ScanRequest) -> None:
    placeholder, result = await run_with_progress(message, pipeline.run(request), language)
    await edit_with_markdown(
        placeholder, format_response(result), reply_markup=virustotal_keyboard(result, language)
    )
