from datetime import datetime

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel

from bot.utils.time import now_phnom_penh


class GroupPreference(SQLModel, table=True):
    __tablename__ = "group_preferences"

    chat_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    language: str | None = None
    group_name: str | None = None
    updated_at: datetime = Field(default_factory=now_phnom_penh)
