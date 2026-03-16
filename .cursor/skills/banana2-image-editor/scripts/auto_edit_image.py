import os
import sys
import argparse

# 强制将标准输出和标准错误输出的编码设置为 utf-8，解决 Windows 下 GBK 无法打印 emoji 的问题
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
import requests
import json
import urllib.request
import concurrent.futures
from datetime import datetime

# --- 配置 Banana2 API ---
API_URL = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"
# 从环境变量读取，勿写死密钥
DEFAULT_ACCESS_KEY_ID = os.environ.get("BANANA2_ACCESS_KEY_ID", "")
DEFAULT_ACCESS_KEY_SECRET = os.environ.get("BANANA2_ACCESS_KEY_SECRET", "")
if not DEFAULT_ACCESS_KEY_ID or not DEFAULT_ACCESS_KEY_SECRET:
    raise SystemExit("请设置环境变量 BANANA2_ACCESS_KEY_ID 和 BANANA2_ACCESS_KEY_SECRET")

def upload_to_tmp(image_path: str) -> str:
    """上传本地图片到免费的中转临时存储获取公网直链 (catbox.moe / tmpfiles.org)"""
    print(f"[*] 正在读取并上传本地图片到临时图床: {image_path}")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"找不到本地图片文件: {image_path}")
    
    with open(image_path, 'rb') as f:
        # Route 1: 尝试使用 catbox.moe
        try:
            print(" |-> 尝试上传至 catbox.moe ...")
            resp = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=60)
            if resp.status_code == 200 and resp.text.startswith("http"):
                url = resp.text.strip()
                print(f"[+] catbox 上传成功: {url}")
                return url
        except Exception as e:
            print(f" |-> [-] catbox.moe 失败: {e}")
        
        # Route 2: 尝试使用 tmpfiles.org 作为备胎 (重置文件指针!)
        f.seek(0)
        try:
            print(" |-> 尝试备用图床 tmpfiles.org ...")
            resp2 = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=60)
            if resp2.status_code == 200:
                data = resp2.json()
                url = data.get("data", {}).get("url")
                if url:
                    # tmpfiles默认给的是查看页，需要将替换为直链
                    direct_url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    print(f"[+] tmpfiles 上传成功: {direct_url}")
                    return direct_url
        except Exception as e2:
            print(f" |-> [-] tmpfiles.org 失败: {e2}")
            
    raise Exception("全部图床上传方式均失败，无法获取网络 URL 进行图生图。")

def generate_image(prompt: str, image_url: str = None, aspect_ratio: str = "1:1", enable_google_search: bool = False):
    """调用 Banana2 API 提交生成/修改图片请求"""
    headers = {
        "X-Request-req-accessKeyId": DEFAULT_ACCESS_KEY_ID,
        "X-Request-req-accessKeySecret": DEFAULT_ACCESS_KEY_SECRET,
        "Content-Type": "application/json"
    }

    final_prompt = prompt
    image_url_list = []
    
    if image_url:
        image_url_list.append(image_url)
        # 根据经验，调用图生图时，结尾加上这句往往强制触发重绘
        suffix = "Generate an image based on the above prompt words and reference pictures"
        if suffix not in final_prompt:
             final_prompt = f"{final_prompt}. {suffix}"

    payload = {
        "prompt": final_prompt,
        "aspectRatio": aspect_ratio,
        "resolution": "1K",  # 默认使用 1K，保障速度
        "outputFormat": "png",
        "enableGoogleSearch": enable_google_search
    }
    
    if image_url_list:
        payload["imageUrlList"] = image_url_list

    print(f"\n[*] 正在调用 Banana2 API 生图...")
    print(f" |-> [Prompt]: {final_prompt[:100]}...\n |-> [Ratio]: {aspect_ratio}")
    
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    
    data = resp.json()
    if data.get("code") == "200" and data.get("data") and data["data"].get("imageList"):
        generated_url = data["data"]["imageList"][0]["url"]
        print(f"[+] 生图成功, 云端新图片链接为: {generated_url}")
        return generated_url
    else:
        raise Exception(f"Banana2 API 抛出错误: {json.dumps(data, ensure_ascii=False)}")

def download_image(url: str, save_path: str):
    """下载生成的最终图片到指定本地路径"""
    print(f"\n[*] 正在将生成的图片下载到本地盘系...\n |-> {save_path}")
    urllib.request.urlretrieve(url, save_path)
    print(f"[+] 文件落地完成！")

def process_single_task(task_id: int, prompt: str, remote_image_url: str, aspect_ratio: str, output_dir: str, base_filename: str):
    try:
        # 第二阶段：调用 Banana2 获取绘图并拿回新图片的网络链接
        result_url = generate_image(
            prompt=prompt,
            image_url=remote_image_url,
            aspect_ratio=aspect_ratio
        )

        # 第三阶段：落地到本地
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"{base_filename}_{timestamp}_{task_id}.png")
            
        download_image(result_url, output_path)
        print(f"\n==== 任务 {task_id} 圆满结束 ====\n✅ 最终图片已保存在路径:\n{output_path}\n")
        return True
    except Exception as e:
        print(f"\n❌ 任务 {task_id} 执行遇到异常: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Banana2 智能改图自动化脚本")
    parser.add_argument("--image", type=str, help="原本地图片的绝对路径 (可选，如果没有则为纯文生图)")
    parser.add_argument("--prompt", type=str, required=True, help="详细的修改意图【中文】描述 / 画面重绘指令")
    parser.add_argument("--ratio", type=str, default="1:1", help="目标画幅比例 (如 1:1, 9:16, 16:9)")
    parser.add_argument("--output", type=str, help="指定生成的图片最终保存目录或文件名前缀 (可选，默认存到桌面)")
    parser.add_argument("--count", type=int, default=1, help="生成图片数量，默认为 1")
    args = parser.parse_args()

    try:
        remote_image_url = None
        # 第一阶段：尝试获取原图的公网链接（只需要上传一次）
        if args.image:
            remote_image_url = upload_to_tmp(args.image)

        # 确定输出目录和文件名前缀
        if args.output:
            if os.path.isdir(args.output):
                output_dir = args.output
                base_filename = "banana2_edited"
            else:
                output_dir = os.path.dirname(args.output) or "."
                base_filename = os.path.splitext(os.path.basename(args.output))[0]
        else:
            skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(skill_dir, "output")
            base_filename = "banana2_edited"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        max_workers = min(args.count, 20)
        print(f"\n[*] 计划生成 {args.count} 张图片，按需启动 {max_workers} 个线程并发处理...")
        
        # 使用多线程执行生图任务
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    process_single_task, 
                    i + 1, 
                    args.prompt, 
                    remote_image_url, 
                    args.ratio, 
                    output_dir, 
                    base_filename
                ) 
                for i in range(args.count)
            ]
            
            # 等待所有任务完成
            for future in concurrent.futures.as_completed(futures):
                future.result()
                
        print("\n==== 所有并发任务已完成 ====")

    except Exception as e:
        print(f"\n❌ 主程序执行遇到异常: {e}")
