from datetime import datetime, timedelta, timezone

from sqlalchemy import BigInteger

from bot.models.group_preference import GroupPreference


def test_group_preference_holds_chat_id_and_language():
    pref = GroupPreference(chat_id=-1001234567890, language="km")
    assert pref.chat_id == -1001234567890
    assert pref.language == "km"


def test_group_preference_auto_generates_updated_at_in_phnom_penh_time():
    pref = GroupPreference(chat_id=1, language="en")
    assert pref.updated_at.utcoffset() == timedelta(hours=7)
    assert (datetime.now(timezone.utc) - pref.updated_at).total_seconds() < 5


def test_chat_id_column_is_primary_key_and_big_integer():
    columns = GroupPreference.__table__.columns
    assert columns["chat_id"].primary_key is True
    assert isinstance(columns["chat_id"].type, BigInteger)


def test_group_preference_accepts_supergroup_chat_id_beyond_int32_range():
    pref = GroupPreference(chat_id=-1001234567890123, language="en")
    assert pref.chat_id == -1001234567890123


def test_group_preference_group_name_defaults_to_none():
    pref = GroupPreference(chat_id=1, language="en")
    assert pref.group_name is None


def test_group_preference_holds_group_name():
    pref = GroupPreference(chat_id=1, language="en", group_name="Scam Watch")
    assert pref.group_name == "Scam Watch"


def test_group_preference_language_defaults_to_none():
    pref = GroupPreference(chat_id=1)
    assert pref.language is None


def test_group_preference_added_by_user_id_defaults_to_none():
    pref = GroupPreference(chat_id=1)
    assert pref.added_by_user_id is None


def test_group_preference_holds_added_by_user_id():
    pref = GroupPreference(chat_id=1, added_by_user_id=999)
    assert pref.added_by_user_id == 999
