---
name: kunlun-output-packaging
status: active
version: 2.2.0
description: Standardized end-of-analysis delivery checklist to prevent version drift and ensure complete knowledge capture. Kunlun ecosystem skill.
---

> **昆仑生态技能** — 分发名：`kunlun-output-packaging` | 版本：v2.1.1
> 与 `kunlun-dashboard`（仪表盘快照）和 `kunlun-knowledge-structure`（insight card入库）衔接。

# Output Packaging Checklist

> **v2.2.0 更新（2026-05-28）：同步 Q-Bridge v1.0 — 协议A→凤口路由卡、协议C→凤口输出协议、eleven-bridges→knowledge-tree
> **v2.0 更新（2026-05-26）：**
> - **SOUL.md 共振腔架构 v3.0** → 本检查清单对齐认知知识图+三视图投影
> - 更新对齐认知知识图+三视图投影
> - 解冻（frozen→active），成为认知知识图三视图出口的可选补充工具

## The Core Problem

After a deep analysis, there are typically 4-7 files that need synchronized updates. Manual tracking has a reliability ceiling. This checklist eliminates that.

## Mandatory Checklist (Run Every Time)

### Step 0: 输出准备的预处理

- [ ] 分析视图的结构已构建完成？含OCGS Core回路、域适应三棱镜、免疫系统证伪、蒸馏塔抽象、窗口赛跑记录、认知盲点
- [ ] 是否需要格式渲染（对外呈现）？
  - 需要 → 产出类型自判+格式渲染+交付（默认自动执行）
  - 不需要 → 直接以MD交付

### Step 0: Knowledge Source Integrity Check

- [ ] 本次分析的推理依据是否全部标注了信度等级？
  - 如果发现未标注 → 补标 `[T1]/[T2]/[T3]`
  - 如果发现使用了T3知识作为推理依据 → 声明"此段判断未经思想库验证"
- [ ] 本次分析产出的新知识 → 标注[T3 待验证]
  - 如果是验证了已有的T3知识 → 标记升T2候选

### ③学科响应网络激活声明（v2.1 取代原Bridge Activation Statement）

> 在产出封装前，记录本次分析的桥激活状态——这是凤口(桥路由)→龙门(挂桥入库)的必填环节。

- [ ] 桥激活声明已填写 → 存入分析报告 §2 桥层声明
  - P0（皇帝）：[桥编号] — 得分+理由
  - P0（宰相）：[桥编号] — 得分+理由（可选）
  - P1（顾问）：[桥编号] — 得分+理由（可选）
  - 跨域映射触发：[M-xxx, M-yyy]（凤口桥共振自动扫描）
  - Gap桥呼唤：[桥编号] → 呼唤计数+[N]（当前总计=[]）
  - 桥间冲突仲裁：[桥组合] → Layer 1/2/3判断

### Cognitive Blind Spot (New Mandatory Step)

> 在完成分析框架和结论后、填写交付清单前，先花30秒记录本次分析的认知盲区。

- [ ] 认知盲点已填写 → 存入分析报告 §9
  - 信息缺失（什么关键数据没拿到）
  - 视角缺失（什么重要视角被忽略）
  - 被迫假设（因证据不足而做的假设）
  - 免疫系统条件标记缺失（哪些结论缺少证伪验证，原因是什么）

### Primary Deliverables

- [ ] Summary — 5-line condensed version output in the chat for immediate consumption
- [ ] **发布审计卡**（如果本次产出涉及版本发布）— 使用 `memory/change-reports/YYYY-MM-DD_release-vX.Y.Z.md` 模板
  - 包含：变更摘要、版本变化、预检结果、安全修复清单、已知限制、回退方案
  - 自动触发：`release-preflight.sh --ci` 预检 + `release-checklist.md` 手工确认
  - 审计卡作为发布流程的最终输出物（§9.2 [5]），写入 `memory/change-reports/`
- [ ] Analysis report — Archived to memory/analysis/ using TEMPLATE.md format
  - Include: problem framework, OCGS structures, circuits, base patterns, BCS stage determination
