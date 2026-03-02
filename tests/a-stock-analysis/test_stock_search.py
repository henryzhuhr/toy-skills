import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def load_search_module() -> ModuleType:
    root = Path(__file__).resolve().parents[2]
    module_path = root / "a-stock-analysis" / "scripts" / "search.py"
    spec = importlib.util.spec_from_file_location("stock_search_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module spec from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload: str):
        self._raw = payload.encode("gbk")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(scope="module")
def search_module():
    return load_search_module()


@pytest.fixture
def searcher(search_module):
    return search_module.StockSearch()


def test_infer_market(searcher):
    assert searcher.infer_market("600000") == "sh"
    assert searcher.infer_market("000001") == "sz"
    assert searcher.infer_market("300750") == "sz"
    assert searcher.infer_market("830000") == "unknown"


def test_parse_sina_suggest_response_filters_invalid_and_duplicate(searcher):
    text = (
        'var suggestdata="11,600000,浦发银行,pfyh,浦发银行,;'
        "12,000001,平安银行,payh,平安银行,;"
        "11,600000,浦发银行,pfyh,浦发银行,;"
        "21,600519,贵州茅台,gzmt,贵州茅台,;"
        '11,abc123,无效,wx,wx,";'
    )
    result = searcher.parse_sina_suggest_response(text)

    assert len(result) == 2
    assert result[0]["code"] == "600000"
    assert result[0]["market"] == "sh"
    assert result[0]["symbol"] == "sh600000"
    assert result[1]["code"] == "000001"
    assert result[1]["market"] == "sz"
    assert result[1]["symbol"] == "sz000001"


def test_parse_sina_suggest_response_handles_empty_or_invalid(searcher):
    assert searcher.parse_sina_suggest_response("") == []
    assert searcher.parse_sina_suggest_response("no quotes") == []
    assert searcher.parse_sina_suggest_response('var x=""') == []


def test_fetch_search_sina_empty_keyword(search_module, searcher, monkeypatch):
    called = False

    def fake_urlopen(*args, **kwargs):
        nonlocal called
        called = True
        raise RuntimeError("should not be called")

    monkeypatch.setattr(search_module.urllib.request, "urlopen", fake_urlopen)
    result = searcher.fetch_search_sina("   ")
    assert result == []
    assert called is False


def test_fetch_search_sina_success_and_limit(search_module, searcher, monkeypatch):
    payload = (
        'var suggestdata="11,600000,浦发银行,pfyh,浦发银行,;'
        '12,000001,平安银行,payh,平安银行,";'
    )

    def fake_urlopen(*args, **kwargs):
        return FakeResponse(payload)

    monkeypatch.setattr(search_module.urllib.request, "urlopen", fake_urlopen)
    result = searcher.fetch_search_sina("银行", limit=1)
    assert len(result) == 1
    assert result[0]["code"] == "600000"


def test_fetch_search_sina_exception_returns_empty(
    search_module, searcher, monkeypatch
):
    def fake_urlopen(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr(search_module.urllib.request, "urlopen", fake_urlopen)
    result = searcher.fetch_search_sina("银行")
    assert result == []
