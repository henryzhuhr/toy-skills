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

- 修改前先阅读目标文件上下文，避免破坏公开接口
- 优先做“最小必要变更”，不引入与任务无关的重构
- 涉及行为变更时，补充最小可运行示例或文档说明
- 修改完成后，执行相关的单元测试，确保功能正确
- 修改完成后，至少执行一次单元测试
