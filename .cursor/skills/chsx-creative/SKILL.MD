---
name: chsx-store-five-image-designer
description: 专为「插花三消」游戏设计商店五图的流程规范。定义原始风格基准与可延展的风格参数框架，用户可自定义背景、花盆、层架、花卉、Banner 等变量，在保持核心玩法与竖版9:16规范的前提下实现风格自由延展。
---

# 插花三消 · 商店五图设计规范（原始风格 + 可延展框架）

## ⚠️ 重要说明

本规范定义**插花三消**的**原始风格基准**（基于参考图提炼），同时提供**风格参数化框架**，用户可通过指定各变量的自定义值来延展任意风格。核心不变：花盆、层架、花卉、合并升级、道具、图鉴的玩法结构。

---

## 📁 目录结构

```
.cursor/skills/chsx-creative/
├── SKILL.MD                  # 本规范文件
├── assets/                   # ⭐ 参考图片目录（生成图像前必须查看）
│   └── *.png / *.jpg         # 往期五图参考素材、竞品截图等视觉参考
├── reference/                # 文字参考资料
│   ├── wutu.MD               # 五图策略参考
│   ├── moloco.md             # Moloco 素材参考
│   └── juqing.md             # 剧情相关参考
└── output/                   # 输出目录（每次生成后自动存入）
    ├── img1_sort_colorful_flowers.png
    ├── img2_match_merge.png
    ├── img3_relaxing_puzzles.png
    ├── img4_use_boosters.png
    └── img5_flower_collection.png
```

> **🔍 生成图像前必读**：在调用生图工具之前，必须先查看 `assets/` 目录中的参考图片，以确保生成的图像与游戏实际风格保持一致。使用 `list_dir` 列出目录内容，再用 `view_file` 查看具体图片。



## 📐 尺寸与比例策略

> **💡 Banana2 生图脚本支持**：本技能目录中已包含专属绘图脚本（`scripts/nano_banana2_api.py`），支持直接通过代码调用并通过 `-AspectRatio "9:16"` 参数等灵活输出原生竖图，**不再受到 1:1 格式限制**。因此，出图时**务必优先使用 scripts 目录下的脚本**进行生图。

---

## 🎨 原始风格规范（从参考图提炼的基准值）

> **用途**：当用户**未指定**风格时，使用以下默认值。用户指定自定义风格时，仅替换其明确提到的变量，其余沿用此处基准。

### 背景
- **颜色**：深色饱和背景，非黑非白，有明显色相倾向：
  - 深紫色（Purple `#2D1B4E`）
  - 深藏青色（Navy Teal `#1A3045`）
  - 深钴蓝色（Cobalt `#1C3A6E`）
  - 深木色（Dark Walnut `#2C1A0E`，用于图鉴图）
- **纹理/装饰**：部分背景有半透明的浅色花纹叠加（云纹/曲线），增加层次感，但不抢眼
- **聚光灯**：核心道具/花盆上方常有白色径向渐变聚光灯效果，突出主体

### 主体视觉元素
- **花盆**：经典陶土花盆（Terracotta `#C4773A`），表面有浮雕花卉图案，厚实温暖
- **层架**：浅褐色木质层板，配金属/深色L型支架，层板有细腻木纹，整体写实质感
- **花卉**：半写实3D卡通风格，每盆1-3株不同花卉混搭，花型清晰辨识度高（玫瑰/郁金香/薰衣草/菊花/水仙/鸢尾等），颜色高饱和但不失真实感
- **引导箭头**：白色虚线圆点弧形箭头（Dashed Arrow），用于展示游戏操作流程

### 底部 Banner（核心识别元素）
- **位置**：图片底部约15-20%区域
- **形状**：全宽横幅，上边缘有轻微的弧形或直线裁切
- **颜色**：每张图配不同颜色的渐变横幅（形成五图差异化）：
  - 图1：玫瑰粉渐变 `#FF69B4 → #FF1493`
  - 图2：薰衣草紫渐变 `#9B59B6 → #6C3483`
  - 图3：活力橙渐变 `#FF8C00 → #FF4500`
  - 图4：清新绿渐变 `#27AE60 → #1E8449`
  - 图5：明黄渐变 `#F1C40F → #E67E22`
