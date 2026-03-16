from mcp.server.fastmcp import FastMCP

from banana2_core import edit_image, generate_images, upload_local_image

mcp = FastMCP("banana2-image-tools-local")


@mcp.tool()
def banana2_generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_format: str = "png",
    output_folder: str = "",
    file_prefix: str = "banana2_generated",
    count: int = 1,
    download: bool = True,
    enable_google_search: bool = False,
    timeout_seconds: int = 120,
) -> dict:
    """
    Banana2 文生图工具。
    参数:
    - prompt: 英文提示词
    - aspect_ratio: 画幅比例，默认 1:1
    - resolution: 输出分辨率，默认 1K
    - output_format: png 或 jpeg
    - output_folder: 输出目录，留空则写入共享工具默认 output/generated
    - file_prefix: 文件名前缀
    - count: 生成张数
    - download: 是否下载到本地
    - enable_google_search: 是否启用搜索增强
    - timeout_seconds: 请求超时秒数
    """
    return generate_images(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        output_format=output_format,
        output_folder=output_folder,
        file_prefix=file_prefix,
        count=count,
        download=download,
        enable_google_search=enable_google_search,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def banana2_edit_image(
    image_path: str,
    prompt: str,
    aspect_ratio: str = "1:1",
    output_folder: str = "",
    file_prefix: str = "banana2_edited",
    count: int = 1,
    enable_google_search: bool = False,
    timeout_seconds: int = 120,
) -> dict:
    """
    Banana2 本地图生图编辑工具。
    参数:
    - image_path: 本地原图绝对路径
    - prompt: 英文编辑提示词
    - aspect_ratio: 画幅比例，默认 1:1
    - output_folder: 输出目录，留空则写入共享工具默认 output/edited
    - file_prefix: 文件名前缀
    - count: 生成张数
    - enable_google_search: 是否启用搜索增强
    - timeout_seconds: 请求超时秒数
    """
    return edit_image(
        image_path=image_path,
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        output_folder=output_folder,
        file_prefix=file_prefix,
        count=count,
        enable_google_search=enable_google_search,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def banana2_upload_local_image(image_path: str) -> dict:
    """
    上传本地图片到临时图床，返回公网链接。
    参数:
    - image_path: 本地图片绝对路径
    """
    return upload_local_image(image_path)


if __name__ == "__main__":
    mcp.run(transport="stdio")
