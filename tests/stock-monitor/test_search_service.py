import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from stock_monitor.search_service import (  # noqa: E402
    parse_tencent_search_payload,
    search_stock_by_keyword,
)


def test_parse_tencent_search_payload_extracts_valid_items_only():
    payload = {
        "code": 0,
        "data": {
            "stock": [
                ["sh", "601899", "紫金矿业", "ZJKY"],
                ["sz", "300750", "宁德时代", "NDSD"],
                ["xx", "123456", "未知市场", "UNK"],
                "bad-item",
            ]
        },
    }

    results = parse_tencent_search_payload(payload)

    assert len(results) == 2
    assert results[0].market == "sh"
    assert results[0].code == "601899"
    assert results[0].name == "紫金矿业"


def test_search_stock_by_keyword_supports_market_filter(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": 0,
                "data": {
                    "stock": [
                        ["sh", "601899", "紫金矿业", "ZJKY"],
                        ["sz", "300750", "宁德时代", "NDSD"],
                    ]
                },
            }

    def fake_get(url, params, timeout):
        _ = (url, params, timeout)
        return DummyResponse()

    import stock_monitor.search_service as search_service

    monkeypatch.setattr(search_service.requests, "get", fake_get)

    results = search_stock_by_keyword("紫金", limit=10, market="sh")

    assert len(results) == 1
    assert results[0].market == "sh"
    assert results[0].code == "601899"
