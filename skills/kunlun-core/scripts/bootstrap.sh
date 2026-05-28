#!/bin/bash
# kunlun-core bootstrap — 昆仑认知系统核心注入脚本
# 安装时自动运行，将昆仑核心组件写入工作区

set -e

ROOT="${OPENCLAW_WORKSPACE:-/home/sandbox/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 昆仑核心注入开始..."

# ── 1. SOUL.md ──
if [ ! -f "$ROOT/SOUL.md" ]; then
    echo "  📄 写入 SOUL.md..."
    cp "$SKILL_DIR/scripts/templates/SOUL.md" "$ROOT/SOUL.md"
else
    echo "  ⚠️  SOUL.md 已存在，跳过"
fi

# ── 2. IDENTITY.md ──
if [ ! -f "$ROOT/IDENTITY.md" ]; then
    echo "  📄 写入 IDENTITY.md..."
    cp "$SKILL_DIR/scripts/templates/IDENTITY.md" "$ROOT/IDENTITY.md"
else
    echo "  ⚠️  IDENTITY.md 已存在，跳过"
fi

# ── 3. contract.md ──
if [ ! -f "$ROOT/contract.md" ]; then
    echo "  📄 写入 contract.md..."
    cp "$SKILL_DIR/scripts/templates/contract.md" "$ROOT/contract.md"
else
    echo "  ⚠️  contract.md 已存在，跳过"
fi

# ── 4. VERSION.md ──
if [ ! -f "$ROOT/VERSION.md" ]; then
    echo "  📄 写入 VERSION.md..."
    cp "$SKILL_DIR/scripts/templates/VERSION.md" "$ROOT/VERSION.md"
else
    echo "  ⚠️  VERSION.md 已存在，跳过"
fi

# ── 5. eleven-bridges/ ──
if [ ! -d "$ROOT/eleven-bridges" ]; then
    echo "  📁 创建 eleven-bridges/..."
    mkdir -p "$ROOT/eleven-bridges"
    cp "$SKILL_DIR/scripts/bridge-templates/registry.md" "$ROOT/eleven-bridges/registry.md"
    cp "$SKILL_DIR/scripts/bridge-templates/NOMENCLATURE.md" "$ROOT/eleven-bridges/NOMENCLATURE.md"
    cp "$SKILL_DIR/scripts/bridge-templates/lifecycle-protocol.md" "$ROOT/eleven-bridges/lifecycle-protocol.md"
    cp "$SKILL_DIR/scripts/bridge-templates/bridge-memory-protocol.md" "$ROOT/eleven-bridges/bridge-memory-protocol.md"
else
    echo "  ⚠️  eleven-bridges/ 已存在，跳过"
fi

# ── 6. memory/ scaffold ──
mkdir -p "$ROOT/memory/analysis"
mkdir -p "$ROOT/memory/views"

for f in MEMORY.md memory-index.md resonance-net.md anti-fragility-pool.md failure-log.md metacognitive-protocol.md; do
    if [ ! -f "$ROOT/memory/$f" ]; then
        echo "  📄 写入 memory/$f..."
        cp "$SKILL_DIR/scripts/templates/$f" "$ROOT/memory/$f"
    else
        echo "  ⚠️  memory/$f 已存在，跳过"
    fi
done

# memory/views/ index files
for f in axiom-cards-index.md study-cards-index.md bridge-cards-index.md case-library-index.md; do
    if [ ! -f "$ROOT/memory/views/$f" ]; then
        echo "  📄 写入 memory/views/$f..."
        cp "$SKILL_DIR/scripts/templates/$f" "$ROOT/memory/views/$f"
    else
        echo "  ⚠️  memory/views/$f 已存在，跳过"
    fi
done

# ── 7. TOOLS.md 追加昆仑规则 ──
TOOLS_MARKER="# 昆仑认知系统规则（kunlun-core 自动注入）"
if [ -f "$ROOT/TOOLS.md" ]; then
    if ! grep -q "$TOOLS_MARKER" "$ROOT/TOOLS.md"; then
        echo "  📄 向 TOOLS.md 追加昆仑规则..."
        cat "$SKILL_DIR/scripts/templates/TOOLS-append.md" >> "$ROOT/TOOLS.md"
    else
        echo "  ⚠️  TOOLS.md 已有昆仑规则，跳过"
    fi
else
    echo "  📄 创建 TOOLS.md（含昆仑规则）..."
    cat "$SKILL_DIR/scripts/templates/TOOLS-append.md" > "$ROOT/TOOLS.md"
fi

echo ""
echo "✅ 昆仑核心注入完成！"
echo ""
echo "下一步："
echo "  1. 如需安装辅助工具（仪表盘/学习管理/治理等），请逐个安装："
echo "     openclaw skills install kunlun-academy"
echo "  2. 重启会话后，你的Agent将自动加载昆仑认知系统。"
echo ""
echo "  愿大成智慧学与你同在。🐒🔥"
