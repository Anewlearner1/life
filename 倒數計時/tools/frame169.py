"""把 ChatGPT 生的 3:2 圖（1536×1024）置中裁成 16:9、縮成 1280×720，給 Flow 當首尾幀。

  python3 tools/frame169.py refs            # refs/*.png|jpg|webp → refs/169/*.png
  python3 tools/frame169.py refs --shift -0.05   # 裁切框往上移 5%（頭頂空間被裁掉時用）
"""
import os, sys
from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else "refs"
shift = float(sys.argv[sys.argv.index("--shift") + 1]) if "--shift" in sys.argv else 0.0
dst = os.path.join(src, "169"); os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        continue
    im = Image.open(os.path.join(src, f)).convert("RGB")
    w, h = im.size
    if w / h > 16 / 9:
        nw = round(h * 16 / 9); box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
    else:
        nh = round(w * 9 / 16); top = int((h - nh) / 2 + shift * h); top = max(0, min(h - nh, top))
        box = (0, top, w, top + nh)
    out = os.path.join(dst, os.path.splitext(f)[0] + ".png")
    im.crop(box).resize((1280, 720), Image.LANCZOS).save(out)
    print(f"{f} {w}x{h} → {out}")
