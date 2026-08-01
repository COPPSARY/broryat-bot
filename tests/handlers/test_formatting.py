from bot.handlers.formatting import format_group_response, format_response
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict
from bot.services.ai.prompt import DISCLAIMER


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


def test_analysis_failed_uses_malicious_virustotal_fallback():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        language="en",
        vt_file=VTFileVerdict(
            sha256="a" * 64,
            status="malicious",
            malicious_count=12,
            total_engines=70,
            detection_names=["Trojan.Generic", "Win32.Malware"],
        ),
        analysis_failed=True,
    )

    text = format_response(result)

    assert "MALICIOUS" in text
    assert "12/70" in text
    assert "Trojan.Generic" in text
    assert "Do not open" in text


def test_analysis_failed_virustotal_fallback_includes_disclaimer():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        language="en",
        vt_file=VTFileVerdict(
            sha256="a" * 64,
            status="malicious",
            malicious_count=12,
            total_engines=70,
        ),
        analysis_failed=True,
    )

    text = format_response(result)

    assert DISCLAIMER["en"] in text


def test_analysis_failed_without_vt_verdict_includes_disclaimer():
    result = ScanResult(risk_level=RiskLevel.SAFE, language="en", analysis_failed=True)

    text = format_response(result)

    assert DISCLAIMER["en"] in text


def test_analysis_failed_uses_khmer_virustotal_fallback():
    result = ScanResult(
        risk_level=RiskLevel.MEDIUM,
        language="km",
        vt_url=VTUrlVerdict(
            url="https://example.com",
            status="suspicious",
            malicious_count=2,
            total_engines=70,
        ),
        analysis_failed=True,
    )

    text = format_response(result)

    assert "គួរឱ្យសង្ស័យ" in text
    assert "2/70" in text
    assert "AI" in text


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


def test_format_group_response_never_shows_the_ai_freeform_message():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        ai=IntentResult(
            risk_level=RiskLevel.HIGH,
            message="THIS EXACT AI SENTENCE SHOULD NOT APPEAR",
            language="en",
        ),
    )

    text = format_group_response(result)

    assert "THIS EXACT AI SENTENCE SHOULD NOT APPEAR" not in text
    assert "Risk Level: HIGH" in text


def test_format_group_response_includes_vt_detection_details():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        ai=IntentResult(risk_level=RiskLevel.HIGH, message="unused", language="en"),
        vt_url=VTUrlVerdict(
            url="https://example.com",
            status="malicious",
            malicious_count=8,
            total_engines=70,
            detection_names=["Phishing.Generic"],
        ),
    )

    text = format_group_response(result)

    assert "8/70" in text
    assert "Phishing.Generic" in text


def test_format_group_response_khmer_safe_result():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message="unused", language="km"),
    )

    text = format_group_response(result)

    assert "សុវត្ថិភាព" in text


def test_format_group_response_shows_retry_message_when_pending():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message="unused", language="en"),
        vt_file=VTFileVerdict(sha256="a" * 64, status="pending"),
    )

    text = format_group_response(result)

    assert "still in progress" in text.lower()


def test_format_group_response_analysis_failed_uses_vt_fallback():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        language="en",
        vt_file=VTFileVerdict(
            sha256="a" * 64, status="malicious", malicious_count=12, total_engines=70
        ),
        analysis_failed=True,
    )

    text = format_group_response(result)

    assert "MALICIOUS" in text
    assert DISCLAIMER["en"] in text


def test_format_group_response_includes_disclaimer():
    result = ScanResult(
        risk_level=RiskLevel.SAFE,
        ai=IntentResult(risk_level=RiskLevel.SAFE, message="unused", language="en"),
    )

    text = format_group_response(result)

    assert DISCLAIMER["en"] in text
