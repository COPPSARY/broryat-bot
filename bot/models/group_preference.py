from datetime import datetime

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import Field, SQLModel

from bot.utils.time import now_phnom_penh


class GroupPreference(SQLModel, table=True):
    __tablename__ = "group_preferences"

    chat_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    language: str | None = None
    group_name: str | None = None
    added_by_user_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, ForeignKey("user_preferences.user_id"), nullable=True, index=True),
    )
    updated_at: datetime = Field(default_factory=now_phnom_penh)
