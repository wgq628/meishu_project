import os
import requests
import json
from nano_banana2_api import NanoBanana2API

import urllib.request
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
            "name": "img1_sort_colorful_flowers.png",
            "prompt": (
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
        },
        {
            "name": "img2_match_merge.png",
            "prompt": (
                "9:16 vertical mobile game store promotional screenshot. "
                "Dark background with dramatic centered spotlight (white radial gradient glow from center). "
                "Main scene: Three-step flower evolution shown vertically with white curved dashed arrows connecting them: "
                "- Top: One small single daffodil stem (simple, small) "
                "- Middle: A terracotta pot with 3 medium daffodils (fuller) "
                "- Bottom (hero shot, largest): A gorgeous overflowing terracotta pot with a massive lush bouquet of 10+ golden daffodils, glowing with warm light, leaves rich green, flowers fully bloomed and radiant. "
                "The evolution path is clear — small → potted → magnificent bouquet. Background fades from dark at edges to warm light at center where the biggest bouquet is. "
                "Bottom banner (20% height): Lavender-purple gradient banner (#9B59B6 to #6C3483), bold white text 'MATCH & MERGE!' in thick rounded font with gold outline. Bottom-left corner: large purple hydrangea cluster decoration. "
                "No human characters. No game UI. Cinematic 3D flower art. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "name": "img3_relaxing_puzzles.png",
            "prompt": (
                "9:16 vertical mobile game store promotional screenshot. "
                "Medium cobalt-blue background (#1C3A6E) with soft decorative arabesque/curl pattern overlay in lighter blue. "
                "Main scene: Five horizontal wooden shelves stacked vertically (shelf bracket style), each shelf holding 4-5 terracotta flower pots densely arranged. Each pot has 2-3 mixed flowers in vivid different color combinations — creating a rich tapestry of reds, whites, purples, yellows, oranges, pinks. One specific pot in the middle of the grid has a white glow/highlight indicating it is selected. Total approximately 20 pots visible — conveying a large puzzle board. "
                "This creates the feel of a busy, colorful, satisfying puzzle grid. "
                "Bottom banner (20% height): Warm orange gradient banner (#FF8C00 to #FF4500), bold white text 'RELAXING PUZZLES' in thick rounded font with gold outline. Bottom-left corner: large golden marigold cluster decoration. "
                "No human characters. Grid-like, satisfying composition. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "name": "img4_use_boosters.png",
            "prompt": (
                "9:16 vertical mobile game store promotional screenshot. "
                "Dark teal-green background (#1A3045) with subtle pattern overlay. "
                "Main scene: Same wooden shelf + terracotta flower pot grid layout as other images (4-5 shelves with various flowers). Center of the image: A GIANT oversized cartoon booster hammer (toy-like, red handle with yellow mallet head, flower icon stamped on the face) slamming down into the center of the grid. The impact point has a dramatic shatter/burst effect — white shockwave and sparkle explosion, a few pots shattered with flowers flying outward. This booster hammer is the absolute hero of the image, taking up approximately 40% of the image area. "
                "Additional small details near the bottom: some pots transformed into topiary spheres (round green bush shapes), a decorative butterfly on one pot — suggesting reward/special content. "
                "Bottom banner (20% height): Fresh green gradient banner (#27AE60 to #1E8449), bold white text 'USE BOOSTERS!' in thick rounded font with gold-yellow outline. Bottom-left corner: large orange-red poppy cluster decoration. "
                "No human characters. Action/impact visual energy. "
                "Professional mobile game App Store screenshot quality."
            )
        },
        {
            "name": "img5_flower_collection.png",
            "prompt": (
                "9:16 vertical mobile game store promotional screenshot. "
                "Dark walnut wood texture background (planks visible, rich dark brown #2C1A0E). "
                "Purple awning/scalloped border along the very top edge of the image. "
                "Main scene: A 3x4 grid (12 cells) of flower collection display medallions. Each medallion: "
                "- Outer ring: Gold circular frame (thick metallic gold border) "
                "- Inner circle: Filled with a single species of flowers in a lush round bouquet arrangement (12 different species: Forget-me-not blue, Daisy white, Tulip red, Orchid pink, Corn Poppy yellow center, Peony pink, Spring red mix, Lilas purple, Jasmine white, Mimosa yellow, Magnolia white, Sunflower yellow) "
                "- Name ribbon: Purple satin ribbon badge below each circle with the flower name in white text "
                "- Progress bar: Green progress bar below the ribbon showing completion (e.g. '4/6', '10/10 ✓') "
                "- Completed medallions show a green checkmark "
                "The grid is clean and evenly spaced, conveying rich collectable content. "
                "Bottom banner (20% height): Bright yellow gradient banner (#F1C40F to #E67E22), bold white text 'FLOWER COLLECTION' in thick rounded font with gold-orange outline. Bottom-left corner: large yellow daffodil cluster decoration. "
                "No human characters. Organized, aspirational content display. "
                "Professional mobile game App Store screenshot quality."
            )
        }
    ]

    for item in images:
        print(f"========== Generating {item['name']} ==========")
        res = api.generate_image(
            prompt=item["prompt"],
            aspectRatio="9:16",
            resolution="2K",     
            enableGoogleSearch=False
        )
        if res and res.get("code") == "200" and res.get("data") and res["data"].get("imageList"):
            img_url = res["data"]["imageList"][0]["url"]
            file_path = os.path.join(output_dir, item["name"])
            download_image(img_url, file_path)
        else:
            print(f"Failed to generate {item['name']}. Response: {json.dumps(res, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()

