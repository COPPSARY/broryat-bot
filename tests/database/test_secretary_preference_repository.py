import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from bot.database.secretary_preference_repository import SecretaryPreferenceRepository
from bot.models.secretary_preference import SecretaryPreference


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def repo(engine):
    return SecretaryPreferenceRepository(engine)


async def test_set_business_connection_then_get_by_connection_finds_owner(repo):
    await repo.set_business_connection(999, "conn-abc")

    pref = await repo.get_by_connection("conn-abc")

    assert pref is not None
    assert pref.user_id == 999
    assert pref.enabled is True


async def test_disabling_connection_clears_lookup(repo):
    await repo.set_business_connection(999, "conn-abc")
    await repo.set_business_connection(999, None)

    assert await repo.get_by_connection("conn-abc") is None


async def test_set_business_connection_upserts_without_duplicate(repo, engine):
    await repo.set_business_connection(999, "conn-1")
    await repo.set_business_connection(999, "conn-2")

    with Session(engine) as session:
        rows = session.exec(
            select(SecretaryPreference).where(SecretaryPreference.user_id == 999)
        ).all()
        assert len(rows) == 1
        assert rows[0].business_connection_id == "conn-2"
