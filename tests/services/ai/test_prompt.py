from bot.services.ai.prompt import DISCLAIMER, build_prompt


def test_prompt_includes_the_message_text():
    prompt = build_prompt("Your Telegram account will be suspended, click here", "en")
    assert "Your Telegram account will be suspended, click here" in prompt


def test_prompt_instructs_full_translation_of_labels_and_risk_word():
    prompt = build_prompt("some text", "en")
    assert "Safe" in prompt and "Low" in prompt and "Medium" in prompt and "High" in prompt
    assert "translate" in prompt.lower()
    assert "risk level" in prompt.lower()
    assert "explanation" in prompt.lower()
    assert "recommendation" in prompt.lower()


def test_prompt_instructs_a_trailing_machine_readable_risk_marker():
    prompt = build_prompt("some text", "en")
    assert "RISK:LEVEL" in prompt
    assert "final line" in prompt.lower()


def test_prompt_mentions_prd_scam_categories():
    prompt = build_prompt("some text", "km")
    for category in ["impersonation", "banking", "investment", "urgency", "credential"]:
        assert category in prompt.lower()


def test_prompt_without_vt_context_still_has_a_vt_section_saying_none_was_provided():
    prompt = build_prompt("some text", "en")
    assert "No file or URL scan result was provided." in prompt


def test_prompt_includes_vt_context_when_provided():
    prompt = build_prompt("some text", "en", vt_context="malicious (12/70 engines detected threats)")
    assert "VirusTotal" in prompt
    assert "malicious (12/70 engines detected threats)" in prompt


def test_prompt_asks_ai_to_classify_malware_type_when_vt_context_given():
    prompt = build_prompt("some text", "en", vt_context="malicious (12/70 engines detected threats)")
    for keyword in ["Trojan", "ransomware", "spyware"]:
        assert keyword in prompt


def test_prompt_instructs_safe_when_scan_result_shows_no_detections():
    prompt = build_prompt("some text", "en", vt_context="URL scan: clean (0/70 engines detected threats)")
    assert "0 detections" in prompt
    assert "report the risk level as Safe" in prompt


def test_prompt_does_not_tell_ai_to_override_a_clean_scan_result():
    prompt = build_prompt("some text", "en", vt_context="URL scan: clean (0/70 engines detected threats)")
    assert "even when VirusTotal reports the URL as clean" not in prompt


def test_prompt_asks_to_mention_tool_count():
    prompt = build_prompt("some text", "en", vt_context="malicious (30/70 engines detected threats)")
    assert "tools" in prompt.lower()


def test_prompt_instructs_telegram_markdown_formatting():
    prompt = build_prompt("some text", "en")
    assert "Markdown" in prompt


def test_prompt_encourages_emoji_without_dictating_which_ones():
    prompt = build_prompt("some text", "en")
    assert "emoji" in prompt.lower()


def test_prompt_does_not_ask_ai_to_write_the_disclaimer():
    prompt = build_prompt("some text", "en")
    for text in DISCLAIMER.values():
        assert text not in prompt


def test_disclaimer_has_english_and_khmer_versions():
    assert set(DISCLAIMER.keys()) == {"en", "km"}
    assert DISCLAIMER["en"] != DISCLAIMER["km"]


def test_prompt_makes_the_scan_result_decide_for_urls_and_files():
    prompt = build_prompt("some text", "en")
    assert "decides the risk level" in prompt.lower()
    assert "never overrule it" in prompt.lower()


def test_prompt_forbids_raising_risk_from_the_ais_own_suspicion_of_a_domain():
    """The AI no longer judges domains itself — VirusTotal decides for links and files."""
    prompt = build_prompt("some text", "en")
    assert "do not raise the risk based on the domain name" in prompt.lower()


def test_prompt_still_judges_message_text_when_no_url_or_file_is_involved():
    prompt = build_prompt("some text", "en")
    assert "no url and no file" in prompt.lower()
    assert "scam intent" in prompt.lower()


def test_prompt_instructs_never_invent_results():
    prompt = build_prompt("some text", "en")
    assert "never invent" in prompt.lower()


def test_prompt_defers_to_a_clean_vt_result_rather_than_overriding_it():
    """Supersedes the earlier rule that pushed independent domain analysis even on a
    clean VT result: a completed 0-detection scan is now reported as Safe."""
    prompt = build_prompt(
        "check https://example.com", "en", vt_context="clean (0/70 engines detected threats)"
    )
    assert "never overrule it" in prompt.lower()
    assert "report the risk level as Safe" in prompt


def test_prompt_reports_safe_when_no_scan_result_was_found():
    """A URL VirusTotal has no result for is not the AI's to flag."""
    prompt = build_prompt("check https://example.com", "en")
    assert "no scan result was found" in prompt.lower()
    assert "report the risk level as Safe" in prompt
