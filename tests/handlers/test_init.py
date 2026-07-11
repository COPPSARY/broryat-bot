from unittest.mock import AsyncMock, MagicMock

from telegram.ext import CommandHandler, MessageHandler

from bot.handlers import register_handlers, set_bot_commands
from bot.handlers.group import handle_group_message
from bot.handlers.media import handle_unsupported_media


async def test_set_bot_commands_registers_all_topic_commands():
    app = MagicMock()
    app.bot.set_my_commands = AsyncMock()

    await set_bot_commands(app)

    app.bot.set_my_commands.assert_awaited_once()
    commands = app.bot.set_my_commands.call_args[0][0]
    command_names = {c.command for c in commands}
    assert command_names == {
        "start", "help", "use", "secure", "password", "addgroup", "donate", "language", "email",
    }


def _register(app):
    register_handlers(
        app,
        pipeline=MagicMock(),
        group_scan_enabled=True,
        user_pref_repo=MagicMock(),
        group_pref_repo=MagicMock(),
        report_repo=MagicMock(),
        scan_repo=MagicMock(),
        admin_chat_id=None,
        breach_client=MagicMock(),
    )


def _message_handlers(app):
    return [call.args[0] for call in app.add_handler.call_args_list if isinstance(call.args[0], MessageHandler)]


def test_register_handlers_wires_media_handler_for_both_chat_types():
    app = MagicMock()
    _register(app)

    media_handlers = [
        h for h in _message_handlers(app) if getattr(h.callback, "func", None) is handle_unsupported_media
    ]
    assert len(media_handlers) == 2
    filter_reprs = {repr(h.filters) for h in media_handlers}
    assert any("PRIVATE" in r and "PHOTO" in r and "VIDEO" in r for r in filter_reprs)
    assert any("GROUPS" in r and "PHOTO" in r and "VIDEO" in r for r in filter_reprs)


def test_register_handlers_group_filter_now_includes_documents():
    app = MagicMock()
    _register(app)

    group_handler = next(
        h for h in _message_handlers(app) if getattr(h.callback, "func", None) is handle_group_message
    )
    filter_repr = repr(group_handler.filters)
    assert "GROUPS" in filter_repr
    assert "TEXT" in filter_repr
    assert "Document" in filter_repr


def test_registers_email_command():
    app = MagicMock()
    _register(app)

    email_handlers = [
        call.args[0]
        for call in app.add_handler.call_args_list
        if isinstance(call.args[0], CommandHandler) and "email" in call.args[0].commands
    ]
    assert len(email_handlers) == 1
