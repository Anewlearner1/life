# 第一批鏡頭檢查（S1、S2、S3、S4、S6）

點數：預算 70，已花 50，剩 20（10 點補生 S5，10 點備用）。
規格：五支都是 1280×720、24fps、7.93 秒，有音軌（合成時會丟掉）。

| 鏡 | 結論 | 取用 | 說明 |
|---|---|---|---|
| S1 | **PASS** | 1.0–5.0 秒 | 第 1.5–2.0 秒眨眼，3.5 秒起瞳孔亮起白光，節奏剛好。白光比較像打在眼球上，不完全是鏡片反光，但畫面上讀得懂 |
| S2 | **PASS** | 0–5 秒 | 鏡頭完全固定。人朝鏡頭走了約 60–130px，已量好每個人的位移，數字會跟著走。前景兩人約 6 秒後走到欄杆後面，不在取用範圍內 |
| S3 | **PASS** | 0.5–5.5 秒 | 揉眼、戴回眼鏡（約 2.5 秒）、驚愕抬頭，動作完整。表情偏驚嚇而不是困惑，反而更貼合劇情。背景學生朝鏡頭走來，「318」已用關鍵幀追蹤 |
| S4 | **PASS** | 0.5–5.5 秒 | 揮手、說話、比拇指指向後方，和提示詞幾乎一致。臉和定裝照相符。「2」穩定浮在頭上 |
| S6 | **PASS（有條件）** | 1.2–6.2 秒 | 0.25–1.0 秒有融化般的瑕疵，兩人左右互換、臉混在一起；6.75 秒溶接到尾幀，構圖跳回女左男右。避開這兩段後，1.2–6.2 秒很乾淨：撿書、對視、鏡頭推近、他微笑。少了相撞那一下，數字因為推鏡沒有頭頂空間，改成追著他頭頂、貼齊畫面上緣滾動 |

S3 和 S6 的主角臉部一致（黑長直髮、瀏海、圓框眼鏡）。S4 的好友和定裝照一致。

**建議**：S6 不重抽。粗剪裡看起來成立，備用的 10 點留給 S5。

## S5 被「知名人士政策」擋下的原因與解法

這條規則看的是**輸入的圖**，不是提示詞。S5_first 是寫實、精緻的年輕臉部大特寫，S5_end 還多了第二張臉，最容易被判成「像某位藝人」。提示詞裡的「Korean high-school drama」也可能加重這種聯想。被擋下的生成會退點，所以下面三個方案可以依序試，只有成功那次會扣 10 點。

### 方案 A（先試）：只放首幀 S5_first，拿掉尾幀，提示詞改成中性描述
- 首幀：`S5_first.png`；尾幀：**不放**
- 取用：1.0–6.0 秒
```
Close-up of a schoolgirl with long black hair and round gold glasses in a rainy school courtyard, her friend a soft blur at the right edge of frame. Gentle handheld camera. 0–2s: her smile slowly fades and her eyes fill with tears. 2–4s: she steps forward and wraps her arms around her friend. 4–8s: the two classmates hold a tight, quiet hug, her eyes closed; the friend laughs softly and hugs her back. Realistic cinematic film look, overcast soft daylight, cool muted colors, shallow depth of field. Original fictional characters. Keep faces, hair, glasses and uniforms exactly as in the first frame. No on-screen text, no subtitles, no numbers. Ambient sound only, no music.
```

### 方案 B（A 被擋時）：用 S4 的最後一格當首幀
這張圖是 Veo 自己生成、已經通過審查的，幾乎不會再被擋，而且和 S4 能無縫接動作。代價是看不到主角的哭臉，情緒改由好友驚訝的表情、字幕「……好。」和配樂來帶。
- 首幀：`refs/169/S5_alt_first_from_S4.png`（已從 S4 取出，1280×720）；尾幀：不放
- 取用：0.5–5.5 秒（timeline.json 的 S5 `src_in` 要改成 0.5）
```
Static over-the-shoulder camera from behind the long-black-haired girl in the left foreground, facing her bob-haired friend. 0–1.5s: the friend smiles, waiting for an answer. 1.5–3s: the long-haired girl suddenly steps forward and throws her arms around her friend. 3–8s: the friend's eyes widen in surprise, then she laughs softly, closes her eyes and hugs her back, chin resting on the girl's shoulder. Realistic cinematic film look, overcast soft daylight, cool muted colors, shallow depth of field. Keep faces, hair and uniforms exactly as in the first frame. No on-screen text, no subtitles, no numbers. Ambient sound only, no music.
```

### 方案 C（A、B 都不行時）：用 ChatGPT 重畫 S5_first，降低「明星臉」特徵
改成中景雙人鏡頭，主角側一點，頭髮和鏡片反光遮掉部分臉，五官畫得普通一點。附上 `ref_location.png`、`char_her.png`、`char_friend.png`，接著貼：
```
Use the attached images as references for the outfits, hairstyles, glasses and courtyard location. Medium two-shot at chest height in the rainy courtyard: the long-black-haired girl with round gold glasses on the left, seen in three-quarter profile, a few strands of hair falling across her cheek and a soft grey reflection on her lenses; her smile is fading and her eyes are glossy with tears. The chestnut-bob friend on the right, half-turned, smiling at her. Both look like ordinary everyday students with natural, imperfect skin, a few freckles and unstyled hair — not models. Photorealistic, overcast soft daylight, cool muted colors, shallow depth of field. No text, no numbers, no watermark. Landscape 3:2.
```
裁成 16:9 後，用方案 A 的提示詞，只放首幀。

---

# 第二批：S5（方案 B）與 S6_v2（重抽）

點數：70／70 用完（S1–S4、S6 共 50，S5 方案 B 10，S6 重抽 10）。

| 鏡 | 結論 | 取用 | 說明 |
|---|---|---|---|
| S5（方案 B，S4 尾幀當首幀） | **PASS** | 1.5–6.0 秒 | 0–1.5 秒好友微笑等待，1.7 秒主角上前抱住，3.3–3.7 秒好友驚訝，4.3 秒起笑開，5.3 秒回抱、閉眼。沒有換臉或跳格，和 S4 動作連貫。小瑕疵：抱住時主角背上多出一個深藍書包，S4 沒有，一閃而過不明顯 |
| S6_v2 | **PASS，採用（取代 v1）** | 0.2–6.0 秒 | 0–0.7 秒拭淚、相撞、書散落，1.0 秒蹲下，1.3 秒她摀臉道歉，2.7–4.3 秒撿書，4.6 秒他轉頭看她，5.3 秒起微笑。全程女左男右、沒有換臉、沒有溶接，鏡頭固定。勝過 v1：保留了相撞，也沒有融化瑕疵 |

原版 S6 保留為 `shots/S6_v1.mp4` 備查。

為了同時放進相撞和對視，剪輯改成 S5 19.0–23.5 秒、S6 23.5–29.25 秒、片尾字卡 29.25–32 秒。字幕、數字（27.8 秒開始滾到 8,760）和配樂（落書聲 24.05 秒、轉大調 27.8 秒）都跟著對齊。
