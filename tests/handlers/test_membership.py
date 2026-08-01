from unittest.mock import AsyncMock, MagicMock

from bot.handlers.membership import handle_bot_membership_update


def _update(*, old_status="left", new_status="member", from_user_id=999, chat_id=-100123, chat_title="Scam Watch"):
    update = MagicMock()
    change = update.my_chat_member
    change.chat.id = chat_id
    change.chat.title = chat_title
    change.old_chat_member.status = old_status
    change.new_chat_member.status = new_status
    change.from_user.id = from_user_id
    change.from_user.username = "janedoe"
    change.from_user.first_name = "Jane"
    change.from_user.last_name = "Smith"
    return update


def _repos():
    return AsyncMock(), AsyncMock()


async def test_records_the_adder_when_bot_joins_a_group():
    update = _update()
    group_pref_repo, user_pref_repo = _repos()

    await handle_bot_membership_update(update, MagicMock(), group_pref_repo, user_pref_repo)

    group_pref_repo.set_added_by.assert_awaited_once_with(-100123, 999)
    group_pref_repo.set_group_name.assert_awaited_once_with(-100123, "Scam Watch")
    user_pref_repo.set_username.assert_awaited_once_with(999, "janedoe")
    user_pref_repo.set_name.assert_awaited_once_with(999, "Jane", "Smith")


async def test_records_the_adder_when_bot_is_promoted_from_kicked():
    update = _update(old_status="kicked", new_status="administrator")
    group_pref_repo, user_pref_repo = _repos()

    await handle_bot_membership_update(update, MagicMock(), group_pref_repo, user_pref_repo)

    group_pref_repo.set_added_by.assert_awaited_once_with(-100123, 999)


async def test_ignores_updates_that_are_not_a_join():
    update = _update(old_status="member", new_status="administrator")
    group_pref_repo, user_pref_repo = _repos()

    await handle_bot_membership_update(update, MagicMock(), group_pref_repo, user_pref_repo)

    group_pref_repo.set_added_by.assert_not_awaited()
    user_pref_repo.set_username.assert_not_awaited()


async def test_ignores_bot_being_removed():
    update = _update(old_status="member", new_status="kicked")
    group_pref_repo, user_pref_repo = _repos()

    await handle_bot_membership_update(update, MagicMock(), group_pref_repo, user_pref_repo)

    group_pref_repo.set_added_by.assert_not_awaited()


async def test_does_nothing_when_my_chat_member_is_missing():
    update = MagicMock()
    update.my_chat_member = None
    group_pref_repo, user_pref_repo = _repos()

    await handle_bot_membership_update(update, MagicMock(), group_pref_repo, user_pref_repo)

    group_pref_repo.set_added_by.assert_not_awaited()
