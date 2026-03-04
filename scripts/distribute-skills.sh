#!/bin/bash

# scripts/distribute-skills.sh
# 这个脚本是为了将 skills 目录下的技能分发到 `.agents/skills` 目录下，供 agent 使用。
# 1. 遍历 skills 目录下的所有技能，skills 目录满足包含 `SKILL.md` 文件
if [[ -n "${ZSH_VERSION:-}" ]]; then
	emulate -L bash
	setopt KSH_ARRAYS
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 目标目录，如果是其他框架，可以将这个路径改为对应框架的技能目录
TARGET_DIR="$ROOT_DIR/.agents/skills"

SOURCE_SKILLS_DIR="$ROOT_DIR/skills"

if [[ -e "$TARGET_DIR" && ! -d "$TARGET_DIR" ]]; then
	echo "目标路径已存在且不是目录: $TARGET_DIR"
	exit 1
fi

mkdir -p "$TARGET_DIR"

SKILL_NAMES=()
SKILL_DIRS=()

has_skill_name() {
	local name="$1"
	local existing
	for existing in "${SKILL_NAMES[@]:-}"; do
		if [[ "$existing" == "$name" ]]; then
			return 0
		fi
	done
	return 1
}

add_skill_if_absent() {
	local name="$1"
	local dir="$2"
	if ! has_skill_name "$name"; then
		SKILL_NAMES+=("$name")
		SKILL_DIRS+=("$dir")
	fi
}

# 优先扫描 skills/ 目录（如果存在）
if [[ -d "$SOURCE_SKILLS_DIR" ]]; then
	while IFS= read -r -d '' skill_md; do
		skill_dir="$(dirname "$skill_md")"
		skill_name="$(basename "$skill_dir")"
		add_skill_if_absent "$skill_name" "$skill_dir"
	done < <(find "$SOURCE_SKILLS_DIR" -mindepth 2 -maxdepth 2 -type f -name "SKILL.md" -print0)
fi

# 兼容当前仓库结构：根目录直接放技能目录
while IFS= read -r -d '' skill_md; do
	skill_dir="$(dirname "$skill_md")"
	skill_name="$(basename "$skill_dir")"

	case "$skill_name" in
		.git|.github|.agents|scripts)
			continue
			;;
	esac

	# 如果同名技能已在 skills/ 中发现，则保留 skills/ 版本
	add_skill_if_absent "$skill_name" "$skill_dir"
done < <(find "$ROOT_DIR" -mindepth 2 -maxdepth 2 -type f -name "SKILL.md" \
	-not -path "$TARGET_DIR/*" -print0)

if [[ ${#SKILL_NAMES[@]} -eq 0 ]]; then
	echo "未发现任何技能目录（需要包含 SKILL.md）"
	exit 0
fi

linked_count=0
skipped_count=0
conflict_count=0

for ((i=0; i<${#SKILL_NAMES[@]}; i++)); do
	skill_name="${SKILL_NAMES[$i]}"
	source_dir="${SKILL_DIRS[$i]}"
	link_path="$TARGET_DIR/$skill_name"

	if [[ "$source_dir" == "$ROOT_DIR/skills/"* ]]; then
		rel_target="../../skills/$skill_name"
	else
		rel_target="../../$skill_name"
	fi

	if [[ -L "$link_path" ]]; then
		current_target="$(readlink "$link_path")"
		if [[ "$current_target" == "$rel_target" ]]; then
			echo "已存在，跳过: $skill_name -> $rel_target"
			skipped_count=$((skipped_count + 1))
			continue
		fi
	fi

	if [[ -e "$link_path" && ! -L "$link_path" ]]; then
		echo "已存在同名非软链接，跳过: $link_path"
		conflict_count=$((conflict_count + 1))
		continue
	fi

	ln -sfn "$rel_target" "$link_path"
	echo "已分发: $skill_name -> $rel_target"
	linked_count=$((linked_count + 1))
done

echo "分发完成，新建/更新 $linked_count 个，跳过重复 $skipped_count 个，冲突 $conflict_count 个"
