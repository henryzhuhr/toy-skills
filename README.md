# toy-skills

## 新增 SKILLS

直接在目录下新增，然后软链接到 `.agents/skills`：

```bash
SKILL_NAME=<your-skill-name>
SKILL_NAME=git-commit-helper
cd .agents/skills && ln -s ../../$SKILL_NAME . &&cd ../../
```

## 添加到自己的仓库

```bash
git clone git@github.com:henryzhuhr/toy-skills.git .agents/skills
```
