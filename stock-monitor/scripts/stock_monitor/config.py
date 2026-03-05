"""配置加载与校验。"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from .enums import STOCK_TYPE, StockMarket
except ImportError:
    _enum_spec = importlib.util.spec_from_file_location(
        "stock_monitor_enums_compat",
        Path(__file__).with_name("enums.py"),
    )
    if _enum_spec is None or _enum_spec.loader is None:
        raise ImportError("Cannot load stock_monitor enums module")
    _enum_module = importlib.util.module_from_spec(_enum_spec)
    _enum_spec.loader.exec_module(_enum_module)
    STOCK_TYPE = _enum_module.STOCK_TYPE
    StockMarket = _enum_module.StockMarket


def _to_stock_market(value: Any, field_name: str = "market") -> StockMarket:
    if isinstance(value, StockMarket):
        return value

    try:
        normalized = str(value).strip().lower()
        return StockMarket(normalized)
    except (TypeError, ValueError) as exc:
        valid_markets = ", ".join(item.value for item in StockMarket)
        raise ValueError(
            f"{field_name} 必须是以下之一: {valid_markets}，收到: {value}"
        ) from exc


def _to_float(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} 不是有效数字: {value}") from exc


def _to_bool(value: Any, field_name: str) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    raise ValueError(f"{field_name} 不是有效布尔值: {value}")


@dataclass
class AlertConfig:
    """预警配置模型。"""

    cost_pct_above: float | None = None
    cost_pct_below: float | None = None
    change_pct_above: float | None = None
    change_pct_below: float | None = None
    volume_surge: float | None = None
    price_above: float | None = None
    price_below: float | None = None
    ma_monitor: bool | None = None
    rsi_monitor: bool | None = None
    gap_monitor: bool | None = None
    trailing_stop: bool | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw_alerts: Any) -> "AlertConfig":
        if raw_alerts is None:
            raw_alerts = {}
        if not isinstance(raw_alerts, dict):
            raise ValueError("alerts 必须是对象")

        float_fields = {
            "cost_pct_above",
            "cost_pct_below",
            "change_pct_above",
            "change_pct_below",
            "volume_surge",
            "price_above",
            "price_below",
        }
        bool_fields = {"ma_monitor", "rsi_monitor", "gap_monitor", "trailing_stop"}

        kwargs: dict[str, Any] = {}
        extras: dict[str, Any] = {}
        for key, value in raw_alerts.items():
            if key in float_fields:
                kwargs[key] = _to_float(value, key)
            elif key in bool_fields:
                kwargs[key] = _to_bool(value, key)
            else:
                extras[key] = value

        return cls(**kwargs, extras=extras)

    def to_dict(self) -> dict[str, Any]:
        fields_in_order = [
            "cost_pct_above",
            "cost_pct_below",
            "change_pct_above",
            "change_pct_below",
            "volume_surge",
            "price_above",
            "price_below",
            "ma_monitor",
            "rsi_monitor",
            "gap_monitor",
            "trailing_stop",
        ]

        data: dict[str, Any] = {}
        for key in fields_in_order:
            value = getattr(self, key)
            if value is not None:
                data[key] = value
        data.update(self.extras)
        return data


@dataclass
class PortfolioItemConfig:
    """单个持仓标的配置模型。"""

    code: str
    name: str
    market: StockMarket
    type: STOCK_TYPE
    cost: float = 0.0
    alerts: AlertConfig = field(default_factory=AlertConfig)
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw_item: Any) -> "PortfolioItemConfig":
        if not isinstance(raw_item, dict):
            raise ValueError("持仓项必须是对象")

        required_fields = ["code", "name", "market", "type"]
        missing_fields = []
        for field_name in required_fields:
            value = raw_item.get(field_name)
            if value is None or value == "":
                missing_fields.append(field_name)
        if missing_fields:
            raise ValueError(f"缺少必要字段: {', '.join(missing_fields)}")

        cost = _to_float(raw_item.get("cost", 0.0), "cost")
        alerts = AlertConfig.from_dict(raw_item.get("alerts", {}))
        extras = {
            key: value
            for key, value in raw_item.items()
            if key not in {"code", "name", "market", "type", "cost", "alerts"}
        }

        try:
            stock_type = (
                raw_item["type"]
                if isinstance(raw_item["type"], STOCK_TYPE)
                else STOCK_TYPE(str(raw_item["type"]))
            )
        except ValueError as exc:
            valid_types = ", ".join(item.value for item in STOCK_TYPE)
            raise ValueError(
                f"type 必须是 {valid_types} 之一: {raw_item['type']}"
            ) from exc

        return cls(
            code=str(raw_item["code"]),
            name=str(raw_item["name"]),
            market=_to_stock_market(raw_item["market"]),
            type=stock_type,
            cost=0.0 if cost is None else cost,
            alerts=alerts,
            extras=extras,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "name": self.name,
            "market": self.market.value,
            "type": self.type.value,
            "cost": self.cost,
            "alerts": self.alerts.to_dict(),
        }
        data.update(self.extras)
        return data


PORTFOLIO_FILE = (
    Path.home() / ".openclaw" / "skills" / "stock-monitor" / "portfolio.json"
)
PORTFOLIO_FILE = Path(
    os.environ.get("STOCK_MONITOR_PORTFOLIO_FILE", str(PORTFOLIO_FILE))
)

_DEFAULT_WATCHLIST_DATA: list[PortfolioItemConfig] = [
    PortfolioItemConfig(
        code="601899",
        name="紫金矿业",
        market=StockMarket.SH,
        type=STOCK_TYPE.INDIVIDUAL,
        cost=0.0,
        alerts=AlertConfig(
            cost_pct_above=15.0,
            cost_pct_below=-12.0,
            change_pct_above=4.0,
            change_pct_below=-4.0,
            volume_surge=2.0,
        ),
    ),
    PortfolioItemConfig(
        code="512400",
        name="有色金属ETF",
        market=StockMarket.SH,
        type=STOCK_TYPE.ETF,
        cost=0.90,
        alerts=AlertConfig(
            cost_pct_above=12.0,
            cost_pct_below=-12.0,
            change_pct_above=2.0,
            change_pct_below=-2.0,
            volume_surge=1.8,
        ),
    ),
    PortfolioItemConfig(
        code="516020",
        name="化工50ETF",
        market=StockMarket.SH,
        type=STOCK_TYPE.ETF,
        cost=0.90,
        alerts=AlertConfig(
            cost_pct_above=12.0,
            cost_pct_below=-12.0,
            change_pct_above=2.0,
            change_pct_below=-2.0,
            volume_surge=1.8,
        ),
    ),
    PortfolioItemConfig(
        code="XAU",
        name="伦敦金(人民币/克)",
        market=StockMarket.FX,
        type=STOCK_TYPE.GOLD,
        cost=4650.0,
        alerts=AlertConfig(
            cost_pct_above=10.0,
            cost_pct_below=-8.0,
            change_pct_above=2.5,
            change_pct_below=-2.5,
        ),
    ),
]


def parse_watchlist(watchlist: Any) -> list[PortfolioItemConfig]:
    """把投资组合原始数据解析为 PortfolioItemConfig 列表。"""
    if not isinstance(watchlist, list):
        raise ValueError("投资组合配置必须是列表")

    parsed_watchlist: list[PortfolioItemConfig] = []
    for idx, raw_item in enumerate(watchlist):
        try:
            if isinstance(raw_item, PortfolioItemConfig):
                parsed_watchlist.append(raw_item)
            elif isinstance(raw_item, dict):
                parsed_watchlist.append(PortfolioItemConfig.from_dict(raw_item))
            else:
                raise ValueError("持仓项必须是对象或 PortfolioItemConfig")
        except ValueError as exc:
            raise ValueError(f"投资组合第 {idx + 1} 项校验失败: {exc}") from exc

    return parsed_watchlist


def serialize_watchlist(watchlist: Any) -> list[dict[str, Any]]:
    """把投资组合序列化为可落盘的字典列表。"""
    parsed_watchlist = parse_watchlist(watchlist)
    return [item.to_dict() for item in parsed_watchlist]


DEFAULT_WATCHLIST = parse_watchlist(_DEFAULT_WATCHLIST_DATA)


def _write_portfolio_file(portfolio_file: Path, watchlist: Any) -> bool:
    """写入投资组合配置文件。"""
    try:
        serialized_watchlist = serialize_watchlist(watchlist)
        portfolio_file.parent.mkdir(parents=True, exist_ok=True)
        with portfolio_file.open("w", encoding="utf-8") as handle:
            json.dump(serialized_watchlist, handle, ensure_ascii=False, indent=2)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"写入投资组合文件失败 {portfolio_file}: {exc}")
        return False


def normalize_watchlist(watchlist: Any) -> list[dict[str, Any]]:
    """用 dataclass 规范化投资组合配置。"""
    return serialize_watchlist(watchlist)


def load_watchlist(portfolio_file: Path = PORTFOLIO_FILE) -> list[dict[str, Any]]:
    """从 portfolio.json 加载监控列表；文件不存在时自动创建默认配置。"""
    portfolio_file = Path(portfolio_file)
    default_watchlist = copy.deepcopy(DEFAULT_WATCHLIST)
    default_watchlist_serialized = serialize_watchlist(default_watchlist)

    if not portfolio_file.exists():
        _write_portfolio_file(portfolio_file, default_watchlist)
        return default_watchlist_serialized

    try:
        with portfolio_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            normalized_watchlist = normalize_watchlist(data)
            if normalized_watchlist != data:
                _write_portfolio_file(portfolio_file, normalized_watchlist)
            return normalized_watchlist
        print(f"投资组合文件格式错误(应为列表): {portfolio_file}")
    except Exception as exc:  # noqa: BLE001
        print(f"读取投资组合文件失败 {portfolio_file}: {exc}")

    _write_portfolio_file(portfolio_file, default_watchlist)
    return default_watchlist_serialized


WATCHLIST = load_watchlist()
