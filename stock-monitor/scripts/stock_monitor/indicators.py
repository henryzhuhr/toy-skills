"""技术指标计算。"""

from __future__ import annotations


def calculate_rsi(closes: list[float], period: int = 14) -> float | None:
    """根据收盘价序列计算 RSI。"""
    if len(closes) < period + 1:
        return None

    gains: list[float] = []
    losses: list[float] = []

    for idx in range(1, period + 1):
        change = closes[-idx] - closes[-idx - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)
