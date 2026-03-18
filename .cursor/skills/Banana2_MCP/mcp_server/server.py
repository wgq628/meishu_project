# -*- coding: utf-8 -*-
"""
Banana2-MCP - 图像智能生图与编辑服务器
将 Banana2 AI 的核心图像处理能力封装为 MCP 工具，支持本地图片上传、重绘以及文生图全流程。

工具列表:
  - banana2_edit_image   : 【改图】参考图 + 描述词进行重绘或局部编辑。
  - banana2_generate_image: 【生图】纯文字描述生成全新图片，无需参考图。
  - banana2_upload_image  : 【工具】上传本地图片并获取公网 URL，供其他流程复用。
"""

import base64
import concurrent.futures
import json
import mimetypes
import os
from datetime import datetime
from typing import Optional

# 引入 MCP SDK 与 网络请求库
from mcp.server.fastmcp import FastMCP
import requests

# ========== 核心配置 ==========
# Banana2 生图 API 接口地址
API_URL = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"

# API 访问密钥（支持从环境变量读取，安全性更高）
# 建议通过环境变量配置：BANANA2_ACCESS_KEY_ID 和 BANANA2_ACCESS_KEY_SECRET
DEFAULT_ACCESS_KEY_ID     = os.environ.get("BANANA2_ACCESS_KEY_ID",     "您的_Access_Key_ID")
DEFAULT_ACCESS_KEY_SECRET = os.environ.get("BANANA2_ACCESS_KEY_SECRET", "您的_ACCESS_KEY_SECRET")

# 各环节超时时间设定（单位：秒）
UPLOAD_TIMEOUT   = 30   # 图片上传至图床的限时
API_TIMEOUT      = 500  # AI 生图任务的限时（生图较慢，需设置较长）
DOWNLOAD_TIMEOUT = 60   # 生成结果下载到本地的限时

# 默认图片存储目录（用户可根据实际情况修改）
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "output")

# 初始化 FastMCP 服务实例
mcp = FastMCP("Banana2-MCP")


# ========== 内部辅助函数 ==========

def _image_to_base64(image_path: str) -> str:
    """
    将本地物理路径的图片转换为 Base64 Data URL 格式。
    用于在图床不可用时，直接将图片数据内嵌在 API 请求中。
    """
    mime, _ = mimetypes.guess_type(image_path)
    if not mime:
        mime = "image/png"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _upload_to_banana2_oss(image_path: str) -> str:
    """
    【首选方案】将图片上传到 Banana2 官方提供的 OSS 存储空间。
    这是最稳定的方案，能保证 API 访问图片的延迟最低。
    """
    upload_url = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/file/upload"
    headers = {
        "X-Request-req-accessKeyId":     DEFAULT_ACCESS_KEY_ID,
        "X-Request-req-accessKeySecret": DEFAULT_ACCESS_KEY_SECRET,
    }
    with open(image_path, "rb") as f:
        resp = requests.post(
            upload_url,
            headers=headers,
            files={"file": (os.path.basename(image_path), f)},
            timeout=UPLOAD_TIMEOUT,
        )
    resp.raise_for_status()
    data = resp.json()
    
    # 兼容处理不同的响应 JSON 结构，提取图片 URL
    url = (
        data.get("url")
        or data.get("data", {}).get("url")
        or data.get("fileUrl")
        or data.get("data", {}).get("fileUrl")
    )
    if url and url.startswith("http"):
        return url
    raise RuntimeError(f"官方 OSS 上传解析失败，响应内容: {data}")


