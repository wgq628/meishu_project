---
name: banana2-image-tools-local
description: 维护项目内共享的 Banana2 MCP 服务与执行脚本时使用。仅在需要配置、升级、排查或迁移 Banana2 生图与改图工具链时触发，不用于普通的图片生成请求。
---

# Banana2 共享 MCP 服务

这是项目内的共享执行层，负责为 `banana2-image-generation` 与 `banana2-image-editor` 提供统一的 Banana2 MCP 工具。

## 作用

1. 统一处理 Banana2 文生图。
2. 统一处理 Banana2 本地图生图编辑。
3. 统一处理本地图片临时上传。
4. 让同事只维护一套脚本，而不是分别维护多个技能目录下的脚本。

## 工具

1. `banana2_generate_image`
2. `banana2_edit_image`
3. `banana2_upload_local_image`

## 目录

1. MCP 服务：`mcp_server.py`
2. 核心逻辑：`banana2_core.py`
3. 默认生图输出：`output/generated`
4. 默认改图输出：`output/edited`

## 配置要求

1. 需要环境变量：`BANANA2_ACCESS_KEY_ID`
2. 需要环境变量：`BANANA2_ACCESS_KEY_SECRET`
3. 需要在 Cursor MCP 配置中注册本目录下的 `mcp_server.py`

## 分享原则

1. 把整个目录跟随项目一起共享给同事。
2. 后续更新时，优先只改本目录下的脚本与说明。
3. 生成技能与编辑技能只负责调用，不再各自维护一套独立执行逻辑。
