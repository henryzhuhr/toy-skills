---
name: git-commit-helper
description: Help create git commits and PRs with properly formatted messages and release notes following CockroachDB conventions. Use when committing changes or creating pull requests.
---

# Git 提交助手

帮助用户创建遵循约定的格式正确的提交消息和发行说明。

## 工作流程

1. **分析变更内容**：运行 `git diff --staged` 或 `git diff`，了解具体修改了哪些内容  
2. **确定包前缀**：识别受影响的主要软件包（package）  
3. **向用户询问**：  
   - 如果尚未明确，请提供相关的 Issue 编号或 Epic 编号  
   - 是否需要发布说明（release notes），以及最适合的分类是什么  
4. **编写提交标题（subject line）**：使用祈使语气，不加句号，长度不超过 72 个字符  
5. **编写提交正文（body）**：说明变更前后的差异，以及为何需要此变更  
6. **添加 Issue 引用**：根据情况包含 `Resolves` 或 `Epic` 等引用信息  
7. **撰写发布说明（release note）**：以用户为中心，清晰描述本次变更带来的影响或改进  
8. **使用格式正确的提交信息创建提交（commit）**
9.

## 规范说明

使用 Conventional Commits 格式：

```bash
<emoji> <type>([optional scope]): <subject>

<body>
```

- `<emoji>` 是尽可能需要的，使用一个 emoji 来表示 commit 的类型，用来增加可读性和趣味性，可以参考 [Gitmoji](https://gitmoji.dev/)。

- `<type>`  是必须的，是关于本次提交类型的标签，也可以参考 [Gitmoji](https://gitmoji.dev/)。

- `<scope>`  用于说明 commit 影响的范围，可选

- `<subject>` 是必须的， commit 的简短描述，要求：
  - 义动词开头，使用第一人称现在时（change，而不是changed）
  - 第一个字母小写
  - 结尾不加句号(.)

- `<body>` 是对 commit 的详细描述，要求：
  - 使用第一人称现在时

## 类型参考

| commit 模板        | 说明                      | Explain                               |
| ---------------- | ----------------------- | ------------------------------------- |
| 🎉 initial:      | 新开项目，初次提交               | Start an adventure                    |
| ✨ feat:          | 引入新特性/功能                | Introduce new features                |
| 🍻 drunk:        | 醉写代码 <br/> 代码没写完        | Write code drunkenly                  |
| 🐛 fix:          | 修复bug                   | Fix a bug                             |
| 🚑️ hotfix:      | 重要补丁                    | Critical hotfix                       |
| 📦 chore:        | 构建过程或辅助工具的变动            | Other modifications                   |
| 🚚 chore:        | 移动或重命名文件                | move/rename file                      |
| 🎨 style:        | 代码格式修改                  | Format                                |
| 📝 docs:         | 修改文档                    | Add or update documentation           |
| 🛠 build:        | 影响项目构建或依赖项修改            |                                       |
| 🏗️ architect:   | 架构的变动                   | Make architectural changes            |
| 🚀 perf:         | 优化程序性能                  | Improve performance                   |
| 🔨 refactor:     | 代码重构                    | Refactor                              |
| 🔬 test:         | 测试用例新增、修改               | Add, update, or pass tests            |
| ⬆️ dependencies: | 更新依赖版本                  | Upgrade dependencies                  |
| ⬇️ dependencies: | 降低依赖版本                  | Downgrade dependencies                |
| 📌 dependencies: | 固定依赖版本                  | Pin dependencies to specific versions |
| ✅ release:       | 发布新版本                   |                                       |
| 🔄 workflow:     | 工作流相关文件修改               |                                       |
| 🔀 merge:        | 合并分支                    | Merge branches                        |
| ⏪️ revert:       | 恢复更改                    | Revert changes                        |
| ⏳ revert:        | 恢复上一次提交                 |                                       |
| 🔖 tag:          | 发布版本                    | Release / Version tags                |
| 🙈 gitignore:    | 添加或更新 `.gitignore`      | Add or update `.gitignore`           |
| 👷 ci/cd:        | 添加 CI 构建系统 / 修复 CI 构建问题 | Fix CI Build                          |
| 🔒 safety:       | 修复安全问题                  |                                       |
| 🐧 linux:        | 修复 Linux 下的问题           | Fix Linux issues                      |
| 🍎 macos:        | 修复 macOS 下的问题           | Fix macOS issues                      |
| 🍏 ios:          | 修复 iOS 下的问题             | Fix iOS issues                        |
| 🤖 android:      | 修复 Android 下的问题         | Fix Android issues                    |
| 🚨 lint:         | 移除 linter 警告            | Remove linter warnings                |
| 🚧               | 工作进行中                   | Working                               |
| 🐳 docker:       | Docker 相关工作             | Docker                                |
| 🌐 i18n:         | 国际化相关                   | Internationalization

## 示例

- ✨ feat(auth): 添加 OAuth 登录支持
- 🐛 fix(api): 修复用户查询返回空值的问题
- 📝 docs(readme): 更新安装说明
