# 规范

> Agent Skills 的完整格式规范。

本文档定义 Agent Skills 格式。

## 目录结构

一个 skill 至少是一个包含 `SKILL.md` 文件的目录：

```
skill-name/
└── SKILL.md          # 必需
```

<Tip>
  你也可以按需加入 [附加目录](#可选目录)，例如 `scripts/`、`references/` 和 `assets/`，用于增强 skill 能力。
</Tip>

## `SKILL.md` 格式

`SKILL.md` 文件必须包含 YAML frontmatter，后接 Markdown 内容。

### Frontmatter（必需）

```yaml  theme={null}
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

可选字段示例：

```yaml  theme={null}
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

| 字段 | 必需 | 约束 |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name` | 是 | 最长 64 个字符。仅允许小写字母、数字和连字符。不能以连字符开头或结尾。 |
| `description` | 是 | 最长 1024 个字符。不能为空。需说明 skill 做什么以及何时使用。 |
| `license` | 否 | 许可证名称，或指向随 skill 打包的许可证文件。 |
| `compatibility` | 否 | 最长 500 个字符。说明环境要求（目标产品、系统依赖、网络访问等）。 |
| `metadata` | 否 | 任意键值形式的附加元数据。 |
| `allowed-tools` | 否 | 空格分隔的预批准工具列表。（实验性） |

#### `name` 字段

必需的 `name` 字段：

* 长度必须为 1-64 个字符
* 仅可包含 Unicode 小写字母、数字和连字符（`a-z` 与 `-`）
* 不能以 `-` 开头或结尾
* 不能包含连续连字符（`--`）
* 必须与父目录名称一致

有效示例：

```yaml  theme={null}
name: pdf-processing
```

```yaml  theme={null}
name: data-analysis
```

```yaml  theme={null}
name: code-review
```

无效示例：

```yaml  theme={null}
name: PDF-Processing  # 不允许大写
```

```yaml  theme={null}
name: -pdf  # 不能以连字符开头
```

```yaml  theme={null}
name: pdf--processing  # 不允许连续连字符
```

#### `description` 字段

必需的 `description` 字段：

* 长度必须为 1-1024 个字符
* 应同时说明 skill 做什么、何时使用
* 应包含有助于智能体识别相关任务的关键词

良好示例：

```yaml  theme={null}
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

较差示例：

```yaml  theme={null}
description: Helps with PDFs.
```

#### `license` 字段

可选的 `license` 字段：

* 指定应用于该 skill 的许可证
* 建议保持简短（许可证名称，或随包许可证文件名）

示例：

```yaml  theme={null}
license: Proprietary. LICENSE.txt has complete terms
```

<a id="compatibility-field"></a>

#### `compatibility` 字段

可选的 `compatibility` 字段：

* 若提供，长度必须为 1-500 个字符
* 仅当 skill 有明确环境要求时才建议提供
* 可用于说明目标产品、系统依赖、网络访问需求等

示例：

```yaml  theme={null}
compatibility: Designed for Claude Code (or similar products)
```

```yaml  theme={null}
compatibility: Requires git, docker, jq, and access to the internet
```

<Note>
  大多数 skill 不需要 `compatibility` 字段。
</Note>

#### `metadata` 字段

可选的 `metadata` 字段：

* 一个从字符串键到字符串值的映射
* 客户端可用它存储 Agent Skills 规范未定义的附加属性
* 建议使用相对独特的键名，以避免意外冲突

示例：

```yaml  theme={null}
metadata:
  author: example-org
  version: "1.0"
```

#### `allowed-tools` 字段

可选的 `allowed-tools` 字段：

* 以空格分隔、预先批准可运行的工具列表
* 实验性字段。不同智能体实现的支持程度可能不同

示例：

```yaml  theme={null}
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

### 正文内容

Frontmatter 之后的 Markdown 正文用于编写 skill 指令。格式不受限制，核心目标是帮助智能体有效完成任务。

推荐包含的部分：

* 分步骤指令
* 输入与输出示例
* 常见边界情况

请注意，一旦智能体决定激活某个 skill，会加载完整的 `SKILL.md`。如果内容较长，建议拆分到引用文件中。

## 可选目录

### scripts/

用于放置智能体可执行的代码。脚本应当：

* 自包含，或清晰说明依赖
* 提供有帮助的错误信息
* 优雅处理边界情况

支持的语言取决于智能体实现。常见选择包括 Python、Bash 和 JavaScript。

### references/

用于放置按需读取的补充文档：

* `REFERENCE.md` - 详细技术参考
* `FORMS.md` - 表单模板或结构化数据格式
* 领域专用文件（`finance.md`、`legal.md` 等）

请保持单个 [参考文件](#文件引用) 聚焦。智能体会按需加载这些文件，文件越小，上下文占用越低。

### assets/

用于放置静态资源：

* 模板（文档模板、配置模板）
* 图片（图示、示例）
* 数据文件（查找表、Schema）

## 渐进式披露

Skill 应按上下文高效使用来组织：

1. **元数据**（约 100 tokens）：启动时加载所有 skills 的 `name` 与 `description`
2. **指令**（建议小于 5000 tokens）：激活 skill 时加载完整 `SKILL.md` 正文
3. **资源**（按需）：仅在需要时加载文件（如 `scripts/`、`references/`、`assets/` 中的内容）

建议将主 `SKILL.md` 控制在 500 行以内。详细参考资料放到独立文件。

## 文件引用

当在 skill 中引用其他文件时，请使用相对于 skill 根目录的路径：

```markdown  theme={null}
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

文件引用建议与 `SKILL.md` 保持一层深度，避免形成层层嵌套的深链。

## 校验

可使用 [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) 参考库校验你的 skill：

```bash  theme={null}
skills-ref validate ./my-skill
```

该命令会检查你的 `SKILL.md` frontmatter 是否有效，并确认命名规范是否符合要求。
