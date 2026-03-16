---
name: banana2-image-generation
description: 使用 Banana2 生成图片。用户提出生图、画图、海报生成、宣传图生成、参考图生图、接入 Banana2 API 等需求时使用。优先调用项目内共享 MCP `banana2-image-tools-local`，便于团队共享和统一升级。
---

# Banana2 生图技能

当用户需要「生图」「画图」「Banana2 绘图」「海报生成」或调用该接口时使用本技能。

---

## 1. 优先使用共享 MCP

优先调用项目内共享 MCP：`banana2-image-tools-local`

推荐工具：`banana2_generate_image`

推荐参数：

- `prompt`：英文提示词
- `aspect_ratio`：比例，默认 `1:1`
- `resolution`：默认 `1K`
- `output_format`：`png` 或 `jpeg`
- `count`：生成张数
- `output_folder`：可选；不传时默认输出到共享目录 `<项目根目录>/.cursor/skills/banana2-image-tools-local/output/generated`

使用规则：

1. 用户自然语言需求先整理为清晰英文提示词。
2. 未明确比例时默认 `1:1`。
3. 海报常用 `9:16`，横版宣传图常用 `16:9`。
4. 如需多张图，设置 `count`。
5. 如需统一留档，可显式传 `output_folder`。

## 2. 适用场景

适合以下需求：

- 文生图
- 海报生成
- 宣传图生成
- 多张候选图生成
- 已有参考图 URL 的参考生图

如果用户给的是本地图片并要求修改原图内容，优先改用 `banana2-image-editor` 技能。

## 3. 环境变量

运行前需要本机配置：

- `BANANA2_ACCESS_KEY_ID`
- `BANANA2_ACCESS_KEY_SECRET`

## 4. 团队共享

共享 MCP 目录：
`<项目根目录>/.cursor/skills/banana2-image-tools-local`

共享优点：

1. 同事可以直接复用同一套 MCP。
2. 后续升级只需要更新共享目录里的脚本。
3. 生图技能本身只保留意图判断和调用规则。

## 5. 脚本兜底

只有在共享 MCP 暂时不可用时，才兜底使用：
`<项目根目录>/.cursor/skills/banana2-image-generation/invoke-banana2-direct.ps1`

不建议把脚本兜底当成主流程，以免后续维护出现两套逻辑分叉。

## 6. 输出规则

1. 成功后优先返回本地输出路径。
2. 如未下载，也要返回云端图片 URL。
3. 如需在聊天中展示，再复制到当前会话可展示目录。


