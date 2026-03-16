---
name: design-image-layer-splitter
description: 将设计好的游戏/应用画面图片智能分层拆解为独立的组成部分（如背景、容器/结构、道具/物品、角色等），类似PS图层拆解。不破坏原图风格、结构和比例，不硬裁剪，而是根据内容语义提炼出每一个组成元素类别。当用户上传了一张设计好的完整画面（游戏截图、UI设计稿、广告素材等），并要求"分层"、"拆解"、"提取元素"、"拆成图层"、"像PS一样分层"等操作时触发。
---

# 设计图智能分层拆解 (Design Image Layer Splitter)

将一张设计好的完整画面按**内容语义**拆解为多个独立图层，每个图层对应一类视觉元素。保持原图的风格、结构与比例，不做硬裁剪，所有提取出的元素放置在干净的白色背景上。

---

## 核心原则

1. **语义分层，非像素分割**：按"这个元素在设计中扮演什么角色"来分层，而非简单的前后景分离
2. **忠实还原，零风格篡改**：每个提取出的元素必须与原图中的外观完全一致——相同的画风、光影、细节、比例
3. **白底独立，即拿即用**：除了背景层外，其余图层统一以纯白背景输出，元素居中、留有呼吸空间
4. **去重不丢**：同类型但不同颜色/状态的元素保留各变体；完全重复的只保留一份

---

## 文件夹规范

- **输出目录**：`<项目根目录>/.cursor/skills/design-image-layer-splitter/output/`
  - 每次拆解会在 output 下自动创建一个以 `时间戳_原图名` 命名的子文件夹
  - **原图也会复制到该子文件夹**，命名为 `00_原图_<文件名>`，方便与各图层直接对比

---

## 执行步骤

### 步骤 1：创建输出子文件夹并复制原图

先创建本次拆解专属的输出子文件夹，然后将原图复制进去作为对照基准：

```powershell
# 创建以时间戳+原图名命名的子文件夹
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$subFolder = "<项目根目录>/.cursor/skills/design-image-layer-splitter/output/${timestamp}_<原图名(不含扩展名)>"
New-Item -ItemType Directory -Path $subFolder -Force

# 将原图复制到子文件夹，加 00_ 前缀确保排在最前面
Copy-Item "<原图路径>" "$subFolder\00_原图_<文件名>" -Force
```

### 步骤 1.5：用 Python 检测原图实际尺寸（必做）

**不要主观判断比例！** 在开始分析之前，先运行以下命令获取精确尺寸：

```powershell
python -c "from PIL import Image; img = Image.open(r'<原图路径>'); w,h = img.size; print(f'宽: {w}, 高: {h}, 比例: {round(w/h,3)}')"
```

根据计算出的宽高比，对照下方比例选择表选择正确的 `--ratio` 参数。

---

### 步骤 2：深度画面结构分析（最关键的一步）

仔细审视原图，以**资深设计师拆 PSD 文件**的思维进行结构分析。你必须识别出画面中所有可分离的**语义类别**，并为每个类别制定一个独立的图层。

#### 分层维度参考（按优先级排序）

| 层级 | 类别名 | 识别要点 | 输出特征 |
|------|--------|----------|----------|
| L1 | **纯背景层** | 画面最底层的场景/环境/氛围（去除所有前景物体后剩余的部分） | 保持原图尺寸比例，填补被移除物体的区域 |
| L2 | **结构/容器层** | 承载其他元素的框架性物体：货架、格子、托盘、桌子、卡槽等 | 白底，保持容器的完整结构，内部清空 |
| L3 | **道具/物品层** | 游戏道具、食物、图标、卡牌等可交互的独立小元素 | 白底，以网格排列所有不重复的物品（sprite sheet 形式） |
| L4 | **角色层** | 人物、NPC、宠物、吉祥物等有"生命感"的主体 | 白底，保持角色原始站位关系或单独提取 |
| L5 | **UI/文字层** | 按钮、标题、分数、logo 等界面叠加元素 | 白底，排列展示所有 UI 组件 |
| L6 | **装饰/特效层** | 光效、粒子、边框花纹、氛围装饰等非功能性视觉点缀 | 白底或按需 |

