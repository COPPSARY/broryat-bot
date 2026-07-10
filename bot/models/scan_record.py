from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import JSON, BigInteger, Column
from sqlmodel import Field, SQLModel


class ScanRecord(SQLModel, table=True):
    __tablename__ = "scan_records"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    chat_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    user_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    chat_type: str
    input_type: str
    url: str | None = None
    domain: str | None = None
    sha256: str | None = None
    file_name: str | None = None
    language: str
    category: list[str] | None = Field(default=None, sa_column=Column(JSON))
    ai_risk_level: str | None = None
    ai_confidence: float | None = None
    ai_explanation: str | None = None
    vt_status: str | None = None
    vt_malicious_count: int | None = None
    vt_total_engines: int | None = None
    vt_detection_names: list[str] | None = Field(default=None, sa_column=Column(JSON))
    final_risk_level: str
