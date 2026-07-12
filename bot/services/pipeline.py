import asyncio
import logging
from pathlib import Path
from urllib.parse import urlparse

from bot.database.repository import ScanRepository
from bot.models.scan_record import ScanRecord
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanRequest, ScanResult
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict
from bot.services.ai.base import AIProvider, AIProviderError
from bot.services.virustotal.cache import get_cached_or_fetch_file, get_cached_or_fetch_url
from bot.services.virustotal.client import VirusTotalClient
from bot.services.virustotal.polling import poll_until_complete
from bot.utils.hashing import sha256_file
from bot.utils.url_extraction import normalize_url

logger = logging.getLogger(__name__)

_STATUS_SEVERITY = {"malicious": 3, "suspicious": 2, "clean": 1, "pending": 0, "unknown": 0}

_NO_TEXT_PLACEHOLDER = "(No message text — only a file or URL was submitted for scanning.)"


def _worst_url_verdict(verdicts: list[VTUrlVerdict]) -> VTUrlVerdict | None:
    if not verdicts:
        return None
    return max(verdicts, key=lambda v: _STATUS_SEVERITY[v.status])


def _verdict_summary(verdict: VTFileVerdict | VTUrlVerdict) -> str:
    if verdict.status in ("pending", "unknown"):
        return "no VirusTotal result available yet"
    summary = f"{verdict.status} ({verdict.malicious_count}/{verdict.total_engines} engines detected threats)"
    if verdict.detection_names:
        summary += f", detected as: {', '.join(verdict.detection_names)}"
    return summary


def _build_vt_context(vt_file: VTFileVerdict | None, vt_url: VTUrlVerdict | None) -> str | None:
    parts = []
    if vt_file is not None:
        parts.append(f"File scan: {_verdict_summary(vt_file)}")
    if vt_url is not None:
        parts.append(f"URL scan: {_verdict_summary(vt_url)}")
    if not parts:
        return None
    return "\n".join(parts)


