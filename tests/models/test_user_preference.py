from datetime import datetime, timedelta, timezone

from sqlalchemy import BigInteger

from bot.models.user_preference import UserPreference


def test_user_preference_holds_user_id_and_language():
    pref = UserPreference(user_id=123, language="km")
    assert pref.user_id == 123
    assert pref.language == "km"


def test_user_preference_auto_generates_updated_at_in_phnom_penh_time():
    pref = UserPreference(user_id=123, language="en")
    assert pref.updated_at.utcoffset() == timedelta(hours=7)
    assert (datetime.now(timezone.utc) - pref.updated_at).total_seconds() < 5


def test_user_id_column_is_primary_key_and_big_integer():
    columns = UserPreference.__table__.columns
    assert columns["user_id"].primary_key is True
    assert isinstance(columns["user_id"].type, BigInteger)


def test_user_preference_accepts_telegram_id_beyond_int32_range():
    pref = UserPreference(user_id=-1001234567890123, language="en")
    assert pref.user_id == -1001234567890123


def test_user_preference_username_defaults_to_none():
    pref = UserPreference(user_id=123, language="en")
    assert pref.username is None


def test_user_preference_holds_username():
    pref = UserPreference(user_id=123, language="en", username="johndoe")
    assert pref.username == "johndoe"


def test_user_preference_language_defaults_to_none():
    pref = UserPreference(user_id=123)
    assert pref.language is None
