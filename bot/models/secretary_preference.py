from datetime import datetime

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel

from bot.utils.time import now_phnom_penh


class SecretaryPreference(SQLModel, table=True):
    __tablename__ = "secretary_preferences"

    user_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    enabled: bool = Field(default=False)
    mode: str = Field(default="warn")
    business_connection_id: str | None = None
    updated_at: datetime = Field(default_factory=now_phnom_penh)
