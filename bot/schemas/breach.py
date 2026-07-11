from pydantic import BaseModel, Field


class BreachRecord(BaseModel):
    breach: str
    domain: str
    xposed_date: str
    xposed_data: list[str]
    password_risk: str


class BreachCheckResult(BaseModel):
    email: str
    found: bool
    records: list[BreachRecord] = Field(default_factory=list)
    risk_label: str | None = None
    risk_score: float | None = None