- **文字样式（严格执行）**：
  - 字体：超粗圆润英文字体（Lilita One / Fredoka One Extra Bold 风格）
  - 颜色：纯白色填充 `#FFFFFF`
  - 描边：黄金色/深色粗描边（约6-8px），让文字在彩色背景上绝对清晰
  - 阴影：深色软阴影，偏移向右下方
- **左下角花卉装饰**：每张图左下角放置一簇半透明/真实感的大花朵图片（与Banner配色呼应），起到视觉收口和品牌一致性的作用

### 图鉴/集合类图特有元素（参考图5）
- 圆形展示框：金色外圆框 + 紫色缎带徽标（标注花卉名称），底部绿色进度条（X/Y格式）
- 深色木纹背景（有别于其他图的纯色背景）
- 3列×4行的整齐网格排列

---

## 🎭 风格参数化框架（用户可自定义延展）

风格**不固定**，用户可通过指定下表变量来自定义任意风格。**未指定的变量**一律使用「原始风格规范」的默认值。

### 可自定义风格变量表

| 变量 | 说明 | 原始默认值（用户未指定时使用） |
|------|------|--------------------------------|
| **background_color** | 背景主色/色系 | 深紫 `#2D1B4E`、深藏青 `#1A3045`、深钴蓝 `#1C3A6E` |
| **background_texture** | 背景纹理/光效 | 半透明云纹、聚光灯效果 |
| **pot_material** | 花盆材质与风格 | 陶土 `#C4773A`、浮雕花卉图案、厚实 |
| **shelf_style** | 层架材质与结构 | 浅褐木质、金属L型支架、细腻木纹 |
| **flower_palette** | 花卉配色/品种倾向 | 玫瑰/郁金香/薰衣草等，高饱和半写实 |
| **banner_five_colors** | 五图 Banner 渐变色 | 图1粉→图2紫→图3橙→图4绿→图5黄 |
| **corner_decoration** | 左下角花卉装饰 | 与 Banner 配色呼应的半透明花簇 |
| **collection_theme** | 图鉴图特殊元素 | 金色圆框、紫色缎带、绿进度条、深木背景 |

### 用户如何自定义

用户可通过**自然语言**描述期望风格，执行者将其转化为上述变量的具体取值。示例：

- 「想要浅色背景、白瓷花盆」→ 设置 `background_color` 为浅色系，`pot_material` 为白瓷
- 「日式简约、竹架、素陶」→ 设置 `shelf_style` 为竹制，`pot_material` 为素陶，`background_texture` 为留白/和纸
- 「梦幻童话、糖果色花盆」→ 设置 `pot_material` 为糖果色陶瓷，`flower_palette` 为粉白/淡紫，`background_color` 为梦幻渐变
- 「万圣节主题」→ 在保持插花三消结构前提下，叠加南瓜、蝙蝠、橙色调等主题元素，文件名加 `halloween_` 前缀

**原则**：用户仅描述希望变化的部分，其余沿用原始默认值；风格可自由组合、无限延展。

---

## 五图规划（内容 × 参考对应）

| 图号 | 功能 | 参考原图对应 | Banner颜色 |
|---|---|---|---|
| 图1 | 核心玩法 · 花盆分类排列 | 参考图1 SORT COLORFUL FLOWERS | 玫瑰粉 |
| 图2 | 合并升级 · 花朵进化链 | 参考图2 MATCH & MERGE | 薰衣草紫 |
| 图3 | 关卡内容 · 满屏花架图 | 参考图3 RELAXING PUZZLES | 活力橙 |
| 图4 | 道具系统 · 强力助推器 | 参考图4 USE BOOSTERS | 清新绿 |
| 图5 | 内容体量 · 花型图鉴集 | 参考图5 FLOWER COLLECTION | 明黄 |

---

## 各图详细 Prompt 规范

