from datetime import datetime, timedelta, timezone

from sqlalchemy import BigInteger

from bot.models.secretary_preference import SecretaryPreference


def test_secretary_preference_defaults() -> None:
    pref = SecretaryPreference(user_id=222)
    assert pref.enabled is False
    assert pref.mode == "warn"
    assert pref.business_connection_id is None


def test_secretary_preference_holds_connection_owner() -> None:
    pref = SecretaryPreference(
        user_id=222,
        business_connection_id="conn-123",
    )
    assert pref.user_id == 222
    assert pref.business_connection_id == "conn-123"


def test_secretary_preference_auto_generates_updated_at_in_phnom_penh_time() -> None:
    pref = SecretaryPreference(user_id=222)
    assert pref.updated_at.utcoffset() == timedelta(hours=7)
    assert (datetime.now(timezone.utc) - pref.updated_at).total_seconds() < 5


def test_user_id_column_is_primary_key_and_big_integer() -> None:
    columns = SecretaryPreference.__table__.columns
    assert columns["user_id"].primary_key is True
    assert isinstance(columns["user_id"].type, BigInteger)
