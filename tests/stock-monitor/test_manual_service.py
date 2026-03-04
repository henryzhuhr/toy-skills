import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from stock_monitor.data_providers import (  # noqa: E402
    build_quote_symbol,
    build_quote_url,
)
from stock_monitor.manual_service import (  # noqa: E402
    analyse_stock_text,
    normalize_stock_input,
)


class FakeMonitor:
    def __init__(self):
        self.provider = object()

    def fetch_sina_realtime(self, stocks):
        _ = stocks
        return {
            "002131": {
                "price": 8.32,
                "prev_close": 8.21,
                "date": "2026-03-04",
                "time": "15:00:00",
            }
        }


class FakeAnalyser:
    def generate_insight(self, stock, price_data, alerts):
        _ = (price_data, alerts)
        return f"INSIGHT:{stock['code']}"


def test_normalize_stock_input_reuses_watchlist_item():
    watchlist = [
        {
            "code": "002131",
            "name": "利欧股份",
            "market": "sz",
            "type": "individual",
            "cost": 0.0,
            "alerts": {"change_pct_above": 4.0, "change_pct_below": -4.0},
        }
    ]

    normalized = normalize_stock_input(
        {"code": "002131", "name": "利欧股份-测试", "cost": 1.23},
        watchlist=watchlist,
    )

    assert normalized["code"] == "002131"
    assert normalized["name"] == "利欧股份-测试"
    assert normalized["market"] == "sz"
    assert normalized["cost"] == 1.23


def test_analyse_stock_text_returns_header_and_insight_without_rules():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {},
    }

    output = analyse_stock_text(
        monitor=FakeMonitor(),
        analyser=FakeAnalyser(),
        stock=stock,
        manual_alerts=["测试标记"],
        run_rules=False,
    )

    assert "利欧股份 (002131)" in output
    assert "价格: 8.32" in output
    assert "INSIGHT:002131" in output


def test_build_quote_helpers_match_expected_symbol_and_url():
    assert build_quote_symbol("sh", "601869") == "sh601869"
    assert build_quote_url("sh", "601869") == "https://hq.sinajs.cn/list=sh601869"
    assert build_quote_symbol("fx", "XAU") == "hf_XAU"
