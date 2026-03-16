# Banana2 共享 MCP

这个目录提供项目内统一的 Banana2 执行层，适合团队共享与后续集中升级。

## 包含内容

1. `mcp_server.py`
   - Banana2 MCP 服务入口
2. `banana2_core.py`
   - 统一封装文生图、图生图、本地上传、下载保存
3. `requirements.txt`
   - 运行依赖
4. `output/generated`
   - 默认文生图输出目录
5. `output/edited`
   - 默认改图输出目录

## 对外工具

1. `banana2_generate_image`
   - 文生图
2. `banana2_edit_image`
   - 本地图生图编辑
3. `banana2_upload_local_image`
   - 上传本地图片并返回公网链接

## 团队共享方式

1. 把 `D:\reo_project\.cursor\skills\banana2-image-tools-local` 跟项目一起共享。
2. 同事拉取或复制项目后，安装依赖：

```bash
pip install -r "<项目根目录>/.cursor/skills/banana2-image-tools-local/requirements.txt"
```

3. 在各自 Cursor 的 MCP 配置里添加：

```json
{
  "mcpServers": {
    "banana2-image-tools-local": {
      "command": "python",
      "args": [
        "<项目根目录>\\.cursor\\skills\\banana2-image-tools-local\\mcp_server.py"
      ]
    }
  }
}
```

4. 重载 Cursor 或重新加载 MCP 配置。

## 后续更新方式

1. 统一改这里的 `banana2_core.py` 或 `mcp_server.py`。
2. 同事同步项目后，通常不需要改技能文档。
3. 如果接口参数变化，只需要同步更新 MCP 配置说明和本目录代码。
4. 同事需要把 MCP 配置里的 `<项目根目录>` 替换成自己机器上的实际项目路径。

## 环境变量

运行前需要在本机设置：

1. `BANANA2_ACCESS_KEY_ID`
2. `BANANA2_ACCESS_KEY_SECRET`
