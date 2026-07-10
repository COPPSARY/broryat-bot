from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict


class ScanRequest(BaseModel):
    chat_id: int
    user_id: int
    chat_type: Literal["private", "group"]
    input_type: Literal["text", "url", "file", "forwarded"]
    text: str | None = None
    urls: list[str] = Field(default_factory=list)
    file_path: str | None = None
    file_name: str | None = None
    language: Literal["km", "en"]


class ScanResult(BaseModel):
    risk_level: RiskLevel
    ai: IntentResult | None = None
    vt_file: VTFileVerdict | None = None
    vt_url: VTUrlVerdict | None = None
    analysis_failed: bool = False
    scan_record_id: UUID | None = None
