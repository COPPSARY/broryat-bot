from bot.schemas.enums import RiskLevel
from bot.schemas.scan import ScanRequest, ScanResult


def test_scan_request_defaults_urls_to_empty_list():
    request = ScanRequest(
        chat_id=1,
        user_id=2,
        chat_type="private",
        input_type="text",
        language="en",
    )
    assert request.urls == []
    assert request.text is None
    assert request.file_path is None


def test_scan_result_defaults_analysis_failed_false():
    result = ScanResult(risk_level=RiskLevel.SAFE)
    assert result.analysis_failed is False
    assert result.ai is None
    assert result.vt_file is None
    assert result.vt_url is None
