from unittest.mock import AsyncMock, MagicMock

from bot.handlers import set_bot_commands


async def test_set_bot_commands_registers_all_topic_commands():
    app = MagicMock()
    app.bot.set_my_commands = AsyncMock()

    await set_bot_commands(app)

    app.bot.set_my_commands.assert_awaited_once()
    commands = app.bot.set_my_commands.call_args[0][0]
    command_names = {c.command for c in commands}
    assert command_names == {
        "start", "help", "use", "secure", "password", "addgroup", "donate", "language",
    }
