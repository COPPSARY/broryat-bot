from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import Field, SQLModel

from bot.utils.time import now_phnom_penh


class UrlReport(SQLModel, table=True):
    __tablename__ = "url_reports"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scan_record_id: UUID = Field(foreign_key="scan_records.id", index=True)
    chat_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    user_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("user_preferences.user_id"), nullable=False, index=True)
    )
    url: str
    created_at: datetime = Field(default_factory=now_phnom_penh)
