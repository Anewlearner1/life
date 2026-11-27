# 倒數計時

> 某天早上，她突然看得見每個人頭上的數字：那是你們還能見面的次數。

| 項目 | 設定 |
|---|---|
| 片長 | 32 秒（6 個 AI 鏡頭共 29 秒，加 3 秒片尾字卡） |
| 畫幅 | 16:9，1920×1080，24fps |
| 畫風 | 參考上傳影片：寫實韓系校園劇。陰天的柔光、酒紅色西裝制服、深藍格紋裙、玻璃帷幕校舍的中庭、淺景深、色調偏冷偏低飽和 |
| 預算 | 60 點（見下方「點數分配」） |
| 配樂 | Python 合成：`tools/music.py`，鋼琴、弦樂 pad、時鐘滴答、心跳 |
| 字幕 | 中文字幕燒進畫面，仿參考片的白字加細黑邊、置中壓底 |
| 頭上的數字 | **不交給 AI 生成**，後製時用 `tools/assemble.py` 疊上去（AI 生成的文字很容易亂碼） |

## 檔案

- `timeline.json`：時間軸總表，包含鏡頭、數字的位置與出現時間、字幕和片尾字卡
- `tools/music.py`：配樂合成
- `tools/assemble.py`：合成成片（鏡頭＋數字＋字幕＋字卡＋配樂）
- `倒數計時_動態分鏡.mp4`：用佔位卡先跑的版本，可以拿來確認節奏和配樂
- `shots/`：AI 生成的鏡頭放這裡，檔名用 `S1.mp4` 到 `S6.mp4`

## 分鏡表

| 鏡 | 時間 | 畫面 | 字幕／對白 | 後製疊字 | 聲音 |
|---|---|---|---|---|---|
| S1 | 0–4s | 她的眼睛隔著圓框眼鏡的大特寫，眨一下眼，鏡片反光裡亮起一點白光 | 那天早上，我開始看得見一些數字。 | – | 鋼琴動機、時鐘滴答 |
| S2 | 4–9s | 中庭大遠景，鏡頭固定不動，學生三三兩兩走過 | 浮在每一個人的頭上。 | 4,812／127／9,030／56 依序浮現 | 呼嘯聲、閃光音效 |
| S3 | 9–14s | 半身鏡頭，她摘下眼鏡揉眼睛再戴回去，困惑地抬頭；背景有一位模糊的路人 | 後來我才知道——那是我們還能見面的次數。 | 背景路人頭上有一個模糊的 318 | 滴答持續 |
| S4 | 14–19s | 短髮好友從畫面右側跑進來，笑著揮手，停在她面前 | （好友）欸！放學要不要一起回家？ | 好友頭上一個很大的 **2** | 滴答停止，低音重擊，心跳 |
| S5 | 19–24s | 她的臉部特寫：笑容僵住，眼眶泛紅，突然一把抱住好友 | ……好。 | – | 弦樂漸強 |
| S6 | 24–29s | 她轉身擦眼淚，撞上一位抱著書的高個子男生，書散落一地，兩人蹲下來對視 | 抱、抱歉——／（他）沒事。我們……見過嗎？ | 他頭上的數字從 0 一路滾到 **8,760** | 書落地的悶響，轉 C 大調，閃光音效 |
| S7 | 29–32s | 黑底字卡 | 有些人，正要離開。／有些人，才剛開始。／— 倒數計時 — | – | 長和弦收尾，最後一聲滴答 |

情緒曲線：好奇（S1–S3）→ 心碎（S4–S5）→ 轉折帶出希望（S6–S7）。8,760 剛好約等於「每天見一次，見 24 年」，留給觀眾在留言區算。

## 角色設定（每個提示詞都貼上同一段，維持一致性）