> **📌 重要**：以下 Prompt 为**原始风格**的示例。用户指定自定义风格时，需将 `background`、`flower pots`、`shelves`、`banner gradient`、`bottom-left flower cluster` 等描述**替换为「风格参数化框架」中用户给出的变量值**；未指定的变量沿用原始默认值。

---

### 🖼️ 图1：核心玩法图 · SORT COLORFUL FLOWERS

**Prompt 示例**：
```
9:16 vertical mobile game store promotional screenshot. 
Deep dark purple background (#2D1B4E) with subtle light floral pattern overlay.
Main scene: Two wooden shelves (warm birch wood, metal bracket supports), each holding 3 terracotta flower pots. Each pot contains 1-3 different colorful 3D semi-realistic flowers (roses, tulips, lavender, daffodils, hibiscus in vivid saturated colors). One purple rose with white glow is shown floating with a curved white dashed arrow from one shelf position to another, indicating player drag-and-sort action. A small white watering can icon near the arrow suggests the merge mechanic.
Flowers in pots are beautifully rendered 3D cartoon style — detailed petals, rich SSS lighting, terracotta pot has embossed floral relief texture.
Bottom banner (20% height): Vivid rose-pink horizontal gradient banner (#FF69B4 to #FF1493), bold white text 'SORT COLORFUL FLOWERS!' in Lilita One style with yellow-gold thick outline and drop shadow. Bottom-left corner: large semi-transparent pink flower cluster decoration.
No human characters. No UI chrome/header. Clean composition.
Professional mobile game App Store screenshot quality.
```

---

### 🖼️ 图2：合并升级图 · MATCH & MERGE

**Prompt 示例**：
```
9:16 vertical mobile game store promotional screenshot.
Dark background with dramatic centered spotlight (white radial gradient glow from center).
Main scene: Three-step flower evolution shown vertically with white curved dashed arrows connecting them:
- Top: One small single daffodil stem (simple, small)
- Middle: A terracotta pot with 3 medium daffodils (fuller)
- Bottom (hero shot, largest): A gorgeous overflowing terracotta pot with a massive lush bouquet of 10+ golden daffodils, glowing with warm light, leaves rich green, flowers fully bloomed and radiant.
The evolution path is clear — small → potted → magnificent bouquet. Background fades from dark at edges to warm light at center where the biggest bouquet is.
Bottom banner (20% height): Lavender-purple gradient banner (#9B59B6 to #6C3483), bold white text 'MATCH & MERGE!' in thick rounded font with gold outline. Bottom-left corner: large purple hydrangea cluster decoration.
No human characters. No game UI. Cinematic 3D flower art.
Professional mobile game App Store screenshot quality.
```

---

### 🖼️ 图3：关卡内容图 · RELAXING PUZZLES

**Prompt 示例**：
```
9:16 vertical mobile game store promotional screenshot.
Medium cobalt-blue background (#1C3A6E) with soft decorative arabesque/curl pattern overlay in lighter blue.
Main scene: Five horizontal wooden shelves stacked vertically (shelf bracket style), each shelf holding 4-5 terracotta flower pots densely arranged. Each pot has 2-3 mixed flowers in vivid different color combinations — creating a rich tapestry of reds, whites, purples, yellows, oranges, pinks. One specific pot in the middle of the grid has a white glow/highlight indicating it is selected. Total approximately 20 pots visible — conveying a large puzzle board.
This creates the feel of a busy, colorful, satisfying puzzle grid.
Bottom banner (20% height): Warm orange gradient banner (#FF8C00 to #FF4500), bold white text 'RELAXING PUZZLES' in thick rounded font with gold outline. Bottom-left corner: large golden marigold cluster decoration.
No human characters. Grid-like, satisfying composition.
Professional mobile game App Store screenshot quality.
```

---

### 🖼️ 图4：道具系统图 · USE BOOSTERS

