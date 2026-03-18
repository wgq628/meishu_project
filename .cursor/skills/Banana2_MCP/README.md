# Banana2-MCP 图像处理工具包

这是一个基于 **MCP (Model Context Protocol)** 协议的图像生成与编辑服务器。它将 Banana2 AI 的核心能力封装为可被 AI 助手（如 Claude Desktop, Gemini 等）直接调用的工具。

## 🌟 功能亮点

- **智能改图 (banana2_edit_image)**：支持参考图 + 提示词进行重绘和风格转换。
- **创意生图 (banana2_generate_image)**：纯文字描述生成高质量图片。
- **图片上传 (banana2_upload_image)**：支持本地图片快速上传，内置 Base64 自动降级方案，极度稳健。

---

## 🛠️ 环境准备

1. **Python 版本**：需要 Python 3.10 或更高版本。
2. **安装依赖**：
   在本项目根目录下运行以下命令安装必要组件：
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ 配置指引

### 1. 修改 mcp_config.json
打开您的 MCP 客户端配置文件（通常位于 `%AppData%\Claude\claude_desktop_config.json` 或类似路径），在 `mcpServers` 节点下添加以下配置：

```json
{
  "mcpServers": {
    "banana2-mcp": {
      "command": "python",
      "args": [
        "C:/您的绝对路径/Banana2_MCP/mcp_server/server.py"
      ],
      "env": {
        "BANANA2_ACCESS_KEY_ID": "您的_Access_Key_ID",
        "BANANA2_ACCESS_KEY_SECRET": "您的_Access_Key_Secret"
      }
    }
  }
}
```

### 2. 获取 API Key
请联系管理员获取您的 `Access Key ID` 和 `Access Key Secret`。您可以直接填入上述配置的 `env` 部分。

---

## 🚀 使用说明

一旦配置完成并重启 MCP 客户端，您的 AI 助手即可识别并调用以下工具：

- **文生图测试**：
  > "帮我画一个未来都市的赛博朋克风插画，16:9 比例。"
- **图片修改**：
  > "参考这张图片 [附图]，把背景换成雪山，并调整为 9:16 竖版。"

---

## 📂 目录结构

- `mcp_server/server.py`：核心程序入口。
- `requirements.txt`：项目依赖库列表。
- `.env.example`：环境变量配置参考文件。

---

## 📜 开源协议
本项目仅供学习与内部交流使用。
