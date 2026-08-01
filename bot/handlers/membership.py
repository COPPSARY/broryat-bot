from telegram import Update
from telegram.ext import ContextTypes

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository

_INACTIVE_STATUSES = {"left", "kicked"}


async def handle_bot_membership_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    group_pref_repo: GroupPreferenceRepository,
    user_pref_repo: UserPreferenceRepository,
) -> None:
    """Record who added the bot to a group when its own membership status changes."""
    change = update.my_chat_member
    if change is None:
        return

    old_status = change.old_chat_member.status
    new_status = change.new_chat_member.status
    if old_status not in _INACTIVE_STATUSES or new_status in _INACTIVE_STATUSES:
        return

    chat_id = change.chat.id
    adder = change.from_user

    await group_pref_repo.set_group_name(chat_id, change.chat.title)
    if adder is not None:
        await group_pref_repo.set_added_by(chat_id, adder.id)
        await user_pref_repo.set_username(adder.id, adder.username)
        await user_pref_repo.set_name(adder.id, adder.first_name, adder.last_name)
