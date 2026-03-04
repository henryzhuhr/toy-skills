import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from stock_monitor.indicators import calculate_rsi  # noqa: E402


def test_calculate_rsi_returns_none_when_data_insufficient():
    assert calculate_rsi([1.0, 1.1, 1.2], period=14) is None


def test_calculate_rsi_returns_valid_range():
    closes = [
        10.0,
        10.2,
        10.1,
        10.4,
        10.6,
        10.5,
        10.7,
        10.9,
        10.8,
        11.0,
        11.1,
        11.0,
        11.3,
        11.5,
        11.4,
        11.6,
    ]
    rsi = calculate_rsi(closes, period=14)

    assert rsi is not None
    assert 0 <= rsi <= 100
