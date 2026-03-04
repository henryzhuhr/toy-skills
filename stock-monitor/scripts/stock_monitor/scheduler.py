"""交易时段与频率策略。"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def get_schedule(
    watchlist: list[dict],
    now: datetime | None = None,
    timezone_name: str = "Asia/Shanghai",
) -> dict:
    """根据北京时间返回是否运行、运行模式、标的和间隔。"""
    current = now or datetime.now(ZoneInfo(timezone_name))
    if current.tzinfo is None:
        current = current.replace(tzinfo=ZoneInfo(timezone_name))
    else:
        current = current.astimezone(ZoneInfo(timezone_name))

    hour = current.hour
    minute = current.minute
    time_val = hour * 100 + minute
    weekday = current.weekday()

    if weekday >= 5:
        return {
            "run": True,
            "mode": "weekend",
            "stocks": [item for item in watchlist if item.get("market") == "fx"],
            "interval": 3600,
        }

    morning_session = 930 <= time_val <= 1130
    afternoon_session = 1300 <= time_val <= 1500

    if morning_session or afternoon_session:
        return {"run": True, "mode": "market", "stocks": watchlist, "interval": 300}

    if 1130 < time_val < 1300:
        return {"run": True, "mode": "lunch", "stocks": watchlist, "interval": 600}

    if 1500 <= time_val <= 2359:
        return {
            "run": True,
            "mode": "after_hours",
            "stocks": watchlist,
            "interval": 1800,
        }

    if 0 <= time_val < 930:
        return {
            "run": True,
            "mode": "night",
            "stocks": [item for item in watchlist if item.get("market") == "fx"],
            "interval": 3600,
        }

    return {"run": False}
