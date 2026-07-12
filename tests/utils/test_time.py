from datetime import timedelta
from zoneinfo import ZoneInfo

from bot.utils.time import now_phnom_penh


def test_now_phnom_penh_is_timezone_aware():
    now = now_phnom_penh()
    assert now.tzinfo is not None


def test_now_phnom_penh_uses_asia_phnom_penh_zone():
    now = now_phnom_penh()
    assert now.utcoffset() == timedelta(hours=7)


def test_now_phnom_penh_matches_the_phnom_penh_wall_clock():
    now = now_phnom_penh()
    expected = now.astimezone(ZoneInfo("Asia/Phnom_Penh"))
    assert abs((now - expected).total_seconds()) < 5
