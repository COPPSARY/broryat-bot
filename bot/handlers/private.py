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
from bot.handlers.reply import edit_with_markdown
from bot.schemas.scan import ScanRequest
from bot.services.pipeline import ScanPipeline
from bot.utils.file_types import MAX_FILE_SIZE_BYTES
from bot.utils.language import detect_language
from bot.utils.url_extraction import extract_urls

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
) -> None:
    message = update.message
    document = message.document

    if document is None:
        menu_topic = resolve_menu_topic(message.text or "")
        if menu_topic is not None:
            await _MENU_HANDLERS[menu_topic](update, context, user_pref_repo, group_pref_repo)
            return

    stored_language = await user_pref_repo.get_language(message.from_user.id)

    if document is not None:
        if document.file_size > MAX_FILE_SIZE_BYTES:
            await message.reply_text("Sorry, this file is too large to scan.")
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
        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="private",
            input_type=_input_type(text, urls, forwarded),
            text=text,
            urls=urls,
            language=stored_language or detect_language(text),
        )

    placeholder, result = await run_with_progress(message, pipeline.run(request), request.language)
    await edit_with_markdown(
        placeholder, format_response(result), reply_markup=virustotal_keyboard(result, request.language)
    )
