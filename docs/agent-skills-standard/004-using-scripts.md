# 在 skill 中使用脚本

> 如何在你的 skill 中运行命令并打包可执行脚本。

Skill 可以指导智能体运行 shell 命令，也可以在 `scripts/` 目录中打包可复用脚本。本指南涵盖一次性命令、自包含且自带依赖的脚本，以及如何为智能体场景设计脚本接口。

## 一次性命令

当现有包已经能满足需求时，你可以在 `SKILL.md` 中直接引用，无需建立 `scripts/` 目录。很多生态都提供可在运行时自动解析依赖的工具。

<Tabs sync={false}>
  <Tab title="uvx">
    [uvx](https://docs.astral.sh/uv/guides/tools/) 在隔离环境中运行 Python 包，并使用激进缓存策略。它随 [uv](https://docs.astral.sh/uv/) 提供。

    ```bash  theme={null}
    uvx ruff@0.8.0 check .
    uvx black@24.10.0 .
    ```

    * 不随 Python 内置，需要单独安装。
    * 很快。缓存策略激进，重复运行几乎瞬时完成。
  </Tab>

  <Tab title="pipx">
    [pipx](https://pipx.pypa.io/) 在隔离环境中运行 Python 包。可通过系统包管理器安装（`apt install pipx`、`brew install pipx`）。

    ```bash  theme={null}
    pipx run 'black==24.10.0' .
    pipx run 'ruff==0.8.0' check .
    ```

    * 不随 Python 内置，需要单独安装。
    * `uvx` 之外的成熟替代方案。虽然 `uvx` 已成为更常见的推荐，但 `pipx` 依然稳定可靠，且在系统包管理器中的可得性更广。
  </Tab>

  <Tab title="npx">
    [npx](https://docs.npmjs.com/cli/commands/npx) 可按需下载并运行 npm 包。它随 npm 提供（npm 随 Node.js 提供）。

    ```bash  theme={null}
    npx eslint@9 --fix .
    npx create-vite@6 my-app
    ```

    * 随 Node.js 内置，无需额外安装。
    * 下载包后执行，并缓存以便后续复用。
    * 使用 `npx package@version` 固定版本，提升可复现性。
  </Tab>

  <Tab title="bunx">
    [bunx](https://bun.sh/docs/cli/bunx) 是 Bun 对应 `npx` 的工具，随 [Bun](https://bun.sh/) 提供。

    ```bash  theme={null}
    bunx eslint@9 --fix .
    bunx create-vite@6 my-app
    ```

    * 在 Bun 环境中可作为 `npx` 的直接替代。
    * 仅当用户环境是 Bun 而非 Node.js 时适用。
  </Tab>

  <Tab title="deno run">
    [deno run](https://docs.deno.com/runtime/reference/cli/run/) 可直接从 URL 或 specifier 运行脚本。它随 [Deno](https://deno.com/) 提供。

    ```bash  theme={null}
    deno run npm:create-vite@6 my-app
    deno run --allow-read npm:eslint@9 -- --fix .
    ```

    * 文件系统/网络访问需要显式权限参数（如 `--allow-read`）。
    * 使用 `--` 将 Deno 参数与工具自身参数分隔开。
  </Tab>

  <Tab title="go run">
    [go run](https://pkg.go.dev/cmd/go#hdr-Compile_and_run_Go_program) 可直接编译并运行 Go 包，它是 `go` 命令内置能力。

    ```bash  theme={null}
    go run golang.org/x/tools/cmd/goimports@v0.28.0 .
    go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.62.0 run
    ```

    * Go 内置，无需额外工具。
    * 固定版本或使用 `@latest`，让命令意图更明确。
  </Tab>
</Tabs>

**在 skill 中使用一次性命令的建议：**

* **固定版本**（例如 `npx eslint@9.0.0`），确保命令在时间维度上行为一致。
* **在 `SKILL.md` 明确前置条件**（例如“需要 Node.js 18+”），不要假设智能体环境一定具备。运行时级别要求可使用 [`compatibility` frontmatter 字段](/specification#compatibility-field)。
* **复杂命令迁移到脚本**。当你只是调用少量参数的一次性工具时，一条命令就够；当命令复杂到很难一次写对时，放入 `scripts/` 的可测试脚本会更可靠。

## 从 `SKILL.md` 引用脚本

请使用**相对于 skill 根目录**的路径引用打包文件。智能体会自动解析这些路径，不需要绝对路径。

在 `SKILL.md` 列出可用脚本，让智能体知道它们存在：

```markdown SKILL.md theme={null}
## 可用脚本

- **`scripts/validate.sh`** — 校验配置文件
- **`scripts/process.py`** — 处理输入数据
```

然后指导智能体运行它们：

````markdown SKILL.md theme={null}
## 工作流

1. 运行校验脚本：
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```

2. 处理结果：
   ```bash
   python3 scripts/process.py --input results.json
   ```
````

<Note>
  同样的相对路径约定也适用于 `references/*.md` 等支持文件。代码块里的脚本执行路径相对于**skill 根目录**，因为智能体会从该目录运行命令。
</Note>

## 自包含脚本

当你需要可复用逻辑时，可在 `scripts/` 中打包脚本，并在脚本内声明依赖。这样智能体只需一条命令即可运行，无需单独清单文件或安装步骤。

多种语言都支持内联依赖声明：

<Tabs sync={false}>
  <Tab title="Python">
    [PEP 723](https://peps.python.org/pep-0723/) 定义了内联脚本元数据标准。可在 `# ///` 标记包裹的 TOML 区块中声明依赖：

    ```python scripts/extract.py theme={null}
    # /// script
    # dependencies = [
    #   "beautifulsoup4",
    # ]
    # ///

    from bs4 import BeautifulSoup

    html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
    print(BeautifulSoup(html, "html.parser").select_one("p.info").get_text())
    ```

    推荐用 [uv](https://docs.astral.sh/uv/) 运行：

    ```bash  theme={null}
    uv run scripts/extract.py
    ```

    `uv run` 会创建隔离环境、安装声明的依赖并执行脚本。[pipx](https://pipx.pypa.io/)（`pipx run scripts/extract.py`）同样支持 PEP 723。

    * 用 [PEP 508](https://peps.python.org/pep-0508/) 规范固定版本：`"beautifulsoup4>=4.12,<5"`。
    * 用 `requires-python` 约束 Python 版本。
    * 用 `uv lock --script` 生成锁文件，获得完整可复现性。
  </Tab>

  <Tab title="Deno">
    Deno 的 `npm:` 与 `jsr:` 导入说明符使脚本默认自包含：

    ```typescript scripts/extract.ts theme={null}
    #!/usr/bin/env -S deno run

    import * as cheerio from "npm:cheerio@1.0.0";

    const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
    const $ = cheerio.load(html);
    console.log($("p.info").text());
    ```

    ```bash  theme={null}
    deno run scripts/extract.ts
    ```

    * npm 包用 `npm:`，Deno 原生包用 `jsr:`。
    * 版本说明符遵循 semver：`@1.0.0`（精确）、`@^1.0.0`（兼容）。
    * 依赖会全局缓存。用 `--reload` 强制重新拉取。
    * 含原生 addon（node-gyp）的包可能无法工作，更推荐自带预编译二进制的包。
  </Tab>

  <Tab title="Bun">
    当找不到 `node_modules` 目录时，Bun 会在运行时自动安装缺失包。可在导入路径中直接固定版本：

    ```typescript scripts/extract.ts theme={null}
    #!/usr/bin/env bun

    import * as cheerio from "cheerio@1.0.0";

    const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
    const $ = cheerio.load(html);
    console.log($("p.info").text());
    ```

    ```bash  theme={null}
    bun run scripts/extract.ts
    ```

    * 不需要 `package.json` 或 `node_modules`。TypeScript 原生支持。
    * 包会全局缓存。首次运行下载，后续运行接近瞬时。
    * 如果目录树任意上级存在 `node_modules`，自动安装会禁用，Bun 将回退到标准 Node.js 解析。
  </Tab>

  <Tab title="Ruby">
    Ruby 2.6 起自带 Bundler。可用 `bundler/inline` 直接在脚本中声明 gem：

    ```ruby scripts/extract.rb theme={null}
    require 'bundler/inline'

    gemfile do
      source 'https://rubygems.org'
      gem 'nokogiri'
    end

    html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
    doc = Nokogiri::HTML(html)
    puts doc.at_css('p.info').text
    ```

    ```bash  theme={null}
    ruby scripts/extract.rb
    ```

    * 建议显式固定版本（如 `gem 'nokogiri', '~> 1.16'`），因为没有 lockfile。
    * 工作目录中的 `Gemfile` 或 `BUNDLE_GEMFILE` 环境变量可能造成干扰。
  </Tab>
</Tabs>

## 面向智能体使用场景设计脚本

当智能体运行你的脚本时，会读取 stdout 和 stderr 来决定下一步动作。以下设计选择能显著提升脚本可用性。

### 避免交互式提示

这是智能体执行环境的硬性要求。智能体运行在非交互式 shell 中，无法响应 TTY 提示、密码对话框或确认菜单。若脚本阻塞在交互输入，会无限挂起。

所有输入应通过命令行参数、环境变量或 stdin 提供：

```
# 错误：等待输入导致挂起
$ python scripts/deploy.py
Target environment: _

# 正确：给出清晰错误和指导
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

### 用 `--help` 说明用法

`--help` 输出是智能体学习脚本接口的主要方式。应包含简要说明、可用参数和示例：

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --output FILE      Write output to FILE instead of stdout
  --verbose          Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

保持简洁，避免占用过多上下文窗口。

### 编写有帮助的错误信息

当智能体收到错误时，错误信息会直接影响下一次尝试。模糊的“Error: invalid input”会浪费回合。应明确说明出错原因、期望值和下一步建议：

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

### 使用结构化输出

优先使用结构化格式（JSON、CSV、TSV），避免自由文本。结构化输出既可被智能体消费，也可被标准工具（`jq`、`cut`、`awk`）处理，便于管道组合。

```
# 按空白对齐——程序难以解析
NAME          STATUS    CREATED
my-service    running   2025-01-15

# 定界格式——字段边界明确
{"name": "my-service", "status": "running", "created": "2025-01-15"}
```

**分离数据与诊断信息：**结构化数据输出到 stdout，进度信息、告警和其他诊断输出到 stderr。这样智能体既能获得可解析结果，也能在需要时获取诊断信息。

### 进一步考虑

* **幂等性。** 智能体可能重试命令，“不存在则创建”比“创建并在重复时报错”更安全。
* **输入约束。** 对模糊输入给出明确错误，而不是猜测。尽量使用枚举和封闭集合。
* **Dry-run 支持。** 对破坏性或有状态操作，提供 `--dry-run` 以便预览。
* **有意义的退出码。** 为不同失败类型使用不同退出码（未找到、参数错误、鉴权失败），并在 `--help` 中说明，让智能体理解每个码的含义。
* **安全默认值。** 评估破坏性操作是否需要显式确认参数（`--confirm`、`--force`）或其他风险控制手段。
* **可预测的输出规模。** 许多智能体执行器会在超过阈值（如 10-30K 字符）时截断输出，可能丢失关键信息。若脚本可能产生大输出，默认给摘要或合理限制，并提供如 `--offset` 之类参数按需获取更多内容。另一种做法是要求智能体显式传入 `--output`，指定输出文件或 `-`，以明确是否写到 stdout。
