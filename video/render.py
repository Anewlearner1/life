"""末日求生 Part 1 — motion-comic renderer.

Turns the 15-panel storyboard into a ~48s 1080p video:
camera moves (Ken Burns), shake / punch-ins, lantern & fire flicker,
embers, film grain, vignette, crossfades and crisp re-typeset subtitles.
Frames are piped raw into ffmpeg; audio comes from audio.py.

usage: python3 render.py <storyboard.png> <out_dir>
"""
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 24
S = 48 / 45  # stretch storyboard timecodes (0-45s) to 48s
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# Panel rectangles in the storyboard (detected from the white gutters).
ROWS = [(0, 264, [(0, 375), (376, 792), (793, 1213)]),
        (266, 516, [(0, 432), (433, 843), (846, 1213)]),
        (518, 755, [(0, 435), (436, 820), (822, 1213)]),
        (757, 1001, [(0, 356), (358, 748), (750, 1213)]),
        (1003, 1297, [(0, 395), (397, 779), (780, 1213)])]

# Each shot: storyboard start/end, subtitle, camera (zoom0, zoom1, centre0, centre1),
# transition in ("cut" | "fade" | "black"), extra effects.
SHOTS = [
    dict(t=(0, 1), sub="末日第 1 天", cam=(1.00, 1.10, (.55, .55), (.60, .62)), tr="black",
         fx={"lantern": (.61, .77)}),
    dict(t=(1, 3), sub="這些……夠活多久？", cam=(1.05, 1.18, (.40, .55), (.60, .42)), tr="fade"),
    dict(t=(3, 3.8), sub=None, cam=(1.00, 1.04, (.5, .5), (.5, .5)), tr="cut",
         fx={"slam": True, "embers": 40}),
    dict(t=(3.8, 8), sub="收音機三天前就沒聲音了。", cam=(1.02, 1.16, (.45, .55), (.55, .45)), tr="fade",
         fx={"fire": True, "embers": 50}),
    dict(t=(8, 13), sub="罐頭 12 個。米 2 袋。", cam=(1.00, 1.22, (.50, .55), (.45, .45)), tr="fade"),
    dict(t=(13, 17), sub="水……只剩半桶。", cam=(1.00, 1.18, (.55, .50), (.42, .62)), tr="fade"),
    dict(t=(17, 21), sub="籬笆是唯一的防線。", cam=(1.04, 1.12, (.35, .55), (.50, .52)), tr="fade",
         fx={"fire": True, "embers": 70, "hits": [17.7, 18.9, 20.1]}),
    dict(t=(21, 25), sub="一天三餐……只夠撐兩天。", cam=(1.00, 1.20, (.50, .55), (.50, .40)), tr="fade"),
    dict(t=(25, 29), sub="我們一起撐。", cam=(1.02, 1.15, (.45, .55), (.55, .55)), tr="fade",
         fx={"fire": True, "embers": 30, "warm": True}),
    dict(t=(29, 32), sub=None, cam=(1.00, 1.22, (.45, .55), (.62, .45)), tr="black",
         fx={"night": True, "window": (.66, .42)}),
    dict(t=(32, 34), sub=None, cam=(1.00, 1.06, (.50, .5), (.52, .5)), tr="cut",
         fx={"knocks": [32.25, 32.85, 33.45]}),
    dict(t=(34, 36), sub=None, cam=(1.12, 1.00, (.45, .45), (.50, .50)), tr="cut",
         fx={"door": (.86, .50), "hits": [34.05]}),
    dict(t=(36, 38), sub="門外……沒有人。", cam=(1.00, 1.25, (.50, .60), (.58, .42)), tr="fade",
         fx={"embers": 25}),
    dict(t=(38, 42), sub=None, cam=(1.00, 1.10, (.40, .62), (.40, .62)), tr="black",
         fx={"question": True, "heartbeat": True}),
    dict(t=(42, 45), sub=None, cam=(1.06, 1.00, (.50, .50), (.50, .50)), tr="fade",
         fx={"fire": True, "embers": 60, "outro": True}),
]
for s in SHOTS:
    s["a"], s["b"] = s["t"][0] * S, s["t"][1] * S
TOTAL = SHOTS[-1]["b"]
NFRAMES = int(round(TOTAL * FPS))

PANELS = []


