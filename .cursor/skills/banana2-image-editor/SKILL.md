---
name: banana2-image-editor
description: 使用 Banana2 处理本地图片编辑、图生图重绘、改比例、换风格、改场景等需求。用户上传图片并要求修改内容时使用。优先调用项目内共享 MCP `banana2-image-tools-local`，去背景需求则优先走独立去背景 MCP。
---

# Banana2 本地图像编辑技能

用于处理用户上传的本地图片编辑诉求。先判断是不是去背景，再决定是否进入 Banana2 改图。

## 决策顺序

1. 如果需求是“移除背景 / 抠图 / 透明背景 / 去底”，优先走 `image-bg-remove-local`。
2. 如果需求是“换风格 / 重绘 / 改横版竖版 / 改背景内容 / 增删元素”，走 Banana2 改图。
3. 如果需求是“先抠图，再继续改图”，先执行去背景，再根据结果继续 Banana2 改图。

## 去背景分支

1. 不要调用 Banana2。
2. 直接使用独立技能 `image-bg-remove-local`。
3. 去背景完成后，如果用户还要继续改图，再回到本技能。

## Banana2 改图分支

### 优先使用共享 MCP

优先调用项目内共享 MCP：`banana2-image-tools-local`

推荐工具：`banana2_edit_image`

推荐参数：

- `image_path`：本地原图绝对路径
- `prompt`：英文编辑提示词
- `aspect_ratio`：默认 `1:1`，横版 `16:9`，竖版 `9:16`
- `count`：生成张数
- `output_folder`：可选；不传时默认输出到 `<项目根目录>/.cursor/skills/banana2-image-tools-local/output/edited`

### 使用规则

1. 先定位用户上传图片的本地绝对路径。
2. 不要要求用户自行保存图片。
3. 先理解用户意图，再整理成清晰英文提示词。
4. 共享 MCP 会自动完成本地图片上传、Banana2 调用、结果下载和落盘。

## 团队共享

共享 MCP 目录：
`<项目根目录>/.cursor/skills/banana2-image-tools-local`

共享优点：

1. 同事共用同一套图床上传和 API 调用逻辑。
2. 后续更新只改共享目录，不需要每人分别改技能脚本。
3. 改图技能只保留意图判断和调用约定。

## 脚本兜底

只有在共享 MCP 暂时不可用时，才兜底使用：
`<项目根目录>/.cursor/skills/banana2-image-editor/scripts/auto_edit_image.py`

## 输出规则

1. 成功后优先返回最终输出文件路径。
2. 如需在聊天中直接展示图片，先复制到当前会话可展示位置。
3. 图片引用使用 Markdown 路径，不要加 `file:///`。

