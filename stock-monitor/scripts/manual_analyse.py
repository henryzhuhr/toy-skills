#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""手动调用分析引擎（单只/批量）。"""

from __future__ import annotations

import argparse
from pathlib import Path

from analyser import StockAnalyser
from monitor import StockAlert
from stock_monitor.enums import STOCK_TYPE, StockMarket
from stock_monitor.manual_service import (
    analyse_stock_text,
    load_batch_configs,
    normalize_stock_input,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="手动调用 stock-monitor 分析引擎（单只/批量）"
    )
    parser.add_argument("--code", help="股票代码，例如 002131")
    parser.add_argument("--name", help="股票名称（可选）")
    parser.add_argument(
        "--market",
        choices=[market.value for market in StockMarket],
        help="市场（可选，默认自动）",
    )
    parser.add_argument(
        "--type",
        dest="stock_type",
        choices=[e.value for e in STOCK_TYPE],
        help=f"标的类型（可选，默认 {STOCK_TYPE.INDIVIDUAL.value}）",
    )
    parser.add_argument("--cost", type=float, default=None, help="持仓成本（可选）")
    parser.add_argument(
        "--batch-file",
        type=Path,
        help="批量分析 JSON 文件路径，数组元素示例见文档",
    )
    parser.add_argument(
        "--alert",
        action="append",
        default=[],
        help="手动补充预警文案，可重复传入",
    )
    parser.add_argument(
        "--no-rules",
        action="store_true",
        help="不跑规则引擎，只输出基础分析+手动标记",
    )

    args = parser.parse_args()
    if not args.batch_file and not args.code:
        parser.error("--code 和 --batch-file 至少提供一个")
    return args


def main() -> int:
    args = parse_args()

    monitor = StockAlert()
    analyser = StockAnalyser()

    if args.batch_file:
        stocks = load_batch_configs(args.batch_file)
    else:
        raw = {
            "code": args.code,
            "name": args.name,
            "market": args.market,
            "type": args.stock_type,
            "cost": args.cost,
        }
        stocks = [normalize_stock_input(raw)]

    for stock in stocks:
        output = analyse_stock_text(
            monitor=monitor,
            analyser=analyser,
            stock=stock,
            manual_alerts=args.alert,
            run_rules=not args.no_rules,
        )
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
