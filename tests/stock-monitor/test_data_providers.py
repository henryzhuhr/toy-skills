import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "stock-monitor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from stock_monitor.data_providers import parse_prev_day_range_from_klines  # noqa: E402


def test_parse_prev_day_range_from_klines_returns_prev_high_low():
    klines = [
        "2026-03-03,9.70,10.00,10.20,9.60,10000,100000",
        "2026-03-04,10.10,10.50,10.80,9.90,11000,120000",
    ]

    prev_day_range = parse_prev_day_range_from_klines(klines)

    assert prev_day_range == (10.2, 9.6)


def test_parse_prev_day_range_from_klines_returns_none_when_insufficient_data():
    klines = ["2026-03-04,10.10,10.50,10.80,9.90,11000,120000"]

    prev_day_range = parse_prev_day_range_from_klines(klines)

    assert prev_day_range is None


def test_parse_prev_day_range_from_klines_returns_none_when_invalid_row():
    klines = [
        "2026-03-03,9.70,10.00,abc,9.60,10000,100000",
        "2026-03-04,10.10,10.50,10.80,9.90,11000,120000",
    ]

    prev_day_range = parse_prev_day_range_from_klines(klines)

    assert prev_day_range is None
