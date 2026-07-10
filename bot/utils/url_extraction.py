import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_URL_PATTERN = re.compile(
    r"https?://[^\s()<>\[\]\"']+"
    r"|(?<![\w@.])(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s()<>\[\]\"']*)?"
)

_TRACKING_PARAM_PREFIXES = ("utm_",)
_TRACKING_PARAMS = {"fbclid", "gclid"}


def extract_urls(text: str) -> list[str]:
    return [match.rstrip(".,;:!?") for match in _URL_PATTERN.findall(text)]


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
