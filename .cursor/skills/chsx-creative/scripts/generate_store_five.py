import requests
import json
import os
import sys

class NanoBanana2API:
    """
    Nano Banana 2 (Gemini 3.1 Flash Image Preview) Wrapper API
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

    def generate_image(self, prompt: str, imageUrlList: list = None, aspectRatio: str = "9:16", resolution: str = "2K", outputFormat: str = "png", enableGoogleSearch: bool = False):
        if imageUrlList is None:
            imageUrlList = []
        
        final_prompt = prompt
        if imageUrlList and "Generate an image based on the above prompt words and reference pictures" not in final_prompt:
            final_prompt = f"{prompt}. Generate an image based on the above prompt words and reference pictures"

        payload = {
            "aspectRatio": aspectRatio,
            "outputFormat": outputFormat,
            "prompt": final_prompt,
            "resolution": resolution,
            "enableGoogleSearch": enableGoogleSearch
        }
        
        if imageUrlList:
            payload["imageUrlList"] = imageUrlList

        print(f"[*] Sending request to generate image...")
        
        try:
            response = requests.post(
                self.url, 
                headers=self.headers, 
                json=payload, 
                timeout=300,
                proxies={"http": None, "https": None}
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            print(f"[-] Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print("Error details:", e.response.text)
            return None

    def download_image(self, image_url: str, save_path: str):
        """Download image to specified path"""
        try:
            response = requests.get(image_url, timeout=60, proxies={"http": None, "https": None})
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"[+] Image saved: {save_path}")
            return True
        except Exception as e:
            print(f"[-] Download failed: {e}")
            return False


def main():
    api = NanoBanana2API()
    
    # Output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(skill_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Five images configuration
    images_config = [
        {
            "name": "img1_sort_colorful_flowers",
            "prompt": """9:16 vertical mobile game store promotional screenshot. 