class ScanPipeline:
    def __init__(self, ai_provider: AIProvider, vt_client: VirusTotalClient, repo: ScanRepository):
        self._ai = ai_provider
        self._vt = vt_client
        self._repo = repo

    async def run(self, request: ScanRequest) -> ScanResult:
        file_task = (
            asyncio.create_task(self._resolve_file_or_none(request.file_path))
            if request.file_path
            else None
        )
        url_tasks = [asyncio.create_task(self._resolve_url_or_none(u)) for u in request.urls]

        file_result = await file_task if file_task else None
        url_results = [r for r in (await asyncio.gather(*url_tasks) if url_tasks else []) if r is not None]

        sha256 = file_result[0] if file_result else None
        vt_file = file_result[1] if file_result else None
        primary_url = url_results[0][0] if url_results else None
        vt_url = _worst_url_verdict([r[1] for r in url_results])

        vt_context = _build_vt_context(vt_file, vt_url)
        text_for_ai = request.text or _NO_TEXT_PLACEHOLDER
        ai_result = await self._classify_or_none(text_for_ai, request.language, vt_context)

        risk_level = ai_result.risk_level if ai_result is not None else RiskLevel.SAFE
        analysis_failed = ai_result is None

        record = await self._repo.insert_scan(
            self._build_record(request, sha256, primary_url, ai_result, vt_file, vt_url, risk_level)
        )

        return ScanResult(
            risk_level=risk_level,
            ai=ai_result,
            vt_file=vt_file,
            vt_url=vt_url,
            analysis_failed=analysis_failed,
            scan_record_id=record.id,
        )

    async def count_recent_scans(self, chat_type: str, identifier: int) -> int:
        return await self._repo.count_recent_scans(chat_type, identifier)

    async def was_recently_scanned(self, request: ScanRequest) -> bool:
        """True if this URL/file already has a recent cached VirusTotal verdict,
        meaning a re-scan reuses the record instead of calling the VT API."""
        for url in request.urls:
            cached = await self._repo.find_recent_by_url(normalize_url(url))
            if cached is not None and cached.vt_status is not None:
                return True
        if request.file_path:
            try:
                sha256 = sha256_file(request.file_path)
            except OSError:
                return False
            cached = await self._repo.find_recent_by_hash(sha256)
            if cached is not None and cached.vt_status is not None:
                return True
        return False

    async def _classify_or_none(
        self, text: str, language: str, vt_context: str | None
    ) -> IntentResult | None:
        try:
            return await self._ai.classify(text, language, vt_context=vt_context)
        except AIProviderError:
            logger.warning("AI provider failed to classify message", exc_info=True)
            return None

    async def _resolve_file_or_none(self, file_path: str) -> tuple[str, VTFileVerdict] | None:
        try:
            sha256 = sha256_file(file_path)
            verdict = await get_cached_or_fetch_file(sha256, self._repo, self._vt)
            if verdict is None:
                analysis_id = await self._vt.upload_file(Path(file_path))
                analysis = await poll_until_complete(lambda: self._vt.get_analysis(analysis_id))
                verdict = VTFileVerdict(
                    sha256=sha256,
                    status=analysis.status,
                    malicious_count=analysis.malicious_count,
                    total_engines=analysis.total_engines,
                    detection_names=analysis.detection_names,
                )
                if analysis.status != "pending":
                    # /analyses/{id} doesn't reliably populate per-engine detection
                    # names alongside its stats — /files/{sha256} does, so re-fetch
                    # the authoritative report now that VT has indexed the hash.
                    full_report = await self._vt.get_file_report(sha256)
                    if full_report is not None:
                        verdict = full_report
            return sha256, verdict
        except Exception:
            logger.exception("Failed to resolve VirusTotal verdict for file %s", file_path)
            return None

    async def _resolve_url_or_none(self, url: str) -> tuple[str, VTUrlVerdict] | None:
        try:
            normalized = normalize_url(url)
            verdict = await get_cached_or_fetch_url(normalized, self._repo, self._vt)
            if verdict is None:
                analysis_id = await self._vt.scan_url(normalized)
                analysis = await poll_until_complete(lambda: self._vt.get_analysis(analysis_id))
                verdict = VTUrlVerdict(
                    url=normalized,
                    status=analysis.status,
                    malicious_count=analysis.malicious_count,
                    total_engines=analysis.total_engines,
                    detection_names=analysis.detection_names,
                )
                if analysis.status != "pending":
                    # /analyses/{id} doesn't reliably populate per-engine detection
                    # names alongside its stats — /urls/{id} does, so re-fetch the
                    # authoritative report now that VT has indexed the URL.
                    full_report = await self._vt.get_url_report(normalized)
                    if full_report is not None:
                        verdict = full_report
            return normalized, verdict
        except Exception:
            logger.exception("Failed to resolve VirusTotal verdict for url %s", url)
            return None

    def _build_record(
        self,
        request: ScanRequest,
        sha256: str | None,
        primary_url: str | None,
        ai_result: IntentResult | None,
        vt_file: VTFileVerdict | None,
        vt_url: VTUrlVerdict | None,
        risk_level,
    ) -> ScanRecord:
        vt_verdict = vt_file or vt_url
        return ScanRecord(
            chat_id=request.chat_id,
            user_id=request.user_id,
            chat_type=request.chat_type,
            input_type=request.input_type,
            url=primary_url,
            domain=urlparse(primary_url).netloc if primary_url else None,
            sha256=sha256,
            file_name=request.file_name,
            language=request.language,
            ai_risk_level=ai_result.risk_level.value if ai_result else None,
            vt_status=vt_verdict.status if vt_verdict else None,
            vt_malicious_count=vt_verdict.malicious_count if vt_verdict else None,
            vt_total_engines=vt_verdict.total_engines if vt_verdict else None,
            vt_detection_names=vt_verdict.detection_names if vt_verdict and vt_verdict.detection_names else None,
            final_risk_level=risk_level.value,
        )
