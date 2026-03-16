# Banana2 生图技能

这个技能现在优先走项目内共享 MCP，而不是各自维护独立脚本逻辑。

## 当前推荐架构

1. 生图技能负责理解用户意图和整理提示词。
2. 共享 MCP 负责真正调用 Banana2 接口并保存结果。
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

1. 在 Cursor 中提出“生图”“画图”“海报生成”等需求。
2. 技能会优先调用共享 MCP 工具 `banana2_generate_image`。
3. 默认输出目录为：
   - `<项目根目录>/.cursor/skills/banana2-image-tools-local/output/generated`

## 兜底方案

如果共享 MCP 暂时不可用，才兜底使用本目录中的：

1. `invoke-banana2-direct.ps1`
2. `invoke-banana2.ps1`


