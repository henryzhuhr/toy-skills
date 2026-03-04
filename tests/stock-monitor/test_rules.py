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
