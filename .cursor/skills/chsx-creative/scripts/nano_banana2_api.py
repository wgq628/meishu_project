import requests
import json
import os

class NanoBanana2API:
    """
    Nano Banana 2 (Gemini 3.1 Flash Image Preview) Wrapper API
    基于 uqualities.com 提供的服务端点。
    """
    def __init__(self, access_key_id=None, access_key_secret=None):
        access_key_id = access_key_id or os.environ.get("BANANA2_ACCESS_KEY_ID", "")
        access_key_secret = access_key_secret or os.environ.get("BANANA2_ACCESS_KEY_SECRET", "")
        if not access_key_id or not access_key_secret:
            raise RuntimeError("请先设置环境变量 BANANA2_ACCESS_KEY_ID 和 BANANA2_ACCESS_KEY_SECRET。")
        self.url = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"
        self.headers = {
            "X-Request-req-accessKeyId": access_key_id,
            "X-Request-req-accessKeySecret": access_key_secret,
            "Content-Type": "application/json"
        }

    def generate_image(self, 
                       prompt: str, 
                       imageUrlList: list = None, 
                       aspectRatio: str = "1:1", 
                       resolution: str = "1K", 
                       outputFormat: str = "png", 
                       enableGoogleSearch: bool = False):
        """
        发送请求生成图片 (调用 Nano Banana 2 接口)
        
        :param prompt: 提示词描述。
        :param imageUrlList: 参考图 URL 的列表，若为纯文生图则留空或传 None。支持最多 14 张参考图（详见官方文档）。
        :param aspectRatio: 长宽比。如 "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9"
        :param resolution: 分辨率。如 "512px", "1K", "2K", "4K"
        :param outputFormat: 期待的输出格式 (如 "png", "jpeg")
        :param enableGoogleSearch: 是否启用 Google 搜索引擎进行搜索增强 (Search Grounding)
        :return: API 响应的原生 JSON 字典
        """
        if imageUrlList is None:
            imageUrlList = []
            
        # 按照 api.txt 中的说明，使用参考图时提示词一般带有后缀
        final_prompt = prompt
        if imageUrlList and "Generate an image based on the above prompt words and reference pictures" not in final_prompt:
            final_prompt = f"{prompt}. Generate an image based on the above prompt words and reference pictures"

        payload: dict = {
            "aspectRatio": aspectRatio,
            "outputFormat": outputFormat,
            "prompt": final_prompt,
            "resolution": resolution,
            "enableGoogleSearch": enableGoogleSearch
        }
        
        # 如果 imageUrlList 不为空才传这个字段，防止后端解析空列表时报错
        if imageUrlList:
            payload["imageUrlList"] = imageUrlList

        print(f"[*] 发送请求至 Nano Banana 2 API...")
        print("[*] 请求体 (Payload):")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        try:
            # 发送 POST 请求 (设置 proxies={"http": None, "https": None} 可防止系统代理导致的 ProxyError)
            response = requests.post(
                self.url, 
                headers=self.headers, 
                json=payload, 
                timeout=300,
                proxies={"http": None, "https": None}
            )
            response.raise_for_status()  # 检查 HTTP 状态码
            result = response.json()
            print("[+] 请求成功！")
            return result
        except requests.exceptions.RequestException as e:
            print(f"[-] 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print("错误详情:", e.response.text)
            return None


if __name__ == "__main__":
    # 实例化 API 并从环境变量读取密钥
    api = NanoBanana2API()
    
    print("========== 开始生成: 插花三消·商店图 ==========")
    
    # 按照技能指南中提供的图1核心玩法图 Prompt 示例编写
    store_prompt = (
        "9:16 vertical mobile game store promotional screenshot. "
        "Deep dark purple background (#2D1B4E) with subtle light floral pattern overlay. "
        "Main scene: Two wooden shelves (warm birch wood, metal bracket supports), each holding 3 terracotta flower pots. "
        "Each pot contains 1-3 different colorful 3D semi-realistic flowers (roses, tulips, lavender, daffodils, hibiscus in vivid saturated colors). "
        "One purple rose with white glow is shown floating with a curved white dashed arrow from one shelf position to another, indicating player drag-and-sort action. "
        "A small white watering can icon near the arrow suggests the merge mechanic. "
        "Flowers in pots are beautifully rendered 3D cartoon style — detailed petals, rich SSS lighting, terracotta pot has embossed floral relief texture. "
        "Bottom banner (20% height): Vivid rose-pink horizontal gradient banner (#FF69B4 to #FF1493), bold white text 'SORT COLORFUL FLOWERS!' in Lilita One style with yellow-gold thick outline and drop shadow. "
        "Bottom-left corner: large semi-transparent pink flower cluster decoration. "
        "No human characters. No UI chrome/header. Clean composition. "
        "Professional mobile game App Store screenshot quality."
    )
    
    res = api.generate_image(
        prompt=store_prompt,
        aspectRatio="9:16",
        resolution="2K",     
        enableGoogleSearch=False
    )
    
    print("API 响应:", json.dumps(res, indent=2, ensure_ascii=False))
