from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, BigInteger, Column
from sqlmodel import Field, SQLModel

from bot.utils.time import now_phnom_penh


class ScanRecord(SQLModel, table=True):
    __tablename__ = "scan_records"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=now_phnom_penh)
    chat_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    user_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    chat_type: str
    input_type: str
    url: str | None = None
    domain: str | None = None
    sha256: str | None = None
    file_name: str | None = None
    language: str
    ai_risk_level: str | None = None
    vt_status: str | None = None
    vt_malicious_count: int | None = None
    vt_total_engines: int | None = None
    vt_detection_names: list[str] | None = Field(default=None, sa_column=Column(JSON))
    final_risk_level: str
