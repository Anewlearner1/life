"""Player character art v2 (24x32 chibi, redrawn from the concept sheet).

Layered build: body/outfit layer + hair layer -> composite -> 1px silhouette outline.
Left views are mirrored Right views. Feet sit on row 30 (outline row 31) in every frame.

Outputs (all under assets/characters/player/):
  walk/CHAR_001_Player_<Dir>_Walk_v01.png          4 frames
  idle/CHAR_003_Player_<Dir>_Idle_v01.png          2 frames
  outfits/CHAR_005_Player_Outfit2_<Dir>_{Walk,Idle}_v01.png
  portraits/CHAR_001_Player_Portrait_v01.png       48x48
  hair_variants/CHAR_004_Player_<Hair>_<Outfit>_<Dir>_{Walk,Idle}_v01.png
  hair/CHAR_004_Hair_Preview_v01.png
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import ASSETS, save, strip  # noqa: E402

W, H = 24, 32
DIRS = ["Down", "Up", "Left", "Right"]


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


# ---- colors (sampled from / matched to the concept sheet) ----
OL = hx("2a191a")
SKIN_L, SKIN_M, SKIN_S = hx("f8d8ae"), hx("ebbd95"), hx("d88d6d")
BLUSH = hx("f0a58a")
MOUTH = hx("b5563f")
EYE_D, EYE_B, EYE_H = hx("0c2947"), hx("2f78b8"), hx("e4f4fc")
WHITE, WHITE_S = hx("f5f7f6"), hx("bbc2c3")
BIB, BIB_H, BIB_S, BIB_D = hx("4f86c6"), hx("78a9dc"), hx("3675af"), hx("1d386d")
PANTS, PANTS_S, PANTS_H = hx("688090"), hx("4d6173"), hx("8498a8")
SHOE, SHOE_D, SHOE_H, CUFF = hx("845744"), hx("5f3a2c"), hx("dbdad7"), hx("aa6d55")
PACK, PACK_S, PACK_H = hx("aa6d55"), hx("7d4a38"), hx("c98a6a")
GOLD = hx("f3be4c")
RED = hx("c03326")

# outfits: shirt = sleeves/body, bib = overall front (None = plain top, no straps)
OUTFITS = {
    "Default": dict(shirt=WHITE, shirt_s=WHITE_S, bib=BIB, bib_h=BIB_H, bib_s=BIB_S, belt=BIB_D,
                    pants=PANTS, pants_s=PANTS_S, pants_h=PANTS_H, has_bib=True),
    "Outfit2": dict(shirt=hx("e2684a"), shirt_s=hx("b2402f"), bib=hx("ee8a62"), bib_h=hx("f7b088"),
                    bib_s=hx("c03326"), belt=hx("5f3a2c"),
                    pants=hx("3e4b60"), pants_s=hx("2a3445"), pants_h=hx("566680"), has_bib=False),
}

# hair: (dark, mid, light)
HAIRS = {
    "Spiky": (hx("3c231d"), hx("6a4033"), hx("b0705a")),
    "Short": (hx("1c1a22"), hx("33303d"), hx("55596b")),
    "Long": (hx("5f3a2c"), hx("8a5a3f"), hx("c08f62")),
    "Bob": (hx("c9985e"), hx("ecc47c"), hx("f9e6aa")),
    "Ponytail": (hx("b8586a"), hx("d98494"), hx("f0b0ba")),
    "Buzz": (hx("6b6c6c"), hx("999991"), hx("cfc9c4")),
}
HAIR_ORDER = ["Spiky", "Short", "Long", "Bob", "Ponytail", "Buzz"]


# ---------------- tiny painter ----------------
class Cv:
    def __init__(self, w=W, h=H):
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def hline(self, y, x0, x1, c):
        for x in range(x0, x1 + 1):
            self.px(x, y, c)


def parse(spec):
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def outline(img, color=OL):
    w, h = img.size
    src = img.load()
    out = img.copy()
    o = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
                        o[x, y] = color
                        break
    return out


def shift(img, dx, dy):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (dx, dy))
    return out


# ---------------- hair data ----------------
def _rows(**kw):
    return kw


def build_hair_spans(style, d):
    """Return ({row: [x..]}, extras[(x,y,color)]) for a style/direction (Down, Up, Right)."""
    R = {}
    extra = []

    def put(row, spec):
        R.setdefault(row, [])
        R[row] = sorted(set(R[row] + parse(spec)))

    def put_range(a, b, spec):
        for r in range(a, b + 1):
            put(r, spec)

    if d == "Down":
        if style == "Spiky":
            put(1, "9-10,13-15"); put(2, "7-16"); put(3, "5-18"); put(4, "4-20"); put(5, "4-19")
            put(6, "3-19"); put(7, "4-19"); put(8, "4-8,10-11,13-14,16-19"); put(9, "4-7,10,17-19")
            put(10, "4,19")
        elif style == "Short":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-10,13-19")
            put(9, "4-6,17-19"); put(10, "4,19")
        elif style == "Long":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-10,13-19")
            put(9, "3-7,16-20"); put_range(10, 17, "3-5,18-20"); put(18, "3-4,19-20")
        elif style == "Bob":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-19")
            put(9, "3-6,17-20"); put_range(10, 13, "3-5,18-20"); put(14, "4-6,17-19"); put(15, "5-6,17-18")
        elif style == "Ponytail":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-10,13-19")
            put(9, "4-6,17-19"); put(10, "4,19")
            put(5, "20-21"); put_range(6, 11, "20-22"); put_range(12, 13, "20-21"); put(14, "21")
            extra += [(20, 5, RED), (21, 5, RED)]
        elif style == "Buzz":
            put(2, "8-15"); put(3, "6-17"); put_range(4, 6, "5-18"); put(7, "5-6,17-18")
    elif d == "Up":
        base = lambda: (put(2, "7-16"), put(3, "5-18"), put_range(4, 12, "4-19"), put(13, "5-18"))
        if style == "Spiky":
            base(); put(1, "9-10,13-15"); put(4, "4-20"); put(6, "3-19"); put(14, "6-8,11-12,15-17")
        elif style == "Short":
            base(); put(14, "7-16")
        elif style == "Long":
            base(); put_range(14, 15, "4-19"); put_range(16, 17, "5-18"); put(18, "6-17"); put(19, "7-16")
        elif style == "Bob":
            base(); put(14, "4-19"); put(15, "5-18")
        elif style == "Ponytail":
            base(); put(14, "7-16")
            # tail on the character's left = viewer's left on the back view (mirror of Down)
            put(5, "2-3"); put_range(6, 11, "1-3"); put_range(12, 13, "2-3"); put(14, "2")
            extra += [(2, 5, RED), (3, 5, RED)]
        elif style == "Buzz":
            put(2, "8-15"); put(3, "6-17"); put_range(4, 9, "5-18"); put(10, "6-17")
    else:  # Right
        if style == "Spiky":
            put(1, "9-10,13-15"); put(2, "7-16"); put(3, "5-18"); put(4, "4-19"); put(5, "4-19")
            put(6, "3-19"); put(7, "4-19"); put(8, "4-9,12-13,15-18"); put(9, "3-9,17-18")
            put(10, "3-9"); put_range(11, 12, "4-8"); put(13, "5-7")
        elif style == "Short":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-9,13-18")
            put(9, "4-9,17-18"); put(10, "4-9"); put(11, "4-8")
        elif style == "Long":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-9,13-18")
            put(9, "3-9,17-18"); put_range(10, 16, "3-9"); put(17, "3-8"); put(18, "3-7"); put(19, "3-6")
        elif style == "Bob":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-18")
            put(9, "3-11,17-18"); put_range(10, 13, "3-11"); put(14, "4-9")
        elif style == "Ponytail":
            put(2, "7-16"); put(3, "5-18"); put_range(4, 7, "4-19"); put(8, "4-9,13-18")
            put(9, "4-9,17-18"); put(10, "4-9"); put(11, "4-8")
            put(6, "3-4"); put_range(7, 15, "1-3"); put(16, "1-2")
            extra += [(3, 6, RED), (4, 6, RED)]
        elif style == "Buzz":
            put(2, "8-15"); put(3, "6-17"); put_range(4, 5, "5-18"); put(6, "4-18"); put(7, "4-9"); put(8, "4-8")
    return R, extra


def hair_layer(style, d):
    spans, extra = build_hair_spans(style, d)
    dark, mid, light = HAIRS[style]
    mask = {(x, y) for y, xs in spans.items() for x in xs}
    cv = Cv()
    for (x, y) in mask:
        above = (x, y - 1) in mask
        below = (x, y + 1) in mask
        n = (x * 7 + y * 13 + x * y * 3) % 11
        if not above:
            c = light if n % 3 == 0 else mid
        elif not below:
            c = dark
        else:
            if n % 9 == 0 and y <= 7:
                c = light
            elif n % 7 == 0 and below and (x, y + 2) not in mask:
                c = dark
            else:
                c = mid
        cv.px(x, y, c)
    for x, y, c in extra:
        cv.px(x, y, c)
    return cv.im


# ---------------- body ----------------
HEAD_ROWS = {2: (8, 15), 3: (6, 17), 14: (6, 17), 15: (7, 16)}


def draw_head_base(cv, d, dy):
    for y in range(2, 16):
        x0, x1 = HEAD_ROWS.get(y, (5, 18))
        cv.hline(y + dy, x0, x1, SKIN_L)
    # soft shade on lower face / chin
    cv.hline(15 + dy, 7, 16, SKIN_M)
    if d == "Up":
        for y in (14, 15):
            cv.hline(y + dy, 8, 15, SKIN_S)
        cv.rect(4, 11 + dy, 4, 12 + dy, SKIN_M)
        cv.rect(19, 11 + dy, 19, 12 + dy, SKIN_M)
        return
    if d == "Down":
        cv.rect(4, 11 + dy, 4, 12 + dy, SKIN_M)
        cv.rect(19, 11 + dy, 19, 12 + dy, SKIN_M)
        cv.px(5, 11 + dy, SKIN_M); cv.px(18, 11 + dy, SKIN_M)
        for ex in (8, 14):
            cv.hline(10 + dy, ex, ex + 1, EYE_D)
            cv.px(ex, 11 + dy, EYE_D); cv.px(ex + 1, 11 + dy, EYE_H)
            cv.hline(12 + dy, ex, ex + 1, EYE_B)
        cv.hline(13 + dy, 6, 7, BLUSH); cv.hline(13 + dy, 16, 17, BLUSH)
        cv.hline(14 + dy, 11, 12, MOUTH)
    else:  # Right
        cv.rect(10, 10 + dy, 11, 12 + dy, SKIN_M)
        cv.px(11, 11 + dy, SKIN_S)
        cv.px(19, 11 + dy, SKIN_L); cv.px(19, 12 + dy, SKIN_M)  # nose
        cv.hline(10 + dy, 14, 15, EYE_D)
        cv.px(14, 11 + dy, EYE_D); cv.px(15, 11 + dy, EYE_H)
        cv.hline(12 + dy, 14, 15, EYE_B)
        cv.hline(13 + dy, 15, 16, BLUSH)
        cv.px(17, 14 + dy, MOUTH)


def draw_leg_front(cv, x0, lift, o, shoes_detail=True, side="L"):
    # pants rows 25..27 (shortened by lift), shoe rows 28..30 (shifted up by lift)
    for y in range(25, 28 - lift):
        cv.hline(y, x0, x0 + 2, o["pants"])
        inner = x0 + 2 if side == "L" else x0
        cv.px(inner, y, o["pants_s"])
    base = 28 - lift
    sx0, sx1 = (7, 10) if side == "L" else (13, 16)
    cv.hline(base, x0, x0 + 2, CUFF)
    cv.hline(base + 1, sx0, sx1, SHOE)
    if shoes_detail:
        a = sx0 + 1 if side == "L" else sx1 - 2
        cv.hline(base + 1, a, a + 1, SHOE_H)
    cv.hline(base + 2, sx0, sx1, SHOE_D)


def draw_torso_front(cv, o, dy, back, armL, armR, armsw):
    sh, shs = o["shirt"], o["shirt_s"]
    y = lambda v: v + dy
    # shoulders / torso
    cv.hline(y(16), 8, 15, sh)
    cv.rect(8, y(17), 15, y(21), sh)
    cv.px(8, y(18), shs); cv.rect(8, y(19), 8, y(21), shs); cv.rect(15, y(19), 15, y(21), shs)
    # sleeves
    for sx in (6, 7, 16, 17):
        cv.rect(sx, y(17), sx, y(18), sh)
    cv.px(7, y(18), shs); cv.px(16, y(18), shs)
    # arms
    for (ax0, ax1, inner, a) in ((6, 7, 7, armL), (16, 17, 16, armR)):
        for yy in range(19, 23 + a):
            for xx in (ax0, ax1):
                cv.px(xx, y(yy), SKIN_M if xx == inner else SKIN_L)
        hy = 22 + a
        cv.hline(y(hy), ax0, ax1, SKIN_S)
    # belt
    cv.hline(y(22), 8, 15, o["belt"])
    if not back:
        if o["has_bib"]:
            cv.rect(9, y(18), 14, y(21), o["bib"])
            cv.hline(y(17), 9, 10, o["bib"]); cv.hline(y(17), 13, 14, o["bib"])
            cv.hline(y(16), 9, 10, o["bib"]); cv.hline(y(16), 13, 14, o["bib"])
            cv.hline(y(21), 9, 14, o["bib_s"])
            cv.hline(y(18), 10, 13, o["bib_h"])
            cv.px(9, y(18), GOLD); cv.px(14, y(18), GOLD)
            cv.rect(10, y(19), 11, y(20), o["bib_h"]); cv.px(13, y(19), GOLD)
            cv.px(9, y(19), o["bib_s"]); cv.px(14, y(19), o["bib_s"])
            cv.px(11, y(22), GOLD); cv.px(12, y(22), GOLD)
        else:
            cv.rect(9, y(18), 14, y(21), o["bib"])
            cv.hline(y(18), 9, 14, o["bib_h"])
            cv.hline(y(21), 9, 14, o["bib_s"])
            cv.px(13, y(19), GOLD); cv.px(13, y(20), hx("fff0c8"))
        cv.hline(y(16), 10, 13, SKIN_S)       # neck
        cv.hline(y(17), 11, 12, SKIN_M)
        cv.px(10, y(17), WHITE); cv.px(13, y(17), WHITE)
    else:
        # backpack
        cv.rect(8, y(17), 15, y(22), PACK)
        cv.hline(y(17), 9, 14, PACK_H)
        cv.hline(y(19), 8, 15, PACK_S)
        cv.rect(8, y(20), 8, y(22), PACK_S); cv.rect(15, y(20), 15, y(22), PACK_S)
        cv.rect(10, y(20), 13, y(22), PACK_S)
        cv.rect(11, y(20), 12, y(21), PACK)
        cv.px(11, y(19), GOLD); cv.px(12, y(19), GOLD)
        cv.hline(y(16), 9, 14, SKIN_S)
        cv.hline(y(16), 8, 8, sh); cv.hline(y(16), 15, 15, sh)


def body_front(o, d, f, mode):
    """f = frame index; mode 'walk' or 'idle'."""
    cv = Cv()
    back = d == "Up"
    lift_l = lift_r = 0
    arm_l = arm_r = 0
    dy = 0
    if mode == "walk":
        if f == 1:
            lift_l, arm_l, arm_r, dy = 1, 1, -1, 1
        elif f == 3:
            lift_r, arm_l, arm_r, dy = 1, -1, 1, 1
    else:
        dy = 1 if f == 1 else 0
    # hips
    cv.rect(8, 23, 15, 24, o["pants"])
    cv.hline(23, 8, 15, o["pants_h"])
    cv.px(11, 24, o["pants_s"]); cv.px(12, 24, o["pants_s"])
    draw_leg_front(cv, 8, lift_l, o, not back, "L")
    draw_leg_front(cv, 13, lift_r, o, not back, "R")
    draw_torso_front(cv, o, dy, back, arm_l, arm_r, 0)
    draw_head_base(cv, d, dy)
    return cv.im, dy


def body_side(o, f, mode):
    """Right-facing view."""
    cv = Cv()
    dy = 0
    near_b = far_b = 10  # shoe x at the bottom
    near_arm = 0
    if mode == "walk":
        if f == 1:
            near_b, far_b, near_arm, dy = 12, 8, -1, 1
        elif f == 3:
            near_b, far_b, near_arm, dy = 8, 12, 1, 1
    else:
        dy = 1 if f == 1 else 0

    def leg(bx, pants, pants_s, shoe_col):
        for y in range(23, 28):
            x = 10 + round((bx - 10) * (y - 23) / 4)
            cv.hline(y, x, x + 2, pants)
            cv.px(x, y, pants_s)
        cv.hline(28, bx, bx + 2, CUFF)
        cv.hline(29, bx, bx + 4, shoe_col)
        cv.hline(30, bx, bx + 4, SHOE_D)
        if shoe_col == SHOE:
            cv.hline(29, bx + 3, bx + 4, SHOE_H)

    leg(far_b, o["pants_s"], o["pants_s"], hx("6e4938"))
    leg(near_b, o["pants"], o["pants_s"], SHOE)
    cv.rect(9, 23, 13, 23, o["pants"])
    y = lambda v: v + dy
    sh, shs = o["shirt"], o["shirt_s"]
    # backpack (behind)
    cv.rect(5, y(17), 8, y(22), PACK)
    cv.hline(y(17), 6, 8, PACK_H)
    cv.rect(5, y(18), 5, y(22), PACK_S)
    cv.hline(y(19), 5, 8, PACK_S)
    cv.rect(6, y(20), 7, y(21), PACK_S)
    cv.px(8, y(19), GOLD)
    # torso
    cv.rect(9, y(16), 14, y(21), sh)
    cv.rect(9, y(17), 9, y(21), shs)
    cv.hline(y(22), 9, 14, o["belt"])
    if o["has_bib"]:
        cv.rect(11, y(18), 14, y(21), o["bib"])
        cv.rect(11, y(16), 12, y(17), o["bib"])
        cv.hline(y(21), 11, 14, o["bib_s"])
        cv.px(11, y(18), GOLD); cv.px(14, y(19), o["bib_h"])
        cv.px(13, y(20), GOLD)
    else:
        cv.rect(10, y(18), 14, y(21), o["bib"])
        cv.hline(y(18), 10, 14, o["bib_h"])
        cv.hline(y(21), 10, 14, o["bib_s"])
        cv.px(13, y(19), GOLD)
    cv.hline(y(16), 11, 13, SKIN_S)
    # near arm
    cv.rect(10, y(17), 11, y(18), sh)
    cv.px(10, y(18), shs)
    for yy, s in ((19, 0), (20, near_arm), (21, near_arm), (22, near_arm)):
        cv.hline(y(yy), 10 + s, 11 + s, SKIN_L)
        cv.px(10 + s, y(yy), SKIN_M)
    cv.hline(y(22 + (1 if near_arm else 0)), 10 + near_arm, 11 + near_arm, SKIN_S)
    draw_head_base(cv, "Right", dy)
    return cv.im, dy


def compose_frame(d, f, mode, outfit, hair):
    o = OUTFITS[outfit]
    if d in ("Down", "Up"):
        body, dy = body_front(o, d, f, mode)
        hl = hair_layer(hair, d)
    else:
        body, dy = body_side(o, f, mode)
        hl = hair_layer(hair, "Right")
    img = Image.alpha_composite(body, shift(hl, 0, dy))
    img = outline(img)
    if d == "Left":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def sheet(d, mode, outfit, hair):
    n = 4 if mode == "walk" else 2
    return strip([compose_frame(d, f, mode, outfit, hair) for f in range(n)])


# ---------------- portrait ----------------
def portrait():
    S = 48
    cv = Cv(S, S)
    ch = Cv(S, S)
    # shoulders / shirt
    for y in range(40, 48):
        half = min(14 + (y - 40) * 3, 22)
        cv.hline(y, 24 - half, 23 + half, WHITE)
        cv.px(24 - half, y, WHITE_S); cv.px(23 + half, y, WHITE_S)
    for y in range(42, 48):  # overall straps
        cv.hline(y, 12, 17, BIB); cv.hline(y, 30, 35, BIB)
        cv.px(12, y, BIB_S); cv.px(35, y, BIB_S)
    cv.px(14, 45, GOLD); cv.px(33, 45, GOLD)
    cv.hline(47, 3, 44, WHITE_S)
    # neck
    cv.rect(19, 38, 28, 42, SKIN_M)
    cv.hline(42, 21, 26, SKIN_S)
    def ell(x, y, cx, cy, rx, ry):
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0
    for y in range(S):
        for x in range(S):
            if ell(x + .5, y + .5, 24, 27, 15.5, 14.2):
                cv.px(x, y, SKIN_L)
            if ell(x + .5, y + .5, 8.2, 29, 2.6, 3.4) or ell(x + .5, y + .5, 39.8, 29, 2.6, 3.4):
                cv.px(x, y, SKIN_M)
    for y in range(39, 42):
        for x in range(S):
            if cv.im.getpixel((x, y)) == SKIN_L:
                cv.px(x, y, SKIN_M)
    # hair
    dark, mid, light = HAIRS["Spiky"]
    mask = set()
    teeth = [26, 24, 27, 25, 28, 25, 27, 24]
    for y in range(5, 36):
        for x in range(S):
            if not ell(x + .5, y + .5, 24, 23.5, 17.0, 18.0):
                continue
            if x < 11 or x > 36:
                lim = 33 if x in (7, 8, 9, 38, 39, 40) else 31
            else:
                lim = teeth[((x - 11) // 3) % 8]
            if y <= lim:
                mask.add((x, y))
    for sx, h in ((13, 3), (17, 4), (22, 3), (26, 4), (31, 3), (35, 3), (10, 2)):
        ty = min((yy for (xx, yy) in mask if xx == sx), default=8)
        for k in range(h):
            for xx in range(sx - (h - k - 1) // 2, sx + (h - k - 1) // 2 + 1):
                mask.add((xx, ty - 1 - k))
    for (x, y) in mask:
        above = (x, y - 1) in mask
        below = (x, y + 1) in mask
        n = (x * 7 + y * 13 + x * y * 3) % 11
        if not above:
            c = light if n % 3 == 0 else mid
        elif not below:
            c = dark
        elif n % 7 == 0 and y <= 18:
            c = light
        elif n % 9 == 0:
            c = dark
        else:
            c = mid
        cv.px(x, y, c)
    # eyes (big, dark with blue + highlight), brows, nose, mouth, blush
    for ex in (14, 30):
        cv.rect(ex, 25, ex + 3, 30, EYE_D)
        cv.rect(ex + 1, 29, ex + 2, 30, EYE_B)
        cv.rect(ex, 26, ex + 1, 27, EYE_H)
        cv.px(ex + 2, 28, EYE_B)
    for bx in (13, 31):
        cv.hline(23, bx, bx + 4, dark)
    cv.px(24, 33, SKIN_S); cv.px(23, 33, SKIN_M)
    cv.hline(37, 21, 26, MOUTH); cv.hline(38, 22, 25, SKIN_S)
    cv.hline(34, 11, 13, BLUSH); cv.hline(34, 34, 36, BLUSH)
    # silhouette outline, then rounded frame + background
    out = outline(cv.im)
    final = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bg = hx("dfe9ef")
    fo = hx("3e4b60")
    for y in range(S):
        for x in range(S):
            corner = (min(x, S - 1 - x) + min(y, S - 1 - y)) < 3 and min(x, S - 1 - x) < 3 and min(y, S - 1 - y) < 3
            if corner:
                continue
            edge = x in (0, S - 1) or y in (0, S - 1)
            if edge:
                final.putpixel((x, y), fo)
            else:
                p = out.getpixel((x, y))
                final.putpixel((x, y), p if p[3] else bg)
    # soften frame corners: one px notch
    for (x, y) in ((1, 1), (S - 2, 1), (1, S - 2), (S - 2, S - 2)):
        final.putpixel((x, y), fo)
    return final


# ---------------- hair preview ----------------
def hair_preview():
    cell = 28
    w, h = cell * len(HAIR_ORDER) + 4, 40
    cream, border = hx("faf3e2"), hx("d5aa89")
    img = Image.new("RGBA", (w, h), cream)
    for x in range(w):
        img.putpixel((x, 0), border); img.putpixel((x, h - 1), border)
    for y in range(h):
        img.putpixel((0, y), border); img.putpixel((w - 1, y), border)
    for i, hn in enumerate(HAIR_ORDER):
        f = compose_frame("Down", 0, "idle", "Default", hn)
        img.alpha_composite(f, (2 + i * cell + 2, 4))
    return img


def main():
    base = "characters/player"
    # remove the old 16x24 overlay files
    hair_dir = ASSETS / base / "hair"
    for p in list(hair_dir.glob("CHAR_004_Hair_*_Down_v01.png")) + list(hair_dir.glob("CHAR_004_BaseHead_Down_v01.png")):
        p.unlink()
    n = 0
    for d in DIRS:
        save(sheet(d, "walk", "Default", "Spiky"), f"{base}/walk/CHAR_001_Player_{d}_Walk_v01.png")
        save(sheet(d, "idle", "Default", "Spiky"), f"{base}/idle/CHAR_003_Player_{d}_Idle_v01.png")
        save(sheet(d, "walk", "Outfit2", "Spiky"), f"{base}/outfits/CHAR_005_Player_Outfit2_{d}_Walk_v01.png")
        save(sheet(d, "idle", "Outfit2", "Spiky"), f"{base}/outfits/CHAR_005_Player_Outfit2_{d}_Idle_v01.png")
        n += 4
        for hn in HAIR_ORDER:
            for on in OUTFITS:
                for mode, tag in (("walk", "Walk"), ("idle", "Idle")):
                    save(sheet(d, mode, on, hn),
                         f"{base}/hair_variants/CHAR_004_Player_{hn}_{on}_{d}_{tag}_v01.png")
                    n += 1
    save(portrait(), f"{base}/portraits/CHAR_001_Player_Portrait_v01.png")
    save(hair_preview(), f"{base}/hair/CHAR_004_Hair_Preview_v01.png")
    print(f"player: wrote {n + 2} files")


if __name__ == "__main__":
    main()
