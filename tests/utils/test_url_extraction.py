from bot.utils.url_extraction import extract_urls, normalize_url


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
