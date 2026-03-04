"""关键词搜索股票信息服务。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import requests

SEARCH_URL = "https://proxy.finance.qq.com/ifzqgtimg/appstock/smartbox/search/get"


@dataclass(frozen=True)
class StockSearchResult:
    market: str
    code: str
    name: str
    abbreviation: str = ""


def _normalize_market(raw_market: str) -> str | None:
    market = raw_market.strip().lower()
    market_map = {
        "sh": "sh",
        "sz": "sz",
        "hk": "hk",
        "us": "us",
    }
    return market_map.get(market)


def parse_tencent_search_payload(payload: dict[str, Any]) -> list[StockSearchResult]:
    """把腾讯搜索接口返回转换为统一结构。"""
    if payload.get("code") != 0:
        return []

    raw_stocks = payload.get("data", {}).get("stock", [])
    if not isinstance(raw_stocks, list):
        return []

    results: list[StockSearchResult] = []
    for item in raw_stocks:
        if not isinstance(item, list) or len(item) < 4:
            continue

        market = _normalize_market(str(item[0]))
        if market is None:
            continue

        result = StockSearchResult(
            market=market,
            code=str(item[1]).strip().lower(),
            name=str(item[2]).strip(),
            abbreviation=str(item[3]).strip(),
        )
        results.append(result)

    return results


def search_stock_by_keyword(
    keyword: str,
    *,
    limit: int = 10,
    market: str | None = None,
    timeout: int = 10,
) -> list[StockSearchResult]:
    """根据关键词搜索股票信息。"""
    if not keyword or not keyword.strip():
        return []

    resp = requests.get(SEARCH_URL, params={"q": keyword.strip()}, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()

    results = parse_tencent_search_payload(payload)

    if market:
        normalized_market = _normalize_market(market)
        if normalized_market:
            results = [item for item in results if item.market == normalized_market]

    if limit > 0:
        results = results[:limit]

    return results


def to_dict_list(results: list[StockSearchResult]) -> list[dict[str, Any]]:
    return [asdict(item) for item in results]
