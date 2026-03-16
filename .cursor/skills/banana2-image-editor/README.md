# Banana2 图像编辑技能

这个技能现在优先走项目内共享 MCP，不再把上传、调用接口、下载结果分散在多个脚本里维护。

## 当前推荐架构

1. 改图技能负责判断用户意图和整理编辑提示词。
2. 共享 MCP 负责上传本地图片、调用 Banana2、下载结果图。
3. 共享 MCP 目录：
   - `<项目根目录>/.cursor/skills/banana2-image-tools-local`

## 同事安装方式

1. 同步整个项目目录。
2. 安装共享 MCP 依赖：
   - `pip install -r "<项目根目录>/.cursor/skills/banana2-image-tools-local/requirements.txt"`
3. 配置环境变量：
   - `BANANA2_ACCESS_KEY_ID`
   - `BANANA2_ACCESS_KEY_SECRET`
4. 在各自 Cursor MCP 配置里注册：
   - `<项目根目录>/.cursor/skills/banana2-image-tools-local/mcp_server.py`

## 使用方式

1. 在 Cursor 中上传图片并说明修改意图。
2. 技能会优先调用共享 MCP 工具 `banana2_edit_image`。
3. 默认输出目录为：
   - `<项目根目录>/.cursor/skills/banana2-image-tools-local/output/edited`

## 去背景说明

如果需求是“去背景 / 抠图 / 透明背景”，不要走本技能，优先走独立技能：

1. `image-bg-remove-local`

## 兜底方案

如果共享 MCP 暂时不可用，才兜底使用本目录中的：

1. `scripts/auto_edit_image.py`


