# 桥↔记忆系统交互协议 — Bridge Memory Protocol

> 创建：2026-05-24 | v1.0 | 昆仑系统
> 协议编号：B
> 方向：桥层 → 记忆系统
> 时机：桥激活后、开始分析前
> 驻留位置：`eleven-bridges/bridge-memory-protocol.md`
> 合规：严格遵循 `eleven-bridges/NOMENCLATURE.md` 命名规范

---

# §1 概述

协议B定义了桥层向记忆系统请求知识的数据契约。当一座桥梁被昆仑天工OS激活后（协议A），必须在分析开始前通过本协议拉取下辖学科的完整工具集、积累共鸣、历史案例和失效条件。

**消费者：** 各桥的工具实现（OCGS建模、持久战判据、十六字诀等）
**供给方：** 记忆系统（MEMORY.md / memory-index.md / views/ / analysis/）
**触发者：** 昆仑天工OS的桥激活决策子流程

---

# §2 请求格式

## 2.1 请求参数

| 字段 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `bridgeId` | string | 是 | 桥编号，Q01~Q11 | "Q04" |
| `requestType` | string | 是 | 请求类型，详见2.2节 | "full" |
| `filters` | object | 否 | 过滤条件，详见2.3节 | — |

## 2.2 请求类型

| 类型 | 含义 | 返回内容 |
|---|---|---|
| `full` | 完整知识拉取 | 学科工具 + 积累共鸣 + 历史案例 + 失效条件 |
| `tools` | 仅拉取学科工具 | 下辖学科的列表+信度+核心用法 |
| `accumulation` | 仅拉取积累共鸣 | 该桥注册以来的积累产物列表 |
| `cases` | 仅拉取历史案例 | 桥层相关的案例分析清单 |
| `failure_conditions` | 仅拉取失效条件 | 该桥的已知失效条件列表 |

## 2.3 过滤条件（可选）

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `minConfidence` | string | 最低信度过滤 | "T2" |
| `onlyCore` | boolean | 是否仅取核心学科（非辅助） | true |
| `maxResults` | number | 最多返回条数 | 10 |
| `sinceDate` | string | 起始日期过滤 | "2026-05-01" |

## 2.4 完整请求示例

```yaml
{
  "bridgeId": "Q04",
  "requestType": "full",
  "filters": {
    "minConfidence": "T3",    // T3及以上
    "onlyCore": false,         // 包含辅助学科
    "maxResults": 20
  }
}
```

---

# §3 响应格式

## 3.1 响应结构

| 字段 | 类型 | 必含 | 说明 |
|---|---|---|---|
| `bridgeId` | string | 是 | 桥编号 |
| `bridgeConfidence` | string | 是 | 桥置信度（T1/T2/T3/—） |
| `bridgeStatus` | string | 是 | 桥状态（活跃/冻结/档案/缺口） |
| `disciplines` | array | 是 | 下辖学科列表，详见3.2节 |
| `accumulation` | array | 是 | 积累共鸣列表，详见3.3节 |
| `cases` | array | 是 | 历史案例列表，详见3.4节 |
| `failureConditions` | array | 是 | 失效条件列表，详见3.5节 |
| `crossDomainMaps` | array | 是 | 跨域映射列表，详见3.6节 |
| `entryLinks` | array | 是 | 所属知识条目链接，详见3.7节 |
| `queryTime` | string | 是 | 查询时间戳 |

## 3.2 学科工具列表（disciplines）

每条学科条目包含：

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `name` | string | 学科全称 | "系统科学·OCGS" |
| `confidence` | string | 信度等级 | "T1" |
| `role` | string | 主桥/辅桥 | "main" |
| `status` | string | 生命周期状态 | "active" |
| `coreTool` | string | 核心工具一句话 | "七步建模：边界→要素→回路→基模→杠杆→涌现" |
| `keyUsage` | string | 在桥内的主要用法 | "系统边界界定 + 回路拆解与基模匹配 + 涌现判定" |
| `lastCalled` | string | 最后调用日期 | "2026-05-24" |
| `callCount` | number | 实战验证次数 | 7 |

## 3.3 积累共鸣列表（accumulation）

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `name` | string | 共鸣产物名称 | "BCS三阶战略" |
| `confidence` | string | 信度 | "T2" |
| `sourceBridges` | string | 来源桥对 | "Q04×Q08" |
| `description` | string | 一句话说明 | "根据地→现金流→制高点的追赶模式" |
| `date` | string | 产生日期 | "2026-05-23" |

## 3.4 历史案例列表（cases）

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `title` | string | 案例名称 | "航发供应链韧性构建" |
| `path` | string | 保存路径 | "memory/analysis/2026-05-23_航发供应链韧性构建.md" |
| `date` | string | 分析日期 | "2026-05-23" |
| `activatedBridges` | string | 激活的桥 | "Q01, Q04, Q08" |

## 3.5 失效条件列表（failureConditions）

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `condition` | string | 失效条件描述 | "系统边界模糊到无法有效界定" |
| `severity` | string | 严重程度 | "critical" (完全失效) / "caution" (部分适用) |
| `verified` | boolean | 是否经实战验证 | true |
| `verifyCount` | number | 验证次数 | 3 |

