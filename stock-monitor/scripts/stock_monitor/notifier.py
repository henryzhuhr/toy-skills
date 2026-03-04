"""预警消息组装。"""

from __future__ import annotations


def format_alert_message(
    stock: dict,
    data: dict,
    alerts: list[tuple[str, str]],
    level: str | None,
) -> str:
    """构建单条预警消息。"""
    change_pct = (
        (data["price"] - data["prev_close"]) / data["prev_close"] * 100
        if data.get("prev_close")
        else 0
    )

    if change_pct > 0:
        color_emoji = "🔴"
    elif change_pct < 0:
        color_emoji = "🟢"
    else:
        color_emoji = "⚪"

    level_icons = {"critical": "🚨", "warning": "⚠️", "info": "📢"}
    level_texts = {"critical": "【紧急】", "warning": "【警告】", "info": "【提醒】"}

    level_icon = level_icons.get(level, "📢")
    level_text = level_texts.get(level, "")

    message = f"<b>{level_icon} {level_text}{color_emoji} {stock['name']} ({stock['code']})</b>\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n"
    message += f"💰 当前价格: <b>{data['price']:.2f}</b> ({change_pct:+.2f}%)\n"

    cost = stock.get("cost", 0)
    if cost > 0:
        cost_change = (data["price"] - cost) / cost * 100
        profit_icon = "🔴+" if cost_change > 0 else "🟢"
        message += f"📊 持仓成本: ¥{cost:.2f} | 盈亏: {profit_icon}{cost_change:.2f}%\n"

    message += f"\n🎯 触发预警 ({len(alerts)}项):\n"
    for _, text in alerts:
        message += f"  • {text}\n"

    try:
        from analyser import StockAnalyser

        analyser = StockAnalyser()
        insight = analyser.generate_insight(
            stock,
            {"price": data["price"], "change_pct": change_pct},
            alerts,
        )
        message += f"\n{insight}"
    except Exception:  # noqa: BLE001
        pass

    return message
