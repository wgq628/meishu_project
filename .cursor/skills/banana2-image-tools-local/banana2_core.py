import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

API_URL = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"
PROMPT_SUFFIX = "Generate an image based on the above prompt words and reference pictures"


def get_api_credentials() -> tuple[str, str]:
    """读取 Banana2 密钥，未配置时直接报错。"""
    access_key_id = os.environ.get("BANANA2_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("BANANA2_ACCESS_KEY_SECRET", "").strip()
    if not access_key_id or not access_key_secret:
        raise RuntimeError("未检测到 Banana2 密钥，请先设置环境变量 BANANA2_ACCESS_KEY_ID 和 BANANA2_ACCESS_KEY_SECRET。")
    return access_key_id, access_key_secret


def ensure_dir(path: str | Path) -> Path:
    """确保目录存在。"""
    target = Path(path).resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target


def upload_local_image(image_path: str) -> dict[str, Any]:
    """将本地图片上传到临时图床，返回可公开访问的图片链接。"""
    local_path = Path(image_path).resolve()
    if not local_path.exists():
        raise FileNotFoundError(f"找不到本地图片文件: {local_path}")

    with local_path.open("rb") as file_obj:
        try:
            response = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": file_obj},
                timeout=60,
            )
            if response.status_code == 200 and response.text.startswith("http"):
                return {
                    "ok": True,
                    "provider": "catbox",
                    "input_path": str(local_path),
                    "url": response.text.strip(),
                }
        except Exception:
            pass

        file_obj.seek(0)
        try:
            response = requests.post(
                "https://tmpfiles.org/api/v1/upload",
                files={"file": file_obj},
                timeout=60,
            )
            if response.status_code == 200:
                payload = response.json()
                page_url = payload.get("data", {}).get("url", "")
                if page_url:
                    return {
                        "ok": True,
                        "provider": "tmpfiles",
                        "input_path": str(local_path),
                        "url": page_url.replace("tmpfiles.org/", "tmpfiles.org/dl/"),
                    }
        except Exception:
            pass

    raise RuntimeError("本地图片上传失败，catbox 和 tmpfiles 两条路径都不可用。")


def build_payload(
    prompt: str,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_format: str = "png",
    reference_image_urls: list[str] | None = None,
    enable_google_search: bool = False,
) -> dict[str, Any]:
    """构造 Banana2 请求体。"""
    clean_prompt = prompt.strip()
    image_url_list = [url.strip() for url in (reference_image_urls or []) if url and url.strip()]
    if image_url_list and PROMPT_SUFFIX not in clean_prompt:
        clean_prompt = f"{clean_prompt}. {PROMPT_SUFFIX}"

    payload: dict[str, Any] = {
        "prompt": clean_prompt,
        "aspectRatio": aspect_ratio,
        "resolution": resolution,
        "outputFormat": output_format,
        "enableGoogleSearch": enable_google_search,
    }
    if image_url_list:
        payload["imageUrlList"] = image_url_list
    return payload


def request_generation(
    prompt: str,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_format: str = "png",
    reference_image_urls: list[str] | None = None,
    enable_google_search: bool = False,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """调用 Banana2 接口并返回原始图片列表。"""
    access_key_id, access_key_secret = get_api_credentials()
    response = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "X-Request-req-accessKeyId": access_key_id,
            "X-Request-req-accessKeySecret": access_key_secret,
        },
        json=build_payload(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format,
            reference_image_urls=reference_image_urls,
            enable_google_search=enable_google_search,
        ),
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "200":
        message = payload.get("msg") or payload.get("data", {}).get("errorMessage") or json.dumps(payload, ensure_ascii=False)
        raise RuntimeError(f"Banana2 接口返回失败: {message}")

    image_list = payload.get("data", {}).get("imageList") or []
    if not image_list:
        raise RuntimeError("Banana2 接口未返回图片。")
    return payload


def save_remote_image(url: str, target_path: str | Path) -> Path:
    """下载远程图片到本地。"""
    output_path = Path(target_path).resolve()
    ensure_dir(output_path.parent)
    urllib.request.urlretrieve(url, output_path)
    return output_path


def resolve_output_folder(output_folder: str | None, mode: str) -> Path:
    """解析默认输出目录。"""
    if output_folder and output_folder.strip():
        return ensure_dir(output_folder)
    base_dir = Path(__file__).resolve().parent
    if mode == "edit":
        return ensure_dir(base_dir / "output" / "edited")
    return ensure_dir(base_dir / "output" / "generated")


def build_output_path(output_dir: Path, file_prefix: str, index: int, extension: str) -> Path:
    """生成带时间戳的输出文件路径。"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_ext = "jpg" if extension.lower() == "jpeg" else extension.lower()
    return output_dir / f"{file_prefix}_{timestamp}_{index}.{safe_ext}"


def generate_images(
    prompt: str,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_format: str = "png",
    reference_image_urls: list[str] | None = None,
    output_folder: str = "",
    file_prefix: str = "banana2_generated",
    count: int = 1,
    download: bool = True,
    enable_google_search: bool = False,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """文生图或带参考图生图。"""
    output_dir = resolve_output_folder(output_folder, "generate")
    results: list[dict[str, Any]] = []
    success_count = 0
    fail_count = 0

    for index in range(1, count + 1):
        try:
            payload = request_generation(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_format=output_format,
                reference_image_urls=reference_image_urls,
                enable_google_search=enable_google_search,
                timeout_seconds=timeout_seconds,
            )
            image = payload["data"]["imageList"][0]
            item: dict[str, Any] = {
                "ok": True,
                "index": index,
                "url": image.get("url", ""),
                "width": image.get("width"),
                "height": image.get("height"),
                "output_path": "",
            }
            if download:
                final_path = build_output_path(output_dir, file_prefix, index, output_format)
                save_remote_image(item["url"], final_path)
                item["output_path"] = str(final_path)
            results.append(item)
            success_count += 1
        except Exception as exc:
            results.append(
                {
                    "ok": False,
                    "index": index,
                    "url": "",
                    "width": None,
                    "height": None,
                    "output_path": "",
                    "error": str(exc),
                }
            )
            fail_count += 1

    return {
        "mode": "generate",
        "output_dir": str(output_dir),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
    }


def edit_image(
    image_path: str,
    prompt: str,
    aspect_ratio: str = "1:1",
    output_folder: str = "",
    file_prefix: str = "banana2_edited",
    count: int = 1,
    enable_google_search: bool = False,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """本地图生图编辑。"""
    upload_result = upload_local_image(image_path)
    output_dir = resolve_output_folder(output_folder, "edit")
    result = generate_images(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        resolution="1K",
        output_format="png",
        reference_image_urls=[upload_result["url"]],
        output_folder=str(output_dir),
        file_prefix=file_prefix,
        count=count,
        download=True,
        enable_google_search=enable_google_search,
        timeout_seconds=timeout_seconds,
    )
    result["mode"] = "edit"
    result["source_image_path"] = str(Path(image_path).resolve())
    result["uploaded_image_url"] = upload_result["url"]
    return result
