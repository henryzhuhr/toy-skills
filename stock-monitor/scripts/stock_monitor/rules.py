"""预警规则定义与执行。"""

from __future__ import annotations

from .config import STOCK_TYPE


def calculate_alert_level(
    alerts: list[tuple[str, str]], weights: list[int]
) -> str | None:
    """计算预警级别。"""
    if not alerts:
        return None

    total_weight = sum(weights)
    alert_count = len(alerts)

    if total_weight >= 5 or alert_count >= 3:
        return "critical"
    if total_weight >= 3 or alert_count >= 2:
        return "warning"
    return "info"


def evaluate_alerts(
    stock_config: dict, data: dict, provider, state_store
) -> tuple[list, str | None]:
    """执行单个标的预警规则。"""
    alerts: list[tuple[str, str]] = []
    weights: list[int] = []

    code = stock_config["code"]
    cfg = stock_config.get("alerts", {})
    cost = stock_config.get("cost", 0)

    raw_stock_type = stock_config.get("type", STOCK_TYPE.INDIVIDUAL)
    try:
        stock_type = STOCK_TYPE(raw_stock_type)
    except ValueError:
        stock_type = raw_stock_type

    price = data["price"]
    prev_close = data["prev_close"]
    change_pct = (price - prev_close) / prev_close * 100 if prev_close else 0

    if cost > 0:
        cost_change_pct = (price - cost) / cost * 100

        if "cost_pct_above" in cfg and cost_change_pct >= cfg["cost_pct_above"]:
            target_price = cost * (1 + cfg["cost_pct_above"] / 100)
            if not state_store.alerted_recently(code, "cost_above"):
                alerts.append(
                    (
                        "cost_above",
                        f"🎯 盈利 {cfg['cost_pct_above']:.0f}% (目标价 ¥{target_price:.2f})",
                    )
                )
                weights.append(3)

        if "cost_pct_below" in cfg and cost_change_pct <= cfg["cost_pct_below"]:
            target_price = cost * (1 + cfg["cost_pct_below"] / 100)
            if not state_store.alerted_recently(code, "cost_below"):
                alerts.append(
                    (
                        "cost_below",
                        f"🛑 亏损 {abs(cfg['cost_pct_below']):.0f}% (止损价 ¥{target_price:.2f})",
                    )
                )
                weights.append(3)

    if (
        "price_above" in cfg
        and price >= cfg["price_above"]
        and not state_store.alerted_recently(code, "above")
    ):
        alerts.append(("above", f"🚀 价格突破 ¥{cfg['price_above']}"))
        weights.append(2)

    if (
        "price_below" in cfg
        and price <= cfg["price_below"]
        and not state_store.alerted_recently(code, "below")
    ):
        alerts.append(("below", f"📉 价格跌破 ¥{cfg['price_below']}"))
        weights.append(2)

    if (
        "change_pct_above" in cfg
        and change_pct >= cfg["change_pct_above"]
        and not state_store.alerted_recently(code, "pct_up")
    ):
        alerts.append(("pct_up", f"📈 日内大涨 {change_pct:+.2f}%"))
        if change_pct >= 7:
            weights.append(3)
        elif change_pct >= 5:
            weights.append(2)
        else:
            weights.append(1)

    if (
        "change_pct_below" in cfg
        and change_pct <= cfg["change_pct_below"]
        and not state_store.alerted_recently(code, "pct_down")
    ):
        alerts.append(("pct_down", f"📉 日内大跌 {change_pct:+.2f}%"))
        if change_pct <= -7:
            weights.append(3)
        elif change_pct <= -5:
            weights.append(2)
        else:
            weights.append(1)

    if stock_type != STOCK_TYPE.GOLD and "volume_surge" in cfg:
        current_volume = data.get("volume", 0)
        if current_volume > 0:
            ma5_volume = provider.fetch_volume_ma5(
                code, 1 if stock_config["market"] == "sh" else 0
            )
            if ma5_volume > 0:
                volume_ratio = current_volume / ma5_volume
                threshold = cfg["volume_surge"]

                if volume_ratio >= threshold and not state_store.alerted_recently(
                    code, "volume_surge"
                ):
                    alerts.append(
                        ("volume_surge", f"📊 放量 {volume_ratio:.1f}倍 (5日均量)")
                    )
                    weights.append(2)
                elif volume_ratio <= 0.5 and not state_store.alerted_recently(
                    code, "volume_shrink"
                ):
                    alerts.append(
                        ("volume_shrink", f"📉 缩量 {volume_ratio:.1f}倍 (5日均量)")
                    )
                    weights.append(1)

    if stock_type != STOCK_TYPE.GOLD and cfg.get("ma_monitor", True):
        ma_data = provider.fetch_ma_data(
            code, 1 if stock_config["market"] == "sh" else 0
        )
        if ma_data:
            if ma_data.get("golden_cross") and not state_store.alerted_recently(
                code, "ma_golden"
            ):
                alerts.append(
                    (
                        "ma_golden",
                        f"🌟 均线金叉 (MA5¥{ma_data['MA5']:.2f}上穿MA10¥{ma_data['MA10']:.2f})",
                    )
                )
                weights.append(3)

            if ma_data.get("death_cross") and not state_store.alerted_recently(
                code, "ma_death"
            ):
                alerts.append(
                    (
                        "ma_death",
                        f"⚠️ 均线死叉 (MA5¥{ma_data['MA5']:.2f}下穿MA10¥{ma_data['MA10']:.2f})",
                    )
                )
                weights.append(3)

            rsi = ma_data.get("RSI")
            if rsi:
                if ma_data.get("RSI_overbought") and not state_store.alerted_recently(
                    code, "rsi_high"
                ):
                    alerts.append(("rsi_high", f"🔥 RSI超买 ({rsi})，可能回调"))
                    weights.append(2)
                elif ma_data.get("RSI_oversold") and not state_store.alerted_recently(
                    code, "rsi_low"
                ):
                    alerts.append(("rsi_low", f"❄️ RSI超卖 ({rsi})，可能反弹"))
                    weights.append(2)

    if stock_type != STOCK_TYPE.GOLD:
        prev_high = data.get("prev_high", 0)
        prev_low = data.get("prev_low", 0)
        current_open = data.get("open", price)

        if prev_high > 0 and current_open > prev_high * 1.01:
            gap_pct = (current_open - prev_high) / prev_high * 100
            if not state_store.alerted_recently(code, "gap_up"):
                alerts.append(("gap_up", f"⬆️ 向上跳空 {gap_pct:.1f}%"))
                weights.append(2)
        elif prev_low > 0 and current_open < prev_low * 0.99:
            gap_pct = (prev_low - current_open) / prev_low * 100
            if not state_store.alerted_recently(code, "gap_down"):
                alerts.append(("gap_down", f"⬇️ 向下跳空 {gap_pct:.1f}%"))
                weights.append(2)

    if cost > 0:
        profit_pct = (price - cost) / cost * 100
        if profit_pct >= 10:
            high_since_cost = data.get("high", price)
            drawdown = (
                (high_since_cost - price) / high_since_cost * 100
                if high_since_cost > cost
                else 0
            )

            if drawdown >= 5 and not state_store.alerted_recently(
                code, "trailing_stop_5"
            ):
                alerts.append(
                    (
                        "trailing_stop_5",
                        f"📉 利润回撤 {drawdown:.1f}%，建议减仓保护利润",
                    )
                )
                weights.append(2)
            elif drawdown >= 10 and not state_store.alerted_recently(
                code, "trailing_stop_10"
            ):
                alerts.append(
                    ("trailing_stop_10", f"🚨 利润回撤 {drawdown:.1f}%，建议清仓止损")
                )
                weights.append(3)

    level = calculate_alert_level(alerts, weights)
    return alerts, level
