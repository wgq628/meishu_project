---
name: image-bg-remove-local
description: 使用本地去背景 MCP 处理上传图片的抠图、移除背景、透明背景、去底、保留主体需求。用户提到“移除背景”“去背景”“抠图”“透明背景”“去底”时使用。固定使用 `<项目根目录>/.cursor/skills/image-bg-remove-local/input` 与 `<项目根目录>/.cursor/skills/image-bg-remove-local/output`，并在处理前清空 input 旧图。
---

# 本地去背景技能

用于处理“移除背景”“抠图”“透明背景”这类需求。该技能只负责去背景，不负责换风格、重绘、补画或替换背景。

## 触发场景

当用户表达以下意图时，直接使用本技能：

- 移除背景
- 去背景
- 抠图
- 透明背景
- 去底
- 只保留主体

如果用户要的是“替换背景”“重绘背景”“换风格”，不要使用本技能，应交给图像编辑或图生图技能。

## 固定目录

- 技能根目录：`<项目根目录>/.cursor/skills/image-bg-remove-local`
- 输入目录：`<项目根目录>/.cursor/skills/image-bg-remove-local/input`
- 输出目录：`<项目根目录>/.cursor/skills/image-bg-remove-local/output`
- MCP 服务脚本：`<项目根目录>/.cursor/skills/image-bg-remove-local/mcp_server.py`
- 去背景脚本：`<项目根目录>/.cursor/skills/image-bg-remove-local/batch_remove_bg.py`

## 标准流程

1. 先清空 `<项目根目录>/.cursor/skills/image-bg-remove-local/input` 里的旧文件。
2. 将当前用户上传的原图复制到 `<项目根目录>/.cursor/skills/image-bg-remove-local/input`。
3. 调用本地 MCP：`user-image-bg-tools-local-batch_remove_background`。
4. 调用参数固定为：
   - `input_folder = "<项目根目录>\\.cursor\\skills\\image-bg-remove-local\\input"`
   - `output_folder = "<项目根目录>\\.cursor\\skills\\image-bg-remove-local\\output"`
5. 从 `<项目根目录>/.cursor/skills/image-bg-remove-local/output` 读取生成的透明 PNG。
6. 如果要在聊天中展示结果，先复制到当前会话可展示的位置，再用 Markdown 图片语法引用。

## 执行要求

1. 不要把历史图片留在 `input` 中。
2. 不要把去背景需求误走到 Banana2 或其他图生图流程。
3. 输出优先保留透明背景 PNG。
4. 如果是单张图，也按批量工具方式执行。

## 结果返回

1. 返回最终输出文件路径。
2. 如有多个结果，明确指出本次新生成的文件。
3. 如果执行失败，用中文说明失败原因和下一步处理方式。
