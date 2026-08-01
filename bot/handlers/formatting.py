from bot.schemas.enums import RiskLevel
from bot.schemas.scan import ScanResult
from bot.services.ai.prompt import DISCLAIMER

_ANALYSIS_FAILED = {
    "en": "Analysis failed. Please try again later.",
    "km": "ការវិភាគបានបរាជ័យ។ សូមព្យាយាមម្តងទៀត។",
}

_VT_FALLBACK = {
    "en": {
        "malicious": (
            "🚨 *VirusTotal verdict: MALICIOUS* 🚨",
            "🚫 Do not open or click it. Delete it and report the sender.",
        ),
        "suspicious": (
            "⚠️ *VirusTotal verdict: SUSPICIOUS* ⚠️",
            "🔍 Avoid opening it until you can verify the sender and content.",
        ),
        "clean": (
            "✅ *VirusTotal verdict: CLEAN* ✅",
            "🙂 No known malware was detected. Stay cautious and verify the sender.",
        ),
        "unknown": (
            "⚠️ *VirusTotal verdict: UNKNOWN* ⚠️",
            "🔁 VirusTotal returned no conclusive result. Please try again later.",
        ),
    },
    "km": {
        "malicious": (
            "🚨 *លទ្ធផល VirusTotal៖ មានគ្រោះថ្នាក់* 🚨",
            "🚫 កុំបើក ឬចុចវា។ សូមលុបវា និងរាយការណ៍អ្នកផ្ញើ។",
        ),
        "suspicious": (
            "⚠️ *លទ្ធផល VirusTotal៖ គួរឱ្យសង្ស័យ* ⚠️",
            "🔍 កុំបើកវា រហូតដល់អ្នកអាចផ្ទៀងផ្ទាត់អ្នកផ្ញើ និងខ្លឹមសារ។",
        ),
        "clean": (
            "✅ *លទ្ធផល VirusTotal៖ ស្អាត* ✅",
            "🙂 មិនបានរកឃើញមេរោគដែលគេស្គាល់ទេ។ សូមប្រុងប្រយ័ត្ន និងផ្ទៀងផ្ទាត់អ្នកផ្ញើ។",
        ),
        "unknown": (
            "⚠️ *លទ្ធផល VirusTotal៖ មិនច្បាស់លាស់* ⚠️",
            "🔁 VirusTotal មិនបានផ្តល់លទ្ធផលច្បាស់លាស់ទេ។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ។",
        ),
    },
}

_AI_UNAVAILABLE = {
    "en": "ℹ️ AI explanation is currently unavailable — this result is from VirusTotal only.",
    "km": "ℹ️ ការពន្យល់ពី AI មិនអាចប្រើបាននៅពេលនេះ — លទ្ធផលនេះមកពី VirusTotal តែប៉ុណ្ណោះ។",
}

_DETECTIONS = {
    "en": "Malicious detections",
    "km": "ការរកឃើញថាមានគ្រោះថ្នាក់",
}

_DETECTED_AS = {
    "en": "Detected as",
    "km": "ត្រូវបានរកឃើញថាជា",
}

_RECOMMENDATION_LABEL = {
    "en": "Recommendation",
    "km": "ការណែនាំ",
}

_VT_PENDING = {
    "en": "⏳ The scan is still in progress. Please send it again in a moment to get the result.",
    "km": "⏳ ការស្កេនកំពុងដំណើរការនៅឡើយ។ សូមផ្ញើម្ដងទៀតបន្តិចទៀត ដើម្បីទទួលបានលទ្ធផល។",
}

