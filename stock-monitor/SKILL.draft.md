---
name: stock-monitor
description: "股票监控技能。支持关键词查代码、规则监控、手动分析、后台守护和复盘。"
---

# Stock Monitor Skill

## 目标

用于管理“选股 -> 建仓后监控 -> 预警响应 -> 复盘调参”的完整流程，核心是风险控制与执行纪律。

## 适用场景

- 只有股票名称，需要先查代码再监控。
- 已有持仓，需要按成本、涨跌、量能、技术指标做自动预警。
- 收到预警后，需要快速人工复核并输出结构化分析。
- 需要后台长期运行，降低盯盘成本。

## 标准工作流

### 1) 标的识别（先确认代码）

```bash
uv run python <this_skill_dir>/scripts/search_stock.py "紫金矿业" --json
```

要求：

- 至少确认 `market`、`code`、`name` 三个字段。
- 同名多市场（A/H/US）时必须明确目标市场。

### 2) 监控配置（先风控后机会）

监控配置路径默认：

```text
~/.openclaw/skills/stock-monitor/portfolio.json
```

最小配置示例：

```json
[
  {
    "code": "601899",
    "name": "紫金矿业",
    "market": "sh",
    "type": "individual",
    "cost": 0.0,
    "alerts": {
      "cost_pct_above": 15.0,
      "cost_pct_below": -12.0,
      "change_pct_above": 4.0,
      "change_pct_below": -4.0,
      "volume_surge": 2.0,
      "ma_monitor": true,
      "rsi_monitor": true,
      "gap_monitor": true,
      "trailing_stop": true
    }
  }
]
```

配置要求：

- `code`、`name`、`market`、`type` 必填。
- 已持仓标的建议填写 `cost`，否则无法输出成本盈亏相关预警。

### 3) 手动验证请求拼接

```bash
uv run python <this_skill_dir>/scripts/show_quote_request.py --market sh --code 601899
```

规则：

- A 股/ETF：`symbol = market + code`（例：`sh601899`）
- 黄金：固定 `hf_XAU`

### 4) 运行监控

单次扫描：

```bash
uv run python <this_skill_dir>/scripts/monitor.py
```

后台守护：

```bash
cd <this_skill_dir>/scripts
bash control.sh start
bash control.sh status
bash control.sh log
bash control.sh stop
```

### 5) 预警响应（按级别执行）

| 级别 | 触发特征 | 默认动作 |
|------|----------|----------|
| `info` | 单条件触发 | 记录观察，不立刻交易 |
| `warning` | 2 条件共振 | 复核仓位与流动性，准备条件单 |
| `critical` | 多条件共振 | 按交易计划执行减仓/止损/止盈 |

执行要求：

- 预警是“决策输入”，不是“自动交易指令”。
- 动作必须与仓位上限、回撤上限一致。

### 6) 手动复核（决策前二次确认）

```bash
# 常规手动分析
uv run python <this_skill_dir>/scripts/manual_analyse.py --code 002131

# 不跑规则，仅看基础分析
uv run python <this_skill_dir>/scripts/manual_analyse.py --code 002131 --no-rules

# 添加人工标签
uv run python <this_skill_dir>/scripts/manual_analyse.py --code 002131 --alert "关注量能持续性"

# 批量分析
uv run python <this_skill_dir>/scripts/manual_analyse.py --batch-file /path/to/stocks.json
```

### 7) 收盘复盘与参数迭代

复盘清单：

1. 今日预警中哪些是有效信号，哪些是噪音。
2. 哪类阈值过紧或过松（如个股 ±4% 需否调整）。
3. 是否出现“应触发未触发”或“重复刷屏”问题。

## 金融风控约束

- 先定义止损阈值，再定义止盈阈值。
- 单票风险预算优先于交易频率。
- 技术指标用于确认，不用于保证预测。
- 重大事件日（财报/政策）提高人工复核频率。

## 输出规范（执行技能时）

- 先给结论：当前状态、风险级别、建议动作。
- 再给依据：价格、涨跌、触发规则、关键指标。
- 最后给命令：可直接复制执行的脚本命令。