Deep dark purple background (#2D1B4E) with subtle light floral pattern overlay.
Main scene: Two wooden shelves (warm birch wood, metal bracket supports), each holding 3 terracotta flower pots. Each pot contains 1-3 different colorful 3D semi-realistic flowers (roses, tulips, lavender, daffodils, hibiscus in vivid saturated colors). One purple rose with white glow is shown floating with a curved white dashed arrow from one shelf position to another, indicating player drag-and-sort action. A small white watering can icon near the arrow suggests the merge mechanic.
Flowers in pots are beautifully rendered 3D cartoon style — detailed petals, rich SSS lighting, terracotta pot has embossed floral relief texture.
Bottom banner (20% height): Vivid rose-pink horizontal gradient banner (#FF69B4 to #FF1493), bold white text 'SORT COLORFUL FLOWERS!' in Lilita One style with yellow-gold thick outline and drop shadow. Bottom-left corner: large semi-transparent pink flower cluster decoration.
No human characters. No UI chrome/header. Clean composition.
Professional mobile game App Store screenshot quality."""
        },
        {
            "name": "img2_match_merge",
            "prompt": """9:16 vertical mobile game store promotional screenshot.
Dark background with dramatic centered spotlight (white radial gradient glow from center).
Main scene: Three-step flower evolution shown vertically with white curved dashed arrows connecting them:
- Top: One small single daffodil stem (simple, small)
- Middle: A terracotta pot with 3 medium daffodils (fuller)
- Bottom (hero shot, largest): A gorgeous overflowing terracotta pot with a massive lush bouquet of 10+ golden daffodils, glowing with warm light, leaves rich green, flowers fully bloomed and radiant.
The evolution path is clear — small → potted → magnificent bouquet. Background fades from dark at edges to warm light at center where the biggest bouquet is.
Bottom banner (20% height): Lavender-purple gradient banner (#9B59B6 to #6C3483), bold white text 'MATCH & MERGE!' in thick rounded font with gold outline. Bottom-left corner: large purple hydrangea cluster decoration.
No human characters. No game UI. Cinematic 3D flower art.
Professional mobile game App Store screenshot quality."""
        },
        {
            "name": "img3_relaxing_puzzles",
            "prompt": """9:16 vertical mobile game store promotional screenshot.
Medium cobalt-blue background (#1C3A6E) with soft decorative arabesque/curl pattern overlay in lighter blue.
Main scene: Five horizontal wooden shelves stacked vertically (shelf bracket style), each shelf holding 4-5 terracotta flower pots densely arranged. Each pot has 2-3 mixed flowers in vivid different color combinations — creating a rich tapestry of reds, whites, purples, yellows, oranges, pinks. One specific pot in the middle of the grid has a white glow/highlight indicating it is selected. Total approximately 20 pots visible — conveying a large puzzle board.
This creates the feel of a busy, colorful, satisfying puzzle grid.
Bottom banner (20% height): Warm orange gradient banner (#FF8C00 to #FF4500), bold white text 'RELAXING PUZZLES' in thick rounded font with gold outline. Bottom-left corner: large golden marigold cluster decoration.
No human characters. Grid-like, satisfying composition.
Professional mobile game App Store screenshot quality."""
        },
        {
            "name": "img4_use_boosters",
            "prompt": """9:16 vertical mobile game store promotional screenshot.
Dark teal-green background (#1A3045) with subtle pattern overlay.
Main scene: Same wooden shelf + terracotta flower pot grid layout as other images (4-5 shelves with various flowers). Center of the image: A GIANT oversized cartoon booster hammer (toy-like, red handle with yellow mallet head, flower icon stamped on the face) slamming down into the center of the grid. The impact point has a dramatic shatter/burst effect — white shockwave and sparkle explosion, a few pots shattered with flowers flying outward. This booster hammer is the absolute hero of the image, taking up approximately 40% of the image area.
Additional small details near the bottom: some pots transformed into topiary spheres (round green bush shapes), a decorative butterfly on one pot — suggesting reward/special content.
Bottom banner (20% height): Fresh green gradient banner (#27AE60 to #1E8449), bold white text 'USE BOOSTERS!' in thick rounded font with gold-yellow outline. Bottom-left corner: large orange-red poppy cluster decoration.
No human characters. Action/impact visual energy.
Professional mobile game App Store screenshot quality."""
        },
        {
            "name": "img5_flower_collection",
            "prompt": """9:16 vertical mobile game store promotional screenshot.
Dark walnut wood texture background (planks visible, rich dark brown #2C1A0E).
Purple awning/scalloped border along the very top edge of the image.
Main scene: A 3x4 grid (12 cells) of flower collection display medallions. Each medallion:
- Outer ring: Gold circular frame (thick metallic gold border)
- Inner circle: Filled with a single species of flowers in a lush round bouquet arrangement (12 different species: Forget-me-not blue, Daisy white, Tulip red, Orchid pink, Corn Poppy yellow center, Peony pink, Spring red mix, Lilas purple, Jasmine white, Mimosa yellow, Magnolia white, Sunflower yellow)
- Name ribbon: Purple satin ribbon badge below each circle with the flower name in white text
- Progress bar: Green progress bar below the ribbon showing completion (e.g. '4/6', '10/10 ✓')
- Completed medallions show a green checkmark
The grid is clean and evenly spaced, conveying rich collectable content.
Bottom banner (20% height): Bright yellow gradient banner (#F1C40F to #E67E22), bold white text 'FLOWER COLLECTION' in thick rounded font with gold-orange outline. Bottom-left corner: large yellow daffodil cluster decoration.
No human characters. Organized, aspirational content display.
Professional mobile game App Store screenshot quality."""
        }
    ]
    
    results = []
    
    for i, config in enumerate(images_config, 1):
        print(f"\n========== Generating {i}/5: {config['name']} ==========")
        
        result = api.generate_image(
            prompt=config['prompt'],
            aspectRatio="9:16",
            resolution="2K",
            outputFormat="png",
            enableGoogleSearch=False
        )
        
        # Parse response - API returns different format
        if result and result.get('code') == '200':
            image_list = result.get('data', {}).get('imageList', [])
            if image_list and len(image_list) > 0:
                image_url = image_list[0].get('url')
                save_path = os.path.join(output_dir, f"{config['name']}.png")
                
                # Download image
                if api.download_image(image_url, save_path):
                    # Save metadata
                    meta_path = os.path.join(output_dir, f"{config['name']}.meta.json")
                    meta_data = {
                        "name": config['name'],
                        "imageUrl": image_url,
                        "prompt": config['prompt'],
                        "aspectRatio": "9:16",
                        "resolution": "2K",
                        "outputFormat": "png",
                        "success": True
                    }
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(meta_data, f, indent=2, ensure_ascii=False)
                    
                    results.append({
                        "name": config['name'],
                        "path": save_path,
                        "url": image_url,
                        "status": "success"
                    })
                else:
                    results.append({
                        "name": config['name'],
                        "status": "download_failed",
                        "url": image_url
                    })
            else:
                results.append({
                    "name": config['name'],
                    "status": "no_image_in_response"
                })
        else:
            error_msg = result.get('msg', 'Unknown error') if result else 'API request failed'
            print(f"[-] Generation failed: {error_msg}")
            results.append({
                "name": config['name'],
                "status": "generation_failed",
                "error": error_msg
            })
    
    # Output summary
    print("\n========== Generation Summary ==========")
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Success: {success_count}/{len(images_config)}")
    
    for r in results:
        status_icon = "[OK]" if r['status'] == 'success' else "[FAIL]"
        print(f"{status_icon} {r['name']}: {r['status']}")
    
    return results


if __name__ == "__main__":
    main()

