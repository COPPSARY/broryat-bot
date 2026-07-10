from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import BigInteger

from bot.models.scan_record import ScanRecord


def _record(**overrides):
    defaults = dict(
        chat_id=123,
        user_id=456,
        chat_type="private",
        input_type="url",
        url="https://example.com/login",
        domain="example.com",
        language="en",
        category=["credential_theft"],
        ai_risk_level="HIGH",
        ai_confidence=0.95,
        ai_explanation="Fake login page.",
        vt_status="malicious",
        vt_malicious_count=10,
        vt_total_engines=70,
        vt_detection_names=["Trojan.GenericKD"],
        final_risk_level="HIGH",
    )
    defaults.update(overrides)
    return ScanRecord(**defaults)


def test_scan_record_auto_generates_uuid_id():
    record = _record()
    assert isinstance(record.id, UUID)


def test_scan_record_auto_generates_created_at_in_utc():
    record = _record()
    assert record.created_at.tzinfo is not None
    assert (datetime.now(timezone.utc) - record.created_at).total_seconds() < 5


def test_scan_record_holds_all_fields():
    record = _record()
    assert record.chat_id == 123
    assert record.url == "https://example.com/login"
    assert record.category == ["credential_theft"]
    assert record.vt_detection_names == ["Trojan.GenericKD"]
    assert record.final_risk_level == "HIGH"


def test_scan_record_optional_fields_default_to_none():
    record = ScanRecord(
        chat_id=1,
        user_id=2,
        chat_type="group",
        input_type="text",
        language="km",
        final_risk_level="SAFE",
    )
    assert record.url is None
    assert record.sha256 is None
    assert record.category is None
    assert record.vt_detection_names is None


def test_chat_id_and_user_id_columns_are_big_integer():
    columns = ScanRecord.__table__.columns
    assert isinstance(columns["chat_id"].type, BigInteger)
    assert isinstance(columns["user_id"].type, BigInteger)


def test_scan_record_accepts_telegram_supergroup_chat_id_beyond_int32_range():
    record = _record(chat_id=-1001234567890123, user_id=456)
    assert record.chat_id == -1001234567890123
