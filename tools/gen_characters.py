"""Generate player + NPC sprites and portraits (16-bit chibi, top-down).

Run:  python3 tools/gen_characters.py

Sprites are drawn from a shared body/head template using "role" palette keys,
then recolored per character (see TEMPLATE KEYS). Outline (1px 'k') is added
automatically around every filled shape so silhouettes stay clean.

TEMPLATE KEYS (recolored by `recolor`):
  N/n  hair main/highlight      s/S  skin main/shade
  b/B  shirt main/shade         A/K  pants main/shade
  (accessories use keys outside this set so they are never recolored by accident)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageOps  # noqa: E402
from pixel import P, recolor, strip, save, CHAR_W, CHAR_H, PORTRAIT  # noqa: E402

DIRS = ["Down", "Up", "Left", "Right"]


# --------------------------------------------------------------------------
# tiny layer helpers: a layer is {(x, y): key}
# --------------------------------------------------------------------------
TR = {"H": "N", "h": "n"}


def parse(rows, y0=1):
    d = {}
    for dy, row in enumerate(rows):
        assert len(row) == CHAR_W, (y0 + dy, row, len(row))
        for x, ch in enumerate(row):
            if ch != ".":
                d[(x, y0 + dy)] = TR.get(ch, ch)
    return d


def setrow(d, y, row):
    assert len(row) == CHAR_W, (y, row)
    for x in range(CHAR_W):
        d.pop((x, y), None)
    for x, ch in enumerate(row):
        if ch != ".":
            d[(x, y)] = TR.get(ch, ch)


def rect(d, x0, y0, x1, y1, k):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d[(x, y)] = k


def to_image(d, w, h, dy=0):
    """Render layer with a 1px 'k' outline (4-neighbourhood)."""
    img = Image.new("RGBA", (w, h), P["_"])
    px = img.load()
    fill = {(x, y + dy): k for (x, y), k in d.items()}
    for (x, y), k in fill.items():
        if 0 <= x < w and 0 <= y < h:
            px[x, y] = P[k]
    for (x, y) in fill:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in fill and 0 <= nx < w and 0 <= ny < h:
                px[nx, ny] = P["k"]
    return img


# --------------------------------------------------------------------------
# HEAD templates (rows 1..10). Row 0 and row 11 are outline rows.
# --------------------------------------------------------------------------
HEAD = {
    "Down": [
        "....HHHHHHHH....",
        "...HHhhHHHHHH...",
        "...HHHHHHHHHH...",
        "...HHHssssHHH...",
        "...HssssssssH...",
        "...HskssssksH...",
        "...HskssssksH...",
        "...HmssssssmH...",
        "....sssRRsss....",
        ".....SSSSSS.....",
    ],
    "Up": [
        "....HHHHHHHH....",
        "...HHhhHHHHHH...",
        "...HHHHHHHHHH...",
        "...HHHHHHHHHH...",
        "...HHHHhhHHHH...",
        "...HHHHHhHHHH...",
        "...HHHHHHHHHH...",
        "...HHHHHHHHHH...",
        "....HHHHHHHH....",
        ".....HHssHH.....",
    ],
    "Left": [
        "....HHHHHHHH....",
        "...HHhhHHHHHH...",
        "...HHHHHHHHHH...",
        "...HHHHHHHHHH...",
        "...ssssHHHHHH...",
        "...skssssHHHH...",
        "...sksssSHHHH...",
        "...smssssHHHH...",
        "....sRsssHHH....",
        ".....ssssHH.....",
    ],
}
HEAD["Left"][5] = "...skssssHHHH..."
HEAD["Left"][6] = "...sksssSHHHH..."


def head_layer(dirn, style, accs, blink=False):
    d = parse(HEAD[dirn])
    # --- hair style variations ---
    if style == "long":
        if dirn == "Down":
            for y in range(9, 15):
                d[(3, y)] = "N"
                d[(12, y)] = "N"
        elif dirn == "Up":
            for y in range(11, 16):
                for x in range(4, 12):
                    d[(x, y)] = "N"
        else:
            for y in range(9, 15):
                for x in (9, 10, 11, 12):
                    d[(x, y)] = "N"
    elif style == "bob":
        if dirn == "Down":
            for y in range(9, 12):
                d[(3, y)] = "N"
                d[(12, y)] = "N"
        elif dirn == "Up":
            for y in range(11, 13):
                for x in range(4, 12):
                    d[(x, y)] = "N"
        else:
            for y in range(9, 12):
                for x in (9, 10, 11, 12):
                    d[(x, y)] = "N"
    elif style == "spiky":
        setrow(d, 1, "....H.HHHH.H....")
        setrow(d, 2, "...HHhHHHHHHH...")
        if dirn == "Down":
            d[(5, 4)] = "s"
            d[(10, 4)] = "s"
    elif style == "pony":
        if dirn == "Down":
            for y in (4, 5, 6):
                d[(13, y)] = "N"
            d[(13, 4)] = "n"
        elif dirn == "Up":
            for y in range(11, 16):
                d[(7, y)] = "N"
                d[(8, y)] = "N"
            d[(7, 11)] = "n"
        else:
            for y in range(4, 10):
                d[(13, y)] = "N"
                d[(14, y)] = "N"
            d[(13, 4)] = "n"

    # --- hats / accessories on head ---
    for a in accs:
        if a == "cap":
            setrow(d, 1, "....bbbbbbbb....")
            setrow(d, 2, "...bbbbbbbbbb...")
            setrow(d, 3, "...bbbbbbbbbb...")
            if dirn == "Down":
                setrow(d, 4, "...BBBBBBBBBB...")
            elif dirn == "Up":
                setrow(d, 4, "...bbbbbbbbbb...")
                setrow(d, 5, "...BBBBBBBBBB...")
            else:
                setrow(d, 4, "..BBBBBBBBBB....")
            d[(7, 2)] = "y"
            d[(8, 2)] = "y"
            if dirn == "Up":
                d[(7, 2)] = "b"
                d[(8, 2)] = "b"
            if dirn == "Left":
                d[(7, 2)] = "b"
                d[(8, 2)] = "b"
        elif a == "strawhat":
            setrow(d, 1, "....yyyyyyyy....")
            setrow(d, 2, "...yyyyyyyyyy...")
            setrow(d, 3, "..YYYYYYYYYYYY..")
            d[(5, 2)] = "Y"
            d[(10, 2)] = "Y"
        elif a == "beret":
            setrow(d, 1, ".....rrrrrr.....")
            setrow(d, 2, "...rrrrrrrrrr...")
            setrow(d, 3, "...RRrrrrrrRR...")
            if dirn == "Left":
                setrow(d, 1, "....rrrrrr......")
                setrow(d, 2, "..rrrrrrrrrr....")
                setrow(d, 3, "..RRrrrrrrRR....")
            d[(8, 1)] = "R"
        elif a == "glasses":
            if dirn == "Down":
                for y in (6, 7):
                    d[(4, y)] = "g"
                    d[(6, y)] = "g"
                    d[(9, y)] = "g"
                    d[(11, y)] = "g"
                d[(7, 6)] = "g"
                d[(8, 6)] = "g"
            elif dirn == "Left":
                d[(3, 6)] = "g"
                d[(3, 7)] = "g"
                d[(5, 6)] = "g"
                d[(5, 7)] = "g"
        elif a == "mustache":
            if dirn == "Down":
                for x in (6, 7, 8, 9):
                    d[(x, 8)] = "g"
            elif dirn == "Left":
                d[(3, 8)] = "g"
                d[(4, 8)] = "g"

    if blink and dirn == "Down":
        d[(5, 6)] = "s"
        d[(10, 6)] = "s"
    if blink and dirn == "Left":
        d[(4, 6)] = "s"
    return d


# --------------------------------------------------------------------------
# BODY (torso, arms, pants, legs). rows 12..22.
# --------------------------------------------------------------------------
def legs(d, dirn, phase):
    """phase: 'stand', 'A', 'B' (walk steps)."""
    if dirn in ("Down", "Up"):
        if phase == "stand":
            rect(d, 5, 20, 6, 21, "A")
            rect(d, 9, 20, 10, 21, "A")
            rect(d, 4, 22, 6, 22, "T")
            rect(d, 9, 22, 11, 22, "T")
        elif phase == "A":      # left leg forward, right lifted
            rect(d, 5, 20, 6, 21, "A")
            rect(d, 9, 20, 10, 20, "A")
            rect(d, 4, 22, 6, 22, "T")
            rect(d, 9, 21, 11, 21, "T")
        else:                   # right leg forward, left lifted
            rect(d, 9, 20, 10, 21, "A")
            rect(d, 5, 20, 6, 20, "A")
            rect(d, 9, 22, 11, 22, "T")
            rect(d, 4, 21, 6, 21, "T")
    else:  # side view, facing left
        if phase == "stand":
            rect(d, 6, 20, 7, 21, "A")
            rect(d, 8, 20, 9, 21, "K")
            rect(d, 4, 22, 8, 22, "T")
        else:
            front, back = ("A", "K") if phase == "A" else ("K", "A")
            # front leg forward (left)
            rect(d, 5, 20, 6, 20, front)
            rect(d, 4, 21, 5, 21, front)
            rect(d, 2, 22, 5, 22, "T")
            # back leg backward (right), foot lifted
            rect(d, 9, 20, 10, 20, back)
            rect(d, 10, 21, 11, 21, back)
            rect(d, 10, 22, 12, 22, "T")


def arms_down(d, left_len, right_len):
    for x, ln in ((4, left_len), (11, right_len)):
        for y in range(12, 12 + ln):
            d[(x, y)] = "B"
        d[(x, 12 + ln)] = "s"


def body_layer(dirn, phase, accs, arm_pose=0):
    d = {}
    # torso
    rect(d, 5, 12, 10, 16, "b")
    rect(d, 5, 16, 10, 16, "B")
    for y in range(12, 16):
        d[(10, y)] = "B"
    # pants
    rect(d, 5, 17, 10, 19, "A")
    for y in range(17, 20):
        d[(10, y)] = "K"
    if dirn == "Down":
        d[(7, 12)] = "s"
        d[(8, 12)] = "s"
        d[(7, 19)] = "K"
        d[(8, 19)] = "K"
        if arm_pose == 0:
            arms_down(d, 3, 3)
        elif arm_pose == 1:
            arms_down(d, 4, 2)
        else:
            arms_down(d, 2, 4)
    elif dirn == "Up":
        d[(7, 19)] = "K"
        d[(8, 19)] = "K"
        if arm_pose == 0:
            arms_down(d, 3, 3)
        elif arm_pose == 1:
            arms_down(d, 4, 2)
        else:
            arms_down(d, 2, 4)
    else:
        d[(5, 12)] = "s"   # neck hint (front of torso, under chin)
        ax = {0: 7, 1: 8, 2: 6}[arm_pose]
        rect(d, ax, 12, ax + 1, 14, "B")
        rect(d, ax, 15, ax + 1, 15, "s")
    # accessories
    for a in accs:
        accessory_body(d, dirn, a)
    legs(d, dirn, phase)
    return d


def accessory_body(d, dirn, a):
    if a == "apron":
        if dirn == "Down":
            rect(d, 6, 13, 9, 16, "w")
            rect(d, 5, 17, 10, 19, "w")
            rect(d, 5, 19, 10, 19, "G")
            d[(7, 13)] = "G"
            d[(8, 13)] = "G"
        elif dirn == "Left":
            rect(d, 5, 14, 7, 16, "w")
            rect(d, 5, 17, 8, 19, "w")
            rect(d, 5, 19, 8, 19, "G")
        else:
            d[(7, 16)] = "w"
            d[(8, 16)] = "w"
            d[(6, 17)] = "w"
            d[(9, 17)] = "w"
    elif a == "tie":
        if dirn == "Down":
            d[(7, 13)] = "r"
            d[(8, 13)] = "r"
            rect(d, 7, 14, 8, 16, "r")
            d[(7, 16)] = "R"
            d[(8, 16)] = "R"
        elif dirn == "Left":
            rect(d, 5, 13, 5, 15, "r")
    elif a == "overalls":
        if dirn == "Down":
            rect(d, 6, 15, 9, 16, "e")
            d[(6, 13)] = "e"
            d[(6, 14)] = "e"
            d[(9, 13)] = "e"
            d[(9, 14)] = "e"
            d[(6, 15)] = "y"
            d[(9, 15)] = "y"
        elif dirn == "Up":
            d[(6, 13)] = "e"
            d[(6, 14)] = "e"
            d[(9, 13)] = "e"
            d[(9, 14)] = "e"
            rect(d, 6, 15, 9, 16, "e")
        else:
            rect(d, 5, 15, 8, 16, "e")
            d[(5, 13)] = "e"
            d[(5, 14)] = "e"
    elif a == "bag":
        if dirn == "Down":
            for i in range(5):
                d[(5 + i, 12 + i)] = "n"
                d[(6 + i, 12 + i)] = "N"
            rect(d, 9, 16, 12, 18, "n")
            rect(d, 9, 18, 12, 18, "N")
            d[(10, 17)] = "y"
        elif dirn == "Up":
            for i in range(5):
                d[(9 - i, 12 + i)] = "n"
                d[(8 - i, 12 + i)] = "N"
            rect(d, 3, 16, 6, 18, "n")
            rect(d, 3, 18, 6, 18, "N")
        else:
            rect(d, 8, 15, 11, 18, "n")
            rect(d, 8, 18, 11, 18, "N")
            d[(9, 16)] = "y"
            for i in range(3):
                d[(6 + i, 12 + i)] = "N"
    elif a == "backpack":
        if dirn == "Down":
            for y in range(12, 16):
                d[(5, y)] = "Y"
                d[(10, y)] = "Y"
        elif dirn == "Up":
            rect(d, 4, 12, 11, 17, "o")
            rect(d, 4, 17, 11, 17, "Y")
            rect(d, 6, 14, 9, 15, "Y")
            d[(7, 14)] = "y"
        else:
            rect(d, 9, 12, 12, 17, "o")
            rect(d, 9, 17, 12, 17, "Y")
            d[(11, 14)] = "Y"
    elif a == "smock":
        if dirn == "Down":
            d[(6, 14)] = "y"
            d[(9, 15)] = "r"
            d[(5, 16)] = "m"
            d[(10, 13)] = "l"
        elif dirn == "Up":
            d[(6, 14)] = "y"
            d[(9, 15)] = "r"
        else:
            d[(8, 16)] = "y"
            d[(6, 14)] = "r"
    elif a == "scarf":
        if dirn == "Down":
            rect(d, 5, 12, 10, 12, "y")
            d[(5, 13)] = "Y"
            d[(6, 13)] = "y"
            d[(6, 14)] = "Y"
        elif dirn == "Up":
            rect(d, 5, 12, 10, 12, "y")
            rect(d, 5, 13, 10, 13, "Y")
        else:
            rect(d, 5, 12, 9, 12, "y")
            rect(d, 8, 13, 9, 14, "y")
            d[(9, 14)] = "Y"


# --------------------------------------------------------------------------
# frame composition
# --------------------------------------------------------------------------
def compose(dirn, phase, accs, style, head_dy=0, arm_pose=0, blink=False):
    base = "Left" if dirn == "Right" else dirn
    body = to_image(body_layer(base, phase, accs, arm_pose), CHAR_W, CHAR_H)
    head = to_image(head_layer(base, style, accs, blink), CHAR_W, CHAR_H, dy=head_dy)
    body.alpha_composite(head)
    return body


def walk_frames(dirn, accs, style):
    base = "Left" if dirn == "Right" else dirn
    seq = [("stand", 0, 0), ("A", 1, 1), ("stand", 0, 0), ("B", 1, 2)]
    if base == "Left":
        # front/back leg alternate, arms swing opposite
        seq = [("stand", 0, 0), ("A", 1, 1), ("stand", 0, 0), ("B", 1, 2)]
    frames = []
    for phase, dy, arm in seq:
        frames.append(compose(base, phase, accs, style, head_dy=dy, arm_pose=arm))
    return frames


def idle_frames(dirn, accs, style):
    base = "Left" if dirn == "Right" else dirn
    f0 = compose(base, "stand", accs, style, 0)
    f1 = compose(base, "stand", accs, style, 1, blink=(base != "Up"))
    return [f0, f1]


def flip(frames):
    return [ImageOps.mirror(f) for f in frames]


def dir_frames(fn, dirn, accs, style):
    if dirn == "Right":
        return flip(fn("Left", accs, style))
    return fn(dirn, accs, style)


def make_mapping(cfg):
    m = {}
    hm, hh = cfg["hair"]
    sm, ss = cfg["skin"]
    tm, ts = cfg["shirt"]
    pm, ps = cfg["pants"]
    m.update({"N": hm, "n": hh, "s": sm, "S": ss, "b": tm, "B": ts, "A": pm, "K": ps})
    m.update(cfg.get("extra", {}))
    return {k: v for k, v in m.items() if k != v}


def render_sheet(cfg, kind, dirn):
    fn = walk_frames if kind == "walk" else idle_frames
    frames = dir_frames(fn, dirn, cfg["accs"], cfg["style"])
    img = strip(frames)
    mapping = make_mapping(cfg)
    if mapping:
        img = recolor(img, mapping)
    return img


# --------------------------------------------------------------------------
# PORTRAITS (48x48, drawn natively at portrait scale)
# --------------------------------------------------------------------------
def ell(d, cx, cy, rx, ry, k, clip=None):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                if clip is None or clip(x, y):
                    d[(x, y)] = k


def inside(cx, cy, rx, ry):
    return lambda x, y: ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0


def line(d, pts, k):
    for x, y in pts:
        d[(x, y)] = k


def portrait(cfg, expr="Neutral"):
    hm, hh = cfg["hair"]
    sm, ss = cfg["skin"]
    tm, ts = cfg["shirt"]
    style = cfg["style"]
    accs = cfg["accs"]
    pants_m = cfg["pants"][0]
    d = {}
    W = PORTRAIT

    head_in = inside(24, 22, 14, 13)

    # ---- back hair ----
    if style in ("long", "bob", "pony"):
        bottom = {"long": 44, "bob": 34, "pony": 30}[style]
        for y in range(11, bottom + 1):
            for x in range(8, 40):
                if y < 18 and not inside(24, 21, 17, 14)(x, y):
                    continue
                if y > bottom - 3 and (x < 9 or x > 38):
                    continue
                d[(x, y)] = hm
    if style == "pony":
        ell(d, 41, 27, 4.5, 9, hm)
        ell(d, 41, 27, 1.5, 6, hh)
        rect(d, 37, 19, 40, 21, "r")

    # ---- neck + shoulders ----
    rect(d, 20, 32, 27, 39, ss)
    for y in range(38, 48):
        half = 12 + int((y - 38) * 1.3)
        for x in range(24 - half, 24 + half):
            if 5 <= x < 43:
                d[(x, y)] = tm
    for y in range(38, 48):
        half = 12 + int((y - 38) * 1.3)
        for x in range(24 + half - 4, 24 + half):
            if 5 <= x < 43:
                d[(x, y)] = ts
    # collar / neckline
    for i in range(5):
        d[(20 + i, 38 + i // 2)] = ss
        d[(27 - i, 38 + i // 2)] = ss
    rect(d, 21, 38, 26, 39, ss)
    for a in accs:
        portrait_body_acc(d, a, tm, ts)

    # ---- face ----
    ell(d, 24, 22, 14, 13, sm)
    for y in range(8, 37):
        for x in range(8, 41):
            if head_in(x, y) and (x >= 34 or y >= 34):
                d[(x, y)] = ss
    ell(d, 10, 24, 2.6, 3, sm)
    ell(d, 38, 24, 2.6, 3, ss)
    rect(d, 10, 24, 10, 25, ss)

    # ---- front hair ----
    hat = [a for a in accs if a in ("cap", "strawhat", "beret")]
    crown = inside(24, 21, 15.5, 14.5)
    zig = [0, 1, 2, 1, 0, 1, 2, 1]
    for y in range(5, 28):
        for x in range(8, 41):
            if not crown(x, y) and not (9 <= x <= 12 or 35 <= x <= 38):
                continue
            if not (head_in(x, y) or crown(x, y)):
                continue
            bang = 16 + zig[(x - 8) % 8]
            if y <= bang and crown(x, y):
                d[(x, y)] = hm
            elif (9 <= x <= 12 or 35 <= x <= 38) and y <= (25 if style == "short" else 27) and head_in(x, y) is not None:
                if (x - 24) ** 2 + (y - 22) ** 2 * 0.6 > 100:
                    d[(x, y)] = hm
    if style == "spiky":
        for cx in (13, 19, 24, 29, 35):
            for i in range(6):
                for x in range(cx - 3 + i // 2, cx + 4 - i // 2):
                    d[(x, 8 - i)] = hm
        for x in range(12, 37):
            for y in (7, 8, 9):
                if crown(x, y):
                    d[(x, y)] = hm
    # highlight arc
    for x in range(14, 31):
        y = 10 + ((x - 21) ** 2) // 30
        if style != "spiky" or True:
            d[(x, y)] = hh
            if x < 22:
                d[(x, y + 1)] = hh
    # long hair side locks in front of shoulders
    if style in ("long", "bob"):
        yb = 44 if style == "long" else 33
        for y in range(23, yb):
            for x in range(8, 13):
                d[(x, y)] = hm
            for x in range(35, 40):
                d[(x, y)] = hm
        for y in range(26, yb - 2):
            d[(9, y)] = hh

    # ---- hats ----
    if "cap" in hat:
        ell(d, 24, 15, 15.5, 9.5, tm, clip=lambda x, y: y <= 17)
        ell(d, 24, 15, 15.5, 9.5, ts, clip=lambda x, y: 14 <= y <= 17)
        rect(d, 11, 17, 38, 19, ts)
        rect(d, 8, 19, 40, 20, tm)
        rect(d, 8, 20, 40, 20, ts)
        d[(24, 10)] = "y"
        d[(23, 11)] = "y"
        d[(24, 11)] = "y"
        d[(25, 11)] = "y"
        d[(24, 12)] = "y"
    if "strawhat" in hat:
        ell(d, 24, 10, 11, 8, "y")
        ell(d, 24, 10, 11, 8, "Y", clip=lambda x, y: x >= 31)
        rect(d, 13, 13, 35, 14, "R")
        ell(d, 24, 17, 22, 5, "y")
        ell(d, 24, 17, 22, 5, "Y", clip=lambda x, y: y >= 19)
        for x in range(4, 44):
            if (x // 2) % 2 == 0:
                d[(x, 17)] = "Y"
    if "beret" in hat:
        ell(d, 21, 12, 17, 8, "r")
        ell(d, 21, 12, 17, 8, "R", clip=lambda x, y: y >= 16 or x >= 34)
        rect(d, 20, 3, 21, 5, "R")
        rect(d, 11, 17, 35, 18, "R")
        d[(16, 9)] = "m"
        d[(17, 9)] = "m"
        d[(15, 10)] = "m"

    # ---- face features ----
    eyes(d, expr, hm)
    # nose
    d[(23, 27)] = ss if ss != sm else "S"
    d[(24, 27)] = ss if ss != sm else "S"
    mouth(d, expr, accs)
    for a in accs:
        if a == "glasses":
            for (x0, x1) in ((14, 22), (26, 34)):
                for x in range(x0, x1 + 1):
                    d[(x, 20)] = "g"
                    d[(x, 28 - 1)] = "g"
                for y in range(20, 28):
                    d[(x0, y)] = "g"
                    d[(x1, y)] = "g"
            rect(d, 23, 22, 25, 22, "g")
        elif a == "mustache":
            rect(d, 19, 28, 28, 29, "g")
            rect(d, 18, 29, 19, 30, "g")
            rect(d, 28, 29, 29, 30, "g")
            d[(23, 28)] = sm
            d[(24, 28)] = sm
            rect(d, 20, 28, 27, 28, "G")
    # clip + outline
    img = Image.new("RGBA", (W, W), P["_"])
    px = img.load()
    for (x, y), k in d.items():
        if 0 <= x < W and 0 <= y < W:
            px[x, y] = P[k]
    for (x, y) in list(d):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in d and 0 <= nx < W and 0 <= ny < W:
                px[nx, ny] = P["k"]
    if cfg.get("extra"):
        img = recolor(img, cfg["extra"])
    return img


def eyes(d, expr, hm):
    L, R = 16, 28   # left eye x0, right eye x0 (each 4 wide)
    y0 = 22
    brow_y = 19
    if expr == "Happy":
        for x0 in (L, R):
            line(d, [(x0, y0 + 3), (x0 + 1, y0 + 2), (x0 + 2, y0 + 2), (x0 + 3, y0 + 3)], "k")
            line(d, [(x0, y0 + 2), (x0 + 3, y0 + 2)], "k")
        for x0 in (L, R):
            line(d, [(x0 + 1, brow_y), (x0 + 2, brow_y)], hm)
    elif expr == "Sad":
        for x0 in (L, R):
            rect(d, x0, y0 + 1, x0 + 3, y0 + 5, "k")
            d[(x0 + 1, y0 + 2)] = "w"
            d[(x0 + 1, y0 + 3)] = "w"
        # tears
        line(d, [(L, y0 + 6), (L, y0 + 7)], "c")
        line(d, [(R + 3, y0 + 6), (R + 3, y0 + 7), (R + 3, y0 + 8)], "c")
        # slanted brows (inner ends up)
        line(d, [(L, brow_y + 1), (L + 1, brow_y + 1), (L + 2, brow_y), (L + 3, brow_y - 0)], hm)
        line(d, [(R, brow_y), (R + 1, brow_y), (R + 2, brow_y + 1), (R + 3, brow_y + 1)], hm)
        d[(L + 3, brow_y - 1)] = hm
        d[(R, brow_y - 1)] = hm
    else:
        for x0 in (L, R):
            rect(d, x0, y0, x0 + 3, y0 + 4, "k")
            d[(x0 + 1, y0 + 1)] = "w"
            d[(x0 + 1, y0 + 2)] = "w"
        for x0 in (L, R):
            line(d, [(x0, brow_y), (x0 + 1, brow_y), (x0 + 2, brow_y), (x0 + 3, brow_y)], hm)
    # blush
    by = 28 if expr != "Sad" else 29
    n = 3 if expr == "Happy" else 2
    for x0 in (13, 32):
        rect(d, x0, by, x0 + 2, by + (n - 2), "m")


def mouth(d, expr, accs):
    my = 31
    if "mustache" in accs:
        my = 32
    if expr == "Happy":
        rect(d, 20, my - 1, 27, my - 1, "k")
        line(d, [(21, my), (26, my)], "k")
        rect(d, 22, my, 25, my, "R")
        rect(d, 22, my + 1, 25, my + 1, "k")
        d[(23, my)] = "m"
        d[(24, my)] = "m"
    elif expr == "Sad":
        rect(d, 22, my, 25, my, "k")
        d[(21, my + 1)] = "k"
        d[(26, my + 1)] = "k"
    else:
        rect(d, 22, my, 25, my, "R")
        d[(21, my - 1)] = "R"
        d[(26, my - 1)] = "R"


def portrait_body_acc(d, a, tm, ts):
    if a == "apron":
        rect(d, 17, 41, 30, 47, "w")
        rect(d, 17, 41, 17, 47, "G")
        rect(d, 30, 41, 30, 47, "G")
        rect(d, 17, 38, 19, 41, "w")
        rect(d, 28, 38, 30, 41, "w")
        rect(d, 21, 44, 26, 46, "G")
    elif a == "tie":
        rect(d, 22, 38, 25, 40, "r")
        rect(d, 22, 41, 25, 47, "r")
        rect(d, 25, 41, 25, 47, "R")
        rect(d, 19, 38, 21, 40, "w")
        rect(d, 26, 38, 28, 40, "w")
    elif a == "overalls":
        rect(d, 16, 41, 31, 47, "e")
        rect(d, 16, 38, 19, 41, "e")
        rect(d, 28, 38, 31, 41, "e")
        rect(d, 31, 41, 31, 47, "E")
        d[(17, 41)] = "y"
        d[(30, 41)] = "y"
        rect(d, 20, 44, 27, 46, "E")
    elif a == "bag":
        for i in range(11):
            for t in range(3):
                x = 13 + i * 2 + t
                y = 38 + i
                if y < 48:
                    d[(x, y)] = "N"
        rect(d, 30, 43, 38, 47, "n")
        rect(d, 30, 47, 38, 47, "N")
        rect(d, 33, 44, 35, 45, "y")
    elif a == "backpack":
        rect(d, 14, 38, 17, 47, "Y")
        rect(d, 30, 38, 33, 47, "Y")
    elif a == "smock":
        for (x, y, k) in ((14, 43, "y"), (31, 41, "r"), (20, 45, "m"), (35, 45, "l"), (11, 46, "y")):
            rect(d, x, y, x + 1, y + 1, k)
    elif a == "scarf":
        rect(d, 16, 36, 31, 39, "y")
        rect(d, 16, 39, 31, 39, "Y")
        rect(d, 27, 40, 31, 46, "y")
        rect(d, 27, 46, 31, 46, "Y")
        rect(d, 29, 41, 29, 45, "Y")


# --------------------------------------------------------------------------
# character configs
# --------------------------------------------------------------------------
PLAYER = dict(
    style="spiky", accs=["overalls", "backpack"],
    hair=("N", "n"), skin=("s", "S"), shirt=("w", "G"), pants=("b", "B"),
    extra={"e": "b", "E": "B", "o": "n", "Y": "N"},
)
PLAYER_OUTFIT2 = dict(
    PLAYER,
    shirt=("y", "Y"), pants=("N", "K"),
    extra={"e": "N", "E": "K", "o": "r", "Y": "R"},
)

NPCS = [
    (1, "CafeOwner", dict(style="bob", accs=["apron"],
                          hair=("u", "y"), skin=("s", "S"), shirt=("m", "r"), pants=("b", "B"))),
    (2, "Shopkeeper", dict(style="short", accs=["mustache"],
                           hair=("G", "w"), skin=("S", "t"), shirt=("e", "E"), pants=("n", "N"))),
    (3, "Neighbor", dict(style="long", accs=[],
                         hair=("m", "w"), skin=("s", "S"), shirt=("c", "b"), pants=("A", "K"))),
    (4, "Student", dict(style="spiky", accs=["glasses", "backpack"],
                        hair=("K", "g"), skin=("s", "S"), shirt=("l", "e"), pants=("B", "K"))),
    (5, "Farmer", dict(style="short", accs=["strawhat", "overalls"],
                       hair=("R", "r"), skin=("t", "T"), shirt=("o", "r"), pants=("e", "E"))),
    (6, "Officeworker", dict(style="short", accs=["tie"],
                             hair=("K", "g"), skin=("S", "t"), shirt=("w", "G"), pants=("A", "K"))),
    (7, "Artist", dict(style="pony", accs=["beret", "smock"],
                       hair=("o", "y"), skin=("s", "S"), shirt=("c", "b"), pants=("p", "B"))),
    (8, "Mailcarrier", dict(style="short", accs=["cap", "bag"],
                            hair=("N", "n"), skin=("T", "N"), shirt=("b", "B"), pants=("B", "K"))),
]


def main():
    n = 0
    # ---- player ----
    for dirn in DIRS:
        save(render_sheet(PLAYER, "walk", dirn), f"characters/player/walk/CHAR_001_Player_{dirn}_Walk_v01.png"); n += 1
        save(render_sheet(PLAYER, "idle", dirn), f"characters/player/idle/CHAR_003_Player_{dirn}_Idle_v01.png"); n += 1
        save(render_sheet(PLAYER_OUTFIT2, "walk", dirn),
             f"characters/player/outfits/CHAR_005_Player_Outfit2_{dirn}_Walk_v01.png"); n += 1
    save(portrait(PLAYER, "Neutral"), "characters/player/portraits/CHAR_001_Player_Portrait_v01.png"); n += 1

    # ---- NPCs ----
    for idx, name, cfg in NPCS:
        folder = f"characters/npcs/npc_{idx:03d}"
        tag = f"NPC_{idx:03d}_{name}"
        for dirn in DIRS:
            save(render_sheet(cfg, "walk", dirn), f"{folder}/{tag}_{dirn}_Walk_v01.png"); n += 1
        save(render_sheet(cfg, "idle", "Down"), f"{folder}/{tag}_Down_Idle_v01.png"); n += 1
        for expr in ("Neutral", "Happy", "Sad"):
            save(portrait(cfg, expr), f"{folder}/{tag}_Portrait_{expr}_v01.png"); n += 1
    print(f"gen_characters: wrote {n} files")


if __name__ == "__main__":
    main()
