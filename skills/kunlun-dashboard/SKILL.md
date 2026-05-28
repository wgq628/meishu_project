---
name: kunlun-dashboard
status: active
description: |
  昆仑·全视 系统可观测性仪表盘生成器 2.6。
  
  从昆仑系统核心数据文件 + 系统运行时数据，生成7+1 Tab静态HTML仪表盘：
  🏠 总览 | 🔌 端口 | 🤖 Agent | ⏰ 定时任务 | 🛠 技能 | 🔗 流水线 | 💰 Token | 🐒 昆仑

  2.7 更新（2026-05-28）：同步 Q-Bridge v1.0 — 新增knowledge-tree覆盖度仪表盘Tab

  适用场景：
  - 每次深度分析闭环后自动生成系统快照
  - 用户主动询问"系统状态"、"仪表盘"、"知识库概览"时
  - 版本升级后验证状态同步

  触发方式：
  - 用户说"查看仪表盘"、"系统状态"、"知识库概览"、"昆仑状态"
  - 分析闭环后按 kunlun-output-packaging 自动触发

  关键触发词：
  - 通用：仪表盘、dashboard、状态、系统状态、知识库
  - 昆仑场景：昆仑状态、昆仑仪表盘、昆仑系统、昆仑·全视
  - 数据展示：知识条目、谐波、反脆弱池、报告索引

  限制条件：
  本技能是为昆仑系统设计的专用仪表盘，依赖昆仑规范的数据文件结构。
  如果在没有遵循昆仑规范的Agent workspace下运行，会因为缺少必要数据文件而报错。
  如需在其他系统使用，请先确保建立了类似的认知系统数据结构。
version: 2.6.0
allowed-tools: Read, Bash, Write, Exec
---

# kunlun-dashboard — 昆仑·全视 系统可观测性仪表盘

## 概述

昆仑·全视仪表盘将昆仑认知数据（知识条目/谐波/报告/反脆弱池）+ 系统运行时数据（端口/Agent/Cron/技能/流水线/Token）可视化为一个单文件7+1 Tab HTML页面。

**2.5 更新（2026-05-25）：**
- 完整重写为7+1 Tab架构（总览/端口/Agent/定时任务/技能/流水线/Token/昆仑）
- 新增系统运行时数据采集（端口扫描、Agent完整性、Cron状态、技能目录遍历、Token消耗）
- 昆仑页集成知识分类统计、谐波全表、反脆弱池、分析报告索引
- Chart.js图表：谐波强度柱状图 + 版本发布时间线
- 所有系统数据纯本地采集，无外部依赖

## 使用方法

```bash
python3 skills/kunlun-dashboard/scripts/generate_dashboard.py
```

输出文件位于当前workspace根目录的 `dashboard.html`。

### 嵌入 workflow（推荐）

在 `skills/kunlun-output-packaging/SKILL.md` 的「System Synchronization」中已有预置步骤。如果目标Agent没有这个skill，建议在分析闭环流程中新增一步：

```
- [ ] Dashboard snapshot — Run `python3 skills/kunlun-dashboard/scripts/generate_dashboard.py`
  ⚠️ 必须先更新 VERSION.md 再生成，否则版本号会滞后
```

## 数据源

### 昆仑认知数据（文件解析）

| 数据源 | 路径 | 用途 |
|---|---|---|
| 知识条目 | `memory-index.md` | 79条条目状态统计+信度分布 |
| 谐波 | `resonance-net.md` | 12条谐波强度和状态 |
| 版本历史 | `VERSION.md` | 版本号（v4.1.1）和时间线 |
| 分析报告 | `memory/analysis/index.md` | 7份报告索引 |
| 反脆弱挑战 | `anti-fragility-pool.md` | 10个挑战+议题状态 |

### 系统运行时数据（自动采集）

| 数据源 | 采集方式 | 用途 |
|---|---|---|
| 端口 | `ss -tlnp` | 系统监听端口+程序+PID |
| Agent | `$OPENCLAW_WORKSPACE` 目录遍历 | Agent SOUL/身份/MEMORY完整性 |
| 定时任务 | `openclaw cron list --json` | Cron调度+结果+投递方式 |
| 技能 | 4个目录遍历 | 技能版本+状态+分类 |
| 流水线 | trajectory `prompt.submitted` | 最近5个会话的提示词摘要 |
| Token | trajectory `model.completed.usage` | 近10个trajectory的Token消耗 |

## 7+1 Tab 说明

| Tab | 内容 | 数据来源 |
|---|---|---|
| 🏠 **总览** | 7张摘要卡（全部模块健康速览） | 聚合所有数据源 |
| 🔌 **端口** | 端口/程序/PID/运行状态 | `ss -tlnp` |
| 🤖 **Agent** | SOUL完整性/身份/记忆/最后活跃 | agents目录 |
| ⏰ **定时任务** | 名称/调度/状态/上下次运行/投递 | cron list --json |
| 🛠 **技能** | 154个技能分类展示+版本+描述 | 4个技能目录 |
| 🔗 **流水线** | 近5个trajectory的提示词摘要+usage | trajectory |
| 💰 **Token** | 总消耗/输入输出/模型拆分/估算费用 | trajectory usage |
| 🐒 **昆仑** | 知识统计/谐波全表/反脆弱池/报告 | 昆仑6个文件 |

## 已知限制

- Chart.js 图表依赖 CDN（`cdn.jsdelivr.net`），无网络时图表不渲染但表格数据仍然可读
- 端口采集在无 `ss` 权限的容器环境中返回空列表
- Token消耗基于trajectory文件中的 `model.completed.usage`，仅记录近10个文件
- 仅支持昆仑系统规范的数据文件结构，非昆仑系统会数据缺失