**Prompt 示例**：
```
9:16 vertical mobile game store promotional screenshot.
Dark teal-green background (#1A3045) with subtle pattern overlay.
Main scene: Same wooden shelf + terracotta flower pot grid layout as other images (4-5 shelves with various flowers). Center of the image: A GIANT oversized cartoon booster hammer (toy-like, red handle with yellow mallet head, flower icon stamped on the face) slamming down into the center of the grid. The impact point has a dramatic shatter/burst effect — white shockwave and sparkle explosion, a few pots shattered with flowers flying outward. This booster hammer is the absolute hero of the image, taking up approximately 40% of the image area.
Additional small details near the bottom: some pots transformed into topiary spheres (round green bush shapes), a decorative butterfly on one pot — suggesting reward/special content.
Bottom banner (20% height): Fresh green gradient banner (#27AE60 to #1E8449), bold white text 'USE BOOSTERS!' in thick rounded font with gold-yellow outline. Bottom-left corner: large orange-red poppy cluster decoration.
No human characters. Action/impact visual energy.
Professional mobile game App Store screenshot quality.
```

---

### 🖼️ 图5：花型图鉴图 · FLOWER COLLECTION

**Prompt 示例**：
```
9:16 vertical mobile game store promotional screenshot.
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
Professional mobile game App Store screenshot quality.
```

---

## 输出目录规范

所有生成的图像必须自动保存到以下固定目录：

```
<项目根目录>/.cursor/skills/chsx-creative/output/
```

**文件命名规范**（固定命名，方便版本管理）：

```
img1_sort_colorful_flowers.png
img2_match_merge.png
img3_relaxing_puzzles.png
img4_use_boosters.png
img5_flower_collection.png
```

如生成的是特定活动主题变体（如万圣节、春节），在文件名前加主题前缀：
```
halloween_img1_hero.png
cny_img2_match_merge.png
```

---

## 执行流程

1. **读取本文档**，确认风格规范、参考描述和尺寸要求。
2. **收集风格参数**：解析用户描述，提取「风格参数化框架」中对应变量的取值；**用户未提到的变量一律使用原始风格默认值**。
3. **构建 Prompt**：以各图 Prompt 示例为模板，**将背景、花盆、层架、Banner 等描述替换为用户指定或默认的风格参数**，再替换游戏名、Banner 文字等游戏特有内容。
4. **优先调用生图脚本（核心）**：出图时，务必优先使用 `<项目根目录>/.cursor/skills/chsx-creative/scripts` 目录下的相关脚本（如 `nano_banana2_api.py`）生图。
   - 示例用法：你可以编写 Python 代码导入该脚本中的 `NanoBanana2API` 进行生图，并从返回的 JSON 中提取 `imageUrl` 下载保存；或根据需要执行相关封装好的 `.bat` 或 `.ps1` 脚本。
   - 使用脚本能直接生成符合 9:16 原生比例且高质量的内容，突破 1:1 限制。
   - 若遇到 API 调用阻塞等不可恢复错误，再备选降级回自带的 `generate_image` 工具（需使用 1:1 居中构图策略）。
5. **输出检查**：
   - ✅ 是否为竖版（9:16）
   - ✅ 背景、花盆、层架等视觉元素是否符合用户指定或默认的风格参数
   - ✅ 底部是否有彩色渐变Banner + 白色粗体文字
   - ✅ 是否有花盆/层架主体元素
   - ✅ 左下角是否有花卉装饰
   - ❌ 是否误出了卡通人物（应无人物）
6. **交付归档**：如果使用了降级的 `generate_image` 导致图片在 Artifacts 目录，**必须**将生成的全部图片移动到 `<项目根目录>/.cursor/skills/chsx-creative/output/` 文件夹。如果使用了 `scripts` 的生图脚本，也必须确保图片成功下载并保存在 `output` 目录下，并正确展示给用户。

---

## 注意事项

- **无人物原则**：本游戏商店图均以花卉、花盆、层架、道具为主体，**不出现任何人物角色**。
- **风格与参数一致**：视觉元素（背景、花盆、层架等）需与用户指定或默认的风格参数一致。
- **竖版强制**：每张图必须为9:16竖版比例，生成后检视，如出现横版或方图立即重新生成。
- **Banner文字优先英文**：默认英文大标题（如 SORT FLOWERS / MATCH & MERGE），中文版本按需调整。
- **五图色系差异化**：五张图的Banner颜色必须各不相同，形成整套素材的视觉区分度。


