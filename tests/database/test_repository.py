from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from bot.database.repository import ScanRepository
from bot.models.scan_record import ScanRecord


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def repo(engine):
    return ScanRepository(engine)


def _record(**overrides):
    defaults = dict(
        chat_id=1,
        user_id=2,
        chat_type="private",
        input_type="url",
        url="https://example.com",
        language="en",
        final_risk_level="HIGH",
    )
    defaults.update(overrides)
    return ScanRecord(**defaults)


async def test_insert_scan_persists_and_returns_the_record(repo):
    record = _record()

    result = await repo.insert_scan(record)

    assert result.id == record.id
    assert result.url == "https://example.com"


async def test_find_recent_by_hash_returns_record_when_found(repo):
    sha256 = "a" * 64
    await repo.insert_scan(_record(input_type="file", url=None, sha256=sha256))

    result = await repo.find_recent_by_hash(sha256, within_hours=24)

    assert result is not None
    assert result.sha256 == sha256


async def test_find_recent_by_hash_returns_none_when_not_found(repo):
    result = await repo.find_recent_by_hash("b" * 64, within_hours=24)

    assert result is None


async def test_find_recent_by_hash_ignores_records_older_than_window(repo):
    sha256 = "c" * 64
    old_record = _record(
        input_type="file",
        url=None,
        sha256=sha256,
        created_at=datetime.now(timezone.utc) - timedelta(hours=48),
    )
    await repo.insert_scan(old_record)

    result = await repo.find_recent_by_hash(sha256, within_hours=24)

    assert result is None


async def test_find_recent_by_url_returns_record_when_found(repo):
    url = "https://example.com/x"
    await repo.insert_scan(_record(url=url))

    result = await repo.find_recent_by_url(url, within_hours=24)

    assert result is not None
    assert result.url == url


async def test_find_recent_by_url_returns_most_recent_match(repo):
    url = "https://example.com/y"
    await repo.insert_scan(_record(url=url, final_risk_level="LOW"))
    await repo.insert_scan(_record(url=url, final_risk_level="HIGH"))

    result = await repo.find_recent_by_url(url, within_hours=24)

    assert result.final_risk_level == "HIGH"


async def test_get_by_id_returns_the_record_when_found(repo):
    record = await repo.insert_scan(_record())

    result = await repo.get_by_id(record.id)

    assert result is not None
    assert result.id == record.id


async def test_get_by_id_returns_none_when_not_found(repo):
    from uuid import uuid4

    result = await repo.get_by_id(uuid4())

    assert result is None