**并非每张图都需要全部 6 层！** 你必须根据实际画面内容灵活决定拆几层、每层包含什么。

#### 分析输出格式

向用户简要汇报你的分层方案，格式如下：

```
📐 画面结构分析结果：

原图描述：[一句话概括画面内容]

计划拆分为 N 个图层：
  • Layer 1 - 背景层：[具体描述这一层包含什么]
  • Layer 2 - 容器层：[具体描述]
  • Layer 3 - 物品层：[具体描述，列举识别到的物品]
  • Layer 4 - 角色层：[具体描述]
  ...

即将并行生成，预计耗时约 X 分钟。
```

### 步骤 3：并行调用 Banana2 生成所有图层

**所有图层的生图命令必须同时发起（并行 Shell），不要串行等待！**

每个图层调用一次 Banana2 脚本，**所有图层的输出路径统一指向步骤 1 创建的子文件夹**：

```powershell
python "<项目根目录>/.cursor/skills/banana2-image-editor/scripts/auto_edit_image.py" `
  --image "<原图路径>" `
  --prompt "<英文 Prompt，见下方各层级规范>" `
  --ratio <与原图一致的比例> `
  --output "$subFolder\L<序号>_<层级名>"
```

输出文件命名规范（确保在文件夹中按序号排列）：
- `00_原图_xxx.png` — 原图（步骤 1 已复制）
- `L1_背景层_xxx.png` — 第一层
- `L2_容器层_xxx.png` — 第二层
- `L3_物品层_xxx.png` — 第三层
- 以此类推…

---

## 各图层 Prompt 编写铁律

### 通用禁忌（所有图层 Prompt 必须遵守）

- **禁止**使用 "create"、"draw"、"design"、"generate"、"imagine" 等创造性动词
- **只用** "keep"、"remove"、"extract"、"isolate"、"preserve"、"show only" 等提取性动词
- **必须**包含 `Preserve the EXACT original art style, colors, lighting, proportions and visual details. Do NOT reinterpret, re-draw, or change any visual characteristic.`
- **必须**包含 `Do NOT add any element that does not already exist in the source image.`
- **视角锁定**：如果原图中元素是正面正交视角（如游戏 UI 货架、格子面板等），**必须**在 Prompt 中明确写 `flat front-facing 2D orthographic view, NO perspective, NO angle, NO visible depth/side, NO 3D rotation`，防止 AI 擅自把 2D 元素"立体化"
- **风格锁定**：如果原图是卡通/手绘风格，**必须**明确写 `cartoon/hand-painted game art style, NOT photorealistic`，防止 AI 把卡通元素"写实化"

---

### L1 纯背景层 Prompt 模板

```
Remove ALL foreground objects from this image, including [逐一列举要移除的元素类别：characters, items, containers, UI elements, text, logos...]. Keep ONLY the background environment/scene. Fill in the areas where objects were removed with the surrounding background texture and colors seamlessly, as if the objects were never there. Preserve the EXACT original art style, colors, lighting, proportions and visual details. Do NOT add any element that does not already exist in the source image. The result should be a clean, continuous background scene with no trace of the removed elements.
[补充描述你观察到的背景特征，例如：The background is a fantasy forest scene with tall pine trees, moss-covered archways, warm golden light rays filtering through the canopy, and lush green vegetation.]
```

### L2 结构/容器层 Prompt 模板

```
Extract ONLY the [容器的具体名称，如 wooden shelf grid / blue food tray / cardboard crate] from this image and place it on a pure white background. Remove everything else — remove all background scenery, characters, items inside the container, and decorations. Show ONLY the empty container/structure itself, centered on a clean white background with adequate padding around it. CRITICAL VIEWING ANGLE: Maintain the EXACT same viewing angle as the source image. [如果原图是正交正面视角则加：The container MUST be shown in a perfectly FLAT, FRONT-FACING, 2D ORTHOGRAPHIC view. There must be ZERO perspective, ZERO angle, ZERO depth visible, ZERO 3D rotation. Do NOT show any side panel or thickness.] CRITICAL STYLE: [如果原图是卡通风格则加：This is a cartoon/hand-painted mobile game art style — NOT photorealistic, NOT realistic texture.] Preserve the EXACT original art style, colors, lighting, proportions, and visual details of the container. Do NOT add any element that does not already exist in the source image.
[补充描述容器的视觉特征，例如：The container is a dark brown wooden grid shelf with 8 rows × 4 columns of square compartments, cartoon style with dark brown color.]
```

