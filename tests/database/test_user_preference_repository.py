import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from bot.database.user_preference_repository import UserPreferenceRepository
from bot.models.user_preference import UserPreference


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def repo(engine):
    return UserPreferenceRepository(engine)


async def test_get_language_returns_none_when_no_preference_set(repo):
    result = await repo.get_language(123)
    assert result is None


async def test_set_language_then_get_language_returns_it(repo):
    await repo.set_language(123, "km")

    result = await repo.get_language(123)

    assert result == "km"


async def test_set_language_upserts_without_duplicating_rows(repo, engine):
    await repo.set_language(123, "en")
    await repo.set_language(123, "km")

    result = await repo.get_language(123)
    assert result == "km"

    with Session(engine) as session:
        rows = session.exec(select(UserPreference).where(UserPreference.user_id == 123)).all()
        assert len(rows) == 1
