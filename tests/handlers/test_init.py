from unittest.mock import AsyncMock, MagicMock

from telegram import Chat, Message, Update, User
from telegram.ext import CommandHandler, MessageHandler

from bot.handlers import register_handlers, set_bot_commands
from bot.handlers.group import handle_group_message
from bot.handlers.media import handle_unsupported_media
from bot.handlers.private import handle_private_message, handle_private_photo


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
        image_extractor=MagicMock(),
        max_file_size_bytes=20 * 1024 * 1024,
    )


def _message_handlers(app):
    return [call.args[0] for call in app.add_handler.call_args_list if isinstance(call.args[0], MessageHandler)]


def test_register_handlers_routes_private_photos_to_the_ocr_handler():
    app = MagicMock()
    _register(app)

    photo_handlers = [
        h for h in _message_handlers(app) if getattr(h.callback, "func", None) is handle_private_photo
    ]
    assert len(photo_handlers) == 1
    filter_repr = repr(photo_handlers[0].filters)
    assert "PRIVATE" in filter_repr
    assert "PHOTO" in filter_repr


def test_register_handlers_wires_unsupported_media_for_private_video_and_group_media():
    app = MagicMock()
    _register(app)

    media_handlers = [
        h for h in _message_handlers(app) if getattr(h.callback, "func", None) is handle_unsupported_media
    ]
    assert len(media_handlers) == 2
    filter_reprs = {repr(h.filters) for h in media_handlers}
    assert any("PRIVATE" in r and "VIDEO" in r for r in filter_reprs)
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


def test_private_and_group_handlers_do_not_match_business_message_updates():
    # A business_message has a private chat and text, so without the UpdateType.MESSAGE
    # guard it would be swallowed by the private/group handlers, which read
    # update.message.animation and crash with AttributeError when update.message is None.
    app = MagicMock()
    _register(app)

    chat = Chat(id=1501880651, type="private", first_name="User")
    user = User(id=1501880651, is_bot=False, first_name="User")
    business = Message(
        message_id=270181,
        date=None,
        chat=chat,
        from_user=user,
        text="Hello there",
        business_connection_id="hsWkBM4dYVfKAwAA2rm3VZADwTk",
    )
    update = Update(update_id=369165443, business_message=business)

    for handler in _message_handlers(app):
        if getattr(handler.callback, "func", None) in (
            handle_private_message,
            handle_group_message,
            handle_private_photo,
            handle_unsupported_media,
        ):
            assert not handler.filters.check_update(update), handler
