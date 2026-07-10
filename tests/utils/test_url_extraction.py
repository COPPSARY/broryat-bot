from bot.utils.url_extraction import extract_urls, is_message_only_urls, normalize_url


def test_extract_urls_finds_http_and_https_links():
    text = "Check this out https://example.com/promo and also http://foo.bar/path"
    urls = extract_urls(text)
    assert urls == ["https://example.com/promo", "http://foo.bar/path"]


def test_extract_urls_returns_empty_list_when_no_links():
    assert extract_urls("just plain text, no links here") == []


def test_extract_urls_ignores_surrounding_punctuation():
    text = "Visit (https://example.com/x) now!"
    assert extract_urls(text) == ["https://example.com/x"]


def test_normalize_url_adds_missing_scheme():
    assert normalize_url("example.com/path") == "https://example.com/path"


def test_normalize_url_lowercases_host_but_not_path():
    assert normalize_url("https://EXAMPLE.com/Path") == "https://example.com/Path"


def test_normalize_url_strips_tracking_params():
    url = "https://example.com/promo?utm_source=fb&utm_medium=cpc&id=1"
    assert normalize_url(url) == "https://example.com/promo?id=1"


def test_normalize_url_strips_trailing_slash():
    assert normalize_url("https://example.com/path/") == "https://example.com/path"


def test_extract_urls_detects_bare_domain_without_scheme():
    assert extract_urls("check this out example.com/promo") == ["example.com/promo"]


def test_extract_urls_detects_common_scam_link_shorteners_without_scheme():
    assert extract_urls("claim your prize at bit.ly/abc123 now") == ["bit.ly/abc123"]
    assert extract_urls("join us t.me/free_crypto_giveaway") == ["t.me/free_crypto_giveaway"]


def test_extract_urls_does_not_treat_email_addresses_as_urls():
    assert extract_urls("contact me at user@example.com") == []


def test_extract_urls_does_not_match_plain_sentences_with_abbreviations():
    assert extract_urls("etc. and e.g. are common abbreviations, U.K. too") == []


def test_extract_urls_still_finds_scheme_urls_alongside_bare_ones():
    text = "Official site https://example.com but scammers use example-fake.com/login"
    assert extract_urls(text) == ["https://example.com", "example-fake.com/login"]


def test_extract_urls_rejects_dotted_log_lines_and_module_paths():
    text = "WARNING:bot.services.virustotal.rate_limiter:VirusTotal rate limit reached; waiting 27.9s"
    assert extract_urls(text) == []


def test_extract_urls_rejects_bare_ipv4_addresses():
    assert extract_urls("connect to 192.168.1.1 now") == []


def test_extract_urls_rejects_scheme_prefixed_ipv4_addresses():
    assert extract_urls("visit http://45.33.12.9/phish for details") == []


def test_extract_urls_rejects_hosts_with_underscores():
    assert extract_urls("check rate_limiter.example for info") == []


def test_extract_urls_still_allows_underscore_in_path_not_host():
    assert extract_urls("join us t.me/free_crypto_giveaway") == ["t.me/free_crypto_giveaway"]


def test_extract_urls_rejects_incomplete_domain_with_fake_tld():
    assert extract_urls("this is not a link: hello.world.of.text") == []


def test_extract_urls_accepts_cambodia_cctld():
    assert extract_urls("visit https://example.com.kh/promo") == ["https://example.com.kh/promo"]


def test_is_message_only_urls_true_for_lone_url():
    assert is_message_only_urls("https://example.com", ["https://example.com"]) is True


def test_is_message_only_urls_false_when_other_text_present():
    text = "check this out https://example.com please"
    assert is_message_only_urls(text, ["https://example.com"]) is False


def test_is_message_only_urls_true_when_multiple_urls_and_nothing_else():
    text = "https://example.com https://other.com"
    assert is_message_only_urls(text, ["https://example.com", "https://other.com"]) is True
