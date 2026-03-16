import os
import sys
import subprocess
import argparse
import requests
import json
import urllib.request
from datetime import datetime

# 自动安装缺失的依赖库
try:
    from PIL import Image, ImageOps
except ImportError:
    print("[*] 正在环境内自动安装需要的 Pillow 图像处理库...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageOps

# --- API 配置 ---
API_URL = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"
DEFAULT_ACCESS_KEY_ID = os.environ.get("BANANA2_ACCESS_KEY_ID", "")
DEFAULT_ACCESS_KEY_SECRET = os.environ.get("BANANA2_ACCESS_KEY_SECRET", "")
if not DEFAULT_ACCESS_KEY_ID or not DEFAULT_ACCESS_KEY_SECRET:
    raise SystemExit("请先设置环境变量 BANANA2_ACCESS_KEY_ID 和 BANANA2_ACCESS_KEY_SECRET，再运行 Moloco 批量脚本。")

# --- 预设合法尺寸及推导相近长宽比的大模型参数 ---
MOLOCO_TARGET_SIZES = {
    "1200x628": "16:9",   # 最佳匹配近似值，用于生图扩展，随后精准裁剪
    "1200x600": "16:9",   
    "1200x222": "5:1",    
    "1200x1600": "3:4",
    "720x1280": "9:16",
    "720x960": "3:4",
    "720x720": "1:1",
    "300x250": "5:4",
    "320x50": "8:1",
    "320x100": "4:1",
    "320x480": "2:3",
    "480x320": "3:2",
    "728x90": "8:1",
    "256x256": "1:1"
}

def upload_to_tmp(image_path: str) -> str:
    """上传本地图片到免费的临时图床获取公网直链。加入异常抵抗"""
    print(f"[*] 正在上传图像素材提取特征: {os.path.basename(image_path)}")
    with open(image_path, 'rb') as f:
        # Route 1: catbox
        try:
            resp = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=40)
            if resp.status_code == 200 and resp.text.startswith("http"):
                return resp.text.strip()
        except:
            pass
        
        # Route 2: tmpfiles
        f.seek(0)
        try:
            resp2 = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=40)
            if resp2.status_code == 200:
                url = resp2.json().get("data", {}).get("url")
                if url:
                    return url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
        except Exception as e:
            print("tmpfiles.org upload failed:", e)
            pass
            
        # Route 3: uguu.se
        f.seek(0)
        try:
            resp3 = requests.post("https://uguu.se/upload.php", files={"files[]": f}, timeout=40)
            if resp3.status_code == 200:
                data = resp3.json()
                if data.get("success") and data.get("files"):
                    return data["files"][0]["url"]
        except Exception as e:
            print("uguu.se upload failed:", e)
            pass
            
    raise Exception(f"图片 {os.path.basename(image_path)} 的云端上传完全失败，请检查网络。")

def generate_image(prompt: str, image_url: str, aspect_ratio: str) -> str:
    """调用 API 按特定画幅比例发散生成近似画面"""
    headers = {
        "X-Request-req-accessKeyId": DEFAULT_ACCESS_KEY_ID,
        "X-Request-req-accessKeySecret": DEFAULT_ACCESS_KEY_SECRET,
        "Content-Type": "application/json"
    }
    
    # 强制加上参考图扩增指令
    final_prompt = f"{prompt}. strictly follow the aspect ratio of {aspect_ratio}. Match the artistic style perfectly. Generate an image based on the above prompt words and reference pictures"
    
    payload = {
        "prompt": final_prompt,
        "aspectRatio": aspect_ratio,
        "resolution": "1K",  # 规范使用 1K 画质
        "outputFormat": "png",
        "imageUrlList": [image_url],
        "enableGoogleSearch": False
    }
    
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") == "200" and data.get("data") and data["data"].get("imageList"):
        return data["data"]["imageList"][0]["url"]
    else:
        raise Exception(f"Banana2 API 抛出错误: {json.dumps(data, ensure_ascii=False)}")

def resize_and_crop(image_path: str, target_w: int, target_h: int, output_path: str):
    """运用 PIL 提供像素级的等比中心裁剪。"""
    img = Image.open(image_path).convert("RGBA")
    
    # 采用无缝中心裁剪，放弃双层模糊方案
    img_cropped = ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS)
    img_cropped.convert("RGB").save(output_path, quality=100)

