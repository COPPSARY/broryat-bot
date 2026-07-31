from unittest.mock import AsyncMock

from bot.models.scan_record import ScanRecord
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict
from bot.services.virustotal.cache import get_cached_or_fetch_file, get_cached_or_fetch_url
from bot.services.virustotal.client import url_id_for

SHA256 = "a" * 64


def _cached_record(vt_status="malicious", malicious_count=5, total_engines=70, detection_names=None):
    return ScanRecord(
        chat_id=1,
        user_id=2,
        chat_type="private",
        input_type="file",
        sha256=SHA256,
        language="en",
        vt_status=vt_status,
        vt_malicious_count=malicious_count,
        vt_total_engines=total_engines,
        vt_detection_names=detection_names,
        final_risk_level="HIGH",
    )


async def test_returns_cached_verdict_without_calling_vt_when_recent_record_exists():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = _cached_record(detection_names=["Trojan.GenericKD"])
    vt_client = AsyncMock()

    verdict = await get_cached_or_fetch_file(SHA256, repo, vt_client)

    assert verdict.status == "malicious"
    assert verdict.malicious_count == 5
    assert verdict.detection_names == ["Trojan.GenericKD"]
    assert verdict.permalink == f"https://www.virustotal.com/gui/file/{SHA256}"
    vt_client.get_file_report.assert_not_awaited()


async def test_falls_back_to_vt_when_no_cached_record():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = None
    vt_client = AsyncMock()
    vt_client.get_file_report.return_value = VTFileVerdict(sha256=SHA256, status="clean", total_engines=70)

    verdict = await get_cached_or_fetch_file(SHA256, repo, vt_client)

    assert verdict.status == "clean"
    vt_client.get_file_report.assert_awaited_once_with(SHA256)


async def test_falls_back_to_vt_when_cached_record_has_no_vt_status():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = _cached_record(vt_status=None)
    vt_client = AsyncMock()
    vt_client.get_file_report.return_value = None

    verdict = await get_cached_or_fetch_file(SHA256, repo, vt_client)

    assert verdict is None
    vt_client.get_file_report.assert_awaited_once_with(SHA256)


async def test_falls_back_to_vt_when_cached_record_status_is_still_pending():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = _cached_record(vt_status="pending")
    vt_client = AsyncMock()
    vt_client.get_file_report.return_value = VTFileVerdict(sha256=SHA256, status="malicious", malicious_count=9, total_engines=70)

    verdict = await get_cached_or_fetch_file(SHA256, repo, vt_client)

    assert verdict.status == "malicious"
    vt_client.get_file_report.assert_awaited_once_with(SHA256)


async def test_returns_none_when_neither_cache_nor_vt_has_data():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = None
    vt_client = AsyncMock()
    vt_client.get_file_report.return_value = None

    verdict = await get_cached_or_fetch_file(SHA256, repo, vt_client)

    assert verdict is None


async def test_url_cache_hit_skips_vt_call():
    url = "https://example.com/phish"
    record = ScanRecord(
        chat_id=1,
        user_id=2,
        chat_type="private",
        input_type="url",
        url=url,
        language="en",
        vt_status="malicious",
        vt_malicious_count=8,
        vt_total_engines=70,
        final_risk_level="HIGH",
    )
    repo = AsyncMock()
    repo.find_recent_by_url.return_value = record
    vt_client = AsyncMock()

    verdict = await get_cached_or_fetch_url(url, repo, vt_client)

    assert verdict.status == "malicious"
    assert verdict.malicious_count == 8
    assert verdict.permalink == f"https://www.virustotal.com/gui/url/{url_id_for(url)}"
    vt_client.get_url_report.assert_not_awaited()


async def test_url_cache_miss_calls_vt():
    url = "https://example.com/safe"
    repo = AsyncMock()
    repo.find_recent_by_url.return_value = None
    vt_client = AsyncMock()
    vt_client.get_url_report.return_value = VTUrlVerdict(url=url, status="clean", total_engines=70)

    verdict = await get_cached_or_fetch_url(url, repo, vt_client)

    assert verdict.status == "clean"
    vt_client.get_url_report.assert_awaited_once_with(url)


async def test_url_falls_back_to_vt_when_cached_record_status_is_still_pending():
    url = "https://example.com/phish"
    record = ScanRecord(
        chat_id=1,
        user_id=2,
        chat_type="private",
        input_type="url",
        url=url,
        language="en",
        vt_status="pending",
        final_risk_level="SAFE",
    )
    repo = AsyncMock()
    repo.find_recent_by_url.return_value = record
    vt_client = AsyncMock()
    vt_client.get_url_report.return_value = VTUrlVerdict(url=url, status="malicious", malicious_count=9, total_engines=70)

    verdict = await get_cached_or_fetch_url(url, repo, vt_client)

    assert verdict.status == "malicious"
    vt_client.get_url_report.assert_awaited_once_with(url)
