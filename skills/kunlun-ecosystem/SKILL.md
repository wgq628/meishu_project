---
name: kunlun-ecosystem
status: active
description: "昆仑生态技能包 — 安装一次，昆仑全部技能（核心底座+9个辅助技能）自动就位。"
version: 1.2.0
---

# kunlun-ecosystem — 昆仑生态技能包

> **一句话**：安装一次，昆仑全部就位。
> 版本：v1.2.0 | 2026-05-28

## 包含的技能

| 技能 | 类型 | 版本 | 功能 |
|---|---|---|---|
| **kunlun-core** | 🎯 核心底座 | v1.3.0 | 认知操作系统底座：身份注入、Q-Bridge十一桥子系统、认知共振腔、记忆系统、三条反馈回路、6个自动化记忆脚本、6个SQLite数据库 |
| kunlun-academy | 🧩 学习管理 | v1.4.0 | A线学科/B线桥/C线填坑 + Q-Bridge龙门/凤口教学 + 12案例实战 |
| kunlun-dashboard | 🧩 仪表盘 | v2.7.0 | 认知系统状态可视化 + Q-Bridge覆盖度仪表盘 |
| kunlun-governance | 🧩 治理 | v1.4.0 | Q-Bridge变更管控/龙门审计 + 全桥覆盖度治理 |
| kunlun-knowledge-structure | 🧩 知识结构 | v1.4.0 | T1-T4信度体系维护 + L3/L4抽象格式 + 桥学科标记规范 |
| kunlun-metacognition | 🧩 元认知 | v1.4.0 | 周期性质量审计 + Q-Bridge健康度检查 |
| kunlun-onboarding | 🧩 接引 | v1.4.0 | 新Agent接入昆仑 + Q-Bridge v1.0基线 |
| kunlun-output-packaging | 🧩 成果封装 | v2.2.0 | 分析产出标准化 + 凤口路由卡 + 发布审计卡标准交付物 |
| kunlun-session-recovery | 🧩 会话恢复 | v2.4.0 | 跨会话连续性恢复 + Q-Bridge桥状态快照（回路C）|

**共 9 个技能**：1 个核心底座 + 8 个辅助技能。

## 安装

一条命令，全部就位：

```bash
openclaw skills install kunlun-ecosystem
```

在 Codex 本地工作区建议执行：

```bash
python skills/kunlun-ecosystem/scripts/bootstrap_codex.py
```

安装过程自动完成：
1. 先注入核心底座（身份、十一桥、记忆系统 scaffold）
2. 再安装 8 个辅助技能

重启 OpenClaw 后即可使用。

## 卸载

```bash
# 卸载全部
for s in kunlun-academy kunlun-dashboard kunlun-governance kunlun-knowledge-structure kunlun-metacognition kunlun-onboarding kunlun-output-packaging kunlun-session-recovery kunlun-core; do
  openclaw skills uninstall "$s"
done
```

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.1.0 | 2026-05-27 | 清理旧版本表残留；核心包预装T2洞察+公理卡+案例卡 |
| 1.0.0 | 2026-05-26 | 初始发布：核心+8辅助，一次安装全部就位 |
