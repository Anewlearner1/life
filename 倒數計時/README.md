# 倒數計時

> 某天早上，她突然看得見每個人頭上的數字：那是你們還能見面的次數。

| 項目 | 設定 |
|---|---|
| 片長 | 32 秒（6 個 AI 鏡頭共 29 秒，從每段 8 秒中取用 4–5 秒，加 3 秒片尾字卡） |
| 畫幅 | 16:9；素材是 720p，成片放大到 1920×1080、24fps 輸出 |
| 畫風 | 參考上傳影片：寫實韓系校園劇。陰天的柔光、酒紅色西裝制服、深藍格紋裙、玻璃帷幕校舍的中庭、淺景深、色調偏冷偏低飽和 |
| 生片 | Google Flow：Veo 3.1 Lite，每段 8 秒、720p、16:9，一段 10 點；用首幀（S5、S6 另加尾幀）生影片 |
| 生圖 | ChatGPT，共 12 張，提示詞與順序見 `生圖提示詞.md` |
| 預算 | 70 點：6 鏡 × 10 = 60，另留 10 點重抽一次 |
| 配樂 | Python 合成：`tools/music.py`，鋼琴、弦樂 pad、時鐘滴答、心跳 |
| 字幕 | 中文字幕燒進畫面，仿參考片的白字加細黑邊、置中壓底 |
| 頭上的數字 | **不交給 AI 生成**，後製時用 `tools/assemble.py` 疊上去（AI 生成的文字很容易亂碼） |

## 檔案

- `timeline.json`：時間軸總表，包含鏡頭、數字的位置與出現時間、字幕和片尾字卡
- `tools/music.py`：配樂合成
- `tools/assemble.py`：合成成片（鏡頭＋數字＋字幕＋字卡＋配樂）
- `倒數計時_動態分鏡.mp4`：用佔位卡先跑的版本，可以拿來確認節奏和配樂
- `生圖提示詞.md`：ChatGPT 生圖的 12 張提示詞、張數與順序
- `tools/frame169.py`：把 3:2 的圖裁成 16:9 的 1280×720，給 Flow 當首尾幀
- `refs/`：ChatGPT 生的圖放這裡
- `shots/`：Veo 生成的鏡頭放這裡，檔名用 `S1.mp4` 到 `S6.mp4`

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

## 角色

- **她（主角）**：17 歲，黑色長直髮，空氣瀏海，細金屬圓框眼鏡，長格紋裙，抱著一本舊的米色精裝書
- **好友**：栗色鮑伯頭，開朗，短格紋裙，書包上掛著小吊飾
- **他**：18 歲，高個子，黑色微亂短髮，溫和，抱著一疊課本

完整外觀描述寫在 `生圖提示詞.md` 的定裝照提示詞裡，以那裡為準。

## Flow 影片提示詞（Veo 3.1 Lite，8 秒，首幀模式）

首幀已經決定了長相和構圖，所以提示詞只寫**動作、鏡頭和時間點**。Veo 自帶的聲音會在合成時丟掉，配樂一律用 `music.py`。
每段只會用到其中 4–5 秒，取用起點寫在 `timeline.json` 的 `src_in`，看過片段後我再幫你調。

共用尾句（貼在每段最後）：
```
Photorealistic Korean high-school drama, overcast soft daylight, cool desaturated grade, shallow depth of field, 35mm film look. Keep faces, hair, glasses and uniforms exactly as in the first frame. No on-screen text, no subtitles, no numbers. Ambient sound only, no music.
```

**S1（首幀 S1_first，取用第 2–6 秒）**
```
Extreme close-up on her eye behind round glasses, very slow push-in for the whole shot. 0–2s: still, calm. 2–3s: one slow blink. 3–6s: a faint white glow blooms in the lens reflection and her pupil widens slightly, as if she sees something appear in front of her. 6–8s: she stares, motionless.
```

**S2（首幀 S2_first，取用第 0–5 秒）**
```
Locked-off static camera, absolutely no camera movement, pan or zoom. The students stroll very slowly and casually, taking only a few small steps, chatting and glancing at each other; they stay roughly where they are, stay spread out and never cross in front of each other. Light breeze in the young trees, rain puddles on the pavement.
```
> 數字是直接疊在首幀量好的位置上，所以人要走得很慢。如果片段裡有人移動明顯，在 `timeline.json` 填該數字的 `vx`／`vy`（每秒位移，畫面比例），數字就會跟著移動。

**S3（首幀 S3_first，取用第 0.5–5.5 秒）**
```
Static camera. 0–2s: she rubs her eyes. 2–4s: she puts her round glasses back on. 4–6s: she looks up and around, confused, glancing at the space above people's heads. 6–8s: she freezes, lips slightly parted. The background student keeps walking slowly, out of focus.
```

**S4（首幀 S4_first，取用第 0.5–5.5 秒）**
```
Static over-the-shoulder camera. 0–3s: the bob-haired friend keeps waving and bounces on her toes, beaming. 3–8s: she lowers her hand and talks excitedly, pointing back toward the school gate with her thumb, then tilts her head waiting for an answer. Keep the empty space above her head.
```

**S5（首幀 S5_first、尾幀 S5_end，取用第 1–6 秒）**
```
Gentle handheld camera. 0–2s: her smile fades and tears well up behind her glasses. 2–4s: she suddenly steps forward and throws her arms around her friend. 4–8s: she hugs her tightly, eyes closed; the friend is surprised, then laughs softly and hugs her back.
```

**S6（首幀 S6_first、尾幀 S6_end，取用第 0.8–5.8 秒）**
```
Slow push-in. 0–1s: the textbooks fall from his arms and hit the wet pavement. 1–3s: both quickly crouch down, she bows her head apologizing. 3–5s: they each pick up a book and look up at the same moment; their eyes meet. 5–8s: he smiles softly, she stares at him, stunned. Keep the empty space above his head.
```

## 點數分配（70 點）

| 用途 | 點數 |
|---|---|
| S1–S6 各生一次（每次 8 秒、720p） | 60 |
| 重抽備用（一次） | 10 |
| **合計** | **70** |

- 生成前確認 Flow 的**每次產出數設為 1**（設成 2 以上會照倍數扣點）。
- 重抽給最容易出錯的鏡頭，優先順序 S6 > S5 > S4。S1、S2、S3 只要大致可用就不重抽，數字和字幕會蓋掉小瑕疵。
- 如果你選用的模式或模型不支援尾幀，S5、S6 就只用首幀，提示詞照貼。

## 執行順序

1. **ChatGPT 生圖**：照 `生圖提示詞.md` 第 1 到 12 張的順序生成，存進 `refs/`。
2. **裁成 16:9**：`python3 tools/frame169.py refs`，輸出到 `refs/169/`。頭頂空間被裁掉的話，加 `--shift -0.05` 讓裁切框往上移。
3. **先把 `refs/169/S2_first.png` 傳給我**：我照人頭位置設定好數字座標，你同時就可以開始生影片。
4. **Flow 生片**，順序 S2 → S3 → S4 → S1 → S5 → S6。先做最簡單的，確認色調沒跑掉，再處理有尾幀的難鏡頭。生完存成 `shots/S1.mp4` 到 `S6.mp4`。
5. **合成**：`python3 tools/assemble.py`，輸出 `倒數計時_成片.mp4`。或把片段丟回來，我幫你對時間、合成。
