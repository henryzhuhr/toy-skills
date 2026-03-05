import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import monitor_daemon as daemon_module  # noqa: E402


def _build_daemon(monkeypatch, schedule):
    class FakeStockAlert:
        def should_run_now(self):
            return schedule

    monkeypatch.setattr(daemon_module, "StockAlert", FakeStockAlert)
    monkeypatch.setattr(daemon_module.signal, "signal", lambda *args, **kwargs: None)
    return daemon_module.MonitorDaemon()


def test_get_sleep_interval_uses_schedule_interval_when_run_true(monkeypatch):
    daemon = _build_daemon(monkeypatch, {"run": True, "interval": 900})

    assert daemon.get_sleep_interval() == 900


def test_get_sleep_interval_defaults_to_300_when_interval_missing(monkeypatch):
    daemon = _build_daemon(monkeypatch, {"run": True})

    assert daemon.get_sleep_interval() == 300


def test_get_sleep_interval_returns_3600_for_night_when_run_false(monkeypatch):
    class NightDatetime:
        @classmethod
        def now(cls):
            return datetime(2026, 3, 4, 2, 0)

    monkeypatch.setattr(daemon_module, "datetime", NightDatetime)
    daemon = _build_daemon(monkeypatch, {"run": False})

    assert daemon.get_sleep_interval() == 3600


def test_get_sleep_interval_returns_300_for_daytime_when_run_false(monkeypatch):
    class DayDatetime:
        @classmethod
        def now(cls):
            return datetime(2026, 3, 4, 14, 0)

    monkeypatch.setattr(daemon_module, "datetime", DayDatetime)
    daemon = _build_daemon(monkeypatch, {"run": False})

    assert daemon.get_sleep_interval() == 300


def test_run_passes_schedule_stocks_to_run_once(monkeypatch):
    schedule_stocks = [{"code": "XAU", "market": "fx"}]
    captured: dict = {}

    class FakeStockAlert:
        def should_run_now(self):
            return {
                "run": True,
                "mode": "night",
                "stocks": schedule_stocks,
                "interval": 1,
            }

        def run_once(self, smart_mode=True, stocks_override=None):
            captured["smart_mode"] = smart_mode
            captured["stocks_override"] = stocks_override
            daemon.running = False
            return []

    monkeypatch.setattr(daemon_module, "StockAlert", FakeStockAlert)
    monkeypatch.setattr(daemon_module.signal, "signal", lambda *args, **kwargs: None)
    daemon = daemon_module.MonitorDaemon()
    daemon.run()

    assert captured["smart_mode"] is False
    assert captured["stocks_override"] == schedule_stocks


def test_run_uses_watchlist_when_schedule_stocks_missing(monkeypatch):
    fallback_watchlist = [{"code": "002131", "market": "sz"}]
    captured: dict = {}

    class FakeStockAlert:
        def should_run_now(self):
            return {"run": True, "mode": "market", "interval": 1}

        def run_once(self, smart_mode=True, stocks_override=None):
            captured["smart_mode"] = smart_mode
            captured["stocks_override"] = stocks_override
            daemon.running = False
            return []

    monkeypatch.setattr(daemon_module, "WATCHLIST", fallback_watchlist)
    monkeypatch.setattr(daemon_module, "StockAlert", FakeStockAlert)
    monkeypatch.setattr(daemon_module.signal, "signal", lambda *args, **kwargs: None)
    daemon = daemon_module.MonitorDaemon()
    daemon.run()

    assert captured["smart_mode"] is False
    assert captured["stocks_override"] == fallback_watchlist
