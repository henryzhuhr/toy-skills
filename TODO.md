# 待办任务

本文件一个临时的任务跟踪的轻量级文档，记录当前需要完成的任务和未来规划。后续会根据实际情况调整和完善。

## 维护规则

- 任务必须有唯一编号（`TSK-xxx`）。
- 任务必须写清楚：任务优先级、状态、任务简介、任务的链接（简单的任务可以在本文档中描述，复杂的可以链接到专门的文档或 PR）。
- 状态仅使用：`todo` / `in_progress` / `blocked` / `done` / `passed`。
- 状态流转建议：`todo` -> `in_progress` -> `done` -> `passed`（人工确认）。
- 每次开始新开发前，先把对应任务改为 `in_progress`。
- `done` 由 Agent 标注，表示实现完成并通过当前验证。
- `passed` 由人工标注，表示人工验收通过、任务完全结束。
- `deprecated` 由人工标注，表示不需要再跟踪的任务，或者已经废弃的任务。
- 所有的状态以 `待办列表` 中的状态为准，任务详情中的状态需要同步更新。

- Agent 不允许直接标注  `passed`/`deprecated`，必须由人工确认后标注。
- 对于已被人工标记为 `passed` 或者 `deprecated` 的任务，需要及时清理相关任务文档和代码中的临时标记，保持仓库整洁。
- `TODO.template.md` 是一个模板文件（仅可人工修改），`TODO.md` 必须**以模板文件为准**

## 优先级定义

- `P0`：阻塞后续开发或高概率导致错误使用，必须优先完成。
- `P1`：显著提升稳定性/可维护性，应在近期迭代完成。
- `P2`：优化体验或增强能力，可排在基础稳定后。

## 待办列表

| ID | 优先级 | 状态 | 任务 | 任务链接 |
| --- | --- | --- | --- | --- |
| TSK-006 | P0 | done | 修复 daemon 调度未生效（夜间/周末仍扫描全量标的） | [TSK-006](#TSK-006-修复-daemon-调度未生效夜间周末仍扫描全量标的) |
| TSK-010 | P1 | deprecated | 修正 README 仓库路径示例与实际路径不一致问题 | [TSK-010](#TSK-010-修正-README-仓库路径示例与实际路径不一致问题) |
| TSK-011 | P1 | done | 补充 rules/scheduler/daemon 关键回归测试覆盖 | [TSK-011](#TSK-011-补充-rulesschedulerdaemon-关键回归测试覆盖) |

## 任务模板（新增任务时复制）

```md
### TSK-xxx 任务名

- 优先级：P0 / P1 / P2
- 状态：todo / in_progress / blocked / done / passed（`passed` 仅人工设置）
- 影响路径：
- 任务描述：
- 验收标准：
- 验证命令：
- 备注/阻塞项：
```

## 任务详情列表

### TSK-006 修复 daemon 调度未生效（夜间/周末仍扫描全量标的）

- 优先级：P0
- 状态：done
- 影响路径：`stock-monitor/scripts/monitor_daemon.py`、`stock-monitor/scripts/stock_monitor/__init__.py`、`tests/stock-monitor/test_monitor_daemon.py`
- 任务描述：daemon 已获取调度结果，但执行监控时固定全量扫描，需确保夜间/周末仅扫描 `fx` 标的。
- 验收标准：daemon 在 `night/weekend` 模式下仅处理 `market=fx`；日志中的扫描数量与调度一致。
- 验证命令：`uv run --group dev pytest -q tests/stock-monitor/test_scheduler.py tests/stock-monitor/test_monitor_daemon.py`
- 备注/阻塞项：可能需要为 daemon 增加可测试的调度注入点。

### TSK-010 修正 README 仓库路径示例与实际路径不一致问题

- 优先级：P1
- 状态：todo
- 影响路径：`stock-monitor/README.md`
- 任务描述：把 README 中硬编码路径改为当前仓库真实路径或通用相对路径，避免用户复制后失败。
- 验收标准：README 示例命令在当前仓库可直接执行，无路径歧义。
- 验证命令：`uv run python stock-monitor/scripts/search_stock.py --help`
- 备注/阻塞项：需与根目录 `AGENTS.md` 中路径示例保持一致。

### TSK-011 补充 rules/scheduler/daemon 关键回归测试覆盖

- 优先级：P1
- 状态：done
- 影响路径：`tests/stock-monitor/test_rules.py`、`tests/stock-monitor/test_scheduler.py`、`tests/stock-monitor/test_monitor_daemon.py`
- 任务描述：为调度选择、规则开关、动态止盈阈值新增回归测试，避免修复后再次回退。
- 验收标准：新增用例覆盖上述行为差异，且全部通过。
- 验证命令：`uv run --group dev pytest -q tests/stock-monitor`
- 备注/阻塞项：daemon 行为若难以直测，可先抽离纯函数后测试。
