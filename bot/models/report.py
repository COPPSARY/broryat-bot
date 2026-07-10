from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel


class UrlReport(SQLModel, table=True):
    __tablename__ = "url_reports"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scan_record_id: UUID
    chat_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    user_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
