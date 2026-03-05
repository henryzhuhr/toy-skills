import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from stock_monitor.rules import evaluate_alerts  # noqa: E402


class FakeProvider:
    def fetch_volume_ma5(self, symbol, market):
        return 100.0

    def fetch_ma_data(self, symbol, market):
        return {
            "MA5": 8.92,
            "MA10": 8.94,
            "golden_cross": False,
            "death_cross": True,
            "RSI": 50.0,
            "RSI_overbought": False,
            "RSI_oversold": False,
        }


class FakeStateStore:
    def alerted_recently(self, code, alert_type):
        return False


class FakeProviderRsiSignal(FakeProvider):
    def fetch_ma_data(self, symbol, market):
        _ = (symbol, market)
        return {
            "MA5": 9.1,
            "MA10": 9.0,
            "golden_cross": False,
            "death_cross": True,
            "RSI": 72.5,
            "RSI_overbought": True,
            "RSI_oversold": False,
        }


def test_evaluate_alerts_returns_critical_when_three_signals_resonate():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {
            "change_pct_above": 4.0,
            "change_pct_below": -4.0,
            "volume_surge": 2.0,
            "ma_monitor": True,
        },
    }
    data = {
        "price": 8.32,
        "prev_close": 8.21,
        "open": 7.91,
        "prev_high": 8.37,
        "prev_low": 8.05,
        "volume": 5180,
    }

    alerts, level = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())

    assert len(alerts) >= 3
    assert level == "critical"


def test_trailing_stop_10_triggers_before_trailing_stop_5():
    stock = {
        "code": "XAU",
        "name": "伦敦金",
        "market": "fx",
        "type": "gold",
        "cost": 100.0,
        "alerts": {"trailing_stop": True},
    }
    data = {
        "price": 114.0,
        "prev_close": 100.0,
        "high": 130.0,
    }

    alerts, _ = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "trailing_stop_10" in alert_types
    assert "trailing_stop_5" not in alert_types


def test_trailing_stop_5_triggers_when_drawdown_between_5_and_10():
    stock = {
        "code": "XAU",
        "name": "伦敦金",
        "market": "fx",
        "type": "gold",
        "cost": 100.0,
        "alerts": {"trailing_stop": True},
    }
    data = {
        "price": 111.6,
        "prev_close": 100.0,
        "high": 120.0,
    }

    alerts, _ = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "trailing_stop_5" in alert_types
    assert "trailing_stop_10" not in alert_types


def test_rsi_monitor_true_still_triggers_when_ma_monitor_false():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {"ma_monitor": False, "rsi_monitor": True},
    }
    data = {"price": 8.21, "prev_close": 8.21}

    alerts, _ = evaluate_alerts(stock, data, FakeProviderRsiSignal(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "rsi_high" in alert_types
    assert "ma_death" not in alert_types


def test_rsi_monitor_false_disables_rsi_alerts():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {"ma_monitor": True, "rsi_monitor": False},
    }
    data = {"price": 8.21, "prev_close": 8.21}

    alerts, _ = evaluate_alerts(stock, data, FakeProviderRsiSignal(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "ma_death" in alert_types
    assert "rsi_high" not in alert_types


def test_gap_monitor_false_disables_gap_alerts():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {"gap_monitor": False, "ma_monitor": False, "rsi_monitor": False},
    }
    data = {
        "price": 10.0,
        "prev_close": 10.0,
        "open": 10.5,
        "prev_high": 10.0,
        "prev_low": 9.5,
    }

    alerts, _ = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "gap_up" not in alert_types
    assert "gap_down" not in alert_types


def test_gap_monitor_true_allows_gap_alerts():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {"gap_monitor": True, "ma_monitor": False, "rsi_monitor": False},
    }
    data = {
        "price": 10.0,
        "prev_close": 10.0,
        "open": 10.5,
        "prev_high": 10.0,
        "prev_low": 9.5,
    }

    alerts, _ = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "gap_up" in alert_types


def test_gap_monitor_true_skips_when_prev_day_range_missing():
    stock = {
        "code": "002131",
        "name": "利欧股份",
        "market": "sz",
        "type": "individual",
        "cost": 0.0,
        "alerts": {"gap_monitor": True, "ma_monitor": False, "rsi_monitor": False},
    }
    data = {
        "price": 10.0,
        "prev_close": 10.0,
        "open": 10.5,
    }

    alerts, _ = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "gap_up" not in alert_types
    assert "gap_down" not in alert_types


def test_trailing_stop_false_disables_trailing_stop_alerts():
    stock = {
        "code": "XAU",
        "name": "伦敦金",
        "market": "fx",
        "type": "gold",
        "cost": 100.0,
        "alerts": {"trailing_stop": False},
    }
    data = {
        "price": 114.0,
        "prev_close": 100.0,
        "high": 130.0,
    }

    alerts, _ = evaluate_alerts(stock, data, FakeProvider(), FakeStateStore())
    alert_types = {alert_type for alert_type, _ in alerts}

    assert "trailing_stop_5" not in alert_types
    assert "trailing_stop_10" not in alert_types