def load_panels(path):
    im = Image.open(path).convert("RGB")
    out = []
    for y0, y1, cols in ROWS:
        for x0, x1 in cols:
            out.append(im.crop((x0 + 2, y0 + 2, x1 - 2, y1 - 2)))
    fixed = []
    for i, p in enumerate(out, 1):
        w, h = p.size
        if i == 13:                       # drop caption + the early "待續…"
            p = p.crop((0, 38, w - 2, 232))
        elif i == 14:                     # black out the question; we re-typeset it
            p = p.copy()
            ImageDraw.Draw(p).rectangle((0, 0, w, 98), fill=(0, 0, 0))
        else:
            p = p.crop((0, 38, w, h))
        # upscale ~6x, soften compression blocks, re-sharpen edges
        p = p.resize((p.width * 6, p.height * 6), Image.LANCZOS)
        p = p.filter(ImageFilter.GaussianBlur(2.2)).filter(ImageFilter.UnsharpMask(4, 80, 2))
        fixed.append(p)
    return fixed


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def noise1(t, seed):
    """cheap smooth 1D noise in [-1,1]."""
    return (math.sin(t * 7.3 + seed) * .5 + math.sin(t * 13.1 + seed * 2.1) * .3
            + math.sin(t * 23.7 + seed * 3.7) * .2)


