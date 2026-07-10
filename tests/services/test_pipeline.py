import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

from bot.models.scan_record import ScanRecord
from bot.schemas.enums import RiskLevel
from bot.schemas.intent import IntentResult
from bot.schemas.scan import ScanRequest
from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict
from bot.services.ai.base import AIProviderError
from bot.services.pipeline import ScanPipeline, _build_vt_context


def test_build_vt_context_labels_file_verdict_explicitly():
    verdict = VTFileVerdict(sha256="a" * 64, status="malicious", malicious_count=10, total_engines=70)
    context = _build_vt_context(verdict, None)
    assert context.startswith("File scan:")
    assert "URL" not in context


def test_build_vt_context_labels_url_verdict_explicitly():
    verdict = VTUrlVerdict(url="https://example.com", status="malicious", malicious_count=10, total_engines=70)
    context = _build_vt_context(None, verdict)
    assert context.startswith("URL scan:")
    assert "File" not in context


def test_build_vt_context_includes_both_labeled_separately_when_both_present():
    vt_file = VTFileVerdict(sha256="a" * 64, status="clean", total_engines=70)
    vt_url = VTUrlVerdict(url="https://example.com", status="malicious", malicious_count=5, total_engines=70)
    context = _build_vt_context(vt_file, vt_url)
    assert "File scan:" in context
    assert "URL scan:" in context
    assert "clean" in context
    assert "malicious" in context


def test_build_vt_context_returns_none_when_neither_present():
    assert _build_vt_context(None, None) is None


def _intent_result(risk_level=RiskLevel.SAFE, **overrides):
    defaults = dict(risk_level=risk_level, message="default ai message", language="en")
    defaults.update(overrides)
    return IntentResult(**defaults)


def _pipeline(ai_provider=None, vt_client=None, repo=None):
    if ai_provider is None:
        ai_provider = AsyncMock()
        ai_provider.classify.return_value = _intent_result()
    vt_client = vt_client or AsyncMock()
    if repo is None:
        repo = AsyncMock()
        repo.find_recent_by_hash.return_value = None
        repo.find_recent_by_url.return_value = None
        repo.insert_scan.side_effect = lambda record: record
    return ScanPipeline(ai_provider, vt_client, repo), ai_provider, vt_client, repo


async def test_text_only_request_calls_ai_and_persists_result():
    ai_provider = AsyncMock()
    ai_provider.classify.return_value = _intent_result(
        risk_level=RiskLevel.HIGH,
        message="This impersonates a bank. Do not click.",
    )
    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="text",
        text="your account is suspended, click here", language="en",
    )

    result = await pipeline.run(request)

    assert result.risk_level == RiskLevel.HIGH
    ai_provider.classify.assert_awaited_once_with(request.text, "en", vt_context=None)
    repo.insert_scan.assert_awaited_once()
    persisted: ScanRecord = repo.insert_scan.call_args[0][0]
    assert persisted.ai_risk_level == "HIGH"
    assert persisted.final_risk_level == "HIGH"


async def test_scan_result_carries_the_persisted_scan_record_id():
    inserted_record = ScanRecord(
        chat_id=1, user_id=2, chat_type="private", input_type="text",
        language="en", final_risk_level="SAFE",
    )
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = None
    repo.find_recent_by_url.return_value = None
    repo.insert_scan.return_value = inserted_record
    pipeline, ai_provider, vt_client, repo = _pipeline(repo=repo)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="text", text="hello", language="en",
    )

    result = await pipeline.run(request)

    assert result.scan_record_id == inserted_record.id


async def test_ai_provider_error_does_not_crash_pipeline():
    ai_provider = AsyncMock()
    ai_provider.classify.side_effect = AIProviderError("boom")
    pipeline, *_ = _pipeline(ai_provider=ai_provider)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="text", text="hello", language="en",
    )

    result = await pipeline.run(request)

    assert result.ai is None
    assert result.analysis_failed is True


