from bot.handlers.formatting import format_response
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult


def test_format_response_returns_the_ai_composed_message_verbatim():
    ai_message = (
        "🛡 Risk: HIGH\n\n"
        "This message impersonates Telegram support and creates urgency.\n\n"
        "Do not click the link. Delete the message. Report the sender."
    )
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        ai=IntentResult(
            risk_level=RiskLevel.HIGH,
            confidence=0.9,
            categories=["Telegram impersonation", "Creates urgency"],
            explanation="Pretends to be Telegram support.",
            message=ai_message,
            language="en",
        ),
    )

    text = format_response(result)

    assert text == ai_message


def test_format_response_passes_through_khmer_ai_message_unchanged():
    ai_message = "🛡 កម្រិតហានិភ័យ៖ HIGH\n\nសារនេះក្លែងបន្លំ Telegram support។"
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        ai=IntentResult(
            risk_level=RiskLevel.HIGH, confidence=0.9, categories=[], explanation="x",
            message=ai_message, language="km",
        ),
    )

    text = format_response(result)

    assert text == ai_message


def test_format_response_analysis_failed_returns_failure_message():
    result = ScanResult(risk_level=RiskLevel.SAFE, analysis_failed=True)

    text = format_response(result)

    assert "failed" in text.lower()


def test_format_response_analysis_failed_uses_khmer_when_ai_language_known():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(
            risk_level=RiskLevel.SAFE, confidence=0.1, categories=[], explanation="x",
            message="unused", language="km",
        ),
        analysis_failed=True,
    )

    text = format_response(result)

    assert "បរាជ័យ" in text
