from uuid import uuid4

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from bot.database.report_repository import ReportRepository
from bot.models.report import UrlReport


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def repo(engine):
    return ReportRepository(engine)


async def test_insert_report_persists_and_returns_the_record(repo):
    report = UrlReport(scan_record_id=uuid4(), chat_id=1, user_id=2, url="https://example.com/x")

    result = await repo.insert_report(report)

    assert result.id == report.id
    assert result.url == "https://example.com/x"
