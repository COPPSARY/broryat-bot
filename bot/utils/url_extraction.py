import ipaddress
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_URL_PATTERN = re.compile(
    r"https?://[^\s()<>\[\]\"']+"
    r"|(?<![\w@.])(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s()<>\[\]\"']*)?"
)

_TRACKING_PARAM_PREFIXES = ("utm_",)
_TRACKING_PARAMS = {"fbclid", "gclid"}

_VALID_TLDS = frozenset({
    # major gTLDs
    "com", "net", "org", "info", "biz", "name", "pro",
    # tech/startup gTLDs
    "io", "co", "ai", "app", "dev", "tech", "cloud", "digital",
    # common cheap/scam-associated gTLDs
    "xyz", "top", "click", "link", "live", "shop", "online", "site",
    "club", "vip", "win", "bid", "loan", "work", "party", "review", "bar",
    "download", "stream", "icu", "buzz", "cyou", "sbs", "cfd",
    # media/short-link gTLDs
    "tv", "cc", "me", "ly", "gg", "fm",
    # institutional
    "gov", "edu", "mil", "int",
    # common ccTLDs (incl. Cambodia and regional neighbors)
    "kh", "us", "uk", "ca", "au", "nz",
    "cn", "jp", "kr", "th", "vn", "sg", "my", "ph", "id", "in", "hk", "tw", "la", "mm",
    "de", "fr", "es", "it", "nl", "be", "ch", "se", "no", "dk", "fi", "pl", "ru", "ua",
    "br", "mx", "ar", "cl",
    "za", "ng", "eg", "ae", "sa", "il", "tr",
})


def _is_valid_host(host: str) -> bool:
    if not host:
        return False

    try:
        ipaddress.ip_address(host.strip("[]"))
        return False
    except ValueError:
        pass

    labels = host.split(".")
    if len(labels) < 2:
        return False
    if any(not re.fullmatch(r"[a-zA-Z0-9-]+", label) for label in labels):
        return False

    tld = labels[-1].lower()
    return tld in _VALID_TLDS


def _candidate_host(match: str) -> str:
    url = match if "://" in match else f"https://{match}"
    return urlparse(url).netloc


def extract_urls(text: str) -> list[str]:
    candidates = [match.rstrip(".,;:!?") for match in _URL_PATTERN.findall(text)]
    return [candidate for candidate in candidates if _is_valid_host(_candidate_host(candidate))]


def is_message_only_urls(text: str | None, urls: list[str]) -> bool:
    stripped = text or ""
    for url in urls:
        stripped = stripped.replace(url, "")
    return not stripped.strip()


def normalize_url(url: str) -> str:
    if "://" not in url:
        url = f"https://{url}"

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or ""

    kept_params = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in _TRACKING_PARAMS and not key.startswith(_TRACKING_PARAM_PREFIXES)
    ]
    query = urlencode(kept_params)

    return urlunparse((parsed.scheme, host, path, "", query, ""))