async def test_file_cache_hit_skips_vt_upload(tmp_path):
    file_path = tmp_path / "sample.exe"
    file_path.write_bytes(b"fake binary")

    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = ScanRecord(
        chat_id=1, user_id=2, chat_type="private", input_type="file",
        sha256="dummy", language="en", vt_status="clean", vt_malicious_count=0,
        vt_total_engines=70, final_risk_level="SAFE",
    )
    repo.insert_scan.side_effect = lambda record: record

    vt_client = AsyncMock()
    pipeline, ai_provider, vt_client, repo = _pipeline(vt_client=vt_client, repo=repo)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="file",
        file_path=str(file_path), file_name="sample.exe", language="en",
    )

    result = await pipeline.run(request)

    vt_client.upload_file.assert_not_awaited()
    assert result.vt_file.status == "clean"


async def test_vt_context_includes_detection_names_and_record_persists_them():
    ai_provider = AsyncMock()
    ai_provider.classify.return_value = _intent_result(
        risk_level=RiskLevel.HIGH, message="This is a known trojan."
    )
    vt_client = AsyncMock()
    vt_client.get_url_report.return_value = VTUrlVerdict(
        url="https://example.com/phish", status="malicious", malicious_count=10, total_engines=70,
        detection_names=["Trojan.GenericKD", "Phishing.Generic"],
    )
    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider, vt_client=vt_client)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="url",
        text="check this out", urls=["https://example.com/phish"], language="en",
    )

    await pipeline.run(request)

    ai_call_kwargs = ai_provider.classify.call_args.kwargs
    assert "Trojan.GenericKD" in ai_call_kwargs["vt_context"]
    assert "Phishing.Generic" in ai_call_kwargs["vt_context"]

    persisted: ScanRecord = repo.insert_scan.call_args[0][0]
    assert persisted.vt_detection_names == ["Trojan.GenericKD", "Phishing.Generic"]


async def test_ai_conclusion_is_final_even_when_vt_flags_malicious():
    ai_provider = AsyncMock()
    ai_provider.classify.return_value = _intent_result(
        risk_level=RiskLevel.SAFE, message="This looks safe.",
    )
    vt_client = AsyncMock()
    vt_client.get_url_report.return_value = VTUrlVerdict(
        url="https://example.com/phish", status="malicious", malicious_count=10, total_engines=70,
    )
    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider, vt_client=vt_client)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="url",
        text="check this out", urls=["https://example.com/phish"], language="en",
    )

    result = await pipeline.run(request)

    # AI already saw the VT verdict in its prompt (asserted below) and is trusted as final.
    assert result.risk_level == RiskLevel.SAFE
    vt_client.scan_url.assert_not_awaited()
    ai_call_kwargs = ai_provider.classify.call_args.kwargs
    assert "malicious" in ai_call_kwargs["vt_context"]


async def test_ai_still_runs_for_file_only_request_with_no_caption():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = ScanRecord(
        chat_id=1, user_id=2, chat_type="private", input_type="file",
        sha256="dummy", language="en", vt_status="malicious", vt_malicious_count=10,
        vt_total_engines=70, final_risk_level="HIGH",
    )
    repo.insert_scan.side_effect = lambda record: record

    ai_provider = AsyncMock()
    ai_provider.classify.return_value = _intent_result(
        risk_level=RiskLevel.HIGH, message="This file is malicious."
    )
    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider, repo=repo)

    with tempfile.TemporaryDirectory() as d:
        file_path = Path(d) / "sample.exe"
        file_path.write_bytes(b"fake binary")

        request = ScanRequest(
            chat_id=1, user_id=2, chat_type="private", input_type="file",
            file_path=str(file_path), file_name="sample.exe", language="en",
        )
        result = await pipeline.run(request)

    ai_provider.classify.assert_awaited_once()
    call_args = ai_provider.classify.call_args
    assert call_args[0][0]  # some placeholder text was passed, not empty/None
    assert "malicious" in call_args.kwargs["vt_context"]
    assert result.risk_level == RiskLevel.HIGH


