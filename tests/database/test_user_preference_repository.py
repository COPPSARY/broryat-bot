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


async def test_set_username_creates_row_when_missing(repo):
    await repo.set_username(123, "johndoe")

    with_session = repo
    result = await with_session.get_language(123)
    assert result is None


async def test_set_username_persists_username(repo, engine):
    await repo.set_username(123, "johndoe")

    with Session(engine) as session:
        pref = session.get(UserPreference, 123)
        assert pref.username == "johndoe"


async def test_set_username_upserts_without_duplicating_rows(repo, engine):
    await repo.set_username(123, "johndoe")
    await repo.set_username(123, "janedoe")

    with Session(engine) as session:
        rows = session.exec(select(UserPreference).where(UserPreference.user_id == 123)).all()
        assert len(rows) == 1
        assert rows[0].username == "janedoe"


async def test_set_username_does_not_overwrite_existing_language(repo, engine):
    await repo.set_language(123, "km")
    await repo.set_username(123, "johndoe")

    with Session(engine) as session:
        pref = session.get(UserPreference, 123)
        assert pref.language == "km"
        assert pref.username == "johndoe"


async def test_set_name_creates_row_when_missing(repo, engine):
    await repo.set_name(123, "John", "Doe")

    with Session(engine) as session:
        pref = session.get(UserPreference, 123)
        assert pref.first_name == "John"
        assert pref.last_name == "Doe"


async def test_set_name_upserts_without_duplicating_rows(repo, engine):
    await repo.set_name(123, "John", "Doe")
    await repo.set_name(123, "Jane", "Smith")

    with Session(engine) as session:
        rows = session.exec(select(UserPreference).where(UserPreference.user_id == 123)).all()
        assert len(rows) == 1
        assert rows[0].first_name == "Jane"
        assert rows[0].last_name == "Smith"


async def test_set_name_does_not_overwrite_existing_username_or_language(repo, engine):
    await repo.set_language(123, "km")
    await repo.set_username(123, "johndoe")
    await repo.set_name(123, "John", "Doe")

    with Session(engine) as session:
        pref = session.get(UserPreference, 123)
        assert pref.language == "km"
        assert pref.username == "johndoe"
        assert pref.first_name == "John"
        assert pref.last_name == "Doe"
