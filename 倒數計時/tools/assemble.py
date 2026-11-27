"""倒數計時 合成腳本：鏡頭 + 頭上數字 + 字幕 + 片尾字卡 + 配樂 → 成片。

  python3 tools/assemble.py            # shots/ 裡有的鏡頭就用，缺的用灰底分鏡卡代替（= 動態分鏡）
  python3 tools/assemble.py --out final.mp4

把 Veo 生成的 8 秒片段放到 shots/S1.mp4 … shots/S6.mp4（原檔就好，Veo 自帶的聲音會被丟掉）。
每段從 timeline.json 的 src_in 秒開始取用所需長度；720p 會放大到 1080p 輸出（字幕和數字因此更銳利），
任何比例都會被裁成 16:9、轉 24fps，長度不足會凍結最後一格補齊。數字的位置在 timeline.json 的 numbers（x, y 是 0–1 的畫面比例），
拿到實際片段後依人物頭頂位置微調即可。
"""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(ROOT, "timeline.json"), encoding="utf-8"))
FPS, W, H, DUR = cfg["fps"], cfg["w"], cfg["h"], cfg["duration"]
KOEN = "--ko-en" in sys.argv   # 韓英雙語字幕＋韓文配音版
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(
    ROOT, "倒數計時_成片_韓英版.mp4" if KOEN else "倒數計時_成片_中文版.mp4")


def font_path():
    for p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
              "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"):
        if os.path.exists(p):
            return p
    return subprocess.run(["fc-match", "-f", "%{file}", ":lang=zh-tw"], capture_output=True, text=True).stdout


FONT = font_path()
KO_FONT = ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 1)   # index 1 = Korean
EN_FONT = ("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 0)
KO_FONT_REG = ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 1)
_fx = {}
def FX(spec, size):
    path, idx = spec
    if not os.path.exists(path):
        return F(size)
    if (path, size) not in _fx:
        _fx[(path, size)] = ImageFont.truetype(path, size, index=idx)
    return _fx[(path, size)]


_fc = {}
def F(size):
    if size not in _fc:
        _fc[size] = ImageFont.truetype(FONT, size)
    return _fc[size]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------- 1. 底片：每個鏡頭轉成統一格式 ----------
tmp = tempfile.mkdtemp(prefix="cd_")
parts = []
for s in cfg["shots"]:
    nf = round(s["end"] * FPS) - round(s["start"] * FPS)  # 以格數切，避免累積誤差
    d = nf / FPS
    p = os.path.join(tmp, f"{s['id']}.mp4")
    src = os.path.join(ROOT, "shots", f"{s['id']}.mp4")
    if s.get("card"):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d={d + 1}", "-frames:v", str(nf), "-pix_fmt", "yuv420p", p])
    elif os.path.exists(src):
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
              f"tpad=stop_mode=clone:stop_duration={d},trim=end_frame={nf},setpts=PTS-STARTPTS")
        run(["ffmpeg", "-y", "-ss", str(s.get("src_in", 0)), "-i", src, "-an", "-vf", vf, "-frames:v", str(nf), "-pix_fmt", "yuv420p", p])
        print("鏡頭", s["id"], "← 實拍片段")
    else:
        img = Image.new("RGB", (W, H), (58, 62, 68))
        g = ImageDraw.Draw(img)
        for y in range(H):  # 陰天感漸層
            c = int(70 + 40 * y / H); g.line([(0, y), (W, y)], fill=(c, c + 3, c + 8))
        g.text((80, 70), s["id"], font=F(110), fill=(230, 230, 230))
        g.text((80, 200), s["label"], font=F(54), fill=(220, 220, 220))
        g.text((80, 280), f"{s['start']:.1f}s – {s['end']:.1f}s（佔位，待放入 shots/{s['id']}.mp4）",
               font=F(32), fill=(180, 180, 180))
        ip = os.path.join(tmp, f"{s['id']}.png"); img.save(ip)
        run(["ffmpeg", "-y", "-loop", "1", "-i", ip, "-r", str(FPS), "-frames:v", str(nf), "-pix_fmt", "yuv420p", p])
        print("鏡頭", s["id"], "← 佔位卡")
    parts.append(p)
