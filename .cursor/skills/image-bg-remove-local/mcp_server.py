from mcp.server.fastmcp import FastMCP

from batch_remove_bg import batch_process

# 创建 MCP 服务实例，名称会显示在客户端工具列表中
mcp = FastMCP("image-bg-remove-local")


@mcp.tool()
def batch_remove_background(input_folder: str = "input", output_folder: str = "output") -> dict:
    """
    批量去除图片背景，输出透明 PNG。
    参数:
    - input_folder: 输入目录路径
    - output_folder: 输出目录路径
    """
    return batch_process(input_folder=input_folder, output_folder=output_folder)


if __name__ == "__main__":
    # 通过 stdio 方式启动，便于被 Cursor 等 MCP 客户端调用
    mcp.run(transport="stdio")
