from typing import Literal

from pydantic import BaseModel

from bot.schemas.enums import RiskLevel


class IntentResult(BaseModel):
    risk_level: RiskLevel
    message: str
    language: Literal["km", "en"]
    raw_response: str | None = None
