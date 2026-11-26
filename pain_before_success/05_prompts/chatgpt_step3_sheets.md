# 步驟 3B–3D｜設定圖提示詞（畫風基準＝style_sample_v1）

用戶已確認：全片畫風照 `03_design/style_sample_v1.png`，也就是溫暖夕陽光下的日系 2D 動畫風。
**每一張都在 ChatGPT 新開對話，先上傳 `style_sample_v1.png`，再貼提示詞。**
v1 的瑕疵在這裡一律修正：髮圈改純黑、鞋子完全素面、頭髮不要細碎亂翹的髮絲。

共用的畫風句子已經寫進每段提示詞，不用另外貼：
> clean modern Japanese 2D animation style exactly like the uploaded image: soft cel shading, thin clean even linework, warm natural palette, gentle soft lighting

---

## 3B 小晴角色設定圖
- **存檔名**：`03_design/char_xiaoqing_v1.png`

```text
Using the uploaded image as the exact style AND character reference, create a clean CHARACTER DESIGN SHEET of this same girl, "Xiao Qing". 16:9, 1920x1080, plain warm light-beige background (#EFE4D2), even soft neutral lighting (no sunset), clean modern Japanese 2D animation style exactly like the uploaded image: soft cel shading, thin clean even linework, warm natural palette.

Keep her face, eyes, bangs, body proportions and skin tone identical to the uploaded image.

Row 1 – full body standing, neutral pose, left to right: FRONT view, LEFT-SIDE profile, BACK view, three-quarter view.
Outfit: plain dark navy sleeveless tank top (#1F2E4A), plain black running shorts, completely plain bright red running shoes (#D7322B) with clean white soles — no stripes, no swoosh, no side markings.

Fixed features, identical in every view: one high ponytail tied at the exact back-center of the head with a PLAIN BLACK hair tie that blends into the hair (no pink or colored scrunchie); straight-cut full bangs; hair drawn smooth and tidy with no stray flyaway strands; no accessories, no jewelry, no watch; no moles or marks on the face.

Row 2 – head and shoulders, front view, five expressions: exhausted and panting with mouth open; eyes closed catching breath; gritted-teeth determination; relieved gentle smile with eyes open; teary happy smile.

No sweat-drop symbols. No text, labels, letters, numbers or logos anywhere on the sheet or the clothes.
```

### 3B-2 小晴服裝設定（同一個對話接著貼）
- **存檔名**：`03_design/char_xiaoqing_outfits_v1.png`

```text
Same character, same style, same plain beige background and lighting. Show her full body, FRONT view, in four outfits side by side, with identical face, bangs, black-tied ponytail and proportions in all four:
1) Home clothes: loose light-gray T-shirt (#BDB6AE) and dark gray shorts, barefoot, one white square gauze pad taped on EACH knee (both knees).
2) Winter training: dark navy long-sleeve windbreaker zipped to mid-chest (#1F2E4A), black full-length running tights, plain red running shoes with white soles.
3) Race day: dark navy sleeveless tank top, black shorts, a PLAIN WHITE rectangular race bib pinned on the chest with absolutely NO numbers or text, plain red running shoes with white soles.
4) Night training in the rain: dark navy tank top and black shorts, OLD dirty white running shoes with blue trim, hair and clothes wet.
No text, labels, numbers or logos anywhere.
```

---

## 3C 媽媽與阿姨設定圖
- **存檔名**：`03_design/char_mom_aunt_v1.png`

```text
Using the uploaded image as the exact style reference (do not copy the girl), create a CHARACTER DESIGN SHEET. 16:9, 1920x1080, plain warm light-beige background (#EFE4D2), even soft neutral lighting, clean modern Japanese 2D animation style exactly like the uploaded image: soft cel shading, thin clean even linework, warm natural palette.

Left half – "Mom": East Asian woman about 45 years old, gentle tired face that resembles the girl in the uploaded image (same eye shape, same skin tone), black chin-length bob haircut, beige open-front knit cardigan (#CDB48A) over a plain white top, dark brown trousers. Full body FRONT view and three-quarter view; below them three head-and-shoulder expressions: worried with reddened teary eyes; tense and holding her breath; crying with a happy smile.

Right half – "Auntie": East Asian woman about 60 years old, short curly gray-white hair (#B9B4AC), friendly round face, plain olive-green top (#4F6B3F), dark trousers. Full body FRONT view sitting on a simple bench, and two head-and-shoulder expressions: neutral, watching; warm smile.

No accessories, jewelry or glasses for either woman. No text, labels, letters, numbers or logos anywhere.
```

---

## 3D 鞋子道具設定圖
- **存檔名**：`03_design/prop_shoes_v1.png`

```text
Using the uploaded image as the exact style reference, create a PROP DESIGN SHEET. 16:9, 1920x1080, plain warm light-beige background (#EFE4D2), even soft neutral lighting, clean modern Japanese 2D animation style exactly like the uploaded image.

Left side – the OLD running shoes: exactly one pair (two shoes), white mesh with blue trim (#4A6FA5), worn, scuffed and dirty, thin worn-out soles. ONLY THE RIGHT SHOE has a small torn hole at the very front of the toe cap; the left shoe has NO hole. Show the pair side by side from a front three-quarter angle (right shoe on the right side of the pair). Below it, show the right shoe alone in side view with the toe hole clearly visible.

Right side – the NEW running shoes: exactly one pair (two shoes), completely plain bright red uppers (#D7322B) with clean white soles, brand new — no stripes, no swoosh, no side markings. Same angle as the old pair. Below it, one new shoe alone in side view.

No logos, brand marks, text, labels, letters or numbers anywhere.
```

---

## 交回之後
4 張圖全部傳給我。我會先用 Python 檢查比例和配色，再交給審核子 Agent 放大檢查一致性：髮圈、瀏海、鞋子數量、破洞只在右鞋、無文字。最後請你確認。
