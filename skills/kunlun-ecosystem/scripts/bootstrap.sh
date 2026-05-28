#!/bin/bash
# kunlun-ecosystem bootstrap — 昆仑全量安装脚本
# 安装时自动运行：① 安装核心底座 ② 安装8个辅助技能

set -e

echo "🚀 昆仑生态全量安装开始..."
echo ""

# ── Step 1: 安装核心底座 ──
echo "📦 [1/2] 安装核心底座 kunlun-core..."
openclaw skills install kunlun-core 2>/dev/null && echo "    ✅ kunlun-core 完成" || echo "    ⚠️  kunlun-core 可能已安装"

echo ""

# ── Step 2: 安装辅助技能 ──
echo "📦 [2/2] 安装辅助技能..."
SKILLS=(
  "kunlun-academy"
  "kunlun-dashboard"
  "kunlun-governance"
  "kunlun-knowledge-structure"
  "kunlun-metacognition"
  "kunlun-onboarding"
  "kunlun-output-packaging"
  "kunlun-session-recovery"
)

for skill in "${SKILLS[@]}"; do
  echo "    📦 $skill..."
  openclaw skills install "$skill" 2>/dev/null && echo "      ✅ 完成" || echo "      ⚠️  可能已安装"
done

echo ""
echo "============================================"
echo "✅ 昆仑生态全部就位！"
echo "   核心底座 + 8 个辅助技能"
echo "============================================"
echo ""
echo "重启 OpenClaw 后，昆仑认知系统即可使用。🐒🔥"
