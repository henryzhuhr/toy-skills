#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""展示 stock-monitor 的行情请求拼接方式。"""

from __future__ import annotations

import argparse

from stock_monitor.data_providers import build_quote_symbol, build_quote_url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="显示 market+code 的行情请求 URL")
    parser.add_argument("--market", required=True, choices=["sh", "sz", "fx"])
    parser.add_argument("--code", required=True, help="股票代码，例如 601869")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    symbol = build_quote_symbol(args.market, args.code)
    url = build_quote_url(args.market, args.code)
    print(f"market={args.market}")
    print(f"code={args.code}")
    print(f"symbol={symbol}")
    print(f"url={url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