## 3.6 跨域映射列表（crossDomainMaps）

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `mapId` | string | 映射编号 | "M-004" |
| `targetBridge` | string | 目标桥 | "Q02" |
| `sourceConcept` | string | 源概念 | "反馈回路" |
| `targetConcept` | string | 目标概念 | "制度自我强化/纠偏" |
| `confidence` | string | 映射信度 | "T2" |

## 3.7 所属条目链接（entryLinks）

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `file` | string | 文件路径 | "MEMORY.md" |
| `section` | string | 章节 | "§3.5" |
| `confidence` | string | 信度 | "T1" |
| `description` | string | 简述 | "OCGS开放复杂巨系统世界观" |

## 3.8 完整响应示例

```yaml
{
  "bridgeId": "Q04",
  "bridgeConfidence": "T1",
  "bridgeStatus": "active",
  "disciplines": [
    {
      "name": "系统科学·OCGS",
      "confidence": "T1",
      "role": "main",
      "status": "active",
      "coreTool": "七步建模：边界→要素→回路→基模→杠杆→涌现",
      "keyUsage": "系统边界界定 + 回路拆解与基模匹配 + 涌现判定",
      "lastCalled": "2026-05-24",
      "callCount": 7
    },
    {
      "name": "生态学·系统韧性",
      "confidence": "T3",
      "role": "auxiliary",
      "status": "active",
      "coreTool": "冲击分类·韧性三维度·故障模式诊断",
      "keyUsage": "OCGS建模每步嵌入韧性追问",
      "lastCalled": "2026-05-24",
      "callCount": 2
    }
  ],
  "accumulation": [],
  "cases": [
    {
      "title": "航发供应链韧性构建",
      "path": "memory/analysis/2026-05-23_航发供应链韧性构建.md",
      "date": "2026-05-23",
      "activatedBridges": "Q01, Q04, Q08"
    }
  ],
  "failureConditions": [
    {"condition": "系统边界模糊到无法有效界定", "severity": "critical", "verified": true, "verifyCount": 3},
    {"condition": "子系统数量过少（<3）导致涌现效应不产生", "severity": "critical", "verified": true, "verifyCount": 2},
    {"condition": "纯线性因果问题使用系统论冗余", "severity": "caution", "verified": true, "verifyCount": 1}
  ],
  "crossDomainMaps": [
    {"mapId": "M-004", "targetBridge": "Q02", "sourceConcept": "反馈回路", "targetConcept": "制度自我强化/纠偏", "confidence": "T2"}
  ],
  "entryLinks": [
    {"file": "MEMORY.md", "section": "§3.5", "confidence": "T1", "description": "OCGS开放复杂巨系统世界观"},
    {"file": "memory-index.md", "section": "系统科学", "confidence": "T1", "description": "系统科学索引条目"}
  ],
  "queryTime": "2026-05-24T11:23:00+08:00"
}
```

---

# §4 错误处理

| 错误场景 | 返回码 | 处理方式 |
|---|---|---|
| 桥编号不存在（非Q01~Q11） | `ERR_BRIDGE_NOT_FOUND` | OS层确认桥编号后重试 |
| 桥状态为档案🔴或缺口⚪ | `ERR_BRIDGE_INACTIVE` | OS层跳过此桥，P1递补 |
| 请求类型的学科在桥下为空 | `ERR_NO_DISCIPLINES` | 返回空列表，不报错（缺口桥场景） |
| 过滤条件导致结果为空 | `SUCCESS_EMPTY` | 返回成功+空列表（非错误） |
| 记忆系统请求超时 | `ERR_TIMEOUT` | OS层等待后重试，最多2次 |

---

# §5 调用时机

```
分析流程时序：
  ① 入口框架显化（矛盾论）
     → 输出：问题特征标签
  ② 桥激活决策（协议A）
     → 输出：激活桥列表
  ③ 协议B — 知识请求       ← 当前位置
     → 每座激活桥独立请求记忆系统
     → 可并行请求（桥间无依赖）
  ④ 各桥学科工具就绪
     → 进入昆仑枢机后续工序（十六字诀→OCGS建模→...）
```

---

# §6 与其他协议的关系

| 协议 | 关系 | 说明 |
|---|---|---|
| **协议A（桥激活决策）** | 协议B的前置条件 | 必须先通过协议A激活桥，才能发起协议B |
| **协议C（反馈分发）** | 协议B的后置反向 | 协议B是分析前的"拉取"，协议C是分析后的"推送" |
| **桥间共振** | 协议B之后 | 协议B提供学科工具→工具在分析中被使用→桥间共振产生 |

---

# §7 扩展规则

1. **并行请求：** 在多座桥同时激活时，协议B请求可并行发出（各桥之间无数据依赖）
2. **缓存策略：** 同一次分析中，如果同一座桥被两次请求（先full再tools），不重复查询
3. **信度传播：** 桥响应中标注的学科信度决定该知识在推理中的使用纪律
