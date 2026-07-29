from bot.schemas.scan import ScanResult

_ANALYSIS_FAILED = {
    "en": "Analysis failed. Please try again later.",
    "km": "ការវិភាគបានបរាជ័យ។ សូមព្យាយាមម្តងទៀត។",
}

_VT_PENDING = {
    "en": "⏳ The scan is still in progress. Please send it again in a moment to get the result.",
    "km": "⏳ ការស្កេនកំពុងដំណើរការនៅឡើយ។ សូមផ្ញើម្ដងទៀតបន្តិចទៀត ដើម្បីទទួលបានលទ្ធផល។",
}


def _is_vt_pending(result: ScanResult) -> bool:
    return (result.vt_file is not None and result.vt_file.status == "pending") or (
        result.vt_url is not None and result.vt_url.status == "pending"
    )


def format_response(result: ScanResult) -> str:
    language = result.ai.language if result.ai else "en"

    if _is_vt_pending(result):
        return _VT_PENDING[language]

    if result.analysis_failed:
        return _ANALYSIS_FAILED[language]

    return result.ai.message
