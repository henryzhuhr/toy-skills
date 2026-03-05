"""Stock Monitor 核心编排。"""

from __future__ import annotations

from datetime import datetime

from .config import STOCK_TYPE, WATCHLIST
from .data_providers import MarketDataProvider
from .notifier import format_alert_message
from .rules import evaluate_alerts
from .scheduler import get_schedule
from .state_store import AlertStateStore


class StockAlert:
    """监控引擎主类。"""

    def __init__(self):
        self.prev_data: dict = {}
        self.provider = MarketDataProvider()
        self.state_store = AlertStateStore()

    @property
    def alert_log(self) -> list[dict]:
        """兼容旧属性访问。"""
        return self.state_store.alert_log

    def should_run_now(self) -> dict:
        """智能频率控制。"""
        return get_schedule(WATCHLIST)

    def fetch_eastmoney_kline(self, symbol: str, market: int) -> dict | None:
        return self.provider.fetch_eastmoney_kline(symbol, market)

    def fetch_volume_ma5(self, symbol: str, market: int) -> float:
        return self.provider.fetch_volume_ma5(symbol, market)

    def fetch_ma_data(self, symbol: str, market: int) -> dict | None:
        return self.provider.fetch_ma_data(symbol, market)

    def fetch_sina_realtime(self, stocks: list[dict]) -> dict[str, dict]:
        return self.provider.fetch_sina_realtime(stocks)

    def fetch_news(self, symbol: str) -> list[str]:
        return self.provider.fetch_news(symbol)

    def _alerted_recently(self, code: str, alert_type: str) -> bool:
        return self.state_store.alerted_recently(code, alert_type)

    def record_alert(self, code: str, alert_type: str) -> None:
        self.state_store.record_alert(code, alert_type)

    def check_alerts(self, stock_config: dict, data: dict) -> tuple[list, str | None]:
        return evaluate_alerts(stock_config, data, self.provider, self.state_store)

    def run_once(
        self,
        smart_mode: bool = True,
        stocks_override: list[dict] | None = None,
    ) -> list[str]:
        """执行一轮监控。"""
        if stocks_override is not None:
            stocks_to_check = stocks_override
        elif smart_mode:
            schedule = self.should_run_now()
            if not schedule.get("run"):
                return []

            stocks_to_check = schedule.get("stocks", WATCHLIST)
            mode = schedule.get("mode", "normal")
            if mode in ["market", "weekend"]:
                now_text = datetime.now().strftime("%H:%M")
                print(f"[{now_text}] {mode}模式扫描 {len(stocks_to_check)} 只标的...")
        else:
            stocks_to_check = WATCHLIST

        data_map = self.fetch_sina_realtime(stocks_to_check)
        triggered: list[str] = []

        for stock in stocks_to_check:
            code = stock["code"]
            if code not in data_map:
                continue

            data = data_map[code]
            if data["price"] <= 0 or data["prev_close"] <= 0:
                continue

            alerts, level = self.check_alerts(stock, data)
            if not alerts:
                continue

            for alert_type, _ in alerts:
                self.record_alert(code, alert_type)

            message = format_alert_message(stock, data, alerts, level)
            triggered.append(message)

        return triggered


__all__ = [
    "STOCK_TYPE",
    "WATCHLIST",
    "StockAlert",
]
