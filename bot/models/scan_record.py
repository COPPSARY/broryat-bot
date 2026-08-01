from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, BigInteger, Column, ForeignKey, Index, text
from sqlmodel import Field, SQLModel

from bot.utils.time import now_phnom_penh


class ScanRecord(SQLModel, table=True):
    __tablename__ = "scan_records"
    __table_args__ = (
        Index(
            "idx_scan_records_sha256_created_at",
            "sha256",
            "created_at",
            postgresql_where=text("sha256 IS NOT NULL"),
        ),
        Index(
            "idx_scan_records_url_created_at",
            "url",
            "created_at",
            postgresql_where=text("url IS NOT NULL"),
        ),
        Index("idx_scan_records_chat_type_user_id_created_at", "chat_type", "user_id", "created_at"),
        Index("idx_scan_records_chat_type_chat_id_created_at", "chat_type", "chat_id", "created_at"),
        Index("idx_scan_records_created_at", "created_at"),
        Index(
            "idx_scan_records_final_risk_level_created_at",
            "final_risk_level",
            "created_at",
            postgresql_where=text("final_risk_level IS NOT NULL"),
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=now_phnom_penh)
    chat_id: int | None = Field(
        sa_column=Column(BigInteger, ForeignKey("group_preferences.chat_id"), nullable=True)
    )
    user_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("user_preferences.user_id"), nullable=False, index=True)
    )
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
