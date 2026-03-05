"""新浪/东财数据适配。"""

from __future__ import annotations

from datetime import datetime

import requests

from .enums import StockMarket
from .indicators import calculate_rsi


def _to_stock_market(
    raw_market: object,
    *,
    default: StockMarket = StockMarket.SZ,
) -> StockMarket:
    if isinstance(raw_market, StockMarket):
        return raw_market
    try:
        return StockMarket(str(raw_market).strip().lower())
    except ValueError:
        return default


def _to_eastmoney_market_id(raw_market: object) -> int:
    return 1 if _to_stock_market(raw_market) == StockMarket.SH else 0


def build_quote_symbol(market: StockMarket | str, code: str) -> str:
    """构造新浪行情 symbol。"""
    normalized_market = _to_stock_market(market)
    if normalized_market == StockMarket.FX:
        return "hf_XAU"
    return f"{normalized_market.value}{code}"


def build_quote_url_by_symbols(symbols: list[str]) -> str:
    """按 symbol 列表构造新浪行情 URL。"""
    return f"https://hq.sinajs.cn/list={','.join(symbols)}"


def build_quote_url(market: StockMarket | str, code: str) -> str:
    """按 market+code 构造新浪行情 URL。"""
    return build_quote_url_by_symbols([build_quote_symbol(market, code)])


def parse_prev_day_range_from_klines(klines: list[str]) -> tuple[float, float] | None:
    """从东财 K 线数据中解析上一交易日最高/最低价。"""
    if len(klines) < 2:
        return None

    prev_parts = klines[-2].split(",")
    if len(prev_parts) < 5:
        return None

    try:
        prev_high = float(prev_parts[3])
        prev_low = float(prev_parts[4])
    except (TypeError, ValueError):
        return None

    if prev_high <= 0 or prev_low <= 0:
        return None
    return prev_high, prev_low


