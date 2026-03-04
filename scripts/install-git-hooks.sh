#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f ".githooks/pre-commit" ] || [ ! -f ".githooks/pre-push" ]; then
    echo "未找到 .githooks/pre-commit 或 .githooks/pre-push"
    exit 1
fi

chmod +x .githooks/pre-commit
chmod +x .githooks/pre-push
git config core.hooksPath .githooks

echo "Git hooks 已安装。"
echo "当前 hooksPath: $(git config --get core.hooksPath)"