**如果画面中有多种不同的容器，则每种容器单独出一张图。**

### L3 道具/物品层 Prompt 模板

```
Extract ONLY the individual game items/props from this image and arrange them neatly on a pure white background in a grid layout (like a sprite sheet). Items to extract: [逐一列举所有识别到的不重复物品，如 red spotted mushroom, four-leaf clover, green fern curl, brown pine cone, gray rabbit, blue-red woodpecker, golden treasure chest]. CRITICAL: Show exactly ONE SINGLE standalone instance of each item type — NOT pairs, NOT groups, NOT clusters. If the same item appears multiple times in the source image, include only ONE instance. If items have color/style variants, keep ALL variants. Each item should be clearly separated with generous white space between them. Arrange in a clear [N×M] grid layout: [明确指定每行放什么，如 Row 1: item1, item2, item3. Row 2: item4, item5, item6.] Preserve the EXACT original cartoon art style, colors, proportions and visual details of each item. Do NOT add, invent or create any item that does not already exist in the source image. STRICTLY reproduce only what is visible.
```

### L4 角色层 Prompt 模板

```
Extract ONLY the character(s) from this image and place them on a pure white background. Characters to extract: [逐一描述每个角色的外观特征，如 a gray-haired woman in yellow-green dress, a young man with black hair wearing a yellow vest and ID badge, a woman with short brown hair in a red off-shoulder top]. Remove ALL background scenery, UI elements, items, containers, and other non-character elements. Show the full body of each character. Maintain their relative positions and spacing to each other. Preserve the EXACT original art style, colors, proportions, poses, facial features and visual details. Do NOT add any element that does not already exist in the source image.
```

**如果画面中有多组角色（如不同场景区域的角色组），则每组单独出一张图。**

### L5 UI/文字层 Prompt 模板

```
Extract ONLY the UI elements, text labels, buttons, logos, score displays, and interface components from this image and arrange them on a pure white background. UI elements to extract: [逐一列举，如 "SMOKIN' HOT BBQ" neon sign, BBQ logo chalkboard, "MENU OF THE DAY" sign, pink pig neon decoration, string lights]. Remove all background, characters, game items, and containers. Arrange UI components with clear spacing. If multiple UI elements share the same shape but differ in color, keep ALL color variants but only ONE instance per unique shape. Preserve the EXACT original art style, colors, proportions and visual details. Do NOT add any element that does not already exist in the source image.
```

---

## 步骤 4：输出与展示

所有并行任务完成后，向用户汇报结果：

```
✅ 分层拆解完成！共生成 N 个图层：

📁 输出文件夹：<项目根目录>/.cursor/skills/design-image-layer-splitter/output/<子文件夹>/

  • 00_原图_xxx.png         ← 原始完整画面（对照用）
  • L1_背景层_xxx.png       ← 纯净背景
  • L2_容器层_xxx.png       ← 容器/结构
  • L3_物品层_xxx.png       ← 道具/物品
  • L4_角色层_xxx.png       ← 角色
  ...

打开这个文件夹即可直接对比原图与每个分层的效果。
```

然后用 Markdown 图片语法依次展示**原图 + 每个图层**的效果（路径用正斜杠，不加 `file:///`），先展示原图，再逐层展示，让用户在对话中也能直观对比。

最后询问用户：
1. 各图层是否符合预期？
2. 是否有遗漏的元素需要单独提取？
3. 是否需要对某个图层进行微调重试？

---

## 常见问题修正策略

