# 投放线 Cursor 技能仓库

这个项目整理了一套适合共享的 Cursor 技能与本地 MCP 工具，重点覆盖：

1. Banana2 文生图
2. Banana2 本地图生图编辑
3. 本地图片去背景
4. 多类游戏创意技能与素材生产规范

## 目录说明

1. `.cursor/skills/`
   - 当前可分享、可维护的技能目录
2. `.cursor/MCP_SETUP.md`
   - MCP 接入与升级说明
3. `.cursor/mcp.config.example.json`
   - 可复制的 MCP 配置示例

## 使用前准备

1. 安装 Python 及依赖
2. 按需安装各技能目录下 `requirements.txt` 中的依赖
3. 为 Banana2 相关能力配置环境变量：
   - `BANANA2_ACCESS_KEY_ID`
   - `BANANA2_ACCESS_KEY_SECRET`
4. 在自己的 Cursor MCP 配置中注册项目里的 MCP 服务

## 路径约定

仓库中的说明文档统一使用：

1. 相对路径
2. 或 `<项目根目录>` 占位写法

存放目录可参照官方文档https://cursor.com/cn/docs/skills 
位置	级别
.agents/skills/	项目级
.cursor/skills/	项目级
~/.cursor/skills/	用户级 (全局)


