import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from stock_monitor.scheduler import get_schedule  # noqa: E402


def test_market_hours_schedule_returns_5min_interval():
    watchlist = [{"code": "002131", "market": "sz"}]
    now = datetime(2026, 3, 4, 10, 0)
    schedule = get_schedule(watchlist, now=now)

    assert schedule["run"] is True
    assert schedule["mode"] == "market"
    assert schedule["interval"] == 300
    assert len(schedule["stocks"]) == 1


def test_night_schedule_only_monitors_fx():
    watchlist = [
        {"code": "002131", "market": "sz"},
        {"code": "XAU", "market": "fx"},
    ]
    now = datetime(2026, 3, 4, 2, 0)
    schedule = get_schedule(watchlist, now=now)

    assert schedule["run"] is True
    assert schedule["mode"] == "night"
    assert schedule["interval"] == 3600
    assert schedule["stocks"] == [{"code": "XAU", "market": "fx"}]


def test_lunch_schedule_returns_10min_interval():
    watchlist = [{"code": "002131", "market": "sz"}]
    now = datetime(2026, 3, 4, 12, 0)
    schedule = get_schedule(watchlist, now=now)

    assert schedule["run"] is True
    assert schedule["mode"] == "lunch"
    assert schedule["interval"] == 600
    assert schedule["stocks"] == watchlist


def test_after_hours_schedule_returns_30min_interval():
    watchlist = [{"code": "002131", "market": "sz"}]
    now = datetime(2026, 3, 4, 20, 0)
    schedule = get_schedule(watchlist, now=now)

    assert schedule["run"] is True
    assert schedule["mode"] == "after_hours"
    assert schedule["interval"] == 1800
    assert schedule["stocks"] == watchlist


def test_timezone_aware_now_is_converted_to_shanghai_time():
    watchlist = [{"code": "002131", "market": "sz"}]
    # 2026-03-04 02:00 UTC = 2026-03-04 10:00 Asia/Shanghai
    now = datetime(2026, 3, 4, 2, 0, tzinfo=ZoneInfo("UTC"))
    schedule = get_schedule(watchlist, now=now)

    assert schedule["run"] is True
    assert schedule["mode"] == "market"
    assert schedule["interval"] == 300