# ---------------------------------------------------------------- per-frame helpers
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = 1 - 0.55 * np.clip(((XX / W - .5) ** 2 * 1.4 + (YY / H - .5) ** 2 * 2.2) * 1.6, 0, 1)[..., None]
rng = np.random.default_rng(7)
GRAIN = [np.asarray(Image.fromarray((rng.normal(128, 40, (H // 2, W // 2))).clip(0, 255).astype(np.uint8))
                    .resize((W, H), Image.BILINEAR), dtype=np.float32)[..., None] / 255 - .5 for _ in range(6)]


def view_box(panel, zoom, cx, cy, dx=0.0, dy=0.0):
    pw, ph = panel.size
    bw = min(pw, ph * W / H)
    bh = bw * H / W
    bw, bh = bw / zoom, bh / zoom
    x = cx * pw - bw / 2 + dx * bw
    y = cy * ph - bh / 2 + dy * bh
    x = min(max(x, 0), pw - bw)
    y = min(max(y, 0), ph - bh)
    return (x, y, x + bw, y + bh)


def to_screen(box, panel, u, v):
    pw, ph = panel.size
    return ((u * pw - box[0]) / (box[2] - box[0]) * W, (v * ph - box[1]) / (box[3] - box[1]) * H)


def glow(cx, cy, radius, color, strength):
    d2 = ((XX - cx) ** 2 + (YY - cy) ** 2) / (radius ** 2)
    return np.exp(-d2)[..., None] * np.array(color, np.float32) * strength


def embers(t, n, seed):
    layer = Image.new("L", (W // 2, H // 2), 0)
    d = ImageDraw.Draw(layer)
    r = np.random.default_rng(seed)
    xs, sp, ph, sz, sw = r.random(n), r.uniform(.04, .14, n), r.random(n), r.uniform(1, 3.2, n), r.random(n) * 6
    for i in range(n):
        y = 1 - ((ph[i] + t * sp[i]) % 1.0)
        x = xs[i] + .02 * math.sin(t * 1.3 + sw[i]) + t * .01
        x = x % 1.0
        a = int(255 * min(1, 4 * y) * (.6 + .4 * math.sin(t * 9 + sw[i])))
        rr = sz[i]
        d.ellipse((x * W / 2 - rr, y * H / 2 - rr, x * W / 2 + rr, y * H / 2 + rr), fill=a)
    core = np.asarray(layer.resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
    halo = np.asarray(layer.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR),
                      np.float32)[..., None] / 255
    return core * np.array([1.0, .75, .35], np.float32) + halo * np.array([1.0, .4, .1], np.float32) * 1.6


def render_shot(idx, t):
    s = SHOTS[idx]
    fx = s.get("fx", {})
    panel = PANELS[idx]
    lt = (t - s["a"]) / (s["b"] - s["a"])
    z0, z1, c0, c1 = s["cam"]
    e = smooth(lt)
    zoom = z0 + (z1 - z0) * e
    cx, cy = c0[0] + (c1[0] - c0[0]) * e, c0[1] + (c1[1] - c0[1]) * e
    dx = dy = 0.0
    bright = 1.0
    flash = 0.0

    def impact(times, amp, punch):
        nonlocal dx, dy, zoom, flash
        for k in times:
            k *= S
            if k <= t < k + .45:
                q = (t - k) / .45
                decay = (1 - q) ** 2
                dx += amp * decay * math.sin(t * 90)
                dy += amp * decay * math.cos(t * 77)
                zoom *= 1 + punch * decay
                flash = max(flash, .35 * decay)

    if "hits" in fx:
        impact(fx["hits"], .010, .015)
    if "knocks" in fx:
        impact(fx["knocks"], .02, .06)
    if fx.get("slam"):
        q = (t - s["a"]) / .22
        if q < 1:
            zoom *= 1 + .35 * (1 - smooth(q))
        k = t - s["a"] - .22
        if 0 <= k < .4:
            dx += .02 * (1 - k / .4) * math.sin(t * 95)
            dy += .02 * (1 - k / .4) * math.cos(t * 81)
            flash = max(flash, .4 * (1 - k / .4))
    if fx.get("heartbeat"):
        beat = (t - s["a"]) % .9
        zoom *= 1 + .012 * math.exp(-beat * 9) + .008 * math.exp(-max(beat - .2, 0) * 9) * (beat > .2)

    box = view_box(panel, zoom, cx, cy, dx, dy)
    img = np.asarray(panel.transform((W, H), Image.EXTENT, box, Image.BICUBIC), np.float32) / 255

    if fx.get("fire"):
        bright *= 1 + .05 * noise1(t * 1.7, idx)
    if fx.get("night"):
        img = img * np.array([.72, .78, 1.0], np.float32)
    if fx.get("warm"):
        img = img * np.array([1.06, 1.0, .9], np.float32)
    img = img * bright

    if "lantern" in fx:
        x, y = to_screen(box, panel, *fx["lantern"])
        f = .55 + .25 * noise1(t * 3, 1) + .08 * math.sin(t * 41)
        img = img * (.82 + .18 * f) + glow(x, y, 330, (1.0, .6, .2), .45 * f)
    if "window" in fx:
        x, y = to_screen(box, panel, *fx["window"])
        f = .7 + .3 * noise1(t * 2.5, 3)
        img = img + glow(x, y, 260, (1.0, .7, .3), .22 * f)
    if "door" in fx:
        x, y = to_screen(box, panel, *fx["door"])
        f = .7 + .3 * noise1(t * 4, 5)
        img = img + glow(x, y, 520, (1.0, .45, .12), .30 * f)
    if "embers" in fx:
        img = img + embers(t, fx["embers"], idx * 11) * .9
    if flash:
        img = img + flash * np.array([1.0, .85, .7], np.float32)
    return np.clip(img, 0, 1)


def text_layer(frame, t):
    """subtitles + typeset overlays, drawn on a PIL image."""
    im = Image.fromarray(frame)
    for s in SHOTS:
        if s["sub"] and s["a"] + .1 <= t < s["b"] - .05:
            a = min(1, (t - s["a"] - .1) / .25, (s["b"] - .05 - t) / .2)
            draw_sub(im, s["sub"], a)
    q = SHOTS[13]
    if q["a"] <= t < q["b"] + .3:
        lt = t - q["a"]
        draw_typed(im, "如果是你，", lt - .3, (1060, 120), 88)
        draw_typed(im, "你會開門嗎？", lt - 1.3, (1060, 240), 88)
    return im


def draw_sub(im, text, alpha):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(FONT, 62)
    tw = d.textlength(text, font=f)
    x, y = (W - tw) / 2, H - 150
    d.text((x + 3, y + 4), text, font=f, fill=(0, 0, 0, 160))
    d.text((x, y), text, font=f, fill=(250, 240, 225, 255), stroke_width=4, stroke_fill=(15, 8, 4, 255))
    _blend(im, layer, alpha)


def draw_typed(im, text, lt, pos, size):
    if lt <= 0:
        return
    n = min(len(text), int(lt / .12) + 1)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(FONT, size)
    d.text(pos, text[:n], font=f, fill=(245, 238, 230, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    im.alpha_composite(layer) if im.mode == "RGBA" else im.paste(layer, (0, 0), layer)


def _blend(im, layer, alpha):
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * max(alpha, 0)))
        layer.putalpha(a)
    im.paste(layer, (0, 0), layer)


def frame_at(i):
    t = i / FPS
    idx = max(k for k, s in enumerate(SHOTS) if s["a"] <= t + 1e-6)
    s = SHOTS[idx]
    img = render_shot(idx, t)
    since = t - s["a"]
    if s["tr"] == "fade" and idx > 0 and since < .35:
        prev = render_shot(idx - 1, t)
        k = smooth(since / .35)
        img = prev * (1 - k) + img * k
    elif s["tr"] == "black" and since < .5:
        img = img * smooth(since / .5)
    if idx + 1 < len(SHOTS) and SHOTS[idx + 1]["tr"] == "black" and s["b"] - t < .35:
        img = img * smooth((s["b"] - t) / .35)
    if TOTAL - t < 1.2:                                   # final fade out
        img = img * smooth((TOTAL - t) / 1.2)
    img = img * VIGNETTE + GRAIN[i % 6] * .045
    frame = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    return text_layer(frame, t).convert("RGB").tobytes()


def init(path):
    global PANELS
    PANELS = load_panels(path)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 3:                                  # preview stills: render.py src out t1 t2 ...
        init(src)
        for ts in sys.argv[3:]:
            i = int(float(ts) * FPS)
            Image.frombytes("RGB", (W, H), frame_at(i)).save(f"{out}/still_{ts}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", f"{out}/video_only.mp4"], stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=init, initargs=(src,)) as pool:
        for n, buf in enumerate(pool.imap(frame_at, range(NFRAMES), chunksize=4)):
            ff.stdin.write(buf)
            if n % 120 == 0:
                print(f"frame {n}/{NFRAMES}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", TOTAL, "s")
