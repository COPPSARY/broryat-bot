import httpx
import pytest
import respx

from bot.services.virustotal.client import VirusTotalClient, url_id_for
from bot.services.virustotal.rate_limiter import VTRateLimiter


@pytest.fixture
def rate_limiter():
    return VTRateLimiter(rpm_limit=1000, daily_limit=100000, monthly_limit=1000000)


@pytest.fixture
def client(rate_limiter):
    return VirusTotalClient(api_key="test-key", rate_limiter=rate_limiter)


SHA256 = "a" * 64


def test_default_client_uses_a_generous_timeout_for_slow_vt_endpoints(rate_limiter):
    vt_client = VirusTotalClient(api_key="test-key", rate_limiter=rate_limiter)

    timeout = vt_client._client.timeout

    assert timeout.connect >= 30
    assert timeout.read >= 30
    assert timeout.write >= 30


@respx.mock
async def test_get_file_report_returns_malicious_verdict(client):
    respx.get(f"https://www.virustotal.com/api/v3/files/{SHA256}").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": SHA256,
                    "attributes": {
                        "last_analysis_stats": {
                            "malicious": 12,
                            "suspicious": 1,
                            "undetected": 55,
                            "harmless": 2,
                            "timeout": 0,
                        },
                        "last_analysis_date": 1750000000,
                        "last_analysis_results": {
                            "EngineA": {"category": "malicious", "result": "Trojan.GenericKD"},
                            "EngineB": {"category": "malicious", "result": "Trojan.GenericKD"},
                            "EngineC": {"category": "suspicious", "result": "Suspicious.Behavior"},
                            "EngineD": {"category": "undetected", "result": None},
                        },
                    },
                }
            },
        )
    )

    verdict = await client.get_file_report(SHA256)

    assert verdict is not None
    assert verdict.status == "malicious"
    assert verdict.malicious_count == 12
    assert verdict.total_engines == 70
    assert verdict.detection_names == ["Trojan.GenericKD", "Suspicious.Behavior"]
    assert verdict.permalink == f"https://www.virustotal.com/gui/file/{SHA256}"


@respx.mock
async def test_get_file_report_returns_none_when_not_found(client):
    respx.get(f"https://www.virustotal.com/api/v3/files/{SHA256}").mock(
        return_value=httpx.Response(404, json={"error": {"code": "NotFoundError"}})
    )

    verdict = await client.get_file_report(SHA256)

    assert verdict is None


@respx.mock
async def test_get_file_report_clean_when_zero_malicious(client):
    respx.get(f"https://www.virustotal.com/api/v3/files/{SHA256}").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": SHA256,
                    "attributes": {
                        "last_analysis_stats": {
                            "malicious": 0,
                            "suspicious": 0,
                            "undetected": 60,
                            "harmless": 10,
                            "timeout": 0,
                        },
                        "last_analysis_date": 1750000000,
                    },
                }
            },
        )
    )

    verdict = await client.get_file_report(SHA256)

    assert verdict.status == "clean"
    assert verdict.malicious_count == 0


@respx.mock
async def test_upload_file_returns_analysis_id(client, tmp_path):
    file_path = tmp_path / "sample.exe"
    file_path.write_bytes(b"fake binary content")

    respx.post("https://www.virustotal.com/api/v3/files").mock(
        return_value=httpx.Response(200, json={"data": {"type": "analysis", "id": "analysis-123"}})
    )

    analysis_id = await client.upload_file(file_path)

    assert analysis_id == "analysis-123"


@respx.mock
async def test_get_analysis_pending_when_not_completed(client):
    respx.get("https://www.virustotal.com/api/v3/analyses/analysis-123").mock(
        return_value=httpx.Response(
            200, json={"data": {"id": "analysis-123", "attributes": {"status": "queued", "stats": {}}}}
        )
    )

    verdict = await client.get_analysis("analysis-123")

    assert verdict.status == "pending"


@respx.mock
async def test_get_analysis_completed_maps_stats(client):
    respx.get("https://www.virustotal.com/api/v3/analyses/analysis-123").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "analysis-123",
                    "attributes": {
                        "status": "completed",
                        "stats": {"malicious": 3, "suspicious": 0, "undetected": 67, "harmless": 0, "timeout": 0},
                        "results": {
                            "EngineA": {"category": "malicious", "result": "Phishing.Generic"},
                        },
                    },
                }
            },
        )
    )

    verdict = await client.get_analysis("analysis-123")

    assert verdict.status == "malicious"
    assert verdict.malicious_count == 3
    assert verdict.total_engines == 70
    assert verdict.detection_names == ["Phishing.Generic"]


@respx.mock
async def test_detection_names_limited_to_five_distinct_entries(client):
    results = {
        f"Engine{i}": {"category": "malicious", "result": f"Threat.Name{i}"} for i in range(10)
    }
    respx.get(f"https://www.virustotal.com/api/v3/files/{SHA256}").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": SHA256,
                    "attributes": {
                        "last_analysis_stats": {"malicious": 10, "undetected": 60},
                        "last_analysis_results": results,
                    },
                }
            },
        )
    )

    verdict = await client.get_file_report(SHA256)

    assert len(verdict.detection_names) == 5


@respx.mock
async def test_scan_url_returns_analysis_id(client):
    respx.post("https://www.virustotal.com/api/v3/urls").mock(
        return_value=httpx.Response(200, json={"data": {"type": "analysis", "id": "url-analysis-1"}})
    )

    analysis_id = await client.scan_url("https://example.com/phish")

    assert analysis_id == "url-analysis-1"


@respx.mock
async def test_get_url_report_returns_none_when_not_found(client):
    url = "https://example.com/never-seen"
    respx.get(f"https://www.virustotal.com/api/v3/urls/{url_id_for(url)}").mock(
        return_value=httpx.Response(404, json={"error": {"code": "NotFoundError"}})
    )

    verdict = await client.get_url_report(url)

    assert verdict is None


@respx.mock
async def test_get_url_report_includes_gui_permalink(client):
    url = "https://example.com/phish"
    respx.get(f"https://www.virustotal.com/api/v3/urls/{url_id_for(url)}").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": url_id_for(url),
                    "attributes": {
                        "last_analysis_stats": {"malicious": 5, "undetected": 65},
                        "last_analysis_results": {},
                    },
                }
            },
        )
    )

    verdict = await client.get_url_report(url)

    assert verdict.permalink == f"https://www.virustotal.com/gui/url/{url_id_for(url)}"


def test_url_id_for_is_urlsafe_base64_without_padding():
    url_id = url_id_for("https://example.com/path")
    assert "=" not in url_id
    assert "/" not in url_id