def main():
    parser = argparse.ArgumentParser(description="Moloco 素材矩阵批量尺寸自动化流水线")
    parser.add_argument("--images", type=str, required=True, help="逗号分隔的本地源图片绝对路径")
    parser.add_argument("--prompt", type=str, required=True, help="对这一批图片的统一风格、元素描述 (中文)")
    parser.add_argument("--sizes", type=str, default="1200x628,1200x600,720x1280,1200x1600,720x720", help="逗号分隔的目标规格尺寸表")
    parser.add_argument("--output", type=str, default=r"output", help="根输出目录")
    
    args = parser.parse_args()
    
    # 清洗入参数组
    image_list = [p.strip() for p in args.images.split(',') if p.strip()]
    size_list = [s.strip() for s in args.sizes.split(',') if s.strip()]
    
    # 建立日期主目录
    date_str = datetime.now().strftime("%Y%m%d")
    date_dir = os.path.join(args.output, date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    print(f"\n==============================================")
    print(f"🚀 Moloco 素材矩阵全自动重构系统 正在启动")
    print(f"==============================================")
    print(f"主存储池: {date_dir}")
    print(f"待处理原生图数量: {len(image_list)} 张")
    print(f"目标渲染尺寸目标: {len(size_list)} 个规格")
    
    # 第一阶段：静默预先上传全部参考源图，缓存直链 (并行)
    uploaded_urls = {}
    print("\n[阶段一] 同铺设图片云端索引(并行上传)...")
    
    import concurrent.futures
    import uuid
    
    def upload_task(img):
        return img, upload_to_tmp(img)
        
    valid_images = [img for img in image_list if os.path.exists(img)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_img = {executor.submit(upload_task, img): img for img in valid_images}
        for future in concurrent.futures.as_completed(future_to_img):
            img = future_to_img[future]
            try:
                img, url = future.result()
                uploaded_urls[img] = url
                print(f"  [√] 图片 {os.path.basename(img)} 上传完毕")
            except Exception as e:
                print(f"  [X] ⚠️ 图片 {os.path.basename(img)} 上传失败: {e}")
    
    if not uploaded_urls:
         print("\n❌ 错误：所有参考图均不存在或无法上传，任务取消。")
         return

    # 第二阶段：遍历每一个目标尺寸规格，针对每张原图调用生图+裁剪 (多线并行)
    print("\n[阶段二] 开始矩阵级 AI 重绘与多规剪裁(并行处理)...")
    tasks = []
    for target_size in size_list:
        if target_size not in MOLOCO_TARGET_SIZES:
            print(f"  [跳过] 不认识的或未支持的商业化尺寸: {target_size}")
            continue
            
        w, h = map(int, target_size.split('x'))
        banana_ratio = MOLOCO_TARGET_SIZES[target_size]
        
        # 为该尺寸创建专属子文件夹
        size_dir = os.path.join(date_dir, target_size)
        os.makedirs(size_dir, exist_ok=True)
        
        for idx, img_path in enumerate(image_list):
            if img_path not in uploaded_urls:
                continue
            tasks.append({
                'target_size': target_size,
                'w': w,
                'h': h,
                'banana_ratio': banana_ratio,
                'size_dir': size_dir,
                'idx': idx,
                'img_url': uploaded_urls[img_path],
                'prompt': args.prompt
            })
            
    def process_task(task):
        target_size = task['target_size']
        idx = task['idx']
        print(f" |-> [{target_size}] 发令重绘第 {idx+1} 张概念图...")
        try:
            # 步骤 A：交由 Banana2 按照近似画幅扩充/发散视野
            gen_url = generate_image(task['prompt'], task['img_url'], task['banana_ratio'])
            
            # 步骤 B：拉取原始生图结果至本地缓存，带 uuid 防止多线程读写覆盖
            temp_path = os.path.join(task['size_dir'], f"_temp_{idx+1}_{uuid.uuid4().hex[:6]}.png")
            urllib.request.urlretrieve(gen_url, temp_path)
            
            # 步骤 C：执行核心逻辑 -> PIL 像素级强制等比切割，保障 Moloco 过审
            final_path = os.path.join(task['size_dir'], f"moloco_img{idx+1}_{target_size}.png")
            resize_and_crop(temp_path, task['w'], task['h'], final_path)
            
            # 步骤 D：打扫战场
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            print(f"     ✅ [{target_size}] 第 {idx+1} 张完成. 落盘至 -> / {os.path.basename(final_path)}")
        except Exception as e:
            print(f"     ❌ [{target_size}] 第 {idx+1} 张失败: {e}")

    # 启动线程池执行并行生成任务
    if tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(process_task, tasks)
            
    print(f"\n🎉 ==== 全矩阵流水线收工！请在 {date_dir} 验收成品。 ====")

if __name__ == "__main__":
    main()
