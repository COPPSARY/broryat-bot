from typing import Protocol

from bot.models.scan_record import ScanRecord
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict
from bot.services.virustotal.client import url_id_for

_DEFAULT_WITHIN_HOURS = 24


class HashRepository(Protocol):
    async def find_recent_by_hash(self, sha256: str, within_hours: int) -> ScanRecord | None: ...


class UrlRepository(Protocol):
    async def find_recent_by_url(self, url: str, within_hours: int) -> ScanRecord | None: ...


class FileFetcher(Protocol):
    async def get_file_report(self, sha256: str) -> VTFileVerdict | None: ...


class UrlFetcher(Protocol):
    async def get_url_report(self, url: str) -> VTUrlVerdict | None: ...


async def get_cached_or_fetch_file(
    sha256: str,
    repo: HashRepository,
    vt_client: FileFetcher,
    within_hours: int = _DEFAULT_WITHIN_HOURS,
) -> VTFileVerdict | None:
    cached = await repo.find_recent_by_hash(sha256, within_hours)
    if cached is not None and cached.vt_status is not None and cached.vt_status != "pending":
        return VTFileVerdict(
            sha256=sha256,
            status=cached.vt_status,
            malicious_count=cached.vt_malicious_count or 0,
            total_engines=cached.vt_total_engines or 0,
            detection_names=cached.vt_detection_names or [],
            permalink=f"https://www.virustotal.com/gui/file/{sha256}",
        )
    return await vt_client.get_file_report(sha256)


async def get_cached_or_fetch_url(
    url: str,
    repo: UrlRepository,
    vt_client: UrlFetcher,
    within_hours: int = _DEFAULT_WITHIN_HOURS,
) -> VTUrlVerdict | None:
    cached = await repo.find_recent_by_url(url, within_hours)
    if cached is not None and cached.vt_status is not None and cached.vt_status != "pending":
        return VTUrlVerdict(
            url=url,
            status=cached.vt_status,
            malicious_count=cached.vt_malicious_count or 0,
            total_engines=cached.vt_total_engines or 0,
            detection_names=cached.vt_detection_names or [],
            permalink=f"https://www.virustotal.com/gui/url/{url_id_for(url)}",
        )
    return await vt_client.get_url_report(url)
