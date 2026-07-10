from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

VTStatus = Literal["clean", "malicious", "suspicious", "unknown", "pending"]


class VTFileVerdict(BaseModel):
    sha256: str
    status: VTStatus = "unknown"
    malicious_count: int = 0
    total_engines: int = 0
    detection_names: list[str] = Field(default_factory=list)
    permalink: str | None = None
    scan_date: datetime | None = None


class VTUrlVerdict(BaseModel):
    url: str
    status: VTStatus = "unknown"
    malicious_count: int = 0
    total_engines: int = 0
    detection_names: list[str] = Field(default_factory=list)
    permalink: str | None = None
    scan_date: datetime | None = None
