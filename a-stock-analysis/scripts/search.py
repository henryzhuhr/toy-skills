#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
股票搜索工具

数据源：新浪财经（统一接口）
支持：沪市(sh)、深市(sz) 股票

Usage:
    uv run search.py --keyword "关键词"
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request


class StockSearch:
    """新浪建议搜索封装。"""

    SINA_SUGGEST_URL = "https://suggest3.sinajs.cn/suggest/type=11,12&key={keyword}"
    STOCK_CODE_PATTERN = re.compile(r"^\d{6}$")
    VALID_STOCK_TYPES = {"11", "12"}

    def infer_market(self, code: str) -> str:
        """根据代码推断市场。"""
        if code.startswith("6"):
            return "sh"
        if code.startswith(("0", "3")):
            return "sz"
        return "unknown"

    def parse_sina_suggest_response(self, text: str) -> list[dict]:
        """解析新浪 suggest 接口响应。"""
        match = re.search(r'"([^"]*)"', text)
        if not match:
            return []

        payload = match.group(1).strip()
        if not payload:
            return []

        results = []
        seen_codes = set()

        # 每条形如: 11,600000,浦发银行,pfyh,浦发银行,
        for raw_item in payload.split(";"):
            item = raw_item.strip()
            if not item:
                continue

            fields = [part.strip() for part in item.split(",")]
            if len(fields) < 3:
                continue

            stock_type = fields[0]
            code = fields[1]
            name = fields[2]
            pinyin = fields[3] if len(fields) > 3 else ""

            if stock_type not in self.VALID_STOCK_TYPES:
                continue
            if not self.STOCK_CODE_PATTERN.match(code):
                continue
            if not name or code in seen_codes:
                continue

            seen_codes.add(code)
            market = self.infer_market(code)
            results.append(
                {
                    "code": code,
                    "name": name,
                    "market": market,
                    "symbol": f"{market}{code}" if market != "unknown" else code,
                    "pinyin": pinyin,
                }
            )

        return results

    def fetch_search_sina(self, keyword: str, limit: int = 20) -> list[dict]:
        """通过新浪 suggest 接口按关键词搜索股票。"""
        clean_keyword = keyword.strip()
        if not clean_keyword:
            return []

        encoded = urllib.parse.quote(clean_keyword)
        url = self.SINA_SUGGEST_URL.format(keyword=encoded)

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Referer": "https://finance.sina.com.cn",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read()
                text = raw.decode("gbk", errors="ignore")
        except Exception as e:
            print(f"搜索接口错误: {e}", file=sys.stderr)
            return []

        results = self.parse_sina_suggest_response(text)
        return results[: max(limit, 0)]

    def search(self, keyword: str, limit: int = 20) -> list[dict]:
        """对外搜索入口。"""
        return self.fetch_search_sina(keyword, limit)


def infer_market(code: str) -> str:
    return StockSearch().infer_market(code)


def parse_sina_suggest_response(text: str) -> list[dict]:
    return StockSearch().parse_sina_suggest_response(text)


def fetch_search_sina(keyword: str, limit: int = 20) -> list[dict]:
    return StockSearch().fetch_search_sina(keyword, limit)


def print_results(results: list[dict]) -> None:
    """打印表格结果。"""
    if not results:
        print("未找到匹配股票")
        return

    print(f"找到 {len(results)} 只股票:")
    print("-" * 56)
    print(f"{'代码':<10}{'名称':<20}{'市场':<8}{'新浪代码':<12}")
    print("-" * 56)
    for item in results:
        print(
            f"{item['code']:<10}{item['name']:<20}{item['market']:<8}{item['symbol']:<12}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A股股票搜索工具（新浪财经）")
    parser.add_argument(
        "--keyword", required=True, help="搜索关键词（支持代码、名称、拼音简写）"
    )
    parser.add_argument("--limit", type=int, default=20, help="返回条数上限，默认20")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results = StockSearch().search(args.keyword, args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_results(results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
