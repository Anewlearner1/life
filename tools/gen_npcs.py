"""Art v2: the 8 NPC sprite sets (24x32 chibi frames, 48x48 portraits), redrawn to match
assets/reference/ArtDirection_ConceptSheet_v01.png.

Everything is drawn procedurally (seeded) on character grids, then an automatic 1px dark outline is added.
Output (overwrites, same names): assets/characters/npcs/npc_00N/
  NPC_00N_<Name>_{Down,Up,Left,Right}_Walk_v01.png   4 frames of 24x32  (96x32)
  NPC_00N_<Name>_Down_Idle_v01.png                    2 frames          (48x32)
  NPC_00N_<Name>_Portrait_{Neutral,Happy,Sad}_v01.png 48x48
Run: python3 tools/gen_npcs.py
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image
from pixel import CP, from_rows, strip, save

FW, FH = 24, 32
PORT = 48

# ---- palette: concept palette + a few exact extras sampled/blended from the concept sheet ----
PAL = dict(CP)


def _x(key, hexs):
    PAL[key] = (int(hexs[1:3], 16), int(hexs[3:5], 16), int(hexs[5:7], 16), 255)


_x("!", "#c98f2e")   # blonde shade
_x("@", "#e07a8a")   # pink hair
_x("#", "#b0506a")   # pink hair shade
_x("$", "#f4a8b0")   # pink hair light
_x("%", "#dc6a2c")   # red-orange hair
_x("&", "#a8421f")   # red-orange shade
_x("*", "#f49a4a")   # red-orange light
_x("~", "#862119")   # beret shade
_x("^", "#e6b27c")   # limb skin
_x("?", "#f09a82")   # blush
_x(",", "#d39a38")   # yellow shirt shade
_x(".", "#e0b078")   # tan face
_x(";", "#c46a52")   # lip / mouth
_x(":", "#8a5a3c")   # eyebrow brown
_x("-", "#bfa070")   # straw shade
_x("`", "#f6efe0")   # eye white highlight

OUT = "0"

# ---------------------------------------------------------------------------------------------
# NPC definitions
# hair: (base, shade, light)   skin: (face, face_shade, limb, limb_shade)
# ---------------------------------------------------------------------------------------------
NPCS = [
    dict(id=1, name="CafeOwner", hair=("E", "D", "F"), style="curly", fringe="part", skin=("L", "H", "^", "H"),
         top=("C", "B", "e"), top2=("P", "8", "7"), pants=("i", "e"), shoes=("F", "D"), lower="shorts",
         outfit="apron", hat="chef", hatc=("P", "8", "7")),
    dict(id=2, name="Shopkeeper", hair=("1", "W", "3"), style="short", fringe="side", skin=("L", "H", "^", "H"),
         top=("M", "L", "G"), top2=("U", "T", "R"), pants=("3", "2"), shoes=("E", "D"), lower="pants",
         outfit="vest", hat=None),
    dict(id=3, name="Neighbor", hair=("6", "4", "8"), style="short", fringe="part", skin=("L", "H", "^", "H"),
         top=("k", "i", "m"), top2=("M", "L", "G"), pants=("2", "1"), shoes=("D", "A"), lower="pants",
         outfit="cardigan", hat=None),
    dict(id=4, name="Student", hair=("I", "!", "K"), style="long", fringe="part", skin=("L", "H", "^", "H"),
         top=("K", ",", "M"), top2=("K", ",", "M"), pants=("G", "F"), shoes=("E", "D"), lower="shorts",
         outfit="hoodie", hat=None),
    dict(id=5, name="Farmer", hair=("D", "A", "E"), style="short", fringe="straight", skin=(".", "H", "H", "F"),
         top=("r", "l", "t"), top2=("J", "G", "L"), pants=("J", "G"), shoes=("E", "A"), lower="pants",
         outfit="overalls", hat="straw", hatc=("K", "-", "M")),
    dict(id=6, name="Officeworker", hair=("@", "#", "$"), style="bob", fringe="straight", skin=("L", "H", "^", "H"),
         top=("X", "+", "=" ), top2=("h", "c", "l"), pants=("h", "c"), shoes=("3", "2"), lower="skirt",
         outfit="blouse", hat=None),
    dict(id=7, name="Artist", hair=("%", "&", "*"), style="wavy", fringe="swept", skin=("L", "H", "^", "H"),
         top=("N", "M", "L"), top2=("o", "l", "r"), pants=("o", "l"), shoes=("D", "A"), lower="skirt",
         outfit="smock", hat="beret", hatc=("B", "~", "C")),
    dict(id=8, name="Mailcarrier", hair=("E", "D", "F"), style="short", fringe="side", skin=("L", "H", "^", "H"),
         top=("o", "l", "r"), top2=("l", "h", "o"), pants=("h", "c"), shoes=("D", "A"), lower="pants",
         outfit="mail", hat="cap", hatc=("h", "c", "l")),
]


# ---------------------------------------------------------------------------------------------
class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [["_"] * w for _ in range(h)]

    def set(self, x, y, k):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = k

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.p[y][x]
        return "_"

    def rect(self, x0, y0, x1, y1, k):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, k)

    def hline(self, y, x0, x1, k):
        for x in range(x0, x1 + 1):
            self.set(x, y, k)

    def vline(self, x, y0, y1, k):
        for y in range(y0, y1 + 1):
            self.set(x, y, k)

    def ell(self, cx, cy, rx, ry, k, ymin=-99, ymax=999):
        for y in range(self.h):
            for x in range(self.w):
                if ymin <= y <= ymax and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.p[y][x] = k

    def stamp(self, x0, y0, rows, mapping=None):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == ".":
                    continue
                self.set(x0 + i, y0 + j, mapping.get(ch, ch) if mapping else ch)

    def outline(self, k=OUT):
        src = [r[:] for r in self.p]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x] != "_":
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[ny][nx] != "_":
                        self.p[y][x] = k
                        break

    def mirror(self):
        g = Grid(self.w, self.h)
        g.p = [r[::-1] for r in self.p]
        return g

    def image(self):
        return from_rows(["".join(r) for r in self.p], PAL)


# ---------------------------------------------------------------------------------------------
# Sprite (24x32)
# ---------------------------------------------------------------------------------------------
import gen_player as gp  # noqa: E402  (read-only reuse of the approved player construction)

hx = gp.hx
SKIN_STD = (hx("f8d8ae"), hx("ebbd95"), hx("d88d6d"))
SKIN_TAN = (hx("eec28f"), hx("dba070"), hx("b97a58"))
BLUSH = hx("f0a58a")
MOUTH = hx("b5563f")
EYE_D, EYE_H = hx("1c1418"), hx("e4f4fc")
WHITE, WHITE_S = hx("f5f7f6"), hx("bbc2c3")
GOLD = hx("f3be4c")
SHOE_BR = (hx("845744"), hx("5f3a2c"), hx("dbdad7"))
SHOE_DK = (hx("4d4a58"), hx("2a2833"), hx("8a8896"))

# ---- per-NPC sprite specs (hex colors; hair = dark, mid, light) ----
SPR = {
    1: dict(hair=(hx("4a2c20"), hx("7d533d"), hx("b07850")), hs="Spiky", curl=True, skin=SKIN_STD, iris=hx("5f3a2c"),
            shirt=(hx("e2684a"), hx("b2402f"), hx("f08a68")), sleeve="short", detail="apron",
            lower="shorts", pants=(hx("4a5568"), hx("2f3846"), hx("66748a")), shoes=SHOE_BR),
    2: dict(hair=(hx("1c1a22"), hx("33303d"), hx("55596b")), hs="Short", skin=SKIN_STD, iris=hx("3a3040"),
            shirt=(hx("f1e2b8"), hx("cdb88a"), hx("fbf3da")), sleeve="short", detail="vest",
            lower="pants", pants=(hx("6b6c6c"), hx("4d4e50"), hx("8e8f90")), shoes=SHOE_BR),
    3: dict(hair=(hx("6b6c6c"), hx("a3a29c"), hx("d9d5cf")), hs="Short", tidy=True, skin=SKIN_STD, iris=hx("4a5a6a"),
            shirt=(hx("355973"), hx("22425a"), hx("557690")), sleeve="long", detail="cardigan",
            lower="pants", pants=(hx("535354"), hx("36393e"), hx("6b6c6c")), shoes=SHOE_DK),
    4: dict(hair=(hx("c9985e"), hx("ecc47c"), hx("f9e6aa")), hs="Long", skin=SKIN_STD, iris=hx("3675af"),
            shirt=(hx("f2ce77"), hx("d39a38"), hx("fbe6a6")), sleeve="short", detail="hoodie",
            lower="shorts", pants=(hx("b18560"), hx("7d533d"), hx("d5aa89")), shoes=SHOE_BR),
    5: dict(hair=(hx("3c231d"), hx("6a4033"), hx("a0684f")), hs="Short", skin=SKIN_TAN, iris=hx("3c231d"),
            shirt=(hx("5187c5"), hx("3675af"), hx("78a9dc")), sleeve="short", detail="overalls",
            lower="pants", pants=(hx("d5aa89"), hx("a8825f"), hx("eccc9d")), shoes=SHOE_BR),
    6: dict(hair=(hx("b8586a"), hx("e08a9a"), hx("f6b8c0")), hs="Bob", skin=SKIN_STD, iris=hx("6a4050"),
            shirt=(hx("f2f6f7"), hx("bbc2c3"), hx("ffffff")), sleeve="short", detail="blouse",
            lower="skirt", pants=(hx("2c4b82"), hx("1d3052"), hx("456aa8")), shoes=SHOE_DK),
    7: dict(hair=(hx("a8421f"), hx("dc6a2c"), hx("f9a455")), hs="Long", wavy=True, skin=SKIN_STD, iris=hx("2f8a8a"),
            shirt=(hx("faf3e2"), hx("d9c7a4"), hx("ffffff")), sleeve="short", detail="smock",
            lower="skirt", pants=(hx("3675af"), hx("275d96"), hx("6aa0d8")), shoes=SHOE_BR),
    8: dict(hair=(hx("5f3a2c"), hx("8a5a3f"), hx("c08f62")), hs="Short", skin=SKIN_STD, iris=hx("3c231d"),
            shirt=(hx("3675af"), hx("275d96"), hx("5f9bd6")), sleeve="short", detail="mail",
            lower="pants", pants=(hx("2c3f7a"), hx("1d2a52"), hx("4259a0")), shoes=SHOE_BR),
}
HATC = {  # hat colors (dark, mid, light) as hex
    "chef": (hx("f5f7f6"), hx("bbc2c3"), hx("dbdad7")),
    "straw": (hx("f2ce77"), hx("c49a50"), hx("f9e6aa")),
    "beret": (hx("c03326"), hx("862119"), hx("e2684a")),
    "cap": (hx("1d386d"), hx("0c2947"), hx("3675af")),
}


def _rgba(c):
    return PAL[c] if isinstance(c, str) else c


# ---------------------------------------------------------------------------------------------
# hair (player span data, per-NPC edge perturbation, 3-tone shading like the player)
# ---------------------------------------------------------------------------------------------
def hair_mask(sp, d, n_id):
    """d in Down/Up/Right. Returns (set of (x,y), extras)."""
    spans, extra = gp.build_hair_spans(sp["hs"], d)
    mask = {(x, y) for y, xs in spans.items() for x in xs}
    rnd = random.Random(1000 + n_id * 17 + {"Down": 0, "Up": 1, "Right": 2}[d])
    # ragged silhouette: nibble / grow outer pixels on rows >= 4 (never the face area)
    outer = []
    for (x, y) in sorted(mask):
        if y >= 4 and ((x - 1, y) not in mask or (x + 1, y) not in mask):
            outer.append((x, y))
    for (x, y) in outer:
        r = rnd.random()
        sx = -1 if (x - 1, y) not in mask else 1
        if r < 0.22 and y >= 6:
            mask.discard((x, y))
        elif r < 0.50:
            mask.add((x + sx, y + (1 if rnd.random() < 0.35 else 0)))
    # tufts on the crown
    for _ in range(3 if d != "Up" else 2):
        tx = rnd.choice([6, 8, 11, 13, 15, 17])
        ty = min((yy for (xx, yy) in mask if xx == tx), default=3)
        mask.add((tx, ty - 1))
    if sp.get("curl"):
        for (x, y) in ((3, 8), (3, 10), (20, 8), (20, 10), (2, 9), (21, 9), (4, 12), (19, 12)):
            if d == "Down":
                mask.add((x, y))
        if d == "Right":
            for (x, y) in ((3, 9), (3, 11), (4, 13), (5, 14)):
                mask.add((x, y))
    if sp.get("wavy") and d in ("Down", "Up"):
        for y in range(10, 20):
            sh = 1 if (y // 3) % 2 else 0
            for x in (3, 4, 19, 20):
                if (x, y) in mask or (x, y - 1) in mask:
                    pass
            if (4, y) in mask and sh:
                mask.add((3, y)); mask.discard((5, y)) if False else None
            if (19, y) in mask and not sh:
                mask.add((20, y))
    if sp.get("wavy") and d == "Down":
        # swept side bangs over the forehead
        for (x, y) in ((8, 8), (9, 8), (10, 8), (11, 8), (12, 8), (8, 9), (9, 9), (10, 9), (7, 10), (8, 10), (15, 8), (16, 9)):
            mask.add((x, y))
        for (x, y) in ((13, 8), (14, 8)):
            mask.discard((x, y))
        for (x, y) in ((5, 21), (6, 21), (17, 21), (18, 21), (4, 20), (19, 20)):
            mask.add((x, y))
    if sp.get("tidy") and d == "Down":
        for (x, y) in ((9, 8), (10, 8), (11, 9), (12, 9)):
            mask.add((x, y))
    return mask, extra


def hair_layer(sp, d, n_id):
    mask, extra = hair_mask(sp, d, n_id)
    dark, mid, light = sp["hair"]
    cv = gp.Cv()
    for (x, y) in mask:
        above = (x, y - 1) in mask
        below = (x, y + 1) in mask
        n = (x * 7 + y * 13 + x * y * 3 + n_id * 5) % 11
        if not above:
            c = light if n % 3 == 0 else mid
        elif not below:
            c = dark
        else:
            if n % 8 == 0 and y <= 8:
                c = light
            elif n % 5 == 0 and below and (x, y + 2) not in mask:
                c = dark
            elif n % 6 == 0:
                c = dark
            else:
                c = mid
        cv.px(x, y, c)
    # highlight streaks (2-3 px diagonal) on the crown
    for (x, y) in ((8, 3), (9, 4), (7, 5), (13, 3), (14, 4)):
        if (x, y) in mask and (x, y + 1) in mask:
            cv.px(x, y, light)
    return cv.im


# ---------------------------------------------------------------------------------------------
# head
# ---------------------------------------------------------------------------------------------
def draw_head(cv, sp, d, dy, n_id):
    sl, sm, ss = sp["skin"]
    for y in range(2, 16):
        x0, x1 = gp.HEAD_ROWS.get(y, (5, 18))
        cv.hline(y + dy, x0, x1, sl)
    cv.hline(15 + dy, 7, 16, sm)
    if d == "Up":
        for y in (14, 15):
            cv.hline(y + dy, 8, 15, ss)
        cv.rect(4, 11 + dy, 4, 12 + dy, sm)
        cv.rect(19, 11 + dy, 19, 12 + dy, sm)
    elif d == "Down":
        cv.rect(4, 11 + dy, 4, 12 + dy, sm)
        cv.rect(19, 11 + dy, 19, 12 + dy, sm)
        cv.px(5, 11 + dy, sm); cv.px(18, 11 + dy, sm)
        for ex in (8, 14):
            cv.hline(10 + dy, ex, ex + 1, EYE_D)
            cv.px(ex, 11 + dy, EYE_D); cv.px(ex + 1, 11 + dy, EYE_H)
            cv.hline(12 + dy, ex, ex + 1, sp["iris"])
        cv.hline(13 + dy, 6, 7, BLUSH); cv.hline(13 + dy, 16, 17, BLUSH)
        cv.hline(14 + dy, 11, 12, MOUTH)
        if n_id == 7:  # artist: lashes + rosy lips
            cv.px(7, 10 + dy, EYE_D); cv.px(16, 10 + dy, EYE_D)
            cv.px(7, 9 + dy, EYE_D); cv.px(16, 9 + dy, EYE_D)
            cv.hline(14 + dy, 11, 12, hx("d8505a"))
            cv.hline(13 + dy, 5, 7, BLUSH); cv.hline(13 + dy, 16, 18, BLUSH)
        if False:  # (glasses only on the Neighbor portrait)
            gl = hx("6b6c6c")
            for ex in (7, 13):
                cv.hline(9 + dy, ex, ex + 3, gl); cv.hline(13 + dy, ex, ex + 3, gl)
                cv.px(ex, 10 + dy, gl); cv.px(ex, 11 + dy, gl); cv.px(ex, 12 + dy, gl)
                cv.px(ex + 3, 10 + dy, gl); cv.px(ex + 3, 11 + dy, gl); cv.px(ex + 3, 12 + dy, gl)
            cv.hline(10 + dy, 11, 12, gl)
    else:  # Right
        cv.rect(10, 10 + dy, 11, 12 + dy, sm)
        cv.px(11, 11 + dy, ss)
        cv.px(19, 11 + dy, sl); cv.px(19, 12 + dy, sm)
        cv.hline(10 + dy, 14, 15, EYE_D)
        cv.px(14, 11 + dy, EYE_D); cv.px(15, 11 + dy, EYE_H)
        cv.hline(12 + dy, 14, 15, sp["iris"])
        cv.hline(13 + dy, 15, 16, BLUSH)
        cv.px(17, 14 + dy, MOUTH)
        if n_id == 7:
            cv.px(16, 10 + dy, EYE_D); cv.px(16, 9 + dy, EYE_D)
            cv.px(17, 14 + dy, hx("d8505a"))
        if False:
            gl = hx("6b6c6c")
            cv.hline(9 + dy, 13, 16, gl); cv.hline(13 + dy, 13, 16, gl)
            for yy in (10, 11, 12):
                cv.px(13, yy + dy, gl); cv.px(16, yy + dy, gl)


# ---------------------------------------------------------------------------------------------
# hats (key-based grid layer, composited over hair)
# ---------------------------------------------------------------------------------------------
def hat_layer(n, view, dy):
    hat = n["hat"]
    if not hat:
        return None
    hb, hs, hl = HATC[hat]
    g = Grid(FW, FH)
    d = 0
    if hat == "chef":
        g.ell(11.5, 4.5, 9.2, 4.2, hb, ymax=6)
        g.hline(1, 6, 17, hb)
        g.hline(5, 4, 19, hb); g.hline(6, 4, 19, hs)
        for (x, y) in ((8, 3), (9, 2), (14, 2), (15, 3), (12, 4), (6, 4), (17, 4)):
            g.set(x, y, hl)
        for (x, y) in ((5, 5), (18, 5), (11, 3), (12, 2), (7, 2), (16, 4)):
            g.set(x, y, hs)
        g.hline(2, 10, 13, hb)
    elif hat == "cap":
        g.ell(11.5, 5.5, 8.6, 4.8, hb, ymax=5)
        g.hline(6, 4, 19, hs)
        if view == "down":
            g.hline(7, 5, 18, hs)
            g.rect(11, 3, 12, 4, "I")
            g.hline(2, 8, 10, hl)
        elif view == "up":
            g.hline(5, 6, 17, hb)
            g.hline(2, 8, 10, hl); g.set(11, 2, hs); g.set(12, 2, hs)
        else:
            g.hline(6, 2, 12, hs); g.hline(7, 3, 9, hs)
            g.set(8, 3, "I"); g.hline(2, 6, 9, hl)
    elif hat == "straw":
        g.ell(11.5, 4, 6.8, 4.0, hb, ymax=5)
        g.hline(5, 5, 18, "B")
        g.ell(11.5, 6.2, 11.5, 1.9, hb)
        g.hline(7, 2, 21, hs); g.hline(6, 2, 21, hb)
        for (x, y) in ((9, 2), (13, 3), (8, 4), (14, 4), (11, 2), (16, 3)):
            g.set(x, y, hl)
        g.hline(6, 6, 7, hl)
        for x in range(4, 20, 3):
            g.set(x, 7, hb)
    elif hat == "beret":
        if view == "side":
            g.ell(11, 4, 9.0, 3.6, hb, ymax=6)
            g.hline(1, 9, 12, hb); g.hline(6, 3, 15, hs)
            g.set(10, 1, hs); g.hline(2, 6, 9, hl)
        else:
            g.ell(12.5, 4, 9.6, 3.7, hb, ymax=6)
            g.hline(1, 10, 14, hb)
            g.hline(6, 4, 19, hs); g.hline(7, 15, 19, hs)
            g.set(20, 6, hb)
            g.hline(2, 8, 11, hl); g.set(7, 3, hl)
            g.hline(5, 5, 8, hs)
    # rgba
    out = gp.Cv()
    for y in range(FH):
        for x in range(FW):
            k = g.p[y][x]
            if k != "_":
                out.px(x, y + dy, _rgba(k))
    img = out.im
    if view == "side":  # drawn facing left; player side views are right-facing
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


# ---------------------------------------------------------------------------------------------
# body
# ---------------------------------------------------------------------------------------------
def draw_leg_front(cv, sp, x0, lift, side):
    o = sp
    pb, ps, ph = o["pants"]
    sk = o["skin"]
    shoe, shoe_d, shoe_h = o["shoes"]
    lower = o["lower"]
    pe = 27 if lower == "pants" else 26
    for y in range(25, pe + 1 - lift):
        if lower == "skirt":
            break
        cv.hline(y, x0, x0 + 2, pb)
        inner = x0 + 2 if side == "L" else x0
        cv.px(inner, y, ps)
    base = 28 - lift
    if lower == "pants":
        cv.hline(base, x0, x0 + 2, ph)
    else:
        for y in range(pe + 1 - lift if lower == "shorts" else 27 - lift, base + 1):
            cv.hline(y, x0, x0 + 2, sk[0])
            inner = x0 + 2 if side == "L" else x0
            cv.px(inner, y, sk[1])
    sx0, sx1 = (7, 10) if side == "L" else (13, 16)
    cv.hline(base + 1, sx0, sx1, shoe)
    a = sx0 + 1 if side == "L" else sx1 - 2
    cv.hline(base + 1, a, a + 1, shoe_h)
    cv.hline(base + 2, sx0, sx1, shoe_d)


def fold_marks(cv, y0, cols, shade, light):
    """small cloth folds/shadows on a torso block (rows from y0)."""
    for (x, y) in cols:
        cv.px(x, y0 + y, shade)


def draw_torso_front(cv, sp, dy, back, arm_l, arm_r):
    sh, shs, shh = sp["shirt"]
    sk = sp["skin"]
    sl, sm, ss = sk
    y = lambda v: v + dy
    det = sp["detail"]
    long_sl = sp["sleeve"] == "long"
    pb, ps, ph = sp["pants"]
    # shoulders / torso
    cv.hline(y(16), 8, 15, sh)
    cv.rect(8, y(17), 15, y(21), sh)
    cv.hline(y(17), 9, 14, shh)
    cv.px(8, y(18), shs); cv.rect(8, y(19), 8, y(21), shs); cv.rect(15, y(19), 15, y(21), shs)
    # sleeves
    n_sl = 5 if long_sl else 2
    for sx in (6, 7, 16, 17):
        cv.rect(sx, y(17), sx, y(16 + n_sl), sh)
    cv.px(7, y(18), shs); cv.px(16, y(18), shs)
    cv.px(6, y(17), shh); cv.px(17, y(17), shh)
    if long_sl:
        for yy in (19, 20, 21):
            cv.px(7, y(yy), shs); cv.px(16, y(yy), shs)
        cv.hline(y(22), 6, 7, ps if False else shs); cv.hline(y(22), 16, 17, shs)
    # arms
    for (ax0, ax1, inner, a) in ((6, 7, 7, arm_l), (16, 17, 16, arm_r)):
        start = 22 if long_sl else 19
        for yy in range(start, 23 + a):
            for xx in (ax0, ax1):
                cv.px(xx, y(yy), sm if xx == inner else sl)
        cv.hline(y(22 + a), ax0, ax1, ss)
    # belt / hem row
    belt = ps if sp["lower"] != "skirt" else ps
    cv.hline(y(22), 8, 15, belt)
    # cloth folds
    cv.px(10, y(20), shs); cv.px(9, y(21), shs); cv.px(13, y(19), shs) if det not in ("hoodie",) else None
    if not back:
        cv.hline(y(16), 10, 13, ss)
        cv.hline(y(17), 11, 12, sm)
        cv.px(10, y(17), shh); cv.px(13, y(17), shh)
        if det == "apron":
            cv.rect(9, y(18), 14, y(22), WHITE)
            cv.hline(y(18), 9, 14, hx("dbdad7"))
            for yy in range(19, 22):
                cv.px(14, y(yy), WHITE_S)
            cv.hline(y(22), 9, 14, WHITE_S)
            cv.rect(11, y(20), 12, y(20), WHITE_S)  # pocket line
            cv.px(9, y(17), WHITE); cv.px(14, y(17), WHITE)  # bib straps
            cv.px(10, y(17), shs if False else sh)
            cv.px(11, y(21), hx("dbdad7")); cv.px(12, y(21), hx("dbdad7"))
        elif det == "vest":
            vb, vs, vh = hx("528447"), hx("2f5c32"), hx("7ba14c")
            cv.rect(8, y(17), 10, y(22), vb); cv.rect(13, y(17), 15, y(22), vb)
            for yy in range(17, 23):
                cv.px(8, y(yy), vs); cv.px(15, y(yy), vs)
            cv.px(10, y(18), vh); cv.px(13, y(18), vh); cv.px(9, y(17), vh); cv.px(14, y(17), vh)
            cv.px(9, y(20), GOLD); cv.px(14, y(20), GOLD)
            cv.px(10, y(21), vs); cv.px(13, y(21), vs)
            cv.hline(y(22), 8, 15, vs)
        elif det == "cardigan":
            lb, ls_, lh = hx("faf3e2"), hx("d9c7a4"), hx("ffffff")
            cv.rect(11, y(17), 12, y(22), lb)
            cv.px(10, y(17), lh); cv.px(13, y(17), lh)
            cv.px(10, y(18), lh); cv.px(13, y(18), lh)
            cv.px(11, y(21), ls_); cv.px(12, y(21), ls_)
            for yy in range(17, 23):
                cv.px(10, y(yy), shs) if yy > 18 else None
                cv.px(13, y(yy), shs) if yy > 18 else None
            cv.px(9, y(20), shh); cv.px(14, y(20), shh)  # pockets
            cv.hline(y(20), 9, 9, shs); cv.hline(y(20), 14, 14, shs)
            cv.px(11, y(19), GOLD)
        elif det == "hoodie":
            cv.hline(y(16), 9, 14, shs); cv.px(11, y(16), ss); cv.px(12, y(16), ss)
            cv.px(10, y(17), shs); cv.px(13, y(17), shs)
            cv.px(10, y(18), hx("fbf3da")); cv.px(13, y(18), hx("fbf3da"))
            cv.px(10, y(19), hx("fbf3da")); cv.px(13, y(19), hx("fbf3da"))
            cv.hline(y(20), 9, 14, shs); cv.hline(y(21), 9, 14, shh)
            cv.px(9, y(21), shs); cv.px(14, y(21), shs)
        elif det == "overalls":
            bb, bs, bh = hx("d5aa89"), hx("a8825f"), hx("eccc9d")
            cv.rect(9, y(18), 14, y(22), bb)
            cv.hline(y(18), 9, 14, bh); cv.hline(y(22), 9, 14, bs)
            for yy in (16, 17):
                cv.px(9, y(yy), bb); cv.px(14, y(yy), bb)
            cv.px(14, y(19), bs); cv.px(14, y(20), bs); cv.px(14, y(21), bs)
            cv.px(9, y(18), GOLD); cv.px(14, y(18), GOLD)
            cv.rect(11, y(19), 12, y(20), bs)  # pocket
            cv.hline(y(19), 11, 12, bh)
        elif det == "blouse":
            cv.px(10, y(16), WHITE); cv.px(13, y(16), WHITE)
            cv.px(9, y(17), WHITE_S); cv.px(14, y(17), WHITE_S)
            cv.px(11, y(17), hx("c03326")); cv.px(12, y(17), hx("c03326"))
            for yy in (18, 19, 20):
                cv.px(11, y(yy), hx("c03326")); cv.px(12, y(yy), hx("862119"))
            cv.px(11, y(21), hx("c03326")); cv.px(12, y(21), hx("862119"))
            cv.px(11, y(22), hx("862119"))
            cv.px(9, y(20), WHITE_S); cv.px(14, y(21), WHITE_S)
        elif det == "smock":
            cv.hline(y(16), 9, 14, hx("c03326")); cv.px(11, y(16), ss)
            cv.px(10, y(17), hx("c03326")); cv.px(13, y(17), hx("e2684a"))
            cv.px(9, y(19), hx("2f78b8")); cv.px(10, y(20), hx("f3be4c")); cv.px(13, y(19), hx("c03326"))
            cv.px(12, y(21), hx("7ba14c")); cv.px(14, y(20), hx("2f78b8")); cv.px(11, y(18), hx("f3be4c"))
            cv.px(9, y(22), hx("c03326"))
            cv.px(8, y(21), hx("2f78b8"))
        elif det == "mail":
            for i in range(5):  # strap
                cv.px(9 + i, y(17 + i), hx("845744"))
                cv.px(10 + i, y(17 + i), hx("aa6d55"))
            cv.px(13, y(19), GOLD); cv.px(13, y(20), GOLD)
            cv.px(9, y(20), shs); cv.px(14, y(18), shh)
            cv.px(11, y(21), hx("1d386d")); cv.px(12, y(21), hx("1d386d"))
            cv.hline(y(22), 8, 15, hx("5f3a2c"))
    else:
        cv.hline(y(16), 9, 14, ss)
        cv.hline(y(16), 8, 8, sh); cv.hline(y(16), 15, 15, sh)
        cv.px(10, y(20), shs); cv.px(13, y(19), shs)
        if det == "apron":
            cv.hline(y(19), 8, 15, WHITE_S)
            cv.px(11, y(20), WHITE); cv.px(12, y(20), WHITE)
            cv.rect(10, y(20), 13, y(22), WHITE); cv.hline(y(22), 10, 13, WHITE_S)
        elif det == "vest":
            vb, vs, vh = hx("528447"), hx("2f5c32"), hx("7ba14c")
            for yy in range(17, 23):
                cv.px(8, y(yy), vs); cv.px(15, y(yy), vs)
            cv.px(11, y(18), vs); cv.px(12, y(18), vs); cv.hline(y(17), 9, 14, vh)
        elif det == "overalls":
            bb, bs = hx("d5aa89"), hx("a8825f")
            cv.rect(9, y(19), 14, y(22), bb); cv.hline(y(19), 9, 14, bs)
            cv.px(10, y(17), bb); cv.px(10, y(18), bb); cv.px(13, y(17), bb); cv.px(13, y(18), bb)
        elif det == "smock":
            cv.px(10, y(20), hx("2f78b8")); cv.px(13, y(19), hx("f3be4c")); cv.px(12, y(21), hx("c03326"))
            cv.hline(y(17), 9, 14, hx("c03326")) if False else None
        elif det == "mail":
            cv.rect(8, y(17), 15, y(22), hx("aa6d55"))
            cv.hline(y(17), 9, 14, hx("c98a6a"))
            cv.hline(y(19), 8, 15, hx("7d4a38"))
            cv.rect(8, y(20), 8, y(22), hx("7d4a38")); cv.rect(15, y(20), 15, y(22), hx("7d4a38"))
            cv.rect(10, y(20), 13, y(22), hx("7d4a38")); cv.rect(11, y(20), 12, y(21), hx("aa6d55"))
            cv.px(11, y(19), GOLD); cv.px(12, y(19), GOLD)
        elif det == "hoodie":
            cv.rect(9, y(17), 14, y(19), shh); cv.hline(y(20), 9, 14, shs)
        elif det == "cardigan":
            for yy in range(17, 22):
                cv.px(11, y(yy), shs)
        elif det == "blouse":
            cv.hline(y(17), 9, 14, WHITE_S)
            cv.px(11, y(19), WHITE_S)
        # hair-less neck handled by head


def body_front(sp, d, f, mode):
    cv = gp.Cv()
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
    pb, ps, ph = sp["pants"]
    cv.rect(8, 23, 15, 24, pb)
    cv.hline(23, 8, 15, ph)
    cv.px(11, 24, ps); cv.px(12, 24, ps)
    if sp["lower"] == "skirt":
        # legs first, skirt over the top
        draw_leg_front(cv, sp, 8, lift_l, "L"); draw_leg_front(cv, sp, 13, lift_r, "R")
        for y in range(24, 27):
            cv.hline(y, 7, 16, pb)
            cv.px(7, y, ph); cv.px(16, y, ps)
        cv.hline(26, 7, 16, ps)
        for x in (9, 11, 13):
            cv.px(x, 25, ps)
        cv.px(8, 24, ph)
        if sp["detail"] == "smock":
            cv.px(9, 25, hx("f3be4c")); cv.px(14, 26, hx("faf3e2"))
    else:
        draw_leg_front(cv, sp, 8, lift_l, "L")
        draw_leg_front(cv, sp, 13, lift_r, "R")
    draw_torso_front(cv, sp, dy, back, arm_l, arm_r)
    return cv.im, dy


def body_side(sp, f, mode):
    """Right-facing view."""
    cv = gp.Cv()
    dy = 0
    near_b = far_b = 10
    near_arm = 0
    if mode == "walk":
        if f == 1:
            near_b, far_b, near_arm, dy = 12, 8, -1, 1
        elif f == 3:
            near_b, far_b, near_arm, dy = 8, 12, 1, 1
    else:
        dy = 1 if f == 1 else 0
    pb, ps, ph = sp["pants"]
    sl, sm, ss = sp["skin"]
    shoe, shoe_d, shoe_h = sp["shoes"]
    lower = sp["lower"]
    det = sp["detail"]

    def leg(bx, pants, pants_s, shoe_col, skin):
        for y in range(23, 28):
            x = 10 + round((bx - 10) * (y - 23) / 4)
            if lower == "pants" or y < 26 or (lower == "skirt" and False):
                cv.hline(y, x, x + 2, pants)
                cv.px(x, y, pants_s)
            else:
                cv.hline(y, x, x + 2, skin)
                cv.px(x, y, ss if False else sm)
        cv.hline(28, bx, bx + 2, ph if lower == "pants" else skin)
        cv.hline(29, bx, bx + 4, shoe_col)
        cv.hline(30, bx, bx + 4, shoe_d)
        if shoe_col == shoe:
            cv.hline(29, bx + 3, bx + 4, shoe_h)

    leg(far_b, ps, ps, shoe_d if False else tuple(max(0, c - 30) if i < 3 else 255 for i, c in enumerate(shoe)), sm)
    leg(near_b, pb, ps, shoe, sl)
    cv.rect(9, 23, 13, 23, pb)
    y = lambda v: v + dy
    sh, shs, shh = sp["shirt"]
    # bag behind (mail) / apron etc
    if det == "mail":
        cv.rect(5, y(18), 8, y(22), hx("aa6d55"))
        cv.hline(y(18), 6, 8, hx("c98a6a"))
        cv.rect(5, y(19), 5, y(22), hx("7d4a38"))
        cv.hline(y(20), 5, 8, hx("7d4a38"))
        cv.px(8, y(20), GOLD)
    # torso
    cv.rect(9, y(16), 14, y(21), sh)
    cv.rect(9, y(17), 9, y(21), shs)
    cv.hline(y(17), 10, 13, shh)
    cv.hline(y(22), 9, 14, ps)
    cv.px(11, y(20), shs); cv.px(12, y(19), shs)
    if lower == "skirt":
        for yy in range(24, 27):
            cv.hline(yy, 8, 15, pb)
        cv.hline(26, 8, 15, ps); cv.px(8, 24, ph); cv.px(15, 25, ps)
    if det == "apron":
        cv.rect(11, y(18), 14, y(22), WHITE); cv.hline(y(18), 11, 14, hx("dbdad7"))
        cv.hline(y(22), 11, 14, WHITE_S); cv.px(14, y(20), WHITE_S)
        cv.px(10, y(19), WHITE_S)
    elif det == "vest":
        cv.rect(11, y(17), 14, y(22), hx("528447")); cv.px(14, y(19), hx("2f5c32")); cv.hline(y(22), 11, 14, hx("2f5c32"))
        cv.hline(y(17), 11, 13, hx("7ba14c")); cv.px(11, y(20), GOLD)
    elif det == "cardigan":
        cv.px(14, y(18), shh); cv.px(14, y(19), hx("faf3e2")); cv.px(14, y(20), hx("faf3e2"))
        cv.px(13, y(21), shs)
    elif det == "hoodie":
        cv.hline(y(16), 10, 13, shs); cv.hline(y(20), 11, 14, shs); cv.px(13, y(18), hx("fbf3da"))
    elif det == "overalls":
        bb, bs = hx("d5aa89"), hx("a8825f")
        cv.rect(11, y(18), 14, y(22), bb); cv.hline(y(22), 11, 14, bs); cv.px(11, y(18), GOLD)
        cv.rect(11, y(16), 12, y(17), bb)
    elif det == "blouse":
        cv.px(14, y(18), hx("c03326")); cv.px(14, y(19), hx("c03326")); cv.px(14, y(20), hx("862119"))
    elif det == "smock":
        cv.px(13, y(19), hx("2f78b8")); cv.px(11, y(20), hx("f3be4c")); cv.px(14, y(21), hx("c03326"))
        cv.hline(y(16), 11, 13, hx("c03326"))
    elif det == "mail":
        for i in range(5):
            cv.px(10 + i // 1 if i < 4 else 14, y(17 + i), hx("845744"))
        cv.px(13, y(20), GOLD)
    cv.hline(y(16), 11, 13, sp["skin"][2]) if det not in ("smock",) else None
    # near arm
    long_sl = sp["sleeve"] == "long"
    n_sl = 5 if long_sl else 2
    cv.rect(10, y(17), 11, y(16 + n_sl), sh)
    cv.px(10, y(18), shs)
    cv.px(10, y(17), shh)
    start = 22 if long_sl else 19
    for yy in range(start, 23):
        s = near_arm if yy > 19 else 0
        cv.hline(y(yy), 10 + s, 11 + s, sl)
        cv.px(10 + s, y(yy), sm)
    cv.hline(y(22 + (1 if near_arm else 0)), 10 + near_arm, 11 + near_arm, ss)
    return cv.im, dy


def compose(n, view, f, mode):
    sp = SPR[n["id"]]
    if view in ("Down", "Up"):
        body, dy = body_front(sp, view, f, mode)
        dh = view
    else:
        body, dy = body_side(sp, f, mode)
        dh = "Right"
    cvh = gp.Cv()
    cvh.im = body
    draw_head(cvh, sp, dh, dy, n["id"])
    img = cvh.im
    # hair on top, shifted with the body bob
    img = Image.alpha_composite(img, gp.shift(hair_layer(sp, dh, n["id"]), 0, dy))
    hl = hat_layer(n, "side" if dh == "Right" else ("up" if dh == "Up" else "down"), dy)
    if hl is not None:
        img = Image.alpha_composite(img, hl)
    img = gp.outline(img)
    if view == "Left":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def walk_frames(n, view):
    return [compose(n, {"down": "Down", "up": "Up"}[view], f, "walk") for f in range(4)]


def side_frames(n, flip):
    return [compose(n, "Left" if not flip else "Right", f, "walk") for f in range(4)]


def idle_frames(n):
    return [compose(n, "Down", f, "idle") for f in range(2)]




# ---------------------------------------------------------------------------------------------
# Portraits (48x48)
# ---------------------------------------------------------------------------------------------
BG = "="
BG2 = "+"


def portrait(n, mood):
    g = Grid(PORT, PORT)
    hb, hs, hl = n["hair"]
    fk, fs, lk, ls = n["skin"]
    st = n["style"]
    # background card
    for y in range(PORT):
        for x in range(PORT):
            g.set(x, y, BG if y < 30 else BG2)
    # ---- shoulders / outfit (drawn first) ----
    tb, ts, tl = n["top"]
    t2b, t2s, t2l = n["top2"]
    g.ell(24, 58, 20, 17, tb, ymin=41)
    g.hline(46, 6, 41, ts) if False else None
    for y in range(44, 48):
        for x in range(0, PORT):
            if g.get(x, y) == tb and x > 34:
                g.set(x, y, ts)
    # neck
    g.rect(20, 36, 27, 42, fs)
    g.rect(21, 36, 27, 40, fk)
    g.rect(20, 40, 27, 41, fs)
    # outfit details
    o = n["outfit"]
    if o == "apron":
        g.rect(14, 43, 33, 47, "P"); g.hline(43, 14, 33, "8")
        g.vline(14, 43, 47, "7"); g.vline(33, 43, 47, "7")
        g.rect(22, 41, 25, 42, fs)
    elif o == "vest":
        g.ell(24, 58, 20, 17, t2b, ymin=42)
        g.rect(21, 42, 26, 47, tb)
        g.set(23, 42, fs); g.set(24, 42, fs)
        g.rect(13, 45, 14, 46, "I")
    elif o == "cardigan":
        g.rect(22, 41, 25, 47, t2b)
        g.rect(21, 41, 22, 43, t2l); g.rect(25, 41, 26, 43, t2l)
    elif o == "hoodie":
        g.hline(41, 15, 32, ts); g.hline(42, 16, 31, ts)
        g.rect(23, 42, 24, 47, "M")
    elif o == "overalls":
        g.rect(15, 43, 32, 47, t2b)
        g.rect(15, 41, 17, 43, t2b); g.rect(30, 41, 32, 43, t2b)
        g.rect(15, 44, 16, 45, "I"); g.rect(31, 44, 32, 45, "I")
    elif o == "blouse":
        g.rect(19, 41, 22, 44, "P"); g.rect(25, 41, 28, 44, "P")
        g.rect(23, 42, 24, 47, "B"); g.rect(22, 47, 25, 47, "~")
        g.set(23, 41, fs); g.set(24, 41, fs)
    elif o == "smock":
        g.rect(19, 41, 28, 43, "B")
        g.rect(14, 45, 15, 46, "p"); g.rect(33, 46, 34, 47, "I"); g.rect(30, 44, 31, 45, "t")
    elif o == "mail":
        for i in range(8):
            g.rect(14 + i * 2, 41 + i // 2 + 0, 15 + i * 2, 42 + i // 2 + 1, "F")
        g.rect(31, 45, 33, 47, "I")
        g.rect(19, 41, 28, 41, tl)
    # ---- long hair behind head ----
    if st in ("long", "wavy"):
        g.ell(24, 30, 21, 20, hb, ymin=20, ymax=47)
        g.rect(4, 30, 11, 47, hb) if False else None
        for y in range(34, 48):
            for x in list(range(4, 12)) + list(range(36, 44)):
                if g.get(x, y) in (BG, BG2) or True:
                    g.set(x, y, hb)
        g.vline(6, 36, 47, hs); g.vline(41, 36, 47, hs)
        g.rect(10, 38, 12, 47, hs); g.rect(35, 38, 37, 47, hs)
        # redraw shoulders over hair's inner part
        g.ell(24, 58, 16, 17, tb, ymin=43)
        g.rect(20, 36, 27, 42, fs); g.rect(21, 36, 27, 40, fk)
    if st == "bob":
        g.ell(24, 24, 20.5, 16.5, hb)
        g.rect(4, 24, 9, 36, hb); g.rect(38, 24, 43, 36, hb)
        for x in range(4, 10):
            g.set(x, 37, hs)
        for x in range(38, 44):
            g.set(x, 37, hs)
        g.vline(4, 34, 36, "_") if False else None
    # ---- head ----
    # hair mass
    cx, cy = 23.5, 21.0
    hair_rx, hair_ry = 18.6, 17.4
    curly = st == "curly"
    for y in range(PORT):
        for x in range(PORT):
            if ((x - cx) / hair_rx) ** 2 + ((y - cy) / hair_ry) ** 2 <= 1.0 and y <= 30:
                g.set(x, y, hb)
    # side hair length per style
    side_end = {"curly": 30, "short": 27, "long": 40, "wavy": 40, "bob": 35}[st]
    if st in ("curly", "short"):
        for y in range(18, side_end + 1):
            for x in range(PORT):
                if ((x - cx) / hair_rx) ** 2 + ((y - cy) / 18.5) ** 2 <= 1.0 and not (13 <= x <= 34 and y > 26):
                    g.set(x, y, hb)
    else:
        for y in range(18, side_end + 1):
            for x in range(5, 11):
                g.set(x, y, hb)
            for x in range(37, 43):
                g.set(x, y, hb)
    # face
    for y in range(PORT):
        for x in range(PORT):
            if ((x - 23.5) / 14.0) ** 2 + ((y - 27.0) / 12.4) ** 2 <= 1.0:
                g.set(x, y, fk)
    # soft chin shade
    for x in range(14, 34):
        if g.get(x, 38) == fk:
            g.set(x, 38, fs)
    for y in range(31, 38):
        for x in (9, 38):
            pass
    # fringe
    fr = n["fringe"]
    for x in range(8, 40):
        t = abs(x - 23.5)
        if fr == "part":
            fl = 17 + 0.50 * t
        elif fr == "straight":
            fl = 22 + 0.10 * t
        elif fr == "side":
            fl = 17 + 0.55 * (x - 14) / 1.0 if x > 14 else 17 + 0.5 * (14 - x) * 0.4
            fl = min(fl, 25.5)
            fl = 16 + (x - 12) * 0.5 if x < 24 else 22 - (x - 24) * 0.35
            fl = max(16, min(25, fl))
        else:  # swept
            fl = 18 + 0.35 * (23.5 - x) if x < 23.5 else 20 + 0.45 * (x - 23.5)
            fl = max(16, min(26, fl))
        jag = 2 if (x % 4 in (0, 1)) else 0
        fl += jag if fr != "straight" else (1 if x % 3 == 0 else 0)
        fl = min(fl, 27)
        for y in range(8, int(fl) + 1):
            if g.get(x, y) in (fk, hb, hs, hl) or ((x - cx) / hair_rx) ** 2 + ((y - cy) / hair_ry) ** 2 <= 1.0:
                g.set(x, y, hb)
        # shade strip right under hair edge
        yy = int(fl)
        if g.get(x, yy + 1) == fk:
            g.set(x, yy + 1, fs)
    # ragged hair silhouette + side locks breaking the face outline (seeded)
    rnd = random.Random(500 + n["id"])
    hairs = (hb, hs, hl)

    def is_bg(x, y):
        return g.get(x, y) in (BG, BG2)

    edge = [(x, y) for y in range(3, 40) for x in range(PORT)
            if g.get(x, y) == hb and any(is_bg(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)))]
    for (x, y) in edge:
        r = rnd.random()
        if r < 0.0:
            pass
        elif r < 0.12:
            for dx, dy in ((1, 0), (-1, 0), (0, -1)):
                if is_bg(x + dx, y + dy):
                    g.set(x + dx, y + dy, hb)
                    if rnd.random() < 0.4:
                        g.set(x + dx * 2, y + dy * 2, hb) if is_bg(x + dx * 2, y + dy * 2) else None
                    break
    if st in ("curly", "short"):
        for (lx, ly0, ly1) in ((11, 20, 29), (12, 21, 27), (36, 20, 29), (35, 21, 27)):
            for yy in range(ly0, ly1 + 1):
                if g.get(lx, yy) == fk:
                    g.set(lx, yy, hb)
    # 3-tone shading like the player: top edge light/mid, interior mid with streaks, bottom edge dark
    mask = {(x, y) for y in range(PORT) for x in range(PORT) if g.get(x, y) in hairs}
    for (x, y) in sorted(mask):
        if g.get(x, y) != hb:
            continue
        above = (x, y - 1) in mask
        below = (x, y + 1) in mask
        h = (x * 7 + y * 13 + x * y * 3 + n["id"] * 5) % 11
        if not above:
            c = hl if h % 3 == 0 else hb
        elif not below:
            c = hs
        elif h % 8 == 0 and y <= 20:
            c = hl
        elif h % 7 == 0 and (x, y + 2) not in mask:
            c = hs
        else:
            c = hb
        g.set(x, y, c)
    # sheen streaks (2px wide diagonal) and long strand lines
    for sx, sy in ((14, 7), (18, 6), (27, 7), (32, 9), (11, 11)):
        for k in range(4):
            if g.get(sx + k, sy + k // 2) == hb:
                g.set(sx + k, sy + k // 2, hl)
    for x, y0, y1 in ((13, 9, 15), (17, 8, 12), (21, 7, 11), (26, 8, 13), (30, 8, 12), (34, 10, 16), (9, 13, 19)):
        for y in range(y0, y1 + 1):
            if g.get(x, y) in (hb, hl):
                g.set(x, y, hs)
    # ears for short styles
    if st in ("short",):
        for y in range(27, 31):
            g.set(9, y, fk); g.set(10, y, fk); g.set(38, y, fk); g.set(37, y, fk)
        g.set(9, 29, fs); g.set(38, 29, fs)
    # curly bumps
    if curly:
        for (x, y) in ((4, 14), (3, 20), (5, 26), (43, 14), (44, 20), (42, 26), (8, 6), (39, 6), (14, 3), (31, 3), (23, 2)):
            for dx in (0, 1):
                g.set(x + dx, y, hb); g.set(x + dx, y + 1, hb)
    # ---- face features ----
    ex_l, ex_r, ey = 15, 29, 26
    brow = ":" if n["hair"][0] not in ("1",) else "2"
    if mood == "Happy":
        for ex in (ex_l, ex_r):
            # closed smiling eye (arc)
            g.hline(ey + 1, ex, ex + 3, "0") if False else None
            g.set(ex, ey + 3, "0"); g.set(ex + 3, ey + 3, "0")
            g.hline(ey + 2, ex, ex + 3, "0") if False else None
            g.set(ex + 1, ey + 2, "0"); g.set(ex + 2, ey + 2, "0")
            g.set(ex, ey + 3, "0"); g.set(ex + 3, ey + 3, "0")
            g.hline(ey + 1, ex + 1, ex + 2, "0")
            g.set(ex, ey + 2, "0"); g.set(ex + 3, ey + 2, "0")
        # brows
        for ex in (ex_l, ex_r):
            g.hline(ey - 3, ex, ex + 3, brow)
        # small open smile
        g.hline(33, 22, 25, "0"); g.set(21, 32, "0"); g.set(26, 32, "0")
        g.set(22, 34, "0"); g.set(25, 34, "0"); g.hline(34, 23, 24, "C")
        g.hline(35, 23, 24, "0")
    else:
        eh = 6
        for ex in (ex_l, ex_r):
            g.rect(ex, ey, ex + 3, ey + eh - 1, "0")
            g.set(ex, ey, "_") if False else None
            g.set(ex, ey, "0")
            # highlights
            g.rect(ex, ey + 1, ex + 1, ey + 2, "`")
            g.set(ex + 3, ey + 4, "`") if False else None
            g.set(ex + 2, ey + 4, "4")
        if mood == "Sad":
            # shift eye shine and add tear
            g.set(ex_l + 1, ey + 5, "x"); g.set(ex_r + 2, ey + 5, "x")
            g.set(ex_l, ey + 6, "v"); g.set(ex_r + 3, ey + 6, "v")
            g.set(ex_l, ey + 7, "v") if False else None
            # brows slanted (inner end higher)
            for i, ex in enumerate((ex_l, ex_r)):
                if i == 0:
                    g.set(ex, ey - 2, brow); g.set(ex + 1, ey - 3, brow); g.set(ex + 2, ey - 4, brow); g.set(ex + 3, ey - 4, brow)
                else:
                    g.set(ex + 3, ey - 2, brow); g.set(ex + 2, ey - 3, brow); g.set(ex + 1, ey - 4, brow); g.set(ex, ey - 4, brow)
            # frown
            g.hline(34, 22, 25, "0"); g.set(21, 35, "0"); g.set(26, 35, "0")
            g.hline(35, 22, 25, ";") if False else None
        else:
            for ex in (ex_l, ex_r):
                g.hline(ey - 3, ex, ex + 3, brow)
            # soft smile
            g.hline(34, 22, 25, "0"); g.set(21, 33, "0"); g.set(26, 33, "0")
            g.hline(35, 23, 24, ";")
    # blush (all moods) - Happy stronger
    bl = "?"
    for (bx) in (11, 33):
        g.hline(31, bx, bx + 3, bl); g.hline(32, bx, bx + 3, bl)
        if mood == "Happy":
            g.hline(30, bx + 1, bx + 2, bl)
    if mood == "Sad":
        for (bx) in (11, 33):
            g.hline(32, bx, bx + 3, fk); g.hline(31, bx, bx + 3, bl)
    # nose
    g.set(23, 31, fs); g.set(24, 31, fs)
    # artist extras: lashes, sparkles, paint smudge
    if n["id"] == 7:
        for (x, y) in ((ex_l - 1, ey), (ex_l - 1, ey - 1), (ex_r + 4, ey), (ex_r + 4, ey - 1)):
            if mood != "Happy":
                g.set(x, y, "0")
        if mood != "Happy":
            g.set(ex_l + 2, ey + 2, "`"); g.set(ex_r + 2, ey + 2, "`")
        # extra charm: stronger blush, flower hairpin
        for bx in (11, 33):
            g.hline(30, bx, bx + 3, "?")
        g.set(11, 24, "I"); g.set(10, 25, "I"); g.set(12, 25, "I"); g.set(11, 26, "I"); g.set(11, 25, "B")
        # lips
        g.hline(34, 23, 24, "C") if mood == "Neutral" else None
    # ---- hats (over hair) ----
    hat = n["hat"]
    if hat:
        hb2, hs2, hl2 = n["hatc"]
        if hat == "chef":
            g.ell(24, 8, 20, 9, hb2, ymax=15)
            g.rect(5, 12, 42, 16, hb2)
            g.hline(16, 5, 42, hs2); g.hline(15, 5, 42, "7")
            for (x, y) in ((12, 6), (18, 3), (28, 4), (35, 7), (24, 8), (9, 11), (39, 11)):
                g.rect(x, y, x + 3, y + 1, hl2)
            g.hline(17, 6, 41, hs2) if False else None
            for x in range(6, 42):
                g.set(x, 11, "8") if x % 6 == 0 else None
            for (x, y) in ((6, 12), (41, 12), (8, 8), (39, 8), (15, 10), (31, 10)):
                g.set(x, y, hs2)
        elif hat == "cap":
            g.ell(24, 10, 18, 9, hb2, ymax=16)
            g.rect(6, 15, 41, 18, hs2)
            g.rect(6, 15, 41, 16, hb2); g.hline(15, 8, 40, hs2) if False else None
            g.rect(8, 17, 39, 19, hs2)
            g.rect(21, 7, 26, 11, "I"); g.hline(11, 21, 26, "Y") if False else None
            g.rect(22, 8, 25, 10, "K")
            for x in range(14, 30):
                g.set(x, 4 + int(abs(x - 20) * 0.2), hl2)
            g.hline(15, 7, 40, hs2)
            g.hline(12, 8, 38, hl2) if False else None
        elif hat == "straw":
            g.ell(24, 11, 14, 8, hb2, ymax=14)
            g.hline(13, 10, 38, "B"); g.hline(12, 10, 38, "B")
            g.ell(24, 17, 23, 5, hb2)
            g.hline(21, 3, 44, hs2); g.hline(22, 6, 41, hs2)
            for x in range(8, 40, 3):
                g.set(x, 17, hs2); g.set(x + 1, 19, hs2)
            for (x, y) in ((17, 6), (24, 4), (30, 7), (20, 9)):
                g.rect(x, y, x + 2, y + 1, hl2)
            for y in range(6, 12):
                g.set(14 + (y % 2) * 18, y, hs2)
        elif hat == "beret":
            g.ell(26, 9, 21, 8.5, hb2, ymax=17)
            g.rect(22, 0, 26, 2, hs2)
            g.rect(23, 0, 25, 1, hb2)
            g.hline(16, 5, 40, hs2); g.hline(17, 12, 38, hs2)
            g.rect(6, 12, 12, 14, hs2) if False else None
            for (x, y) in ((12, 8), (13, 6), (17, 5), (31, 8), (36, 12), (40, 14)):
                g.rect(x, y, x + 2, y + 1, hl2) if x < 28 else g.rect(x, y, x + 1, y + 1, hs2)
            g.hline(13, 9, 14, hs2)
    # glasses for neighbor
    if n["id"] == 3:
        for ex in (ex_l, ex_r):
            g.hline(ey - 1, ex - 2, ex + 5, "K") if False else None
            g.hline(ey - 1, ex - 1, ex + 4, "4")
            g.hline(ey + 7, ex - 1, ex + 4, "4")
            g.vline(ex - 2, ey, ey + 6, "4"); g.vline(ex + 5, ey, ey + 6, "4")
        g.hline(ey + 2, 21, 26, "4")
    # outline for the figure, then frame
    # (figure outline first: only where figure touches transparent -> none here; so frame it)
    frame = Grid(PORT, PORT)
    for y in range(PORT):
        for x in range(PORT):
            c = 3
            dx = min(x, PORT - 1 - x); dy = min(y, PORT - 1 - y)
            if dx + dy < c:
                continue
            if dx == 0 or dy == 0 or dx + dy == c:
                frame.set(x, y, "0")
            else:
                frame.set(x, y, g.get(x, y))
    # soft inner border line
    return frame


# ---------------------------------------------------------------------------------------------
def main():
    random.seed(7)
    for n in NPCS:
        folder = f"characters/npcs/npc_{n['id']:03d}/"
        base = f"NPC_{n['id']:03d}_{n['name']}"
        for view, label in (("down", "Down"), ("up", "Up")):
            save(strip(walk_frames(n, view)), f"{folder}{base}_{label}_Walk_v01.png")
        save(strip(side_frames(n, flip=False)), f"{folder}{base}_Left_Walk_v01.png")
        save(strip(side_frames(n, flip=True)), f"{folder}{base}_Right_Walk_v01.png")
        save(strip(idle_frames(n)), f"{folder}{base}_Down_Idle_v01.png")
        for mood in ("Neutral", "Happy", "Sad"):
            save(portrait(n, mood).image(), f"{folder}{base}_Portrait_{mood}_v01.png")
    print("NPC sprites + portraits written")


if __name__ == "__main__":
    main()
