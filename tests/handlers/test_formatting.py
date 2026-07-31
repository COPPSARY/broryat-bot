from bot.handlers.formatting import format_response
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict


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
        ai=IntentResult(risk_level=RiskLevel.HIGH, message=ai_message, language="km"),
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
            risk_level=RiskLevel.SAFE,
            message="unused",
            language="km",
        ),
        analysis_failed=True,
    )

    text = format_response(result)

    assert "បរាជ័យ" in text


def test_format_response_shows_retry_message_when_vt_file_is_pending():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message="unused, would say Safe", language="en"),
        vt_file=VTFileVerdict(sha256="a" * 64, status="pending"),
    )

    text = format_response(result)

    assert "still in progress" in text.lower()
    assert text != "unused, would say Safe"


def test_format_response_shows_retry_message_when_vt_url_is_pending():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message="unused, would say Safe", language="km"),
        vt_url=VTUrlVerdict(url="https://example.com", status="pending"),
    )

    text = format_response(result)

    assert "ដំណើរការ" in text


def test_format_response_pending_takes_priority_over_analysis_failed():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message="unused", language="en"),
        vt_file=VTFileVerdict(sha256="a" * 64, status="pending"),
        analysis_failed=True,
    )

    text = format_response(result)

    assert "still in progress" in text.lower()


def test_format_response_does_not_show_retry_message_for_completed_vt_status():
    ai_message = "🛡 Risk: SAFE\n\nNo threats found."
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message=ai_message, language="en"),
        vt_file=VTFileVerdict(sha256="a" * 64, status="clean"),
    )

    text = format_response(result)

    assert text == ai_message
