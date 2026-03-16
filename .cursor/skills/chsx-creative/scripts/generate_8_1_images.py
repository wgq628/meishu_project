import os
import urllib.request
import json
from nano_banana2_api import NanoBanana2API

def download_image(url, filepath):
    print(f"Downloading {url} to {filepath}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Saved to {filepath}")
    except Exception as e:
        print(f"Failed to download image: {e}")

def main():
    api = NanoBanana2API()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(skill_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    images = [
        {
            "id": "img1",
            "name": "sort_magic_flowers",
            "prompt": (
                "Mobile game store promotional screenshot. "
                "Deep dark purple spooky background (#2D1B4E) with subtle light cobweb and bat pattern overlay. "
                "Main scene: Two wooden shelves (aged dark wood, iron bracket supports), each holding 3 jack-o'-lantern shaped terracotta flower pots. "
                "Each pot contains 1-3 different colorful 3D semi-realistic flowers (dark roses, glowing orange tulips, purple lavender, magic flowers in vivid saturated colors). "
                "One glowing purple rose is shown floating with a curved white dashed arrow from one shelf position to another, indicating player drag-and-sort action. "
                "A small white ghost icon near the arrow suggests the merge mechanic. "
                "Flowers in pots are beautifully rendered 3D cartoon style — detailed petals, rich SSS lighting, pumpkin pot has carved face relief texture. "
                "Bottom banner (20% height): Vivid rose-pink horizontal gradient banner (#FF69B4 to #FF1493), bold white text 'SORT MAGIC FLOWERS!' in Lilita One style with yellow-gold thick outline and drop shadow. "
                "Bottom-left corner: large semi-transparent glowing pink flower and bat decoration. "
                "No human characters. No UI chrome/header. Clean composition. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "id": "img2",
            "name": "match_merge",
            "prompt": (
                "Mobile game store promotional screenshot. "
                "Dark spooky background with dramatic centered spotlight (purple radial gradient glow from center). "
                "Main scene: Three-step magic flower evolution shown vertically with white curved dashed arrows connecting them: "
                "- Top: One small single dark purple magical stem (simple, small) "
                "- Middle: A jack-o'-lantern terracotta pot with 3 medium glowing purple flowers (fuller) "
                "- Bottom (hero shot, largest): A gorgeous overflowing spooky terracotta pot with a massive lush bouquet of 10+ glowing purple and orange magical flowers, glowing with warm eerie light, leaves dark green, flowers fully bloomed and radiant with tiny floating sparkles. "
                "The evolution path is clear — small → potted → magnificent bouquet. Background fades from dark at edges to warm light at center where the biggest bouquet is. "
                "Bottom banner (20% height): Lavender-purple gradient banner (#9B59B6 to #6C3483), bold white text 'MATCH & MERGE!' in thick rounded font with gold outline. Bottom-left corner: large purple spooky hydrangea cluster and spiderweb decoration. "
                "No human characters. No game UI. Cinematic 3D flower art. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "id": "img3",
            "name": "spooky_puzzles",
            "prompt": (
                "Mobile game store promotional screenshot. "
                "Medium cobalt-blue night sky background (#1C3A6E) with soft decorative cobweb overlay in lighter blue and floating dust. "
                "Main scene: Five horizontal wooden shelves stacked vertically, each shelf holding 4-5 jack-o'-lantern terracotta flower pots densely arranged. Each pot has 2-3 mixed magical flowers in vivid different color combinations (deep reds, glowing purples, bright oranges, ghostly whites). One specific pot in the middle of the grid has a bright orange glow/highlight indicating it is selected. Total approximately 20 pots visible — conveying a large puzzle board. Little floating bats and glowing embers add Halloween atmosphere. "
                "Bottom banner (20% height): Warm orange gradient banner (#FF8C00 to #FF4500), bold white text 'SPOOKY PUZZLES' in thick rounded font with gold outline. Bottom-left corner: large golden glowing marigold cluster decoration. "
                "No human characters. Grid-like, satisfying composition. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "id": "img4",
            "name": "use_boosters",
            "prompt": (
                "Mobile game store promotional screenshot. "
                "Dark teal-green eerie background (#1A3045) with subtle spooky pattern overlay. "
                "Main scene: Same aged wooden shelf + jack-o'-lantern terracotta flower pot grid layout as other images. Center of the image: A GIANT oversized cartoon booster glowing pumpkin bomb (toy-like, purple handle with glowing orange head) slamming down into the center of the grid. The impact point has a dramatic shatter/burst effect — lime green magical shockwave and star explosion, a few pumpkin pots shattered with magical flowers flying outward. This booster is the absolute hero of the image, taking up approximately 40% of the image area. "
                "Additional small details near the bottom: some pots transformed into creepy vines, a decorative glowing bat on one pot — suggesting reward/special content. "
                "Bottom banner (20% height): Fresh green gradient banner (#27AE60 to #1E8449), bold white text 'USE BOOSTERS!' in thick rounded font with gold-yellow outline. Bottom-left corner: large orange-red glowing poppy cluster decoration. "
                "No human characters. Action/impact visual energy. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "id": "img5",
            "name": "magic_collection",
            "prompt": (
                "Mobile game store promotional screenshot. "
                "Dark walnut wood texture background (planks visible, rich dark brown #2C1A0E) covered with faint transparent cobwebs. "
                "Spooky purple and orange scalloped border along the very top edge of the image. "
                "Main scene: A 3x4 grid (12 cells) of magic flower collection display medallions. Each medallion: "
                "- Outer ring: Antique gold circular frame (thick metallic gold border) "
                "- Inner circle: Filled with a single species of magic Halloween flowers in a lush round bouquet arrangement. "
                "- Name ribbon: Purple satin ribbon badge below each circle with the flower name in white text "
                "- Progress bar: Green progress bar below the ribbon showing completion (e.g. '4/6', '10/10 ✓') "
                "- Completed medallions show a green checkmark "
                "The grid is clean and evenly spaced, conveying rich collectable content. "
                "Bottom banner (20% height): Bright yellow gradient banner (#F1C40F to #E67E22), bold white text 'MAGIC COLLECTION' in thick rounded font with gold-orange outline. Bottom-left corner: large yellow glowing daffodil cluster decoration. "
                "No human characters. Organized, aspirational content display. "
                "Professional mobile game App Store screenshot quality."
            )
        }
    ]

    ratio_val = "8:1"
    generated_files = []

    print(f"\n===================== TARGET RATIO: {ratio_val} =====================")
    for item in images:
        file_name = f"halloween_8_1_{item['id']}_{item['name']}.png"
        full_prompt = f"8:1 ultra-wide panoramic shape. " + item["prompt"]
        print(f"========== Generating {file_name} ==========")
        res = api.generate_image(
            prompt=full_prompt,
            aspectRatio=ratio_val,
            resolution="2K",     
            enableGoogleSearch=False
        )
        if res and res.get("code") == "200" and res.get("data") and res["data"].get("imageList"):
            img_url = res["data"]["imageList"][0]["url"]
            file_path = os.path.join(output_dir, file_name)
            download_image(img_url, file_path)
            print(f"Successfully saved {file_name}")
            generated_files.append({
                "title": item['name'].replace('_', ' ').title(), 
                "file_name": file_name, 
                "prompt": full_prompt
            })
        else:
            print(f"Failed to generate {file_name}. Response: {json.dumps(res, indent=2, ensure_ascii=False)}")

    # Generate a MarkDown file for previewing all downloaded images
    preview_md_path = os.path.join(output_dir, "halloween_8_1_preview.md")
    try:
        with open(preview_md_path, "w", encoding="utf-8") as md_file:
            md_file.write("# 🎃 万圣节商店宣传图预览 (8:1 全景宽屏版)\n\n")
            md_file.write("本文档由生图脚本自动生成，用于快速预览当次生成的 5 张 8:1 比例超广角/横幅插花三消商店图。\n\n")
            
            for item in generated_files:
                md_file.write(f"### {item['title']}\n\n")
                md_file.write(f"![{item['title']}](./{item['file_name']})\n\n")
                md_file.write(f"> **Prompt**: {item['prompt']}\n\n")
                md_file.write("---\n\n")
        print(f"\n[+] 成功生成可视化预览文档: {preview_md_path}")
    except Exception as e:
        print(f"\n[-] 生成可视化预览文档失败: {e}")

if __name__ == "__main__":
    main()