| 问题 | Prompt 修正方式 |
|------|----------------|
| 背景层有残留物体 | 在 prompt 中用更具体的词汇描述要移除的物体：`completely erase the [具体物体名] that was located at [位置], fill with surrounding [背景材质]` |
| 提取的元素风格被改变 | 强化：`STRICTLY preserve pixel-accurate visual appearance, exact same art style, exact same color saturation, no artistic reinterpretation whatsoever` |
| 元素层出现原图中不存在的新元素 | 强化：`WARNING: ONLY extract elements that ALREADY EXIST in the source image. Creating, inventing, or imagining new elements is STRICTLY FORBIDDEN.` |
| 容器内部没清空干净 | 强化：`Remove ALL items and objects from inside the container. Show the container completely EMPTY with nothing inside any compartment or slot.` |
| 物品 sprite sheet 排列混乱 | 明确网格：`Arrange items in a clean N×M grid layout with equal spacing. Row 1: [item1, item2, item3]. Row 2: [item4, item5, item6].` |
| 角色被裁切/不完整 | 强化：`Show the COMPLETE full body of each character from head to toe, do not crop or cut off any body part` |
| 多组角色混在一起 | 拆分为多次调用，每次只描述一组角色的特征 |
| **容器视角被改为3D透视**（原图是正交正面） | 在 prompt 中强制锁定：`FLAT FRONT-FACING 2D ORTHOGRAPHIC view, ZERO perspective, ZERO angle, ZERO depth visible, ZERO 3D rotation, do NOT show any side panel or thickness` |
| **卡通风格被写实化** | 在 prompt 中强制锁定：`cartoon/hand-painted mobile game art style, NOT photorealistic, NOT realistic wood grain/texture` |
| **物品出现成对/成组而非单个** | 强化：`exactly ONE SINGLE standalone instance of each item, NOT pairs, NOT groups, NOT clusters` |
| **容器格子行列数不对**（如4列变6列） | 在 prompt 中用极强的措辞精确锁定：`EXACTLY N COLUMNS wide and M ROWS tall. NOT N+1 columns, NOT N+2 columns — strictly N columns only. Total compartments = N x M = X.` 同时用正/反面陈述双重约束 |
| **容器形状被改变**（如矩形变成L形/阶梯形） | 明确写：`SINGLE SIMPLE RECTANGLE shape — NOT an L-shape, NOT a step shape, NOT a staircase. Do NOT include any platform, ledge, or other structure that is not part of the shelf.` |
| **密集构图中的中心主物体无法用减法提取**（如花阵包围的茶壶、被棋子环绕的目标物） | **使用"两步涂白法"**：**第一步**：不说"remove flowers"，改为"white out the entire image EXCEPT for the [目标物]"，让模型理解任务是"给背景区域涂白"而非"移除元素"。核心句型：`White out the entire image EXCEPT for the [目标物描述] at the center. The only pixels that should NOT be white are the pixels belonging to [目标物]. Fill everything else with solid pure white.` **第二步**：把第一步结果作为新输入 (`--image`)，专门清理残留物：`Clean up this image. Keep the [目标物] exactly as is. Erase [残留元素描述] from [位置], replace with solid pure white. The background must be 100% flat solid white with no ghost shapes or outlines.` |
| **同一主物体连续多轮提取失败（超过 3 次）** | 立刻切换策略：先尝试"两步涂白法"（见上条）；若仍然失败，改用"正向描述法"：以原图作为风格参考 (`--image` 参数不变)，将 prompt 改为正向资产展示描述，格式：`A single [物体名] displayed as a standalone game asset on a pure white background. [详细描述外观特征]. Centered on a completely empty pure white background. No other objects, no background scene — only this single object on white. [风格说明]` |
| **UI 区域（分数栏、进度条等）无法从游戏场景中单独提取**（绘图模型持续保留棋盘/背景） | **放弃绘图模型，改用 PIL 直接裁剪原图**：先用像素扫描（`img.getpixel`）确定 UI 区域的精确 y 坐标范围，然后用 `img.crop((0, y_start, w, y_end))` 精确裁剪，放置于白底画布上。比绘图模型更精确、更快速。 |
| **UI 层中的多个角色头像框被当作一个整体提取**（两个玩家面板合在同一张图里） | 将每个头像框/玩家面板拆分成独立的单独请求，分别生成 L4a、L4b 等。每次请求只描述一个面板，并明确说明该面板的位置（左/右）、边框颜色（绿色/金色等）、头像内容。 |

