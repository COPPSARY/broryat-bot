import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.models.group_preference import GroupPreference


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def repo(engine):
    return GroupPreferenceRepository(engine)


async def test_get_language_returns_none_when_no_preference_set(repo):
    result = await repo.get_language(-100123)
    assert result is None


async def test_set_language_then_get_language_returns_it(repo):
    await repo.set_language(-100123, "km")

    result = await repo.get_language(-100123)

    assert result == "km"


async def test_set_language_upserts_without_duplicating_rows(repo, engine):
    await repo.set_language(-100123, "en")
    await repo.set_language(-100123, "km")

    result = await repo.get_language(-100123)
    assert result == "km"

    with Session(engine) as session:
        rows = session.exec(select(GroupPreference).where(GroupPreference.chat_id == -100123)).all()
        assert len(rows) == 1
