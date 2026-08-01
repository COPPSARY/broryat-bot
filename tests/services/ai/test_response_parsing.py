import pytest

from bot.schemas.enums import RiskLevel
from bot.services.ai.response_parsing import parse_ai_response


def test_extracts_risk_level_from_trailing_marker_line():
    text = "Some fully localized message here.\n\nRISK:HIGH"
    risk_level, message = parse_ai_response(text)
    assert risk_level == RiskLevel.HIGH
    assert message == "Some fully localized message here."


@pytest.mark.parametrize("level", ["SAFE", "LOW", "MEDIUM", "HIGH", "UNKNOWN"])
def test_parses_each_risk_level(level):
    text = f"Visible content.\n\nRISK:{level}"
    risk_level, _ = parse_ai_response(text)
    assert risk_level == RiskLevel(level)


def test_is_case_insensitive_on_the_marker():
    text = "Visible content.\n\nrisk:high"
    risk_level, message = parse_ai_response(text)
    assert risk_level == RiskLevel.HIGH
    assert message == "Visible content."


def test_marker_line_is_removed_from_the_visible_message_even_with_extra_whitespace():
    text = "Visible content.\n\n   RISK: HIGH   \n"
    risk_level, message = parse_ai_response(text)
    assert risk_level == RiskLevel.HIGH
    assert message == "Visible content."


def test_visible_message_can_be_fully_in_a_non_english_language():
    text = "កម្រិតហានិភ័យ៖ ខ្ពស់\n\nសារនេះគឺជាការបោកប្រាស់។\n\nRISK:HIGH"
    risk_level, message = parse_ai_response(text)
    assert risk_level == RiskLevel.HIGH
    assert "RISK:HIGH" not in message
    assert "ខ្ពស់" in message


def test_raises_value_error_when_no_marker_found():
    with pytest.raises(ValueError):
        parse_ai_response("This response forgot to include the marker line.")


def test_raises_value_error_when_marker_is_not_on_its_own_line():
    with pytest.raises(ValueError):
        parse_ai_response("Some text ending with RISK:HIGH inline, not on its own line")
