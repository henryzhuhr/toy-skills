# toy-skills

## 新增 SKILLS

为了适配不同的 agent 框架，在 `.agents/skills` 保存实际文件，其他框架可以通过下面命令进行软链接：

```bash
dir=".github"
mkdir -p $dir && ln -s ../.agents/skills $dir/skills
```
