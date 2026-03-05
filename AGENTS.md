# Repository Guidelines

## 项目结构与模块组织

本仓库是一个以 Python 为主的技能（skill）工作区，核心内容按技能目录组织。

```bash
├── .agents 
│   └── skills # 软链接到各技能目录
│       └── <my-skill> -> ../../<my-skill>
│           └── SKILL.md
├── <my-skill>
│   └── SKILL.md
├── tests
│   └── <my-skill> # 按照 skill 名称划分测试用例，测试文件以 test_*.py 命名
├── scripts # 实用脚本目录
├── AGENTS.md
└── pyproject.toml
```

## 项目管理和构建

项目使用 `uv` 作为包管理器，新增依赖后请同步更新 `pyproject.toml`，重新生成 `uv.lock`

## 代码风格与命名规范

- 遵循 PEP 8，统一 4 空格缩进。
- 函数与变量使用 `snake_case`，模块文件名使用小写。
- CLI 脚本优先使用 `argparse`，保持参数明确、入口清晰。
- 公共函数尽量补充类型标注。
- 注释保持简短，仅解释不直观的意图或约束。

## 测试指南

当前未建立完整自动化测试。提交前至少执行关键 CLI 冒烟验证：

新增复杂逻辑时，建议引入 `pytest`，在 `tests/` 下新增 `test_*.py`，覆盖空数据、解析失败、非法参数等边界场景。

测试的时候可以使用下面的命令

```bash
uv run --group dev pytest tests/<my-skill>/test_*.py
# 安静模式，输出简洁的测试结果
uv run --group dev pytest -q tests/<my-skill>/test_*.py
```

## 提交与合并请求规范

现有历史使用带 scope 的 Conventional Commits（可带 emoji），例如：

- `feat(skills): ...`
- `chore(skills): ...`

建议格式：`<type>(<scope>): <summary>`，主题行使用祈使句并保持简洁。

PR 应包含：

- 变更目的与行为差异说明；
- 受影响路径（如 `a-stock-analysis/scripts/analyze.py`）；
- 已执行的验证命令；
- CLI 输出示例（如有交互或展示变更）。

## Agent 执行约束

### 基本原则

- 修改前先阅读目标文件上下文，避免破坏公开接口
- 优先做“最小必要变更”，不引入与任务无关的重构
- 涉及行为变更时，补充最小可运行示例或文档说明
- 修改完成后，执行相关的单元测试，确保功能正确

### 任务与待办

对于**复杂的任务**或者**可优化点**，你应该进行规划，并记录在 `TODO.md` 里，按照优先级排序，并在完成后标记状态。

`TODO.template.md` 是一个模板文件（仅可人工修改），`TODO.md` 必须**以模板文件为准**

如果不存在 `TODO.md` 或者 `TODO.md` 损坏，你需要严格参考 `TODO.template.md` 的格式创建或修复 `TODO.md`，确保后续任务跟踪的规范性和一致性。

### 静态检查

每次做完修改后，你需要使用如下的命令对**修改的文件**进行静态检查

```bash
uv run --group dev ruff format path/to/file.py
uv run --group dev ruff check --fix path/to/file.py
uv run --group dev ruff check path/to/file.py
```

对于出现的问题，你需要修复它们，直到没有问题为止。

### CLI 入口与示例原则

- 优先在 `<skill>/scripts/` 下提供可直接运行的脚本入口（例如：`uv run stock-monitor/scripts/search_stock.py "紫金矿业"`）。
- `scripts/*.py` 应保持“薄入口”职责：只做参数解析、调用已有函数、输出规范化，不承载复杂业务逻辑。
- 可复用业务逻辑应下沉到模块目录（如 `stock-monitor/scripts/stock_monitor/`），方便测试与调试。
- 不新增 `demo/` 或 `examples/` 目录；示例统一通过 `<skill>/scripts/` 下可执行脚本提供。
- 示例说明写在对应 skill 的 README 中，并给出可直接执行的命令。

## 项目文档

- `docs/agent-skills-standard/000-index.md`：技能开发标准文档，包含技能设计原则、开发流程、最佳实践等内容。