lst = os.path.join(tmp, "list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
base = os.path.join(tmp, "base.mp4")
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

# ---------- 2. 逐格疊字 ----------
shot_end = {s["id"]: s["end"] for s in cfg["shots"]}
shot_start = {s["id"]: s["start"] for s in cfg["shots"]}


def glow_text(layer, xy, text, size, alpha, blur_extra=0):
    """頭上數字：細白字 + 柔光。"""
    f = F(size)
    tw = layer.textlength(text, font=f) if hasattr(layer, "textlength") else f.getlength(text)
    x, y = xy[0] - tw / 2, xy[1] - size / 2
    glow = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(glow)
    gd.text((x, y), text, font=f, fill=(200, 230, 255, int(255 * alpha)))
    glow = glow.filter(ImageFilter.GaussianBlur(10 + blur_extra))
    sharp = Image.new("RGBA", (W, H)); sd = ImageDraw.Draw(sharp)
    sd.text((x, y), text, font=f, fill=(255, 255, 255, int(235 * alpha)))
    if blur_extra:
        sharp = sharp.filter(ImageFilter.GaussianBlur(blur_extra))
    return Image.alpha_composite(glow, sharp)


def fmt_roll(target, k):
    v = int(round(int(target.replace(",", "")) * k))
    return f"{v:,}"


def overlay(t):
    layer = Image.new("RGBA", (W, H))
    for n in cfg["numbers"]:
        if not (n["t_in"] <= t < shot_end[n["shot"]]):
            continue
        a = min((t - n["t_in"]) / 0.5, 1.0)
        flick = 0.85 + 0.15 * math.sin(t * 23 + n["x"] * 40) if a >= 1 else 1
        rise = (1 - a) ** 2 * 24
        bob = math.sin(t * 2.2 + n["x"] * 9) * 4
        text = n["text"]
        if n.get("rollup"):
            k = min((t - n["t_in"]) / n["rollup"], 1.0)
            text = fmt_roll(text, 1 - (1 - k) ** 3)
        el = t - shot_start[n["shot"]]
        if n.get("track"):  # [[秒(鏡內), x, y], ...] 線性內插，前後夾住
            tr = n["track"]
            if el <= tr[0][0]:
                nx, ny = tr[0][1], tr[0][2]
            elif el >= tr[-1][0]:
                nx, ny = tr[-1][1], tr[-1][2]
            else:
                for (t0, x0, y0), (t1, x1, y1) in zip(tr, tr[1:]):
                    if t0 <= el <= t1:
                        k = (el - t0) / (t1 - t0); nx, ny = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
                        break
        else:
            nx, ny = n["x"] + n.get("vx", 0) * el, n["y"] + n.get("vy", 0) * el
        ny = max(ny, n.get("ymin", 0))
        layer = Image.alpha_composite(layer, glow_text(layer, (nx * W, ny * H + rise + bob), text,
                                                         n["size"], a * flick, n.get("blur", 0)))
    d = ImageDraw.Draw(layer)
    if KOEN:
        draw_bilingual(d, t)
        return layer
    for s in cfg["subs"]:
        if s["start"] <= t < s["end"]:
            lines = s["text"].split("\n")
            for i, line in enumerate(reversed(lines)):
                f = F(44); tw = f.getlength(line)
                x, y = (W - tw) / 2, H - 110 - i * 60
                for dx, dy in ((2, 2), (-1, -1), (2, 0), (0, 2)):
                    d.text((x + dx, y + dy), line, font=f, fill=(0, 0, 0, 170))
                d.text((x, y), line, font=f, fill=(255, 255, 255, 255))
    c = cfg["card"]
    if t >= c["start"]:
        lt = t - c["start"]
        for i, line in enumerate(c["lines"]):
            a = max(0.0, min((lt - 0.2 - i * 0.7) / 0.5, 1.0))
            f = F(56); tw = f.getlength(line)
            d.text(((W - tw) / 2, H / 2 - 110 + i * 84), line, font=f, fill=(240, 240, 240, int(255 * a)))
        a = max(0.0, min((lt - 1.8) / 0.5, 1.0))
        f = F(34); line = "— " + c["title"] + " —"; tw = f.getlength(line)
        d.text(((W - tw) / 2, H / 2 + 110), line, font=f, fill=(170, 200, 230, int(255 * a)))
    return layer


def shadow_text(d, xy, text, font, fill, alpha):
    x, y = xy
    for dx, dy in ((2, 2), (-1, -1), (2, 0), (0, 2), (1, 3)):
        d.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, int(150 * alpha)))
    d.text((x, y), text, font=font, fill=fill[:3] + (int(255 * alpha),))