- [ ] Insight cards — Written to memory-index.md with proper section tagging
  - Each insight now includes **信度等级** field (T1/T2/T3/T4)
  - Use **规范引用别名** in the "对应memory-index条目" column of the insight card table
  - ⚡ Auto-run: `python3 memory/maintain_counters.py count` — reads the latest report's insight card table, matches aliases, updates counts

### Knowledge Trust & Cards

- [ ] New knowledge entry → determine trust level:
  - T3 (learning): write to memory-index.md → optionally create study-card if new discipline
  - T2 (verified): write to memory-index.md → create axiom-card or case-card
  - T1 (axiom): write to MEMORY.md → update axiom-cards-index.md
- [ ] If new discipline involved → create study card in `memory/views/study-cards-index.md`
- [ ] If T2+ knowledge → update axiom-cards-index.md or case-library-index.md
- [ ] Cross-domain validation — When this is the second+ analysis in a family, compare structures

### Ecosystem Synchronization

- [ ] **Eco health check** — Run `python3 kunlun-dist/scripts/ecosync-check.py` to detect version drift
  - If '❌ 有差异': decide whether sync is needed → run `ecosync-sync.sh`
  - If drift is intentional (e.g. deployed ahead of dist): update SKILLS-VERSION.md
- [ ] VERSION.md — Updated with new version number and change summary
- [ ] MEMORY.md — Status section synchronized (completed/in-progress/blocked/todo)
- [ ] Daily log — New cognitive event entry added to memory/YYYY-MM-DD.md
- [ ] **凤口输出回喂** — 分析闭环后回喂分流：
  - 跨桥交叉产物 → 桥积累库（`knowledge-tree/bridge-memory-integration.md` 通道D）
  - 可复用法则/命题 → 记忆系统（MEMORY.md + memory-index.md）
  - 单系统内条目碰撞 → 共鸣网络（`resonance-net.md` RP#编号）
  - 缺口桥标记 → 呼唤次数+1（如有）
- [ ] **Bridge state update** — 本次激活的桥 {Qxx, Qyy} 各强度+1，最后激活时间更新
- [ ] Anti-fragility pool — New strong counter-examples added to anti-fragility-pool.md
- [ ] Dashboard snapshot — Run `python3 generate_dashboard.py` to regenerate dashboard.html with latest state

  > ⚠️ The VERSION.md must be updated **before** regenerating the dashboard — the dashboard reads the version number from VERSION.md's `当前版本：` field.

### Optional (by need)

- [ ] **格式渲染** → 通过内容产线路由表调度（xiaoyi-report / xiaoyi-ppt / xiaoyi-xlsx / xiaoyi-pdf），不走独立格式路由
- [ ] Skill knowledge sync (if analysis affected any kunlun-dist skill contents)

## Typical Execution Order

```
Knowledge Source Integrity Check
  学科响应网络激活声明（v2.1）— 特征向量匹配度+自激活学科列表+跨域映射
  Summary (chat)
  Report archive
  Insight cards + trust level + anti-fragility pool
  Cards (study-card / axiom-card / case-card)
  凤口输出回喂 — 分流桥积累/记忆系统/共鸣网络
  Bridge state update — 强度+1 / 缺口呼唤+1
  Cross-domain validation
  Version + MEMORY + daily log
  Dashboard snapshot
```

## References

- `kunlun-pivot-essentials.md` — 昆仑枢要（完整指南）
- `memory/views/axiom-cards-index.md` — 公理卡视图
- `memory/views/study-cards-index.md` — 学习卡视图
- `memory/views/case-library-index.md` — 案例库视图
- `references/TEMPLATE.md` — The canonical analysis report template

### Step 6: 质量回映（认知知识图三视图投影后强制）

- [ ] 执行回映三问
  - [ ] Q1: 回映指数（1-5分）— 回答最初问题了吗？
  - [ ] Q2: 薄弱自识别 — 最弱环节是什么？
  - [ ] Q3: 工序跳过声明 — 跳过了哪步？原因？
- [ ] 自评置信度判定
  - [ ] 高 → 独立交付
  - [ ] 中 → 标记“建议乾坤抽检”
  - [ ] 低 → 强制召唤乾坤复核
- [ ] 质量回映区块写入分析报告末尾
- [ ] 回映指数计入 learning-progress.md（月度趋势追踪）
