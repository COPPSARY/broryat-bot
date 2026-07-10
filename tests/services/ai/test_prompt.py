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


def test_prompt_includes_website_analysis_rules():
    prompt = build_prompt("some text", "en")
    assert "phishing" in prompt.lower()
    assert "https" in prompt.lower()
    assert "subdomain" in prompt.lower()


def test_prompt_instructs_not_to_trust_https_alone():
    prompt = build_prompt("some text", "en")
    assert "only because it uses https" in prompt.lower()


def test_prompt_instructs_never_invent_results():
    prompt = build_prompt("some text", "en")
    assert "never invent" in prompt.lower()


def test_prompt_instructs_independent_domain_analysis_regardless_of_vt_result():
    prompt = build_prompt(
        "check https://example.com", "en", vt_context="clean (0/70 engines detected threats)"
    )
    assert "does not detect phishing" in prompt.lower()
    assert "you must still" in prompt.lower() or "independently" in prompt.lower()


def test_prompt_pushes_independent_domain_analysis_even_without_vt_context():
    prompt = build_prompt("check https://example.com", "en")
    assert "phishing" in prompt.lower()
