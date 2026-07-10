from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import BigInteger

from bot.models.report import UrlReport


def _report(**overrides):
    defaults = dict(
        scan_record_id=uuid4(),
        chat_id=123,
        user_id=456,
        url="https://example.com/phish",
    )
    defaults.update(overrides)
    return UrlReport(**defaults)


def test_url_report_auto_generates_uuid_id():
    report = _report()
    assert isinstance(report.id, UUID)


def test_url_report_auto_generates_created_at_in_utc():
    report = _report()
    assert report.created_at.tzinfo is not None
    assert (datetime.now(timezone.utc) - report.created_at).total_seconds() < 5


def test_url_report_holds_all_fields():
    scan_id = uuid4()
    report = _report(scan_record_id=scan_id, url="https://example.com/x")
    assert report.scan_record_id == scan_id
    assert report.url == "https://example.com/x"
    assert report.chat_id == 123
    assert report.user_id == 456


def test_chat_id_and_user_id_columns_are_big_integer():
    columns = UrlReport.__table__.columns
    assert isinstance(columns["chat_id"].type, BigInteger)
    assert isinstance(columns["user_id"].type, BigInteger)


def test_url_report_accepts_telegram_supergroup_chat_id_beyond_int32_range():
    report = _report(chat_id=-1001234567890123)
    assert report.chat_id == -1001234567890123