class MarketDataProvider:
    """行情与技术指标数据提供器。"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self._volume_cache: dict[tuple[str, int], float] = {}
        self._ma_cache: dict[tuple[str, int], dict] = {}
        self._prev_day_range_cache: dict[
            tuple[str, int], tuple[float, float] | None
        ] = {}
        self._prev_day_range_warned: set[tuple[str, int]] = set()

    def fetch_eastmoney_kline(self, symbol: str, market: int) -> dict | None:
        """获取最新日 K 数据。"""
        secid = f"{market}.{symbol}"
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "0",
            "end": "20500101",
            "lmt": "2",
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            klines = data.get("data", {}).get("klines", [])
            if len(klines) >= 1:
                today = klines[-1].split(",")
                prev_close = float(today[2])
                if len(klines) >= 2:
                    prev_close = float(klines[-2].split(",")[2])
                payload = {
                    "name": data.get("data", {}).get("name", symbol),
                    "price": float(today[2]),
                    "prev_close": prev_close,
                    "volume": int(float(today[5])),
                    "amount": float(today[6]),
                    "date": today[0],
                    "time": "15:00:00",
                }
                prev_day_range = parse_prev_day_range_from_klines(klines)
                if prev_day_range is not None:
                    payload["prev_high"] = prev_day_range[0]
                    payload["prev_low"] = prev_day_range[1]
                return payload
        except Exception as exc:  # noqa: BLE001
            print(f"东财K线获取失败 {symbol}: {exc}")
        return None

    def fetch_prev_day_range(
        self, symbol: str, market: int
    ) -> tuple[float, float] | None:
        """获取上一交易日最高/最低价，用于跳空缺口判断。"""
        cache_key = (symbol, market)
        if cache_key in self._prev_day_range_cache:
            return self._prev_day_range_cache[cache_key]

        secid = f"{market}.{symbol}"
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "0",
            "end": "20500101",
            "lmt": "2",
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            klines = data.get("data", {}).get("klines", [])
            prev_day_range = parse_prev_day_range_from_klines(klines)
            self._prev_day_range_cache[cache_key] = prev_day_range
            return prev_day_range
        except Exception as exc:  # noqa: BLE001
            print(f"获取昨高昨低失败 {symbol}: {exc}")
            self._prev_day_range_cache[cache_key] = None
            return None

    def _warn_missing_prev_day_range(self, symbol: str, market: int, name: str) -> None:
        cache_key = (symbol, market)
        if cache_key in self._prev_day_range_warned:
            return
        self._prev_day_range_warned.add(cache_key)
        print(f"  {name}: 缺少真实昨高昨低，已跳过跳空缺口规则")

    def fetch_volume_ma5(self, symbol: str, market: int) -> float:
        """获取 5 日平均成交量。"""
        cache_key = (symbol, market)
        if cache_key in self._volume_cache:
            return self._volume_cache[cache_key]

        secid = f"{market}.{symbol}"
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "0",
            "end": "20500101",
            "lmt": "6",
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            klines = data.get("data", {}).get("klines", [])
            if len(klines) >= 2:
                volumes: list[float] = []
                for row in klines[:-1]:
                    parts = row.split(",")
                    volumes.append(float(parts[5]))
                ma5 = sum(volumes) / len(volumes) if volumes else 0.0
                self._volume_cache[cache_key] = ma5
                return ma5
        except Exception as exc:  # noqa: BLE001
            print(f"获取均量失败 {symbol}: {exc}")

        self._volume_cache[cache_key] = 0.0
        return 0.0

    def fetch_ma_data(self, symbol: str, market: int) -> dict | None:
        """获取 MA5/MA10/MA20 与 RSI。"""
        cache_key = (symbol, market)
        if cache_key in self._ma_cache:
            return self._ma_cache[cache_key]

        secid = f"{market}.{symbol}"
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "0",
            "end": "20500101",
            "lmt": "30",
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            klines = data.get("data", {}).get("klines", [])
            if len(klines) >= 20:
                closes = [float(item.split(",")[2]) for item in klines]
                ma5 = sum(closes[-5:]) / 5
                ma10 = sum(closes[-10:]) / 10
                ma20 = sum(closes[-20:]) / 20

                prev_ma5 = sum(closes[-6:-1]) / 5
                prev_ma10 = sum(closes[-11:-1]) / 10

                rsi = calculate_rsi(closes, 14)
                result = {
                    "MA5": ma5,
                    "MA10": ma10,
                    "MA20": ma20,
                    "MA5_trend": "up" if ma5 > prev_ma5 else "down",
                    "MA10_trend": "up" if ma10 > prev_ma10 else "down",
                    "golden_cross": prev_ma5 <= prev_ma10 and ma5 > ma10,
                    "death_cross": prev_ma5 >= prev_ma10 and ma5 < ma10,
                    "RSI": rsi,
                    "RSI_overbought": rsi > 70 if rsi else False,
                    "RSI_oversold": rsi < 30 if rsi else False,
                }
                self._ma_cache[cache_key] = result
                return result
        except Exception as exc:  # noqa: BLE001
            print(f"获取均线失败 {symbol}: {exc}")

        return None

    def fetch_sina_realtime(self, stocks: list[dict]) -> dict[str, dict]:
        """获取实时行情（实时优先，收盘后回退到日 K）。"""
        stock_list = [
            item
            for item in stocks
            if _to_stock_market(item.get("market")) != StockMarket.FX
        ]
        fx_list = [
            item
            for item in stocks
            if _to_stock_market(item.get("market")) == StockMarket.FX
        ]
        results: dict[str, dict] = {}

        if stock_list:
            symbols = [
                build_quote_symbol(item.get("market", StockMarket.SZ), item["code"])
                for item in stock_list
            ]
            url = build_quote_url_by_symbols(symbols)
            try:
                resp = self.session.get(
                    url,
                    headers={"Referer": "https://finance.sina.com.cn"},
                    timeout=10,
                )
                resp.encoding = "gb18030"
                for line in resp.text.strip().split(";"):
                    if "hq_str_" not in line or "=" not in line:
                        continue
                    key = line.split("=")[0].split("_")[-1]
                    if len(key) < 8:
                        continue
                    data_str = line[line.index('"') + 1 : line.rindex('"')]
                    parts = data_str.split(",")
                    if len(parts) > 30 and float(parts[3]) > 0:
                        results[key[2:]] = {
                            "name": parts[0],
                            "price": float(parts[3]),
                            "prev_close": float(parts[2]),
                            "open": float(parts[1]),
                            "high": float(parts[4]),
                            "low": float(parts[5]),
                            "volume": int(parts[8]),
                            "amount": float(parts[9]),
                            "date": parts[30],
                            "time": parts[31],
                        }
            except Exception as exc:  # noqa: BLE001
                print(f"实时行情获取失败: {exc}")

            for stock in stock_list:
                code = stock["code"]
                market = _to_eastmoney_market_id(stock.get("market", StockMarket.SZ))
                if code not in results or results[code]["price"] <= 0:
                    kline_data = self.fetch_eastmoney_kline(code, market)
                    if kline_data:
                        results[code] = kline_data
                        print(f"  {stock['name']}: 使用日K收盘价 {kline_data['price']}")

                if code not in results or results[code]["price"] <= 0:
                    continue

                if "prev_high" in results[code] and "prev_low" in results[code]:
                    continue

                prev_day_range = self.fetch_prev_day_range(code, market)
                if prev_day_range is not None:
                    results[code]["prev_high"] = prev_day_range[0]
                    results[code]["prev_low"] = prev_day_range[1]
                else:
                    self._warn_missing_prev_day_range(code, market, stock["name"])

        if fx_list:
            url = build_quote_url(StockMarket.FX, "XAU")
            try:
                resp = self.session.get(
                    url,
                    headers={"Referer": "https://finance.sina.com.cn"},
                    timeout=10,
                )
                line = resp.text.strip()
                if '"' in line:
                    data_str = line[line.index('"') + 1 : line.rindex('"')]
                    parts = data_str.split(",")
                    if len(parts) >= 13:
                        price = float(parts[0])
                        results["XAU"] = {
                            "name": "伦敦金",
                            "price": price,
                            "prev_close": float(parts[7]),
                            "volume": 0,
                            "amount": 0,
                            "date": parts[11]
                            if len(parts) > 11
                            else datetime.now().strftime("%Y-%m-%d"),
                            "time": parts[6],
                        }
            except Exception as exc:  # noqa: BLE001
                print(f"伦敦金获取失败: {exc}")

        return results

    def fetch_news(self, symbol: str) -> list[str]:
        """抓取个股最近新闻（简化版）。"""
        try:
            url = (
                "https://emweb.securities.eastmoney.com/PC_HSF10/"
                "CompanySurvey/CompanySurveyAjax"
            )
            params = {"code": symbol}
            self.session.get(url, params=params, timeout=5)
            return ["新闻模块已就绪 (市场收盘中)"]
        except Exception:  # noqa: BLE001
            return []
