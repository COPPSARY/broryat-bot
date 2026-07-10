from bot.schemas.scan import ScanResult

_ANALYSIS_FAILED = {
    "en": "Analysis failed. Please try again later.",
    "km": "ការវិភាគបានបរាជ័យ។ សូមព្យាយាមម្តងទៀត។",
}


def format_response(result: ScanResult) -> str:
    if result.analysis_failed:
        language = result.ai.language if result.ai else "en"
        return _ANALYSIS_FAILED[language]

    return result.ai.message
