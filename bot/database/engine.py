from sqlmodel import SQLModel, create_engine

from bot.models.group_preference import GroupPreference  # noqa: F401  (registers the table with SQLModel.metadata)
from bot.models.report import UrlReport  # noqa: F401  (registers the table with SQLModel.metadata)
from bot.models.scan_record import ScanRecord  # noqa: F401  (registers the table with SQLModel.metadata)
from bot.models.user_preference import UserPreference  # noqa: F401  (registers the table with SQLModel.metadata)


def get_engine(database_url: str, **engine_kwargs):
    return create_engine(database_url, **engine_kwargs)


def create_db_and_tables(engine) -> None:
    SQLModel.metadata.create_all(engine)