- **她（主角）**：17 歲東亞女生，黑色長直髮，有空氣瀏海，戴細金屬圓框眼鏡，素顏，安靜書卷氣；酒紅色西裝外套、白襯衫、深藍蝴蝶結、深藍格紋長裙，手上抱著一本舊的米色精裝書
- **好友**：17 歲東亞女生，下巴長度的栗色鮑伯頭，表情開朗，制服相同、配短格紋裙，書包背帶掛著一個小吊飾
- **他**：18 歲東亞男生，高個子，黑色微亂短髮，五官溫和，酒紅色西裝外套、白襯衫、深藍領帶，懷裡抱著一疊課本

建議做法：先用平台的文生圖（通常不扣影片點數，或扣得很少）各生一張角色定裝照，之後每個鏡頭都用**圖生影片**，拿定裝照當參考圖。

## 共用風格字串（貼在每個提示詞最後）

```
photorealistic Korean high-school drama, overcast soft daylight, modern glass-and-concrete campus courtyard with lawn and young trees, burgundy blazer uniforms, shallow depth of field, cool desaturated color grade, 35mm film look, natural skin texture, 24fps cinematic, 16:9. No text, no subtitles, no numbers, no logos.
```

## 各鏡提示詞（英文直接貼進平台，每段 5 秒）

**S1（4 秒，生成 5 秒後剪掉前面）**
```
Extreme close-up of a 17-year-old East Asian girl's eye behind thin round metal glasses, long black hair with bangs at the edge of frame. She blinks slowly; a faint white glint blooms in the lens reflection, as if she sees something appear. Very slow push-in. [角色:她] [風格字串]
```

**S2**
```
Static wide shot from a second-floor balcony looking down into a school courtyard. 6–8 students in burgundy blazers walk across the paved path in small groups at different distances, spaced apart, heads clearly visible against the lawn. Locked-off camera, no camera movement. [風格字串]
```
> 鏡頭一定要固定不動，數字才能直接疊在固定位置。生成後依人頭位置修改 `timeline.json` 裡 S2 的 x、y。

**S3**
```
Medium shot, the girl stands in the courtyard holding an old beige book. She takes off her round glasses, rubs her eyes, puts the glasses back on and looks up and around in confusion. A blurred student walks in the far background, right side. Static camera. [角色:她] [風格字串]
```

**S4**
```
Over-the-shoulder from behind the girl. A cheerful girl with a chestnut chin-length bob runs in from the right, waving and smiling widely, stops right in front of her and talks happily. Static camera, plenty of headroom above the bob-haired girl. [角色:好友] [風格字串]
```

**S5**
```
Close-up on the long-haired girl with round glasses. Her smile freezes, her eyes slowly well up with tears, then she suddenly steps forward and hugs her bob-haired friend tightly; the friend looks surprised, then laughs and hugs back. Handheld, gentle. [角色:她+好友] [風格字串]
```

**S6**
```
The long-haired girl turns away wiping her tears and bumps into a tall boy carrying a stack of textbooks; the books fall to the wet pavement. Both crouch to pick them up and their eyes meet; he smiles softly. Medium shot, slow push-in, generous headroom above the boy. [角色:她+他] [風格字串]
```

負面提示詞（平台有提供欄位就填）：`text, subtitles, numbers, watermark, deformed hands, extra fingers, cartoon, anime, oversaturated`

## 點數分配（60 點）

各平台計價不同。下面假設「5 秒、1080p、圖生影片」一段 8 點：

| 用途 | 點數 |
|---|---|
| S1–S6 各生一次 | 48 |
| 預留重抽 | 12（優先給 S6 和 S5，動作最複雜） |
| **合計** | **60** |

如果你的平台一段要 10 點（6 段＝60 點，沒有重抽空間），就**刪掉 S1**：改用 `ffmpeg` 從 S3 第一格做 4 秒慢推，數字和字幕照常，省下 10 點留給重抽。順序優先度：S4 > S6 > S5 > S2 > S3 > S1。

## 出片流程

```bash
# 1. 把生成好的片段放進 shots/（S1.mp4 … S6.mp4，任何長度、比例都可以）
# 2. 依實際人頭位置調整 timeline.json 的 numbers.x / numbers.y
python3 tools/assemble.py                # → 倒數計時_成片.mp4（缺少的鏡頭會用佔位卡補上）
```
