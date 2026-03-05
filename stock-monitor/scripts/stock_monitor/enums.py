"""股票监控相关枚举定义。"""

from __future__ import annotations

from enum import StrEnum


class STOCK_TYPE(StrEnum):
    """标的类型。"""

    INDIVIDUAL = "individual"
    ETF = "etf"
    GOLD = "gold"


class StockMarket(StrEnum):
    """市场类型。"""

    SH = "sh"
    """上海证券交易所"""

    SZ = "sz"
    """深圳证券交易所"""

    FX = "fx"
    """外汇市场"""
