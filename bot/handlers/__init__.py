from functools import partial

from telegram import BotCommand
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.report_repository import ReportRepository
from bot.database.repository import ScanRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers.commands import (
    addgroup_command,
    donate_command,
    help_command,
    language_command,
    password_command,
    secure_command,
    start_command,
    use_command,
)
from bot.handlers.email_breach import email_command
from bot.handlers.group import handle_group_message
from bot.handlers.language import handle_language_choice
from bot.handlers.media import handle_unsupported_media
from bot.handlers.private import handle_private_message, handle_private_photo
from bot.handlers.report import handle_report_callback
from bot.services.ai.image_extractor import HuggingFaceImageExtractor
from bot.services.breach_check.client import BreachCheckClient
from bot.services.pipeline import ScanPipeline

BOT_COMMANDS = [
    BotCommand("start", "Welcome & choose your language"),
    BotCommand("help", "How to use this bot"),
    BotCommand("use", "How to use this bot"),
    BotCommand("secure", "How to secure your account"),
    BotCommand("password", "Password tips"),
    BotCommand("addgroup", "How to add me to a group"),
    BotCommand("donate", "Support this project"),
    BotCommand("language", "Change your language"),
    BotCommand("email", "Check if an email was in a data breach"),
]


async def set_bot_commands(app: Application) -> None:
    await app.bot.set_my_commands(BOT_COMMANDS)


def register_handlers(
    app: Application,
    pipeline: ScanPipeline,
    group_scan_enabled: bool,
    user_pref_repo: UserPreferenceRepository,
    group_pref_repo: GroupPreferenceRepository,
    report_repo: ReportRepository,
    scan_repo: ScanRepository,
    admin_chat_id: int | None,
    breach_client: BreachCheckClient,
    image_extractor: HuggingFaceImageExtractor,
) -> None:
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(
        CommandHandler(
            "help",
            partial(help_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )
    app.add_handler(
        CommandHandler(
            "use",
            partial(use_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )
    app.add_handler(
        CommandHandler(
            "secure",
            partial(secure_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )
    app.add_handler(
        CommandHandler(
            "password",
            partial(password_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )
    app.add_handler(
        CommandHandler(
            "addgroup",
            partial(addgroup_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )
    app.add_handler(
        CommandHandler(
            "donate",
            partial(donate_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )
    app.add_handler(
        CommandHandler(
            "language",
            partial(language_command, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
        )
    )

    app.add_handler(
        CommandHandler(
            "email",
            partial(
                email_command,
                breach_client=breach_client,
                user_pref_repo=user_pref_repo,
                group_pref_repo=group_pref_repo,
            ),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            partial(handle_language_choice, user_pref_repo=user_pref_repo, group_pref_repo=group_pref_repo),
            pattern="^lang:",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            partial(
                handle_report_callback,
                report_repo=report_repo,
                scan_repo=scan_repo,
                admin_chat_id=admin_chat_id,
            ),
            pattern="^report:",
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.TEXT | filters.Document.ALL),
            partial(
                handle_private_message,
                pipeline=pipeline,
                user_pref_repo=user_pref_repo,
                group_pref_repo=group_pref_repo,
                image_extractor=image_extractor,
            ),
        )
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & (filters.TEXT | filters.Document.ALL),
            partial(
                handle_group_message,
                pipeline=pipeline,
                group_pref_repo=group_pref_repo,
                group_scan_enabled=group_scan_enabled,
            ),
        )
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.PHOTO,
            partial(
                handle_private_photo,
                pipeline=pipeline,
                image_extractor=image_extractor,
                user_pref_repo=user_pref_repo,
                group_pref_repo=group_pref_repo,
            ),
        )
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.VIDEO,
            partial(
                handle_unsupported_media,
                pipeline=pipeline,
                user_pref_repo=user_pref_repo,
                group_pref_repo=group_pref_repo,
            ),
        )
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & (filters.PHOTO | filters.VIDEO),
            partial(
                handle_unsupported_media,
                pipeline=pipeline,
                user_pref_repo=user_pref_repo,
                group_pref_repo=group_pref_repo,
            ),
        )
    )
