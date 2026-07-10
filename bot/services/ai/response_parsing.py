import re

from bot.schemas.enums import RiskLevel

_MARKER_PATTERN = re.compile(r"risk\s*:\s*(SAFE|LOW|MEDIUM|HIGH)", re.IGNORECASE)


def parse_ai_response(text: str) -> tuple[RiskLevel, str]:
    """Extract the risk level from a trailing "RISK:LEVEL" marker line and strip it out.

    The marker is always plain English (SAFE/LOW/MEDIUM/HIGH) so parsing never depends
    on the language of the user-visible message, which may be fully localized.
    """
    lines = text.strip().splitlines()
    if not lines:
        raise ValueError("Empty AI response")

    last_line = lines[-1].strip()
    match = _MARKER_PATTERN.fullmatch(last_line)
    if not match:
        raise ValueError("No trailing RISK:LEVEL marker line found in AI response")

    risk_level = RiskLevel(match.group(1).upper())
    message = "\n".join(lines[:-1]).strip()
    return risk_level, message
