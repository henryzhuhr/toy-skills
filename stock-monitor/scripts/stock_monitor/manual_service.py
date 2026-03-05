"""手动分析服务：供 demo 与人工调试调用。"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .config import WATCHLIST
from .enums import STOCK_TYPE, StockMarket
from .rules import evaluate_alerts


class NoDedupState:
    """手动分析场景不做告警去重，避免历史状态影响结果。"""

    def alerted_recently(self, code: str, alert_type: str) -> bool:
        _ = (code, alert_type)
        return False


def _normalize_market(raw_market: object) -> StockMarket:
    if isinstance(raw_market, StockMarket):
        return raw_market
    try:
        return StockMarket(str(raw_market).strip().lower())
    except ValueError:
        return StockMarket.SZ


def build_default_alerts(stock_type: str) -> dict[str, Any]:
    """按标的类型返回默认预警阈值。"""
    if stock_type == STOCK_TYPE.ETF.value:
        return {
            "change_pct_above": 2.0,
            "change_pct_below": -2.0,
            "volume_surge": 1.8,
            "ma_monitor": True,
            "rsi_monitor": True,
            "gap_monitor": True,
            "trailing_stop": True,
        }
    if stock_type == STOCK_TYPE.GOLD.value:
        return {
            "change_pct_above": 2.5,
            "change_pct_below": -2.5,
        }
    return {
        "change_pct_above": 4.0,
        "change_pct_below": -4.0,
        "volume_surge": 2.0,
        "ma_monitor": True,
        "rsi_monitor": True,
        "gap_monitor": True,
        "trailing_stop": True,
    }


def find_in_watchlist(
    code: str,
    watchlist: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """在监控列表中按 code 查找。"""
    source = WATCHLIST if watchlist is None else watchlist
    for item in source:
        if item.get("code") == code:
            return copy.deepcopy(item)
    return None


def normalize_stock_input(
    raw: dict[str, Any],
    watchlist: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """把用户输入规范化为分析配置。"""
    code = str(raw.get("code", "")).strip()
    if not code:
        raise ValueError("缺少 code")

    existing = find_in_watchlist(code, watchlist=watchlist)
    if existing:
        existing["market"] = _normalize_market(existing.get("market", StockMarket.SZ))
        if raw.get("name"):
            existing["name"] = raw["name"]
        if raw.get("market"):
            existing["market"] = _normalize_market(raw["market"])
        if raw.get("type"):
            existing["type"] = raw["type"]
        if raw.get("cost") is not None:
            existing["cost"] = float(raw["cost"])
        return existing

    stock_type = str(raw.get("type") or STOCK_TYPE.INDIVIDUAL.value)
    market = _normalize_market(raw.get("market") or StockMarket.SZ)

    return {
        "code": code,
        "name": str(raw.get("name") or f"股票{code}"),
        "market": market,
        "type": stock_type,
        "cost": float(raw.get("cost") or 0.0),
        "alerts": build_default_alerts(stock_type),
    }


def load_batch_configs(
    path: Path,
    watchlist: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """从 JSON 文件加载批量分析配置。"""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError("批量文件必须是 JSON 数组")

    return [normalize_stock_input(item, watchlist=watchlist) for item in payload]


def analyse_stock_text(
    monitor,
    analyser,
    stock: dict[str, Any],
    manual_alerts: list[str] | None = None,
    run_rules: bool = True,
) -> str:
    """执行单只股票分析，返回可读文本。"""
    manual_alerts = manual_alerts or []

    data_map = monitor.fetch_sina_realtime([stock])
    data = data_map.get(stock["code"])
    if not data:
        return f"❌ {stock['name']} ({stock['code']}) 无法获取行情数据"

    price = float(data["price"])
    prev_close = float(data.get("prev_close") or 0)
    change_pct = (price - prev_close) / prev_close * 100 if prev_close else 0

    alerts: list[tuple[str, str]] = []
    if run_rules:
        auto_alerts, _ = evaluate_alerts(
            stock_config=stock,
            data=data,
            provider=monitor.provider,
            state_store=NoDedupState(),
        )
        alerts.extend(auto_alerts)

    for text in manual_alerts:
        alerts.append(("manual", f"🧪 手动标记: {text}"))

    if not alerts:
        alerts = [("manual", "ℹ️ 当前未触发规则，输出基础分析")]

    header = (
        f"\n=== {stock['name']} ({stock['code']}) ===\n"
        f"价格: {price:.2f}  涨跌幅: {change_pct:+.2f}%"
        f"  时间: {data.get('date', '')} {data.get('time', '')}\n"
    )

    insight = analyser.generate_insight(
        stock=stock,
        price_data={"price": price, "change_pct": change_pct},
        alerts=alerts,
    )

    return header + insight