# Group replies never surface the AI's own freeform message — only a fixed,
# structured summary keyed off the final merged risk level.
_RISK_LEVEL_SUMMARY = {
    "en": {
        RiskLevel.HIGH: (
            "🚨 *Risk Level: HIGH* 🚨",
            "🚫 Do not click, open, or reply to it. Delete it and report the sender.",
        ),
        RiskLevel.MEDIUM: (
            "⚠️ *Risk Level: MEDIUM* ⚠️",
            "🔍 Be cautious — verify the sender and content before taking any action.",
        ),
        RiskLevel.LOW: (
            "🟡 *Risk Level: LOW* 🟡",
            "🔍 Low risk detected. Stay cautious and verify before acting.",
        ),
        RiskLevel.SAFE: (
            "✅ *Risk Level: SAFE* ✅",
            "🙂 No threats were detected. Stay cautious and verify the sender.",
        ),
        RiskLevel.UNKNOWN: (
            "⚠️ *Risk Level: UNKNOWN* ⚠️",
            "🔁 No conclusive result. Please try again later.",
        ),
    },
    "km": {
        RiskLevel.HIGH: (
            "🚨 *កម្រិតគ្រោះថ្នាក់៖ ខ្ពស់* 🚨",
            "🚫 កុំចុច បើក ឬឆ្លើយតបវា។ សូមលុបវា និងរាយការណ៍អ្នកផ្ញើ។",
        ),
        RiskLevel.MEDIUM: (
            "⚠️ *កម្រិតគ្រោះថ្នាក់៖ មធ្យម* ⚠️",
            "🔍 សូមប្រុងប្រយ័ត្ន — ផ្ទៀងផ្ទាត់អ្នកផ្ញើ និងខ្លឹមសារ មុននឹងធ្វើសកម្មភាពណាមួយ។",
        ),
        RiskLevel.LOW: (
            "🟡 *កម្រិតគ្រោះថ្នាក់៖ ទាប* 🟡",
            "🔍 បានរកឃើញហានិភ័យទាប។ សូមប្រុងប្រយ័ត្ន និងផ្ទៀងផ្ទាត់មុននឹងធ្វើសកម្មភាព។",
        ),
        RiskLevel.SAFE: (
            "✅ *កម្រិតគ្រោះថ្នាក់៖ សុវត្ថិភាព* ✅",
            "🙂 មិនបានរកឃើញការគំរាមកំហែងទេ។ សូមប្រុងប្រយ័ត្ន និងផ្ទៀងផ្ទាត់អ្នកផ្ញើ។",
        ),
        RiskLevel.UNKNOWN: (
            "⚠️ *កម្រិតគ្រោះថ្នាក់៖ មិនច្បាស់លាស់* ⚠️",
            "🔁 គ្មានលទ្ធផលច្បាស់លាស់ទេ។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ។",
        ),
    },
}


def _format_verdict_details(verdict, language: str) -> list[str]:
    if verdict is None:
        return []
    details = []
    if verdict.total_engines:
        details.append(f"{_DETECTIONS[language]}: {verdict.malicious_count}/{verdict.total_engines}")
    if verdict.detection_names:
        details.append(f"{_DETECTED_AS[language]}: {', '.join(verdict.detection_names[:3])}")
    return details


def _is_vt_pending(result: ScanResult) -> bool:
    return (result.vt_file is not None and result.vt_file.status == "pending") or (
        result.vt_url is not None and result.vt_url.status == "pending"
    )


def format_vt_fallback(result: ScanResult, language: str) -> str:
    verdict = result.vt_file or result.vt_url
    if verdict is None:
        return f"{_ANALYSIS_FAILED[language]}\n\n{DISCLAIMER[language]}"

    title, recommendation = _VT_FALLBACK[language].get(
        verdict.status, _VT_FALLBACK[language]["unknown"]
    )

    lines = [title, ""]

    details = _format_verdict_details(verdict, language)
    if details:
        lines.extend(details)
        lines.append("")

    lines.append(_AI_UNAVAILABLE[language])
    lines.append("")
    lines.append(f"*{_RECOMMENDATION_LABEL[language]}:*")
    lines.append(recommendation)
    lines.append("")
    lines.append(f"{DISCLAIMER[language]}")

    return "\n".join(lines)


def format_group_response(result: ScanResult) -> str:
    language = result.ai.language if result.ai else result.language

    if _is_vt_pending(result):
        return _VT_PENDING[language]

    if result.analysis_failed:
        return format_vt_fallback(result, language)

    title, recommendation = _RISK_LEVEL_SUMMARY[language].get(
        result.risk_level, _RISK_LEVEL_SUMMARY[language][RiskLevel.UNKNOWN]
    )

    lines = [title, ""]

    details = _format_verdict_details(result.vt_file or result.vt_url, language)
    if details:
        lines.extend(details)
        lines.append("")

    lines.append(f"*{_RECOMMENDATION_LABEL[language]}:*")
    lines.append(recommendation)
    lines.append("")
    lines.append(DISCLAIMER[language])

    return "\n".join(lines)


def format_response(result: ScanResult) -> str:
    language = result.ai.language if result.ai else result.language

    if _is_vt_pending(result):
        return _VT_PENDING[language]

    if result.analysis_failed:
        return format_vt_fallback(result, language)

    return result.ai.message
