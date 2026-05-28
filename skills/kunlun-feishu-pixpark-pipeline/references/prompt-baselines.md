# Prompt Baselines

## 1) 图生图基础模板（保原风格）

```text
仅参考当前上传的唯一垫图（不要参考其他图片）。
保持垫图的原游戏美术风格、材质、光影和UI克制感，不花哨。
手机竖版9:16投放素材。
{玩法变化描述}
保留深灰纯色背景，顶部文案 NO TIMER，小尺寸手势引导不抢眼。
禁止夸张特效、复杂装饰、角色和多余UI按钮。
```

## 2) 需求2（双色）示例变量

```text
不规则棋盘，复杂度高于单色版本但不过度复杂；
使用两种亮色小球（绿色+紫色），分散排布；
每种颜色小球总数不超过16颗；
孔洞与两种颜色对应，孔洞右上角数字角标表示对应颜色小球总数。
```

## 3) 任务参数建议

### generateImgUsingPOST（优先）

- `isEdit=1`
- `singleBatchSize`: 按用户张数拆分（建议 1~3）
- `referenceWeight`: `0.68 ~ 0.78`（越高越贴近垫图）
- `targetImgWidth/targetImgHigh`:
  - 9:16 推荐 `1080x1920`
  - 快速草图可 `768x1365`

### imageGenerationUsingPOST（兜底）

- `version=3`（Banana2）
- `imageUrls`: 传已上传参考图 URL
- `imageScale`: `9:16`
- `resolution`: `2K`

## 4) 轮询与重试建议

1. 每 6~10 秒轮询一次。
2. `90` 秒无结果且持续 `taskStatus=0`：切兜底链路。
3. `imageStatue!=1` 的结果视为失败，补单到满足目标张数。
