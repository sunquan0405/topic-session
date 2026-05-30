#!/bin/bash
# topic-session 安装脚本
# 1. 创建话题目录
# 2. 安装 topic-select 到 PATH

set -e

TOPIC_DIR="${TOPIC_DIR:-$HOME/.topic-session/topics}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Topic Session Install ==="

# Create topic directory
mkdir -p "$TOPIC_DIR"
echo "✓ Topic directory: $TOPIC_DIR"

# Install topic-select script
if [[ ":$PATH:" == *":$HOME/bin:"* ]]; then
    INSTALL_DIR="$HOME/bin"
elif [[ ":$PATH:" == *":/usr/local/bin:"* ]]; then
    INSTALL_DIR="/usr/local/bin"
else
    INSTALL_DIR="$HOME/bin"
    mkdir -p "$INSTALL_DIR"
    echo "⚠ Add to your shell config: export PATH=\"\$HOME/bin:\$PATH\""
fi

SCRIPT_SRC="$SCRIPT_DIR/scripts/topic-select.py"
SCRIPT_DST="$INSTALL_DIR/topics"

cp "$SCRIPT_SRC" "$SCRIPT_DST"
chmod +x "$SCRIPT_DST"
echo "✓ Script installed: $SCRIPT_DST"

echo ""
echo "=== Done ==="
echo "Usage in chat:  --topic 话题名"
echo "Terminal:       topics"
echo "List topics:    topics --list"
