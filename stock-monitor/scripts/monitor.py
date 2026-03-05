#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""自选股监控预警工具入口。"""

from __future__ import annotations

from stock_monitor import StockAlert
from stock_monitor.config import (
    DEFAULT_WATCHLIST,
    PORTFOLIO_FILE,
    WATCHLIST,
    AlertConfig,
    PortfolioItemConfig,
    load_watchlist,
    normalize_watchlist,
    parse_watchlist,
    serialize_watchlist,
)
from stock_monitor.enums import STOCK_TYPE, StockMarket

__all__ = [
    "AlertConfig",
    "DEFAULT_WATCHLIST",
    "PORTFOLIO_FILE",
    "STOCK_TYPE",
    "StockMarket",
    "PortfolioItemConfig",
    "WATCHLIST",
    "StockAlert",
    "load_watchlist",
    "normalize_watchlist",
    "parse_watchlist",
    "serialize_watchlist",
]


if __name__ == "__main__":
    monitor = StockAlert()
    for alert in monitor.run_once():
        print(alert)
