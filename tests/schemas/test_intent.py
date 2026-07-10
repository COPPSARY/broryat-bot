import pytest
from pydantic import ValidationError

from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult


def test_intent_result_holds_risk_level_and_message():
    result = IntentResult(
        risk_level=RiskLevel.HIGH,
        message="🛡 Risk: HIGH\n\nThis looks like a bank scam. Do not respond.",
        language="km",
    )
    assert result.risk_level == RiskLevel.HIGH
    assert "bank scam" in result.message


def test_intent_result_requires_message():
    with pytest.raises(ValidationError):
        IntentResult(risk_level=RiskLevel.LOW, language="en")


def test_intent_result_raw_response_defaults_to_none():
    result = IntentResult(risk_level=RiskLevel.SAFE, message="x", language="en")
    assert result.raw_response is None
