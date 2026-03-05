# 什么是 skills？

> Agent Skills 是一种轻量、开放的格式，用于通过专业知识和工作流扩展 AI 智能体能力。

从本质上讲，skill 就是一个包含 `SKILL.md` 文件的文件夹。该文件包含元数据（至少包括 `name` 和 `description`）以及指令，用来告诉智能体如何执行某项特定任务。Skill 也可以打包脚本、模板和参考资料。

```directory  theme={null}
my-skill/
├── SKILL.md          # 必需：说明 + 元数据
├── scripts/          # 可选：可执行代码
├── references/       # 可选：文档资料
└── assets/           # 可选：模板、资源
```

## skills 如何工作

Skills 使用**渐进式披露（progressive disclosure）**来高效管理上下文：

1. **发现（Discovery）**：启动时，智能体只加载每个可用 skill 的名称和描述，仅保留判断是否相关所需的最小信息。

2. **激活（Activation）**：当任务匹配某个 skill 的描述时，智能体将完整的 `SKILL.md` 指令读入上下文。

3. **执行（Execution）**：智能体遵循指令，按需加载引用文件或执行打包代码。

这种方式让智能体保持高效，同时在需要时获取更多上下文。

## `SKILL.md` 文件

每个 skill 都从一个 `SKILL.md` 文件开始，文件包含 YAML frontmatter 和 Markdown 指令正文：

```mdx  theme={null}
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
---

# PDF Processing

## When to use this skill
Use this skill when the user needs to work with PDF files...

## How to extract text
1. Use pdfplumber for text extraction...

## How to fill forms
...
```

`SKILL.md` 顶部必须包含以下 frontmatter 字段：

* `name`：简短标识符
* `description`：说明何时使用此 skill

Markdown 正文承载实际指令，对结构和内容没有硬性限制。

这种简单格式有几个关键优势：

* **自解释**：skill 作者或用户都能通过阅读 `SKILL.md` 理解其作用，便于审计与改进。

* **可扩展**：skill 复杂度可从纯文本指令扩展到可执行代码、资源和模板。

* **可移植**：skill 本质就是文件，易于编辑、版本管理和分享。

## 下一步

* [查看规范](/specification) 以了解完整格式。
* [为你的智能体接入 skills 支持](/integrate-skills) 以构建兼容客户端。
* 在 GitHub 查看 [示例 skills](https://github.com/anthropics/skills)。
* 阅读 [编写最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 以写出高质量 skill。
* 使用 [参考库](https://github.com/agentskills/agentskills/tree/main/skills-ref) 校验 skill 并生成 prompt XML。
