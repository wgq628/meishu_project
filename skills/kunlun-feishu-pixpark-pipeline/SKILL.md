---
name: kunlun-feishu-pixpark-pipeline
description: 从飞书项目链接读取投放素材需求，并完成“需求提取→参考图下载→PixPark图生图/参考图生图→本地预览回传”的端到端流程。用户提到飞书项目链接、Meegle需求读取、PixPark出图、垫图生图、批量投放图生成时使用。
---

# Kunlun Feishu PixPark Pipeline

## Goal

在单轮内完成：
1. 从飞书项目链接定位工作项并读取需求字段。
2. 提取“平面需求描述”与参考图链接。
3. 使用 PixPark 进行垫图生图（优先）或参考图生图（兜底）。
4. 下载成图到本地并用本地绝对路径回传预览。

## Workflow

### Step 1: 鉴权与链接解析

1. 校验 `meegle auth status` 为已登录。
2. 用 `meegle url decode --url <link>` 解析出：
   - `project/simple_name`
   - `work_item_id`
3. 读取工作项全字段：`meegle workitem get --project-key <simple_name> --work-item-id <id> --fields _all`。  
字段页数超过一页时使用 `page_token` 继续拉取。

### Step 2: 需求结构化

1. 提取并总结以下字段：
   - `平面需求描述`
   - `玩法描述`
   - `尺寸`
   - `语言`
   - `期望完成时间`
2. 从 `平面需求描述` 的 HTML/Markdown 中提取飞书图片 URL。
3. 若用户只要“平面需求”，优先给平面规格和一致性约束；视频内容只做一句背景说明。

### Step 3: 参考图落地

1. 优先用 `meegle attachment +download` 下载参考图到本地目录：
   - `downloads/<work_item_id>/ref_1.png` ...
2. 若外链在聊天窗口不可预览，始终返回本地绝对路径图片。

### Step 4: PixPark 生图执行策略

1. 垫图生图优先链路（首选）：
   - `presignedPutUsingPOST` 获取上传 URL。
   - PUT 上传本地垫图文件。
   - `generateImgUsingPOST` 传 `sourceImageUrl`、`isEdit=1`、目标尺寸、提示词。
2. 若 `generateImgUsingPOST` 长时间卡住（例如 90 秒仍仅 `taskStatus=0`）：
   - 切换 `imageGenerationUsingPOST`，通过 `imageUrls` 传参考图 URL 做参考图生图。
3. 始终用 `queryTaskUsingPOST` 轮询结果，取 `targetImageUrl`。
4. 成功判定：
   - `taskStatus=2` 且 `result[].imageStatue=1`。
   - 被审核拦截或失败的图片自动补单直到满足用户张数。

### Step 5: 回传规范

1. 先给用户结果摘要（成功张数/失败张数/补单次数）。
2. 再给图片：
   - 优先本地路径预览（防外链拦截）。
   - 同时可附外链作为备份。
3. 如用户要求“对比纠偏”，必须同步提供：
   - 实际垫图路径
   - 实际提交提示词
   - 实际任务号（taskCode）

## Style Guardrails

默认遵循投放线“保原风格”策略：
1. 保持原游戏 UI 材质、光影、构图语言。
2. 不加花哨视觉特效（粒子、镜头光晕、赛博滤镜等）。
3. 仅改用户指定变量（颜色数、棋盘复杂度、球数、文案、尺寸）。

## Prompt Baseline

常用模板和参数在 [references/prompt-baselines.md](references/prompt-baselines.md)。
