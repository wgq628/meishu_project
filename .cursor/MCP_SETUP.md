# 项目内 MCP 接入说明

这个项目已经把常用图像能力整理成项目内共享 MCP，适合直接给同事复用。

## 当前共享 MCP

1. Banana2 生图与改图
   - 目录：`<项目根目录>/.cursor/skills/banana2-image-tools-local`
   - 服务入口：`<项目根目录>/.cursor/skills/banana2-image-tools-local/mcp_server.py`

2. 本地去背景
   - 目录：`<项目根目录>/.cursor/skills/image-bg-remove-local`
   - 服务入口：`<项目根目录>/.cursor/skills/image-bg-remove-local/mcp_server.py`

## 同事首次使用步骤

1. 同步整个项目目录。
2. 安装依赖：

```bash
pip install -r "<项目根目录>/.cursor/skills/banana2-image-tools-local/requirements.txt"
pip install -r "<项目根目录>/.cursor/skills/image-bg-remove-local/requirements.txt"
```

3. 在自己本机设置 Banana2 环境变量：
   - `BANANA2_ACCESS_KEY_ID`
   - `BANANA2_ACCESS_KEY_SECRET`

4. 在自己 Cursor 的 MCP 配置中加入以下内容。
   - 使用前请把下面示例中的 `<项目根目录>` 替换成自己机器上的实际项目路径。

```json
{
  "mcpServers": {
    "banana2-image-tools-local": {
      "command": "python",
      "args": [
        "<项目根目录>\\.cursor\\skills\\banana2-image-tools-local\\mcp_server.py"
      ]
    },
    "image-bg-tools-local": {
      "command": "python",
      "args": [
        "<项目根目录>\\.cursor\\skills\\image-bg-remove-local\\mcp_server.py"
      ]
    }
  }
}
```

5. 重载 Cursor 或重新加载 MCP 配置。

## 后续版本更新方式

1. Banana2 升级时，优先更新：
   - `<项目根目录>/.cursor/skills/banana2-image-tools-local/banana2_core.py`
   - `<项目根目录>/.cursor/skills/banana2-image-tools-local/mcp_server.py`

2. 去背景升级时，优先更新：
   - `<项目根目录>/.cursor/skills/image-bg-remove-local` 下的脚本

3. 技能说明只负责意图判断，执行逻辑尽量都集中在共享 MCP 中。

## 为什么这样更适合团队

1. 同事拿到项目后就能看到完整脚本和说明，不再依赖某个人家目录里的私有技能。
2. 后续升级只改共享目录，不用到处同步多份脚本。
3. 问题排查更集中，执行逻辑更统一。
