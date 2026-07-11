from bot.utils.trusted_domains import is_own_domain, is_trusted_domain


def test_exact_trusted_domain_match():
    assert is_trusted_domain("https://google.com") is True


def test_trusted_subdomain_match():
    assert is_trusted_domain("https://accounts.google.com/login") is True
    assert is_trusted_domain("https://mail.google.com") is True
    assert is_trusted_domain("https://www.facebook.com") is True


def test_bare_domain_without_scheme_is_matched():
    assert is_trusted_domain("google.com") is True


def test_suffix_attack_domain_is_not_trusted():
    assert is_trusted_domain("https://google.com.attacker.example") is False


def test_lookalike_domain_is_not_trusted():
    assert is_trusted_domain("https://micros0ft-login.com") is False


def test_unrelated_domain_is_not_trusted():
    assert is_trusted_domain("https://example.com") is False


def test_misspelled_domain_is_not_trusted():
    assert is_trusted_domain("https://gooogle.com") is False


def test_additional_big_tech_and_social_domains_are_trusted():
    assert is_trusted_domain("https://github.com") is True
    assert is_trusted_domain("https://youtube.com") is True
    assert is_trusted_domain("https://telegram.org") is True
    assert is_trusted_domain("https://paypal.com") is True
    assert is_trusted_domain("https://wikipedia.org") is True


def test_cambodia_government_domain_is_trusted():
    assert is_trusted_domain("https://nbc.gov.kh") is True
    assert is_trusted_domain("https://moh.gov.kh") is True


def test_ai_companies_and_assistants_are_trusted():
    assert is_trusted_domain("https://chatgpt.com") is True
    assert is_trusted_domain("https://claude.ai") is True
    assert is_trusted_domain("https://chat.openai.com") is True
    assert is_trusted_domain("https://perplexity.ai") is True
    assert is_trusted_domain("https://huggingface.co") is True


def test_more_regional_and_mainstream_domains_are_trusted():
    assert is_trusted_domain("https://netflix.com") is True
    assert is_trusted_domain("https://line.me") is True
    assert is_trusted_domain("https://booking.com") is True
    assert is_trusted_domain("https://discord.com") is True


def test_own_domain_is_recognized():
    assert is_own_domain("https://broryat.tech") is True
    assert is_own_domain("https://www.broryat.tech") is True
    assert is_own_domain("broryat.tech") is True


def test_lookalike_of_own_domain_is_not_recognized():
    assert is_own_domain("https://broryat.tech.attacker.example") is False
    assert is_own_domain("https://broryat-tech.com") is False


def test_other_trusted_domain_is_not_own_domain():
    assert is_own_domain("https://google.com") is False
