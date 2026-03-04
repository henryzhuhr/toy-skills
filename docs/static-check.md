# 静态检查与 Git Hook 自动化

本文档说明如何在本仓库使用 Ruff 和 Git Hook 自动执行格式化、静态检查与测试。

## 1. 一次性安装 Hook

在仓库根目录执行：

```bash
bash scripts/install-git-hooks.sh
```

安装后会设置：

```bash
git config core.hooksPath .githooks
```

查看是否生效：

```bash
git config --get core.hooksPath
# 期望输出: .githooks
```

## 2. Hook 自动化行为

### pre-commit（提交前）

脚本：`.githooks/pre-commit`

对暂存区中的 Python 文件（`*.py`, `*.pyi`）自动执行：

1. `ruff format`
2. `ruff check --fix`
3. `ruff check`
4. 自动 `git add` 回暂存区

### pre-push（推送前）

脚本：`.githooks/pre-push`

自动执行：

```bash
uv run --group dev pytest -q tests
```

测试失败会阻止 push。

## 3. 如何手动执行 Hook

在仓库根目录执行：

```bash
bash .githooks/pre-commit
bash .githooks/pre-push
```

说明：

- `pre-commit` 只处理“已暂存”的 Python 文件。
- `pre-push` 会跑测试集 `tests/`。

## 4. Ruff 手动命令

### 全量检查（推荐）

```bash
uv run --group dev ruff format .
uv run --group dev ruff check --fix .
uv run --group dev ruff check .
```

### 仅检查某些文件

```bash
uv run --group dev ruff format path/to/file.py
uv run --group dev ruff check --fix path/to/file.py
uv run --group dev ruff check path/to/file.py
```

### 提交前本地完整自检

```bash
uv run --group dev ruff check .
uv run --group dev pytest -q tests
```

## 5. Ruff 配置位置

Ruff 规则在 `pyproject.toml`：

- `[tool.ruff]`
- `[tool.ruff.lint]`
- `[tool.ruff.format]`
