import base64
import logging
from collections.abc import Sequence
from pathlib import Path

import httpx

from bot.schemas.virustotal import VTFileVerdict, VTStatus, VTUrlVerdict
from bot.services.virustotal.rate_limiter import VTRateLimiter

_BASE_URL = "https://www.virustotal.com/api/v3"
_DEFAULT_TIMEOUT = httpx.Timeout(60.0, connect=30.0)
_ROTATABLE_STATUS_CODES = {401, 402, 403, 429}

logger = logging.getLogger(__name__)


def url_id_for(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")


_MAX_DETECTION_NAMES = 5


def _status_from_stats(stats: dict) -> tuple[VTStatus, int, int]:
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    total = sum(stats.values())

    if total == 0:
        return "unknown", 0, 0
    if malicious > 0:
        status: VTStatus = "malicious"
    elif suspicious > 0:
        status = "suspicious"
    else:
        status = "clean"
    return status, malicious, total


def _extract_detection_names(engine_results: dict, limit: int = _MAX_DETECTION_NAMES) -> list[str]:
    names: list[str] = []
    for engine_result in engine_results.values():
        if engine_result.get("category") not in ("malicious", "suspicious"):
            continue
        name = engine_result.get("result")
        if name and name not in names:
            names.append(name)
        if len(names) >= limit:
            break
    return names


class VirusTotalClient:
    def __init__(
        self,
        api_key: str | None,
        rate_limiter: VTRateLimiter,
        base_url: str = _BASE_URL,
        client: httpx.AsyncClient | None = None,
        api_keys: Sequence[str] | None = None,
    ):
        keys = list(dict.fromkeys(key for key in (api_keys or [api_key]) if key))
        if client is None and not keys:
            raise ValueError("At least one VirusTotal API key is required")

        self._rate_limiter = rate_limiter
        self._clients = (
            (client,)
            if client is not None
            else tuple(
                httpx.AsyncClient(
                    base_url=base_url,
                    headers={"x-apikey": key},
                    timeout=_DEFAULT_TIMEOUT,
                )
                for key in keys
            )
        )
        self._client = self._clients[0]
        self._client_index = 0

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_response = None
        for _ in self._clients:
            await self._rate_limiter.acquire()
            for value in (kwargs.get("files") or {}).values():
                file_obj = value[-1] if isinstance(value, tuple) else value
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)

            index = self._client_index
            response = await self._clients[index].request(method, url, **kwargs)
            if (
                response.status_code not in _ROTATABLE_STATUS_CODES
                or len(self._clients) == 1
            ):
                return response

            last_response = response
            self._client_index = (index + 1) % len(self._clients)
            logger.warning(
                "VirusTotal key %d rejected with HTTP %d; trying next key",
                index + 1,
                response.status_code,
            )

        return last_response

    async def get_file_report(self, sha256: str) -> VTFileVerdict | None:
        response = await self._request("GET", f"/files/{sha256}")
        if response.status_code == 404:
            return None
        response.raise_for_status()

        attributes = response.json()["data"]["attributes"]
        status, malicious, total = _status_from_stats(attributes["last_analysis_stats"])
        detection_names = _extract_detection_names(attributes.get("last_analysis_results", {}))
        return VTFileVerdict(
            sha256=sha256,
            status=status,
            malicious_count=malicious,
            total_engines=total,
            detection_names=detection_names,
            permalink=f"https://www.virustotal.com/gui/file/{sha256}",
        )

    async def upload_file(self, file_path: Path) -> str:
        with open(file_path, "rb") as f:
            response = await self._request("POST", "/files", files={"file": (Path(file_path).name, f)})
        response.raise_for_status()
        return response.json()["data"]["id"]

    async def get_analysis(self, analysis_id: str) -> VTFileVerdict:
        response = await self._request("GET", f"/analyses/{analysis_id}")
        response.raise_for_status()

        attributes = response.json()["data"]["attributes"]
        if attributes["status"] != "completed":
            return VTFileVerdict(sha256="", status="pending")

        status, malicious, total = _status_from_stats(attributes["stats"])
        detection_names = _extract_detection_names(attributes.get("results", {}))
        return VTFileVerdict(
            sha256="", status=status, malicious_count=malicious, total_engines=total,
            detection_names=detection_names,
        )

    async def scan_url(self, url: str) -> str:
        response = await self._request("POST", "/urls", data={"url": url})
        response.raise_for_status()
        return response.json()["data"]["id"]

    async def get_url_report(self, url: str) -> VTUrlVerdict | None:
        response = await self._request("GET", f"/urls/{url_id_for(url)}")
        if response.status_code == 404:
            return None
        response.raise_for_status()

        attributes = response.json()["data"]["attributes"]
        status, malicious, total = _status_from_stats(attributes["last_analysis_stats"])
        detection_names = _extract_detection_names(attributes.get("last_analysis_results", {}))
        return VTUrlVerdict(
            url=url,
            status=status,
            malicious_count=malicious,
            total_engines=total,
            detection_names=detection_names,
            permalink=f"https://www.virustotal.com/gui/url/{url_id_for(url)}",
        )