def draw_bilingual(d, t):
    """韓文在上（大、白），英文在下（小、淡灰藍），整組貼齊畫面下緣、置中，不壓到臉。"""
    for s in SUBS:
        if not (s["t0"] <= t < s["t1"]):
            continue
        a = min((t - s["t0"]) / 0.12, (s["t1"] - t) / 0.12, 1.0)
        ko = s["ko"].split("\n"); en = s["en"].split("\n")
        fk, fe = FX(KO_FONT, 46), FX(EN_FONT, 31)
        y = H - 64 - len(en) * 40 - len(ko) * 60
        for line in ko:
            shadow_text(d, ((W - fk.getlength(line)) / 2, y), line, fk, (255, 255, 255), a); y += 60
        y += 4
        for line in en:
            shadow_text(d, ((W - fe.getlength(line)) / 2, y), line, fe, (214, 224, 236), a); y += 40
    c = cfg["card"]
    if t >= c["start"]:
        lt = t - c["start"]
        fk, fe = FX(KO_FONT, 58), FX(EN_FONT, 30)
        for i, (k, e) in enumerate(zip(c["ko"], c["en"])):
            a = max(0.0, min((lt - (0.15, 1.35)[i]) / 0.5, 1.0))
            y0 = H / 2 - 170 + i * 150
            d.text(((W - fk.getlength(k)) / 2, y0), k, font=fk, fill=(242, 242, 242, int(255 * a)))
            d.text(((W - fe.getlength(e)) / 2, y0 + 78), e, font=fe, fill=(165, 180, 198, int(255 * a)))
        a = max(0.0, min((lt - 2.0) / 0.4, 1.0))
        ft = FX(KO_FONT_REG, 28); line = f"{c['title_ko']}   ·   {c['title_en']}"
        d.text(((W - ft.getlength(line)) / 2, H / 2 + 150), line, font=ft, fill=(150, 190, 230, int(255 * a)))


music = os.path.join(tmp, "music.wav")
if KOEN:
    tj = os.path.join(tmp, "timing.json")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "mix.py"), music, tj], check=True)
    timing = json.load(open(tj))
    SUBS = []
    order = sorted(cfg["subs"], key=lambda s: timing[s["id"]][0])
    for i, s in enumerate(order):
        t0, t1 = timing[s["id"]]
        nxt = timing[order[i + 1]["id"]][0] if i + 1 < len(order) else cfg["card"]["start"]
        SUBS.append(dict(s, t0=t0 - 0.08, t1=min(t1 + 0.4, nxt - 0.06, cfg["card"]["start"])))
else:
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "music.py"), music], check=True)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-i", music, "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                       stdin=subprocess.PIPE)
fsz = W * H * 3
i = 0
while True:
    buf = dec.stdout.read(fsz)
    if len(buf) < fsz:
        break
    t = i / FPS
    frame = Image.frombytes("RGB", (W, H), buf).convert("RGBA")
    frame = Image.alpha_composite(frame, overlay(t)).convert("RGB")
    enc.stdin.write(frame.tobytes())
    i += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(f"完成：{out}（{i} 格，{i / FPS:.2f}s）")
