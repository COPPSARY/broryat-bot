from telegram import Update
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers.group import _DAILY_LIMIT, _LIMIT_REACHED as _GROUP_LIMIT_REACHED, run_group_scan
from bot.handlers.private import _limit_reached_message as _private_limit_reached_message, run_private_scan
from bot.schemas.scan import ScanRequest
from bot.services.pipeline import ScanPipeline
from bot.utils.language import detect_language
from bot.utils.trusted_domains import is_own_domain, is_trusted_domain
from bot.utils.url_extraction import extract_urls, is_message_only_urls

_MEDIA_NOT_SUPPORTED = {
    "en": "Sorry, I can't check photos or videos yet — please send text, a link, or a document instead.",
    "km": "សូមអភ័យទោស ខ្ញុំមិនទាន់អាចត្រួតពិនិត្យរូបភាព ឬវីដេអូបានទេ សូមផ្ញើជាអក្សរ តំណភ្ជាប់ ឬឯកសារជំនួសវិញ។",
}

_TRUSTED_SITE = {
    "en": "✅ This is a well-known, trusted website. No scan needed.",
    "km": "✅ នេះជាគេហទំព័រផ្លូវការដែលគេស្គាល់ទូទៅ និងមានសុវត្ថិភាពខ្ពស់។ លោកអ្នកអាចទុកចិត្តបាន ដោយមិនបាច់ត្រូវការស្កេនឡើយបាទ/ចាស! ",
}

_OWN_WEBSITE = {
    "en": "🤖 This is our official website. Please rest assured, there is no need to scan it!",
    "km": "🤖 នេះជាគេហទំព័រផ្លូវការរបស់ពួកយើងខ្ញុំផ្ទាល់។ សូមលោកអ្នកកុំបារម្ភអី បណ្តាញនេះមានសុវត្ថិភាពខ្ពស់ និងមិនបាច់ត្រូវការស្កេនឡើយបាទ/ចាស! ",
}


def _private_fallback_text(language: str | None) -> str:
    if language:
        return _MEDIA_NOT_SUPPORTED[language]
    return f"{_MEDIA_NOT_SUPPORTED['en']}\n\n{_MEDIA_NOT_SUPPORTED['km']}"


def _trusted_site_message(language: str | None) -> str:
    if language:
        return _TRUSTED_SITE[language]
    return f"{_TRUSTED_SITE['en']}\n\n{_TRUSTED_SITE['km']}"


def _own_website_message(language: str | None) -> str:
    if language:
        return _OWN_WEBSITE[language]
    return f"{_OWN_WEBSITE['en']}\n\n{_OWN_WEBSITE['km']}"


def _is_lone_link(caption: str, urls: list[str]) -> bool:
    return len(urls) == 1 and is_message_only_urls(caption, urls)


def _is_lone_trusted_link(caption: str, urls: list[str]) -> bool:
    return _is_lone_link(caption, urls) and is_trusted_domain(urls[0])


def _is_lone_own_website_link(caption: str, urls: list[str]) -> bool:
    return _is_lone_link(caption, urls) and is_own_domain(urls[0])


async def handle_unsupported_media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline: ScanPipeline,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
) -> None:
    message = update.message
    is_private = update.effective_chat.type == "private"
    caption = message.caption or ""
    urls = extract_urls(caption)

    if is_private:
        stored_language = await user_pref_repo.get_language(update.effective_user.id)
    else:
        stored_language = await group_pref_repo.get_language(message.chat_id)

    if not urls:
        if is_private:
            await message.reply_text(_private_fallback_text(stored_language))
        # In groups we stay silent for media we can't read.
        return

    if _is_lone_own_website_link(caption, urls):
        language = stored_language if is_private else (stored_language or "km")
        await message.reply_text(_own_website_message(language))
        return

    if _is_lone_trusted_link(caption, urls):
        if is_private:
            await message.reply_text(_trusted_site_message(stored_language))
        return

    if is_private:
        language = stored_language or detect_language(caption)
        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="private",
            input_type="url",
            text=caption,
            urls=urls,
            language=language,
        )
        if await pipeline.count_recent_scans("private", message.from_user.id) >= _DAILY_LIMIT:
            await message.reply_text(_private_limit_reached_message(language))
            return
        await run_private_scan(message, pipeline, language, request)
    else:
        language = stored_language or "km"
        request = ScanRequest(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            chat_type="group",
            input_type="url",
            text=caption,
            urls=urls,
            language=language,
        )
        if await pipeline.count_recent_scans("group", message.chat_id) >= _DAILY_LIMIT:
            await message.reply_text(_GROUP_LIMIT_REACHED[language])
            return
        await run_group_scan(message, context, pipeline, language, request)