def _get_image_remote_url(image_path: str) -> str:
    """
    智能图片上传策略（分级降级）：
    1. 优先尝试官方 OSS（速度最快，Api 原生支持）。
    2. 若官方失败，立即降级为 Base64 方案（最稳健，无需依赖外部图床）。
    
    注：Banana2 API 同时支持图片 HTTP 链接和 Base64 数据流。
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"指定的本地图片不存在: {image_path}")

    # 第一级：官方 OSS
    try:
        url = _upload_to_banana2_oss(image_path)
        return url
    except Exception as e:
        print(f"[上传] 官方 OSS 失败，尝试 Base64 降级: {e}")

    # 第二级：Base64 兜底
    b64_url = _image_to_base64(image_path)
    return b64_url


def _call_banana2_api(
    prompt: str,
    image_url: Optional[str] = None,
    aspect_ratio: str = "1:1",
    enable_google_search: bool = False,
) -> str:
    """
    封装对 Banana2 生图 API 的底层调用逻辑。
    支持参考图（URL 或 Base64）和纯文字 Prompt。
    """
    headers = {
        "X-Request-req-accessKeyId":     DEFAULT_ACCESS_KEY_ID,
        "X-Request-req-accessKeySecret": DEFAULT_ACCESS_KEY_SECRET,
        "Content-Type": "application/json",
    }

    final_prompt = prompt
    image_url_list = []
    if image_url:
        # 如果有参考图，需要将其加入 imageUrlList，并微调 Prompt 以增强关联性
        image_url_list.append(image_url)
        suffix = "Generate an image based on the above prompt words and reference pictures"
        if suffix not in final_prompt:
            final_prompt = f"{final_prompt}. {suffix}"

    payload = {
        "prompt":             final_prompt,
        "aspectRatio":        aspect_ratio,
        "resolution":         "1K",  # 默认生成 1K 高清图
        "outputFormat":       "png",
        "enableGoogleSearch": enable_google_search,
    }
    if image_url_list:
        payload["imageUrlList"] = image_url_list

    # 发起 POST 请求并等待生图完成
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=API_TIMEOUT)
    resp.raise_for_status()

    data = resp.json()
    # 校验并提取生成后的图片公网下载链接
    if (
        data.get("code") == "200"
        and data.get("data")
        and data["data"].get("imageList")
    ):
        return data["data"]["imageList"][0]["url"]
    else:
        raise RuntimeError(f"生图接口返回业务错误: {json.dumps(data, ensure_ascii=False)}")


def _download_image(url: str, save_path: str) -> str:
    """通过公网 URL 下载图片并持久化存储到本地磁盘。"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path


def _make_output_path(output_dir: str, base_name: str, task_id: int = 1) -> str:
    """构造带有时间戳和任务 ID 的唯一文件名，防止覆盖。"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{base_name}_{ts}_{task_id}.png")


# ========== MCP 外部工具暴露 ==========

@mcp.tool()
def banana2_edit_image(
    image_path: str,
    prompt: str,
    ratio: str = "1:1",
    output_dir: str = "",
    count: int = 1,
) -> str:
    """
    【改图工具】根据参考图（垫图）+ Prompt 描述进行重绘、风格转换或修复。

    参数:
      image_path : 本地待处理图片的绝对路径。
      prompt     : 针对改图的详细英文指令。
      ratio      : 图片比例，如 "1:1"、"16:9"、"9:16"。
      output_dir : 自定义保存目录。
      count      : 同时生成多张结果（最大支持 20 张并发）。
    """
    out_dir = output_dir if output_dir else DEFAULT_OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    # 上传参考图
    remote_url = _get_image_remote_url(image_path)

    # 启动多线程并发执行生图下载任务
    actual_count = max(1, min(count, 20))
    results = []

    def _task(task_id: int):
        save_path = _make_output_path(out_dir, "banana2_edited", task_id)
        result_url = _call_banana2_api(prompt, remote_url, ratio)
        _download_image(result_url, save_path)
        return save_path

    with concurrent.futures.ThreadPoolExecutor(max_workers=actual_count) as executor:
        futures = {executor.submit(_task, i + 1): i for i in range(actual_count)}
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(f"[错误] 任务 {futures[future]+1} 失败: {str(e)}")

    return json.dumps({"success": True, "saved_paths": results}, ensure_ascii=False)


@mcp.tool()
def banana2_generate_image(
    prompt: str,
    ratio: str = "1:1",
    output_dir: str = "",
    count: int = 1,
) -> str:
    """
    【生图工具】纯文字创作工具，无需输入参考图片。

    参数:
      prompt     : 核心英文描述词（Prompt）。
      ratio      : 目标比例，如 "1:1"、"16:9"、"9:16"。
      output_dir : 结果保存目录。
      count      : 生成张数。
    """
    out_dir = output_dir if output_dir else DEFAULT_OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    actual_count = max(1, min(count, 20))
    results = []

    def _task(task_id: int):
        save_path = _make_output_path(out_dir, "banana2_gen", task_id)
        result_url = _call_banana2_api(prompt, None, ratio)
        _download_image(result_url, save_path)
        return save_path

    with concurrent.futures.ThreadPoolExecutor(max_workers=actual_count) as executor:
        futures = {executor.submit(_task, i + 1): i for i in range(actual_count)}
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(f"[错误] 任务 {futures[future]+1} 失败: {str(e)}")

    return json.dumps({"success": True, "saved_paths": results}, ensure_ascii=False)


@mcp.tool()
def banana2_upload_image(image_path: str) -> str:
    """
    【辅助工具】将本地图片预上传至公网环境。
    支持 官方 OSS 优先，Base64 自动降级兜底方案。
    """
    url = _get_image_remote_url(image_path)
    return json.dumps({"success": True, "public_url": url}, ensure_ascii=False)


# ========== 执行入口 ==========
if __name__ == "__main__":
    mcp.run(transport="stdio")
