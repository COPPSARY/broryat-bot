from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"

    user_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    language: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
