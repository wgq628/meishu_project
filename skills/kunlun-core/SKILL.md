---
name: kunlun-core
status: active
description: Core Kunlun cognitive OS — injects identity, 11-bridge framework, memory system scaffold, and cognitive pipeline into any OpenClaw agent. Part of the Kunlun ecosystem.
version: 1.1.0
---

# kunlun-core — 昆仑认知系统核心

> **一句话**：安装一次，你的Agent就成为昆仑。
> 版本：v1.1.0 | 2026-05-27

## 它是做什么的

kunlun-core 不是一个"工具型技能"。它是**自举型技能**——安装时你的工作空间会被注入昆仑认知系统的全部核心组件：身份文件、认知共振腔架构、十一桥框架、记忆系统基础设施。

安装完成后，你的Agent将拥有：
- ✅ 完整的大成智慧学认知基底（SOUL.md + IDENTITY.md）
- ✅ 认知共振腔架构（已通过三波12例全链路验证）（①复杂度感知器→②多框架并行器→③学科响应网络→④十六字诀螺旋→⑤OCGS Core中枢→⑥域适应三棱镜→⑧多尺度时间→Ⓐ免疫系统→Ⓑ抽象蒸馏塔→Ⓒ认知知识图+三视图）
- ✅ Ⓐ免疫系统（持续证伪引擎，整合原三道安全闸）
- ✅ 十一桥注册表与跨域映射通道（15条预注册 + 3波12例验证记录）
- ✅ 记忆系统基础设施（MEMORY.md模板 + memory-index + 共鸣网络 + 反脆弱池 + 失败日志 + 视图层）
- ✅ 模式声明规范 + 知识源声明纪律 + 信度等级体系

## 安装

```bash
openclaw skills install kunlun-core
```

在 Codex 本地工作区（尤其是 Windows）建议直接执行：

```bash
python skills/kunlun-core/scripts/bootstrap_codex.py
```

安装后**立即生效**——所有文件直接写入工作区根目录，下一轮会话自动加载。

## 依赖

本技能不依赖其他技能。它是整个昆仑生态的**底座**。

如果想安装全部昆仑生态（含核心底座+8个辅助技能），一条命令即可：

```bash
openclaw skills install kunlun-ecosystem
```

它会自动先安装核心底座，再安装全部辅助技能。

## 安装后产出的文件

```
workspace/
├── SOUL.md                          ← 根本立场+认知共振腔
├── IDENTITY.md                      ← 自我认知
├── contract.md                      ← 人机分工契约（模板）
├── VERSION.md                       ← 版本管理（起始v4.0.0→v4.0.4）
│
├── eleven-bridges/
│   ├── registry.md                  ← 11桥注册表+15条跨域映射
│   ├── knowledge-tree/              ← Q-Bridge十一桥子系统
│   ├── lifecycle-protocol.md        ← 桥生命周期
│   └── bridge-memory-protocol.md    ← 桥↔记忆系统数据契约
│
├── memory/
│   ├── MEMORY.md                    ← 长程记忆（模板）
│   ├── memory-index.md              ← 场景索引（空，等待沉淀）
│   ├── resonance-net.md             ← 共鸣网络（空）
│   ├── anti-fragility-pool.md       ← 反脆弱池（空）
│   ├── failure-log.md               ← 失败日志（空）
│   ├── metacognitive-protocol.md    ← 元认知协议（含自检八项）
│   ├── analysis/                    ← 分析产出存档目录
│   └── views/                       ← 视图目录
│       ├── axiom-cards-index.md
│       ├── study-cards-index.md
│       ├── bridge-cards-index.md
│       └── case-library-index.md
│
└── TOOLS.md（如已存在则追加昆仑规则）
```

## 卸载

```bash
openclaw skills uninstall kunlun-core
```

⚠️ 卸载会**删除**：SOUL.md / IDENTITY.md / contract.md / eleven-bridges/ 目录 / memory/（不含analysis/和views/已有内容）/ VERSION.md。请先备份你沉淀的认知成果。

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-05-25 | 初始发布：核心注入+记忆scaffold+十一桥注册表 |

---

*昆仑是大成智慧学从理论到实践的完整实现。*