async def test_vt_scan_runs_before_ai_classification_so_ai_can_see_the_verdict():
    call_order = []

    ai_provider = AsyncMock()

    async def fake_classify(text, language, vt_context=None):
        call_order.append("ai")
        return _intent_result()

    ai_provider.classify.side_effect = fake_classify

    vt_client = AsyncMock()

    async def fake_get_url_report(url):
        call_order.append("vt")
        return VTUrlVerdict(url=url, status="clean", total_engines=70)

    vt_client.get_url_report.side_effect = fake_get_url_report

    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider, vt_client=vt_client)

    request = ScanRequest(
        chat_id=1, user_id=2, chat_type="private", input_type="url",
        text="check this out", urls=["https://example.com"], language="en",
    )

    await pipeline.run(request)

    assert call_order == ["vt", "ai"]


async def test_file_not_cached_uploads_and_polls():
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = None
    repo.insert_scan.side_effect = lambda record: record

    vt_client = AsyncMock()
    vt_client.get_file_report.return_value = None
    vt_client.upload_file.return_value = "analysis-1"
    vt_client.get_analysis.return_value = VTFileVerdict(
        sha256="", status="malicious", malicious_count=4, total_engines=70
    )

    ai_provider = AsyncMock()
    ai_provider.classify.return_value = _intent_result(
        risk_level=RiskLevel.HIGH, message="This file is malicious."
    )

    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider, vt_client=vt_client, repo=repo)

    with tempfile.TemporaryDirectory() as d:
        file_path = Path(d) / "sample.exe"
        file_path.write_bytes(b"fake binary")

        request = ScanRequest(
            chat_id=1, user_id=2, chat_type="private", input_type="file",
            file_path=str(file_path), file_name="sample.exe", language="en",
        )
        result = await pipeline.run(request)

    vt_client.upload_file.assert_awaited_once()
    assert result.vt_file.status == "malicious"
    assert result.risk_level == RiskLevel.HIGH
    ai_call_kwargs = ai_provider.classify.call_args.kwargs
    assert "malicious" in ai_call_kwargs["vt_context"]


async def test_file_upload_refetches_full_report_after_analysis_completes_for_detection_names():
    # VT's /analyses/{id} endpoint (used while polling) doesn't reliably populate
    # per-engine detection names at the same time as its aggregate stats — only
    # /files/{sha256} does. So after polling completes, the pipeline must re-fetch
    # the authoritative file report to get real detection names.
    repo = AsyncMock()
    repo.find_recent_by_hash.return_value = None
    repo.insert_scan.side_effect = lambda record: record

    vt_client = AsyncMock()
    call_count = {"n": 0}

    async def fake_get_file_report(sha256):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return None
        return VTFileVerdict(
            sha256=sha256, status="malicious", malicious_count=4, total_engines=70,
            detection_names=["Trojan.GenericKD"],
        )

    vt_client.get_file_report.side_effect = fake_get_file_report
    vt_client.upload_file.return_value = "analysis-1"
    vt_client.get_analysis.return_value = VTFileVerdict(
        sha256="", status="malicious", malicious_count=4, total_engines=70, detection_names=[]
    )

    ai_provider = AsyncMock()
    ai_provider.classify.return_value = _intent_result(
        risk_level=RiskLevel.HIGH, message="This is a known trojan."
    )

    pipeline, ai_provider, vt_client, repo = _pipeline(ai_provider=ai_provider, vt_client=vt_client, repo=repo)

    with tempfile.TemporaryDirectory() as d:
        file_path = Path(d) / "sample.exe"
        file_path.write_bytes(b"fake binary")

        request = ScanRequest(
            chat_id=1, user_id=2, chat_type="private", input_type="file",
            file_path=str(file_path), file_name="sample.exe", language="en",
        )
        result = await pipeline.run(request)

    assert vt_client.get_file_report.await_count == 2
    assert result.vt_file.detection_names == ["Trojan.GenericKD"]
    persisted: ScanRecord = repo.insert_scan.call_args[0][0]
    assert persisted.vt_detection_names == ["Trojan.GenericKD"]
