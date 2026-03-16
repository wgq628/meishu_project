---
name: Grillsort-creative
description: 专门用于“烧烤三消/排序”类超休闲游戏（如Grill Sort类）的美术设定、UI界面（如关卡选择）、宣传相关素材设计、局内元素设计与效果反馈规范。当用户要求设计“烧烤三消”、“烧烤排序”类游戏资产或相关界面时触发。
---

# Grillsort-creative

本技能旨在帮助用户稳定输出、设计并生成“烧烤三消/物品排序 (BBQ/Grill Sort)”类超休闲游戏的视觉资产。所有生成与设计输出必须严格遵循此类游戏核心的**“高饱和、多汁诱人、粗体果冻感”**休闲美术基调。

---

## 🎨 核心美术视觉规范 (必须严格遵守)

在生成任何该类游戏相关的UI、关卡或图标时，务必将以下规范融入 Prompt 设定中：

### 1. 整体氛围与视角 (Overall Vibe & Perspective)
*   **视觉基调**：轻度/超休闲（Hyper-casual）写实卡通风格（2.5D/3D渲染2D）。
*   **核心关键词**：明快 (Bright)、轻松 (Fun)、充满烟火气、令人垂涎欲滴 (Mouth-watering/Appetizing)、高饱和度 (High saturation)。
*   **镜头透视**：局内玩法（如烤架排序）必须采用**正面微俯视（近似平视，Orthographic-ish 3D）**，确保前后层级关系（如竹签、烤肉的叠放）清晰无遮挡误差。

### 2. 色彩构成与光影 (Color Palette & Lighting)
*   **主色系**：食物与烧烤环境主打**高饱和度暖色调**（如焦糖色、红棕色、明黄色、亮红色）。
*   **对比色标**：交互UI（如Play按钮、进度条、加号）需使用鲜艳的**草绿色 (Bright Green)** 或 **亮蓝色** 形成强视觉对比。
*   **光影表现**：全局采用明亮通透照明（Global Illumination），**严禁使用浓重黑死阴影**。元素底部应当使用柔和模糊的落影（Soft Drop Shadow）托底，以营造立体分量感。

### 3. UI与环境背景 (UI & Environment)
*   **UI 材质**：所有按钮及面板需呈现**厚重圆润感 (Chunky/Gummy)**。具有明显的Z轴厚度（3D质感），边缘大圆角，带有明显的顶部高亮/光泽（Glossy），强调“可点击感（Clickability）”。
*   **环境背景**：通常为暖色木纹桌面、野餐布或流理台。必须经过**景深模糊处理 (DoF blur)**，绝不能喧宾夺主，以便烘托前景食物。

### 4. 游戏元素模型 (Game Elements/Food Items)
*   **造型与排布**：必须严格遵循工作区 `references/food_design_plan.md` 的规范，强制对任何食物进行“竖向形魔改”适配（Vertical Grid Fitting），彻底去除写实杂点。
*   **质感差异化**：必须遵循 `references/style_reference.md` 的三大流派指引。根据用户需求（或系统默认）选取特定的生图咒语后缀（如“黏土果冻”、“浓郁烧烤”或“潮玩塑料波普”）。

---

## 🛠 子技能与生图参考模板 (Prompts)

### 场景 1：生成关卡选择界面 (Level Selection Screen)
**触发条件**：用户需要设计带有多城市/多主题的选关界面。
**生图 Prompt 结构参考**：
> A hyper-casual mobile game level selection screen for a BBQ match-3 game. 2.5D bright, colorful, cartoony 3D style. The background is a slightly blurred warm wooden picnic table. In the center, there are [数量] large, chunky, rounded 3D UI cards representing [主题/城市名称]. 
> The card features a stylized, appetizing 3D cartoony illustration of [具体烧烤食物，如 Korean BBQ meat] with a tiny [背景地标剪影] in the background. 
> Below each card, there is a big chunky, glossy, bright green 3D 'PLAY' button with white text. 
> The UI elements should be glossy, high saturation, appetizing, and have soft drop shadows. The overall vibe is bright, fun, mouth-watering, and highly polished hyper-casual UI. No text other than 'PLAY'.

### 场景 2：生成局内烧烤架 (In-game Grill Board)
**触发条件**：用户需要设计实际游玩时的棋盘（即烤网或烤炉）。
**生图 Prompt 结构参考**：
> A top-down isometric view of a clean, cartoonish 3D BBQ grill grate for a hyper-casual match-3 mobile game puzzle board. 
> The grill is made of thick, rounded metal bars, placed over glowing, warm, stylized cartoonish orange embers (no scary fire, just cozy glow). 
> High saturation, bright lighting, soft drop shadows. Empty grill ready for skewers. 
> Background is a deeply blurred wooden texture. UI style, chunky, glossy, 2.5D.

### 场景 3：生成游戏物件/道具 (Food Elements / Board Items)
**触发条件**：用户需要单个肉串、多个食材或极具代表性的消除道具九宫格（3x3 grid layout）。
**生图 Prompt 结构参考**：
> [布局描述，如 A 3x3 grid layout of 9 DIFFERENT food items...] 
> [风格流派后缀，**必须**从 `references/style_reference.md` 中选取一整段，例如 Style: Juicy appetizing BBQ, extremely glossy...]
> [具体物件形态，**必须**结合 `references/food_design_plan.md` 强制要求 vertically oriented / chunky]
> [统一环境设定，如 Solid simple light background. Soft drop shadows. Clean vector aesthetics.]
> **⚠️ 注意**：千万不要生造过于写实的Prompt。遇到食物生成任务，**请先阅读 references 文件夹内的规范设定**！

---

## 🚀 自动化生图工具调用 (核心执行机制)

本技能直接复用并集成了外部的 **Banana2 API 绘图脚本** 来执行实际的图像生成任务。当你明确知晓用户的意图，并组合好上述的生图 Prompt 后，**必须**使用 `run_command` 工具调用下方的 Python 脚本来出图。

### 核心脚本路径
`<项目根目录>/.cursor/skills/banana2-image-editor/scripts/auto_edit_image.py`

### 终端调用命令示例
```bash
python "<项目根目录>/.cursor/skills/banana2-image-editor/scripts/auto_edit_image.py" --prompt "<你组合好的英文 Prompt>" --ratio "<画幅比例,例如 16:9 或 1:1>" --output "<项目根目录>/.cursor/skills/Grillsort-creative/output/<生成的文件名>.png"
```

### 执行步骤约定
1. **阅读规范文件 (极重要)**：只要用户提到“生成烧烤三消食物/道具”，**必须第一时间使用工具查看本级 `references/` 文件夹下的两大核心 `.md` 指南**。
2. **组合生成 Prompt**：基于用户的短需求、参考文档内的“竖向重构法则”以及“风格流派后缀”，将它们拼接为高信息密度的强管制英文 Prompt。
3. **确认比例**：除非用户指定，长条图使用 `16:9`，九宫格排列或单物件使用 `1:1`，手机竖版宣发图使用 `9:16`。
4. **调用脚本**：通过 `run_command` 运行上述 Python 脚本。若需对比，可一并开启多个命令跑不同的流派风格。
5. **展示结果**：脚本运行完毕后，**必须将生成好的图片复制到当前对话的 Artifact 目录中**，然后使用 Markdown 及其绝对路径向用户展示，并引导用户确认质感差异。

> **💡 说明**：如果用户同时上传了一张需要修改的草图（图生图需求），你可以在上述命令中额外加上 `--image "<原图绝对路径>"` 参数，脚本会自动处理图床上传与重绘请求。


