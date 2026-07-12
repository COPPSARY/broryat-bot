from datetime import datetime
from zoneinfo import ZoneInfo

PHNOM_PENH = ZoneInfo("Asia/Phnom_Penh")


def now_phnom_penh() -> datetime:
    """Current time in Cambodia (Asia/Phnom_Penh, UTC+7)."""
    return datetime.now(PHNOM_PENH)
