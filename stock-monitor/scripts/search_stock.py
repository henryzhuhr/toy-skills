#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""按关键词搜索股票信息（可独立调用）。"""

from __future__ import annotations

import argparse
import json

from stock_monitor.enums import StockMarket
from stock_monitor.search_service import search_stock_by_keyword, to_dict_list


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="通过关键词模糊搜索股票信息")
    parser.add_argument("keyword", help="关键词，例如 紫金矿业 / 601869")
    parser.add_argument("--limit", type=int, default=10, help="最多返回条数，默认 10")
    parser.add_argument(
        "--market", choices=[m.value for m in StockMarket], help="按市场过滤"
    )
    parser.add_argument(
        "--json", action="store_true", help="以 JSON 输出（默认是表格文本）"
    )
    return parser.parse_args()


def print_table(results: list[dict[str, str]]) -> None:
    if not results:
        print("未找到匹配的股票")
        return

    print(f"共找到 {len(results)} 条：")
    print("market  code      name               abbreviation")
    print("------  --------  -----------------  ------------")
    for item in results:
        print(
            f"{item['market']:<6}  {item['code']:<8}  {item['name'][:17]:<17}"
            f"  {item['abbreviation'][:12]}"
        )


def main() -> int:
    args = parse_args()
    results = search_stock_by_keyword(
        args.keyword,
        limit=args.limit,
        market=args.market,
    )
    data = to_dict_list(results)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_table(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
