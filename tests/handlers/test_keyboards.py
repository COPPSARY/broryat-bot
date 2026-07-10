from bot.handlers.keyboards import (
    main_menu_keyboard,
    other_language_keyboard,
    resolve_menu_topic,
    virustotal_keyboard,
)
from bot.schemas.enums import RiskLevel
from bot.schemas.scan import ScanResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict


def test_returns_none_when_no_vt_verdict_present():
    result = ScanResult(risk_level=RiskLevel.SAFE)
    assert virustotal_keyboard(result, "en") is None


def test_returns_none_when_verdict_has_no_permalink():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        vt_file=VTFileVerdict(sha256="a" * 64, status="malicious", malicious_count=5, total_engines=70),
    )
    assert virustotal_keyboard(result, "en") is None


def test_builds_button_for_file_verdict():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        vt_file=VTFileVerdict(
            sha256="a" * 64, status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/file/" + "a" * 64,
        ),
    )
    markup = virustotal_keyboard(result, "en")
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(buttons) == 1
    assert buttons[0].url == "https://www.virustotal.com/gui/file/" + "a" * 64


def test_builds_button_for_url_verdict():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        vt_url=VTUrlVerdict(
            url="https://example.com/phish", status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/url/xyz",
        ),
    )
    markup = virustotal_keyboard(result, "en")
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(buttons) == 1
    assert buttons[0].url == "https://www.virustotal.com/gui/url/xyz"


def test_includes_report_button_when_url_verdict_present():
    from uuid import uuid4

    scan_id = uuid4()
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        scan_record_id=scan_id,
        vt_url=VTUrlVerdict(
            url="https://example.com/phish", status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/url/xyz",
        ),
    )
    markup = virustotal_keyboard(result, "en")
    buttons = [b for row in markup.inline_keyboard for b in row]
    report_buttons = [b for b in buttons if b.callback_data == f"report:{scan_id}"]
    assert len(report_buttons) == 1
    assert report_buttons[0].text == "🚩 Report this URL"


def test_no_report_button_when_no_url_verdict():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        vt_file=VTFileVerdict(
            sha256="a" * 64, status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/file/" + "a" * 64,
        ),
    )
    markup = virustotal_keyboard(result, "en")
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert not any(b.callback_data and b.callback_data.startswith("report:") for b in buttons)


def test_builds_separate_buttons_when_both_file_and_url_present():
    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        vt_file=VTFileVerdict(
            sha256="a" * 64, status="clean", total_engines=70,
            permalink="https://www.virustotal.com/gui/file/" + "a" * 64,
        ),
        vt_url=VTUrlVerdict(
            url="https://example.com/phish", status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/url/xyz",
        ),
    )
    markup = virustotal_keyboard(result, "en")
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(buttons) == 2


def test_button_labels_are_localized_to_khmer():
    from uuid import uuid4

    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        scan_record_id=uuid4(),
        vt_file=VTFileVerdict(
            sha256="a" * 64, status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/file/" + "a" * 64,
        ),
        vt_url=VTUrlVerdict(
            url="https://example.com/phish", status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/url/xyz",
        ),
    )
    markup = virustotal_keyboard(result, "km")
    texts = [b.text for row in markup.inline_keyboard for b in row]
    assert all("View" not in t and "Report" not in t for t in texts)


def test_button_labels_are_localized_to_english():
    from uuid import uuid4

    result = ScanResult(
        risk_level=RiskLevel.HIGH,
        scan_record_id=uuid4(),
        vt_url=VTUrlVerdict(
            url="https://example.com/phish", status="malicious", malicious_count=5, total_engines=70,
            permalink="https://www.virustotal.com/gui/url/xyz",
        ),
    )
    markup = virustotal_keyboard(result, "en")
    texts = [b.text for row in markup.inline_keyboard for b in row]
    assert "🔍 View Analysis on VirusTotal" in texts
    assert "🚩 Report this URL" in texts


def test_main_menu_keyboard_has_seven_english_buttons():
    markup = main_menu_keyboard("en")
    buttons = [b.text for row in markup.keyboard for b in row]
    assert len(buttons) == 7
    assert all(resolve_menu_topic(text) is not None for text in buttons)


def test_main_menu_keyboard_has_seven_khmer_buttons():
    markup = main_menu_keyboard("km")
    buttons = [b.text for row in markup.keyboard for b in row]
    assert len(buttons) == 7
    assert all(resolve_menu_topic(text) is not None for text in buttons)


def test_resolve_menu_topic_matches_english_and_khmer_labels():
    en_markup = main_menu_keyboard("en")
    km_markup = main_menu_keyboard("km")
    en_texts = {b.text for row in en_markup.keyboard for b in row}
    km_texts = {b.text for row in km_markup.keyboard for b in row}

    expected_topics = {"use", "secure", "password", "add_to_group", "donate", "help", "language"}
    assert {resolve_menu_topic(t) for t in en_texts} == expected_topics
    assert {resolve_menu_topic(t) for t in km_texts} == expected_topics


def test_resolve_menu_topic_returns_none_for_unrelated_text():
    assert resolve_menu_topic("your account is suspended, click here") is None


def test_other_language_keyboard_offers_english_when_current_is_khmer():
    markup = other_language_keyboard("km")
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(buttons) == 1
    assert buttons[0].callback_data == "lang:en"


def test_other_language_keyboard_offers_khmer_when_current_is_english():
    markup = other_language_keyboard("en")
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(buttons) == 1
    assert buttons[0].callback_data == "lang:km"


def test_other_language_keyboard_offers_both_when_no_language_stored():
    markup = other_language_keyboard(None)
    buttons = [b for row in markup.inline_keyboard for b in row]
    callback_data = {b.callback_data for b in buttons}
    assert callback_data == {"lang:en", "lang:km"}
