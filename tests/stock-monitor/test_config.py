import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def load_config_module(module_name: str, portfolio_file: Path) -> ModuleType:
    root = Path(__file__).resolve().parents[2]
    module_path = root / "stock-monitor" / "scripts" / "stock_monitor" / "config.py"

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module spec from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    setattr(module, "PORTFOLIO_FILE", portfolio_file)
    spec.loader.exec_module(module)
    return module


def test_create_default_portfolio_file_when_missing(tmp_path, monkeypatch):
    portfolio_file = (
        tmp_path / "openclaw" / "skills" / "stock-monitor" / "portfolio.json"
    )
    monkeypatch.setenv("STOCK_MONITOR_PORTFOLIO_FILE", str(portfolio_file))

    module = load_config_module("stock_monitor_config_test_create", portfolio_file)

    assert module.PORTFOLIO_FILE == portfolio_file
    assert portfolio_file.exists()
    assert isinstance(module.DEFAULT_WATCHLIST[0], module.PortfolioItemConfig)
    assert isinstance(module.DEFAULT_WATCHLIST[0].market, module.StockMarket)

    saved = json.loads(portfolio_file.read_text(encoding="utf-8"))
    serialized_defaults = module.serialize_watchlist(module.DEFAULT_WATCHLIST)
    assert saved == serialized_defaults
    assert module.WATCHLIST == serialized_defaults


def test_load_existing_portfolio_file(tmp_path, monkeypatch):
    portfolio_file = (
        tmp_path / "openclaw" / "skills" / "stock-monitor" / "portfolio.json"
    )
    portfolio_file.parent.mkdir(parents=True, exist_ok=True)

    custom_portfolio = [
        {
            "code": "000001",
            "name": "平安银行",
            "market": "SZ",
            "type": "individual",
            "cost": "10.0",
            "alerts": {
                "cost_pct_above": "8.0",
                "cost_pct_below": -8,
                "change_pct_above": 3,
                "change_pct_below": "-3.0",
            },
        }
    ]
    portfolio_file.write_text(
        json.dumps(custom_portfolio, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    monkeypatch.setenv("STOCK_MONITOR_PORTFOLIO_FILE", str(portfolio_file))

    module = load_config_module("stock_monitor_config_test_load", portfolio_file)

    assert module.PORTFOLIO_FILE == portfolio_file
    assert module.WATCHLIST[0]["code"] == "000001"
    assert module.WATCHLIST[0]["market"] == "sz"
    assert module.WATCHLIST[0]["cost"] == 10.0
    assert module.WATCHLIST[0]["alerts"]["cost_pct_above"] == 8.0
    assert module.WATCHLIST[0]["alerts"]["change_pct_below"] == -3.0

    saved = json.loads(portfolio_file.read_text(encoding="utf-8"))
    assert saved == module.WATCHLIST


def test_parse_watchlist_raises_for_invalid_market(tmp_path, monkeypatch):
    portfolio_file = (
        tmp_path / "openclaw" / "skills" / "stock-monitor" / "portfolio.json"
    )
    monkeypatch.setenv("STOCK_MONITOR_PORTFOLIO_FILE", str(portfolio_file))

    module = load_config_module(
        "stock_monitor_config_test_invalid_market", portfolio_file
    )

    with pytest.raises(ValueError, match="market 必须是以下之一"):
        module.parse_watchlist(
            [
                {
                    "code": "000001",
                    "name": "平安银行",
                    "market": "xx",
                    "type": "individual",
                    "cost": 10.0,
                    "alerts": {},
                }
            ]
        )