---

## 比例选择指引

**必须先用 PIL 测量原图尺寸（步骤 1.5），不要依赖视觉判断！**

根据实际测量的宽高比（宽 / 高）选择 `--ratio` 参数：

| 原图宽/高比 | 典型尺寸 | 推荐比例 |
|------------|---------|----------|
| 约 0.56 | 1080×1920 | `9:16`（标准竖屏手游） |
| 约 0.75~0.85 | 819×1024、768×1024 | `4:5`（非标准竖屏，如 Carrom 类） |
| 约 1.0 | 1024×1024 | `1:1`（方形） |
| 约 1.33 | 1024×768 | `4:3` |
| 约 1.78 | 1920×1080 | `16:9`（横屏） |
| 提取单个元素/容器到白底 | — | `1:1` |
| 提取 sprite sheet（物品 ≤ 9） | — | `1:1` |
| 提取 sprite sheet（物品 > 9） | — | `16:9` |
| 提取角色组（横排） | — | `16:9` 或 `1:1` |
---

## 完整案例演示

### 案例：森林主题货架排序游戏

**原图**：竖屏森林场景，中央有一个 8×4 木质格子货架，架上摆满蘑菇、四叶草、蕨类、松果、兔子、啄木鸟、宝箱等物品，背景是有苔藓拱门的奇幻森林，右下角有一个方块角色吉祥物。

**分层方案**：

| 图层 | 名称 | Prompt 关键内容 | 比例 |
|------|------|----------------|------|
| L1 | 纯背景 | Remove ALL: wooden shelf, all items inside shelves, the cube mascot character. Keep ONLY the forest background with moss archway, pine trees, golden light rays, ferns. Fill shelf area with continuous forest scenery. | 9:16 |
| L2 | 空货架+背景 | Remove ALL items inside the shelf compartments and the cube mascot. Keep the forest background AND the empty wooden grid shelf structure intact. Show empty compartments with nothing inside. | 9:16 |
| L3 | 纯货架白底 | Extract ONLY the wooden grid shelf structure, place on pure white background. Remove forest background, all items, the mascot. Show empty dark brown wooden shelf with 8×4 compartments. | 9:16 |
| L4 | 物品图鉴 | Extract these items onto white background in 3×3 grid: red spotted mushrooms, four-leaf clovers, green fern curls, brown pine cones, gray rabbit, red-blue woodpecker, golden treasure chest. ONE of each. | 1:1 |

### 案例：BBQ 餐厅排序游戏

**原图**：竖屏画面分上下两个场景。上方是 BBQ 烧烤吧台区：3 个角色站在柜台后，面前有木箱装的食物和蓝色托盘，墙上有霓虹灯招牌。下方是餐厅用餐区：3 个不同的角色坐在红色卡座前，面前也有木箱食物。

**分层方案**：

| 图层 | 名称 | Prompt 关键内容 | 比例 |
|------|------|----------------|------|
| L1 | 纯背景 | Remove ALL characters, food items, containers. Keep ONLY the restaurant interior: brick walls, neon signs, string lights, bar counter, dining booths with tables. | 1:1 |
| L2 | 木箱容器 | Extract ONLY one wooden crate/box container on white background. Brown cardboard-style open-top box. | 1:1 |
| L3 | 蓝色托盘 | Extract ONLY one blue food serving tray on white background. Blue-rimmed rectangular tray with gray/white interior, standing on dark legs. | 1:1 |
| L4 | 食物图鉴 | Extract all food items onto white background in 3×3 grid: bread buns, hot dog, salad, hamburger, fried chicken leg, waffle rolls, pink donuts, french fries, pizza. | 1:1 |
| L5 | 上方角色组 | Extract the 3 characters from the top area: gray-haired woman in yellow-green outfit, young man with yellow vest and badge, woman in red off-shoulder top. White background, maintain relative positions. | 1:1 |
| L6 | 下方角色组 | Extract the 3 characters from the bottom area: elderly lady in turquoise suit with straw hat, stern man in purple suit, young woman with red glasses and brown jacket. White background. | 1:1 |


