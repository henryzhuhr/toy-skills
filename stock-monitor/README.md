# Stock Monitor 脚本使用手册

本文档只关注一件事：`stock-monitor/scripts/` 下的脚本如何直接使用。

## 目录结构

```text
stock-monitor/
├── scripts/
│   ├── monitor.py                # 单次监控扫描
│   ├── monitor_daemon.py         # 后台守护进程主程序（通常由 control.sh 调用）
│   ├── control.sh                # 后台进程管理（start/stop/status/log）
│   ├── search_stock.py           # 关键词模糊搜索股票
│   ├── manual_analyse.py         # 手动分析（单只/批量）
│   ├── show_quote_request.py     # 查看 market+code 的行情请求拼接
│   ├── analyser.py               # 分析引擎（通常由 monitor/manual_analyse 调用）
│   └── stock_monitor/            # 核心业务模块（非直接入口）
└── README.md
```

## 运行前提

在仓库根目录执行命令（推荐使用 `uv`）：

```bash
cd /Users/henryzhu/project/toy-skills
```

## 1. 关键词搜索股票代码

用途：你只有名字或关键词，先查 code。

```bash
# 文本表格输出
uv run python stock-monitor/scripts/search_stock.py "紫金矿业"

# JSON 输出（便于复制/后续处理）
uv run python stock-monitor/scripts/search_stock.py "长飞光纤" --json

# 只看 A 股上交所，最多返回 5 条
uv run python stock-monitor/scripts/search_stock.py "紫金" --market sh --limit 5
```

## 2. 查看行情请求拼接

用途：确认监控请求如何从 `market+code` 变成接口 URL。

```bash
uv run python stock-monitor/scripts/show_quote_request.py --market sh --code 601869
```

示例输出：

- `symbol=sh601869`
- `url=https://hq.sinajs.cn/list=sh601869`

说明：`fx`（黄金）当前固定走 `hf_XAU`。

## 3. 手动分析（单次）

用途：人工临时分析，不需要启动守护进程。

```bash
# 单只分析
uv run python stock-monitor/scripts/manual_analyse.py --code 002131 --name 利欧股份 --market sz

# 只输出基础分析（不跑规则）
uv run python stock-monitor/scripts/manual_analyse.py --code 002131 --no-rules

# 手动附加标签（可重复）
uv run python stock-monitor/scripts/manual_analyse.py \
  --code 002131 \
  --alert "关注成交量持续性" \
  --alert "娱乐模式：今天看多"
```

批量分析（自备 JSON 文件）：

```bash
uv run python stock-monitor/scripts/manual_analyse.py --batch-file /path/to/stocks.json
```

`stocks.json` 示例：

```json
[
  {
    "code": "601899",
    "name": "紫金矿业",
    "market": "sh",
    "type": "individual",
    "cost": 0.0
  },
  {
    "code": "002131",
    "name": "利欧股份",
    "market": "sz",
    "type": "individual",
    "cost": 0.0
  }
]
```

查看所有参数：

```bash
uv run python stock-monitor/scripts/manual_analyse.py --help
```

## 4. 单次监控扫描

用途：按当前持仓配置跑一轮监控，立即输出触发预警。

```bash
uv run python stock-monitor/scripts/monitor.py
```

## 5. 后台常驻监控

用途：长期运行，按交易时段自动轮询。

```bash
cd stock-monitor/scripts
bash control.sh start
bash control.sh status
bash control.sh log
bash control.sh stop
```

备注：`control.sh` 会优先用 `uv run python`，无 `uv` 时回退 `python3`。

## 6. 分析引擎脚本

`analyser.py` 是分析能力模块，通常被 `monitor.py` 和 `manual_analyse.py` 调用。

可直接运行内置测试：

```bash
uv run python stock-monitor/scripts/analyser.py
```

## 7. 持仓配置文件

默认配置路径：

```text
~/.openclaw/skills/stock-monitor/portfolio.json
```

可用环境变量覆盖：

```bash
export STOCK_MONITOR_PORTFOLIO_FILE=/tmp/portfolio.json
```

配置项最小示例：

```json
[
  {
    "code": "601869",
    "name": "长飞光纤",
    "market": "sh",
    "type": "individual",
    "cost": 0.0,
    "alerts": {
      "change_pct_above": 4.0,
      "change_pct_below": -4.0,
      "volume_surge": 2.0
    }
  }
]
```

## 8. 常见排查

依赖问题：

```bash
uv run python stock-monitor/scripts/search_stock.py "紫金矿业"
```

如果能运行，说明脚本依赖环境正常。

测试：

```bash
uv run --group dev pytest -q tests/stock-monitor
```
