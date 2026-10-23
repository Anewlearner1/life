"""Family + weather art pack (art direction v2). Run: python3 tools/gen_family_weather.py

Reuses (read-only) the approved constructions from gen_player / gen_npcs / gen_ui / gen_world:
  1. Children  (24x32 chibi frames, 48x48 portraits)   assets/characters/children/CHAR_006_Child_{A,B,C}_*
  2. Elder look (player, gray hair + cardigan)           assets/characters/player/elder/CHAR_007_Player_Elder_*
  3. Props      crib, ring (shop icon), double bed       assets/objects/{furniture,products}/
  4. HUD icons  weather x4, season x4, family tab, ring  assets/ui/hud/UI_014/015/007/016
  5. FX         rain drop, snow flake, lamp glow, wedding hearts   assets/effects/weather/
Children: big head, short body; feet on the same bottom baseline as the adults (shoes rows 29-30, outline row 31).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402

import gen_player as gp  # noqa: E402
import gen_ui as ui  # noqa: E402
import gen_world as gw  # noqa: E402
from pixel import CP, save, strip  # noqa: E402

hx = gp.hx
Cv = gp.Cv
DIRS = ["Down", "Up", "Left", "Right"]
W, H = 24, 32

# ============================================================================================
# 1. CHILDREN
# ============================================================================================
SKIN_L, SKIN_M, SKIN_S = gp.SKIN_L, gp.SKIN_M, gp.SKIN_S
BLUSH, MOUTH = gp.BLUSH, gp.MOUTH
EYE_D, EYE_H = gp.EYE_D, gp.EYE_H
SHOE, SHOE_D, SHOE_H = gp.SHOE, gp.SHOE_D, gp.SHOE_H
SOCK, SOCK_S = gp.WHITE, gp.WHITE_S
GOLD, RED = gp.GOLD, gp.RED

CHILDREN = {
    "A": dict(  # brown spiky-hair boy, green tee + denim shorts
        style="spiky", hair=(hx("4a2a1c"), hx("84553a"), hx("c08a58")), iris=hx("3a2a20"),
        shirt=(hx("4d9a5a"), hx("33743f"), hx("7cc27a")), trim=GOLD, dress=False,
        lower=(hx("3675af"), hx("275d96"), hx("5f9bd6")), mid="skin"),
    "B": dict(  # orange pigtails girl, teal dress, white socks
        style="pigtails", hair=(hx("a8421f"), hx("dc6a2c"), hx("f9a455")), iris=hx("2f78b8"),
        shirt=(hx("48a9a6"), hx("2f7f82"), hx("86d4c8")), trim=hx("fff0c8"), dress=True,
        lower=(hx("48a9a6"), hx("2f7f82"), hx("86d4c8")), mid="sock"),
    "C": dict(  # black bob, red hoodie + gray pants
        style="bob", hair=(hx("1c1a22"), hx("33303d"), hx("5a5e72")), iris=hx("0c2947"),
        shirt=(hx("c03326"), hx("8a2219"), hx("e2684a")), trim=hx("f5f7f6"), dress=False,
        lower=(hx("6b6c6c"), hx("4d4e50"), hx("8e8f90")), mid="pants"),
}

# head: rows 9..21, 14 px wide, rounded corners (ears sit outside, hair overlays them)
HEAD_ROWS = {9: (8, 15), 10: (6, 17), 20: (6, 17), 21: (8, 15)}


def _parse(spec):
    return gp.parse(spec)


def child_hair_spans(style, d):
    R = {}

    def put(rows, spec):
        for r in ([rows] if isinstance(rows, int) else rows):
            R[r] = sorted(set(R.get(r, []) + _parse(spec)))

    if style == "spiky":
        put(6, "7,11-12,16"); put(7, "6-8,10-13,15-17"); put(8, "5-18"); put(9, "4-19")
        put(range(10, 13), "4-19")
        if d == "Down":
            put(13, "4-9,11-13,15-19"); put(14, "4-6,8,18-19"); put(15, "4,19")
        elif d == "Up":
            put(range(13, 19), "4-19"); put(19, "5-18"); put(20, "7-8,11-12,15-16")
        else:
            put(13, "4-9,12-13,15-18"); put(14, "4-9,17-18"); put(15, "4-9"); put(16, "4-9"); put(17, "5-9")
    elif style == "pigtails":
        put(8, "6-17"); put(9, "5-18"); put(range(10, 13), "4-19")
        tails = lambda: (put(12, "2-3,20-21"), put(range(13, 18), "1-3,20-22"), put(range(18, 20), "1-2,21-22"))
        if d == "Down":
            put(13, "4-10,13-19"); put(14, "4-6,17-19"); put(15, "4-5,18-19"); tails()
        elif d == "Up":
            put(range(13, 20), "4-19"); put(20, "6-17"); tails()
        else:
            put(13, "4-9,13-18"); put(14, "4-9,17-18"); put(range(15, 18), "4-9"); put(18, "5-8")
            put(12, "2-3"); put(range(13, 18), "1-3"); put(range(18, 20), "1-2")
    else:  # bob
        put(8, "6-17"); put(9, "5-18"); put(range(10, 14), "4-19")
        if d == "Down":
            put(range(14, 20), "3-5,18-20"); put(20, "4-6,17-19")
        elif d == "Up":
            put(range(14, 20), "3-20"); put(20, "4-19"); put(21, "5-18")
        else:
            put(14, "4-9,17-18"); put(range(15, 20), "3-9"); put(20, "4-8")
    return R


def child_hair_layer(cd, d):
    spans = child_hair_spans(cd["style"], d)
    dark, mid, light = cd["hair"]
    mask = {(x, y) for y, xs in spans.items() for x in xs}
    cv = Cv()
    for (x, y) in mask:
        above, below = (x, y - 1) in mask, (x, y + 1) in mask
        n = (x * 7 + y * 13 + x * y * 3) % 11
        if not above:
            c = light if n % 3 == 0 else mid
        elif not below:
            c = dark
        elif n % 9 == 0 and y <= 12:
            c = light
        elif n % 7 == 0 and below and (x, y + 2) not in mask:
            c = dark
        else:
            c = mid
        cv.px(x, y, c)
    if cd["style"] == "pigtails":  # hair ties
        for x in (2, 3, 20, 21) if d != "Right" else (2, 3):
            cv.px(x, 12, RED)
    return cv.im


def draw_child_head(cv, cd, d, dy):
    for y in range(9, 22):
        x0, x1 = HEAD_ROWS.get(y, (5, 18))
        cv.hline(y + dy, x0, x1, SKIN_L)
    cv.hline(21 + dy, 8, 15, SKIN_M)
    cv.hline(20 + dy, 7, 16, SKIN_L)
    if d == "Up":
        cv.hline(20 + dy, 6, 17, SKIN_M)
        return
    iris = cd["iris"]
    if d == "Down":
        for yy in range(16, 19):  # ears
            cv.px(4, yy + dy, SKIN_M); cv.px(19, yy + dy, SKIN_M)
        for ex in (8, 13):  # 3x3 big eyes
            cv.hline(15 + dy, ex, ex + 2, EYE_D)
            cv.hline(16 + dy, ex, ex + 2, EYE_D); cv.px(ex, 16 + dy, EYE_H)
            cv.hline(17 + dy, ex, ex + 2, iris); cv.px(ex + 2, 17 + dy, EYE_D)
        cv.hline(18 + dy, 6, 7, BLUSH); cv.hline(18 + dy, 16, 17, BLUSH)
        cv.hline(19 + dy, 11, 12, MOUTH)
    else:  # Right
        cv.rect(10, 16 + dy, 11, 18 + dy, SKIN_M); cv.px(11, 17 + dy, SKIN_S)
        cv.px(19, 17 + dy, SKIN_L); cv.px(19, 18 + dy, SKIN_L)  # nose
        cv.hline(15 + dy, 14, 16, EYE_D)
        cv.hline(16 + dy, 14, 16, EYE_D); cv.px(14, 16 + dy, EYE_H)
        cv.hline(17 + dy, 14, 16, iris); cv.px(16, 17 + dy, EYE_D)
        cv.hline(18 + dy, 15, 16, BLUSH)
        cv.px(17, 20 + dy, MOUTH)


def _leg_colors(cd):
    low, low_s, low_h = cd["lower"]
    mid = {"skin": SKIN_M, "sock": SOCK, "pants": low}[cd["mid"]]
    return low, low_s, low_h, mid


def child_body_front(cd, d, f, mode):
    cv = Cv()
    back = d == "Up"
    lift_l = lift_r = arm_l = arm_r = dy = 0
    if mode == "walk":
        if f == 1:
            lift_l, arm_l, arm_r, dy = 1, 1, -1, 1
        elif f == 3:
            lift_r, arm_l, arm_r, dy = 1, -1, 1, 1
    else:
        dy = 1 if f == 1 else 0
    low, low_s, low_h, mid = _leg_colors(cd)
    sh, shs, shl = cd["shirt"]

    def leg(x0, lift, side):
        sx0, sx1 = (8, 11) if side == "L" else (12, 15)
        for y in range(26, 29 - lift):
            c = mid if y == 28 else low
            cv.hline(y, x0, x0 + 2, c)
            cv.px(x0 + 2 if side == "L" else x0, y, low_s if c == low else (SOCK_S if cd["mid"] == "sock" else SKIN_S))
        cv.hline(29 - lift, sx0, sx1, SHOE)
        if not back:
            a = sx0 + 1 if side == "L" else sx1 - 2
            cv.hline(29 - lift, a, a + 1, SHOE_H)
        cv.hline(30 - lift, sx0, sx1, SHOE_D)

    leg(9, lift_l, "L"); leg(12, lift_r, "R")
    if cd["dress"]:  # flared skirt (fixed to the hips, torso bobs above it)
        for y, (a, b) in ((26, (8, 15)), (27, (7, 16))):
            cv.hline(y, a, b, sh)
        cv.hline(27, 7, 16, shs); cv.hline(27, 9, 14, sh)
        cv.px(7, 26, shs); cv.px(16, 26, shs)
        cv.hline(26, 10, 13, shl)
    y = lambda v: v + dy
    # torso + arms
    cv.rect(8, y(22), 15, y(25), sh)
    cv.rect(8, y(23), 8, y(25), shs); cv.rect(15, y(23), 15, y(25), shs)
    for (ax0, ax1, a) in ((6, 7, arm_l), (16, 17, arm_r)):
        cv.rect(ax0, y(23), ax1, y(24), sh)
        cv.px(ax0 if ax0 == 6 else ax1, y(24), shs)
        for yy in range(25, 26 + a):
            for xx in (ax0, ax1):
                cv.px(xx, y(yy), SKIN_L if xx == (ax0 if ax0 == 6 else ax1) else SKIN_M)
        cv.hline(y(26 + a), ax0, ax1, SKIN_S)
    cv.hline(y(25), 9, 14, shs) if not cd["dress"] else None
    if not back:
        cv.hline(y(22), 10, 13, SKIN_S)  # neck / collar
        if cd["style"] == "spiky":  # tee with a gold star stripe
            cv.hline(y(23), 9, 14, shl); cv.hline(y(24), 11, 12, cd["trim"])
        elif cd["style"] == "pigtails":  # dress with a cream collar + buttons
            cv.hline(y(22), 9, 14, cd["trim"]); cv.hline(y(22), 11, 12, SKIN_S)
            cv.hline(y(23), 10, 13, shl); cv.px(11, y(24), cd["trim"]); cv.px(12, y(24), cd["trim"])
        else:  # hoodie: strings + pocket
            cv.hline(y(23), 9, 14, shl); cv.px(10, y(23), cd["trim"]); cv.px(13, y(23), cd["trim"])
            cv.px(10, y(24), cd["trim"]); cv.px(13, y(24), cd["trim"])
            cv.hline(y(25), 10, 13, shs)
    else:
        if cd["style"] == "pigtails":  # bow on the back
            cv.hline(y(23), 10, 13, RED); cv.px(11, y(24), RED); cv.px(12, y(24), RED); cv.px(11, y(23), hx("e2684a"))
        elif cd["style"] == "bob":  # hood
            cv.hline(y(22), 8, 15, shl); cv.hline(y(23), 9, 14, shs)
        else:
            cv.hline(y(22), 9, 14, shl)
    draw_child_head(cv, cd, d, dy)
    return cv.im, dy


def child_body_side(cd, f, mode):
    cv = Cv()
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
    low, low_s, low_h, mid = _leg_colors(cd)
    sh, shs, shl = cd["shirt"]

    def leg(bx, pants, pants_s, mid_c, shoe_col):
        for y in range(26, 29):
            x = 10 + round((bx - 10) * (y - 26) / 3)
            cv.hline(y, x, x + 2, mid_c if y == 28 else pants)
            cv.px(x, y, pants_s)
        cv.hline(29, bx, bx + 3, shoe_col)
        cv.hline(30, bx, bx + 3, SHOE_D)
        if shoe_col == SHOE:
            cv.hline(29, bx + 2, bx + 3, SHOE_H)

    leg(far_b, low_s, low_s, low_s if cd["mid"] == "pants" else (SOCK_S if cd["mid"] == "sock" else SKIN_S), hx("6e4938"))
    leg(near_b, low, low_s, mid, SHOE)
    cv.rect(9, 26, 13, 26, low)
    if cd["dress"]:
        cv.rect(8, 26, 14, 27, sh); cv.hline(27, 8, 14, shs)
    y = lambda v: v + dy
    cv.rect(9, y(22), 14, y(25), sh)
    cv.rect(9, y(23), 9, y(25), shs)
    cv.hline(y(22), 11, 13, SKIN_S)
    if cd["style"] == "spiky":
        cv.hline(y(23), 12, 14, shl)
    elif cd["style"] == "pigtails":
        cv.px(14, y(24), cd["trim"])
    else:
        cv.hline(y(23), 12, 14, shl); cv.px(14, y(24), cd["trim"])
    # near arm
    cv.rect(10, y(23), 11, y(24), sh); cv.px(10, y(24), shs)
    for yy in (25, 26):
        cv.hline(y(yy + (near_arm if yy == 26 else 0)), 10 + near_arm, 11 + near_arm, SKIN_L)
    cv.hline(y(26 + (1 if near_arm else 0)), 10 + near_arm, 11 + near_arm, SKIN_S)
    draw_child_head(cv, cd, "Right", dy)
    return cv.im, dy


def child_frame(key, d, f, mode):
    cd = CHILDREN[key]
    if d in ("Down", "Up"):
        body, dy = child_body_front(cd, d, f, mode)
        hl = child_hair_layer(cd, d)
    else:
        body, dy = child_body_side(cd, f, mode)
        hl = child_hair_layer(cd, "Right")
    img = Image.alpha_composite(body, gp.shift(hl, 0, dy))
    img = gp.outline(img)
    if d == "Left":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def child_sheet(key, d, mode):
    return strip([child_frame(key, d, f, mode) for f in range(4 if mode == "walk" else 2)])


# ---------------------------------------------------------------- child portraits (48x48, NPC portrait style)
PORT = 48


class PCv(Cv):
    def ell(self, cx, cy, rx, ry, c, ymin=-99, ymax=999):
        for y in range(self.h):
            for x in range(self.w):
                if ymin <= y <= ymax and ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1.0:
                    self.px(x, y, c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.im.getpixel((x, y))
        return (0, 0, 0, 0)

    def vline(self, x, y0, y1, c):
        for y in range(y0, y1 + 1):
            self.px(x, y, c)


PORTRAIT_SPEC = {
    "A": dict(top=(hx("4d9a5a"), hx("33743f"), hx("7cc27a")), collar=hx("f2e6c0"), eye=hx("3a2a20"), brow=hx("4a2a1c")),
    "B": dict(top=(hx("48a9a6"), hx("2f7f82"), hx("86d4c8")), collar=hx("fff0c8"), eye=hx("2f78b8"), brow=hx("a8421f")),
    "C": dict(top=(hx("c03326"), hx("8a2219"), hx("e2684a")), collar=hx("f5f7f6"), eye=hx("2c4b62"), brow=hx("1c1a22")),
}
PBG, PBG2, PFRAME = CP["="], CP["+"], CP["0"]
HLITE = hx("f6efe0")


def child_portrait(key):
    cd = CHILDREN[key]
    ps = PORTRAIT_SPEC[key]
    hb, hs, hl = cd["hair"]
    st = cd["style"]
    fk, fs = SKIN_L, SKIN_M
    g = PCv(PORT, PORT)
    for y in range(PORT):
        for x in range(PORT):
            g.px(x, y, PBG if y < 30 else PBG2)
    tb, ts, tl = ps["top"]
    # hair behind the head (pigtails / bob)
    if st == "pigtails":
        for cx in (6.0, 41.0):
            g.ell(cx, 35, 4.6, 10.5, hb)
            g.ell(cx, 35, 4.6, 10.5, hb)
            for y in range(26, 46):
                x = int(cx) + (1 if cx < 20 else -1) + (-2 if cx < 20 else 1)
                g.px(x, y, hs)
    if st == "bob":
        g.ell(24, 25, 21, 17.5, hb)
        g.rect(3, 25, 10, 38, hb); g.rect(37, 25, 44, 38, hb)
        for x in list(range(3, 11)) + list(range(37, 45)):
            g.px(x, 39, hs)
    # shoulders / outfit
    g.ell(24, 62, 17.5, 21, tb, ymin=42)
    for y in range(44, 48):
        for x in range(PORT):
            if g.get(x, y) == tb and x > 33:
                g.px(x, y, ts)
    g.rect(21, 38, 26, 43, fs)
    g.hline(42, 21, 26, SKIN_S)
    if key == "A":   # tee: round neck + star stripe
        g.rect(19, 42, 28, 43, tb); g.rect(21, 42, 26, 42, fs); g.rect(20, 41, 27, 41, ts) if False else None
        g.hline(45, 20, 27, tl); g.rect(23, 46, 24, 47, GOLD)
    elif key == "B":  # dress: cream collar + buttons
        g.rect(18, 42, 29, 43, ps["collar"]); g.rect(22, 42, 25, 42, fs)
        g.rect(23, 45, 24, 46, ps["collar"]); g.hline(44, 20, 27, tl)
    else:             # hoodie: strings
        g.hline(42, 18, 29, ts); g.rect(21, 42, 26, 42, fs)
        for sx in (21, 26):
            g.rect(sx, 43, sx + 1, 47, ps["collar"])
    # hair mass over the top of the head
    cx, cy, hrx, hry = 23.5, 22.5, 19.0, 17.5
    g.ell(cx, cy, hrx, hry, hb, ymax=31)
    for y in range(20, 34):
        for x in range(PORT):
            if ((x + .5 - cx) / hrx) ** 2 + ((y + .5 - cy) / 19.0) ** 2 <= 1.0 and y <= (31 if st == "spiky" else 29):
                g.px(x, y, hb)
    # face (big round child face)
    g.ell(23.5, 28.5, 15.2, 12.8, fk)
    for x in range(14, 34):
        if g.get(x, 41) == fk:
            g.px(x, 41, fs)
    for y in (40, 41):
        for x in range(PORT):
            if g.get(x, y) == fk:
                g.px(x, y, fs if y == 41 else fk)
    # fringe
    for x in range(8, 40):
        t = abs(x - 23.5)
        if st == "spiky":
            fl = 19.5 + abs(((x + 1) % 6) - 3) * 1.4
        elif st == "pigtails":
            fl = 18 + 0.42 * t + (2 if x % 4 in (0, 1) else 0)
            if 22 <= x <= 25:
                fl = 15.5
        else:
            fl = 23 + (1 if x % 3 == 0 else 0)
        fl = min(fl, 27)
        for y in range(7, int(fl) + 1):
            if g.get(x, y) in (fk, hb, hs, hl, PBG, PBG2) and ((x + .5 - cx) / (hrx + .5)) ** 2 + ((y + .5 - cy) / 19.5) ** 2 <= 1.0:
                g.px(x, y, hb)
        if g.get(x, int(fl) + 1) == fk:
            g.px(x, int(fl) + 1, fs)
    # spiky tufts on top
    if st == "spiky":
        for sx, h in ((11, 3), (16, 4), (21, 3), (26, 4), (31, 3), (36, 3), (7, 2), (40, 2)):
            ty = min((yy for yy in range(0, 30) if g.get(sx, yy) == hb), default=8)
            for k in range(h):
                for xx in range(sx - (h - k - 1) // 2, sx + (h - k - 1) // 2 + 1):
                    g.px(xx, ty - 1 - k, hb)
    if st == "pigtails":  # hair-tie bands + bow clip
        for cx2 in (6, 41):
            g.rect(cx2 - 3, 26, cx2 + 3, 29, RED); g.hline(26, cx2 - 3, cx2 + 3, hx("e2684a")); g.hline(29, cx2 - 3, cx2 + 3, hx("8a2219"))
    # 3-tone hair shading
    hairs = (hb, hs, hl)
    mask = {(x, y) for y in range(PORT) for x in range(PORT) if g.get(x, y) in hairs}
    for (x, y) in sorted(mask):
        if g.get(x, y) != hb:
            continue
        above, below = (x, y - 1) in mask, (x, y + 1) in mask
        h = (x * 7 + y * 13 + x * y * 3 + ord(key) * 5) % 11
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
        g.px(x, y, c)
    for sx, sy in ((14, 8), (19, 7), (28, 8), (33, 10), (11, 13)):
        for k in range(4):
            if g.get(sx + k, sy + k // 2) == hb:
                g.px(sx + k, sy + k // 2, hl)
    for x, y0, y1 in ((13, 10, 16), (18, 9, 13), (22, 8, 12), (27, 9, 14), (31, 9, 13), (35, 11, 17)):
        for y in range(y0, y1 + 1):
            if g.get(x, y) in (hb, hl):
                g.px(x, y, hs)
    # ears for spiky / pigtails (bob covers them)
    if st != "bob":
        for y in range(28, 33):
            g.px(8, y, fk); g.px(9, y, fk); g.px(39, y, fk); g.px(38, y, fk)
        g.px(8, 30, fs); g.px(39, 30, fs)
    # ---- face: 5x7 sparkly eyes ----
    ey = 26
    for ex in (14, 29):
        g.rect(ex, ey, ex + 4, ey + 6, EYE_D)
        g.px(ex, ey, EYE_D)
        g.rect(ex + 1, ey + 4, ex + 3, ey + 5, ps["eye"])
        g.rect(ex + 1, ey + 1, ex + 2, ey + 2, HLITE)
        g.px(ex + 3, ey + 4, HLITE)
    for ex in (14, 29):
        g.hline(ey - 3, ex + 1, ex + 3, ps["brow"])
    g.hline(34 + 1, 11, 13, BLUSH); g.hline(35 + 1, 10, 13, BLUSH)
    g.hline(35, 34, 36, BLUSH); g.hline(36, 34, 37, BLUSH)
    g.px(23, 33, fs); g.px(24, 33, fs)
    # open smile
    g.hline(37, 22, 25, EYE_D); g.px(21, 36, EYE_D); g.px(26, 36, EYE_D)
    g.hline(38, 23, 24, MOUTH)
    # frame (NPC style: dark rounded frame, 3px corner cut)
    out = Image.new("RGBA", (PORT, PORT), (0, 0, 0, 0))
    for y in range(PORT):
        for x in range(PORT):
            dx, dy = min(x, PORT - 1 - x), min(y, PORT - 1 - y)
            if dx + dy < 3:
                continue
            out.putpixel((x, y), PFRAME if (dx == 0 or dy == 0 or dx + dy == 3) else g.im.getpixel((x, y)))
    return out


# ============================================================================================
# 2. ELDER LOOK (the player, gray hair, thinner spiky shape, cardigan tint)
# ============================================================================================
ELDER_HAIR = (hx("8a8a94"), hx("c4c4cc"), hx("f2f2f6"))
CARDI, CARDI_S, CARDI_H = hx("8a5a4a"), hx("5f3a30"), hx("b07d68")
ELDER_OUTFITS = {
    # cardigan over a cream vest, gray trousers
    "Default": dict(shirt=CARDI, shirt_s=CARDI_S, bib=hx("ecdcb8"), bib_h=hx("fff0c8"), bib_s=hx("c4ae82"),
                    belt=hx("5f3a30"), pants=hx("6f7078"), pants_s=hx("4d4e56"), pants_h=hx("8e8f98"), has_bib=True),
    "Outfit2": dict(gp.OUTFITS["Outfit2"]),
}
_orig_spans = gp.build_hair_spans


def _elder_spans(style, d):
    """Spiky shape but slimmer: outer-most hair columns trimmed, a few spike tips removed."""
    if style != "Elder":
        return _orig_spans(style, d)
    R, extra = _orig_spans("Spiky", d)
    lo, hi = (5, 18) if d != "Right" else (4, 18)
    out = {}
    for y, xs in R.items():
        keep = [x for x in xs if lo <= x <= hi] if len(xs) > 7 else list(xs)
        if y == 1:
            keep = [x for x in keep if x in (10, 14)]
        if keep:
            out[y] = keep
    return out, extra


def elder_frame(d, f, mode, outfit):
    gp.build_hair_spans = _elder_spans
    gp.HAIRS["Elder"] = ELDER_HAIR
    gp.OUTFITS["Elder" + outfit] = ELDER_OUTFITS[outfit]
    try:
        return gp.compose_frame(d, f, mode, "Elder" + outfit, "Elder")
    finally:
        gp.build_hair_spans = _orig_spans


def elder_sheet(d, mode, outfit):
    return strip([elder_frame(d, f, mode, outfit) for f in range(4 if mode == "walk" else 2)])


# ============================================================================================
# 3. PROPS (concept palette via gen_world helpers)
# ============================================================================================
def crib():
    im = gw.new(16, 24)
    rect, px = (lambda *a: gw.rect(im, *a)), (lambda *a: gw.px(im, *a))
    # corner posts + head board
    rect(1, 1, 14, 5, "G"); rect(1, 1, 14, 1, "J"); rect(1, 5, 14, 5, "E")
    for x in (3, 5, 7, 8, 10, 12):
        rect(x, 2, x, 4, "F")
    rect(1, 0, 2, 22, "G"); rect(13, 0, 14, 22, "G")      # side rails / posts
    rect(1, 0, 2, 0, "J"); rect(13, 0, 14, 0, "J")
    rect(2, 1, 2, 22, "E"); rect(13, 1, 13, 22, "E")
    # mattress, pillow, blanket
    rect(3, 6, 12, 18, "N"); rect(3, 6, 12, 6, "M")
    rect(4, 7, 11, 10, "9"); rect(4, 10, 11, 10, "8"); rect(5, 7, 6, 8, "V")
    rect(3, 11, 12, 18, "t"); rect(3, 11, 12, 12, "x"); rect(3, 18, 12, 18, "o")
    rect(4, 14, 6, 14, "x"); rect(9, 15, 11, 15, "x"); rect(7, 13, 8, 13, "I")
    # foot rail: top bar, bars, bottom bar
    rect(1, 19, 14, 20, "J"); rect(1, 20, 14, 20, "G")
    for x in range(3, 13, 2):
        rect(x, 21, x, 22, "F")
    rect(1, 22, 14, 22, "E")
    rect(1, 0, 14, 0, "J") if False else None
    # tiny gold finials
    px(1, 0, "K"); px(14, 0, "K")
    return gw.outline(im, "A")


def double_bed():
    im = gw.new(16, 32)
    rect, px = (lambda *a: gw.rect(im, *a)), (lambda *a: gw.px(im, *a))
    rect(1, 1, 14, 30, "E"); rect(2, 1, 13, 4, "G"); rect(2, 1, 13, 1, "J")
    rect(2, 5, 13, 29, "N")
    # two pillows side by side
    rect(2, 6, 7, 11, "9"); rect(8, 6, 13, 11, "9")
    rect(2, 11, 7, 11, "7"); rect(8, 11, 13, 11, "7")
    rect(3, 6, 4, 9, "V"); rect(9, 6, 10, 9, "V")
    rect(7, 6, 8, 11, "N")                                   # pillow gap
    # warm duvet (two-tone) with fold and a heart
    rect(2, 14, 13, 29, "C"); rect(2, 14, 13, 16, "@"); rect(2, 16, 13, 16, "B")
    rect(2, 17, 13, 29, "!"); rect(2, 17, 13, 17, "@")
    rect(2, 24, 13, 24, "B")                                 # fold line
    rect(2, 27, 5, 27, "@"); rect(10, 26, 13, 26, "@")
    for (x, y, k) in ((5, 19, "9"), (6, 19, "9"), (9, 19, "9"), (10, 19, "9"), (5, 20, "9"), (6, 20, "9"), (7, 20, "9"),
                      (8, 20, "9"), (9, 20, "9"), (10, 20, "9"), (6, 21, "9"), (7, 21, "9"), (8, 21, "9"), (9, 21, "9"),
                      (7, 22, "9"), (8, 22, "9")):
        px(x, y, k)
    px(5, 19, "V"); px(6, 20, "V")
    rect(2, 29, 13, 30, "E"); rect(2, 29, 13, 29, "G")
    return gw.outline(im, "A")


def ring_icon():
    """Shop product icon: gold band with a blue gem."""
    im = ui.new(16, 16)
    band = ui.disc_cells(8, 10.6, 4.9) - ui.disc_cells(8, 10.6, 2.6)
    ui.shade_cells(im, band, "gold", "goldl", "goldd", deep=True)
    for (x, y) in ((6, 6), (7, 6), (8, 6), (9, 6)):          # prongs / setting
        ui.put(im, x, y, "gold")
    ui.put(im, 6, 6, "goldl"); ui.put(im, 9, 6, "goldd")
    gem = ui.cells_from_rows([".XX.", "XXXX", "XXXX", ".XX."], "X", 6, 2)
    ui.shade_cells(im, gem, "azure", "sky", "blue", deep=True)
    ui.put(im, 6, 3, "white"); ui.put(im, 7, 2, "white")
    ui.put(im, 9, 4, "blue")
    return ui.outline_img(im, "outw")


# ============================================================================================
# 4. HUD ICONS (16x16)
# ============================================================================================
def _cloud_cells(dx=0.0, dy=0.0, s=1.0):
    """Cloud = 3 discs + flat base. s scales the whole shape; (dx, dy) shifts it."""
    c = (ui.disc_cells(4.8 * s + dx, 7.6 * s + dy, 3.0 * s) | ui.disc_cells(8.6 * s + dx, 5.6 * s + dy, 3.9 * s)
         | ui.disc_cells(11.9 * s + dx, 8.0 * s + dy, 2.9 * s))
    for y in range(16):
        for x in range(16):
            if 4.5 * s + dx <= x + .5 <= 12.5 * s + dx and 8.0 * s + dy <= y + .5 <= 10.9 * s + dy:
                c.add((x, y))
    return {(x, y) for (x, y) in c if y + .5 <= 10.9 * s + dy and 0 <= x < 16 and 0 <= y < 16}


def _cloud(im, base, light, dark, dx=0.0, dy=0.0, s=1.0):
    cells = _cloud_cells(dx, dy, s)
    ui.shade_cells(im, cells, base, light, dark, deep=True)
    return cells


def weather(kind):
    im = ui.new(16, 16)
    if kind == "Sunny":
        core = ui.disc_cells(8, 8, 3.7)
        ui.shade_cells(im, core, "gold", "goldl", "orange", deep=True)
        ui.outline_img(im, "oranged")
        for (x, y) in ((8, 1), (8, 0), (8, 14), (8, 15), (1, 8), (0, 8), (14, 8), (15, 8),
                       (3, 3), (2, 2), (12, 3), (13, 2), (3, 12), (2, 13), (12, 12), (13, 13)):
            ui.put(im, x, y, "orange" if (x, y) not in ((8, 1), (1, 8), (14, 8), (8, 14), (3, 3), (12, 3), (3, 12), (12, 12)) else "gold")
        ui.put(im, 6, 6, "white"); ui.put(im, 7, 6, "white"); ui.put(im, 6, 7, "white")
        return im
    if kind == "Cloudy":   # dark storm-grey cloud with a small pale puff behind (concept s08 dark cloud)
        _cloud(im, "grayl", "snow", "gray", dx=0.0, dy=0.2, s=0.62)
        ui.outline_img(im, "out")
        front = _cloud_cells(0.0, 2.4, 1.0)
        for c in front:
            ui.put(im, c[0], c[1], "gray")
        ui.shade_cells(im, front, "fogd", "fog", "grayd", deep=True)
        for (x, y) in front:
            if (x, y + 1) not in front:
                ui.put(im, x, y, "grayd")
            elif (x, y + 2) not in front and (x - 1, y) in front and (x + 1, y) in front:
                ui.put(im, x, y, "grayd")
        return ui.outline_img(im, "out")
    _cloud(im, "white", "creamh", "mist", dy=0.4)
    cells = ui.cells_of(im)
    for (x, y) in cells:   # soft blue underside like the concept clouds
        if (x, y + 1) not in cells:
            ui.put(im, x, y, "fog")
        elif (x, y + 2) not in cells and (x + 1, y) in cells and (x - 1, y) in cells:
            ui.put(im, x, y, "ice")
    ui.outline_img(im, "out")
    if kind == "Rain":
        for (x0, y0) in ((4, 12), (8, 13), (12, 12)):
            ui.put(im, x0, y0, "sky"); ui.put(im, x0, y0 + 1, "azure"); ui.put(im, x0 - 1, y0 + 1, "azure")
            ui.put(im, x0 - 1, y0 + 2, "blue")
    else:  # Snow
        for (x0, y0) in ((3, 12), (7, 13), (11, 12), (5, 15), (9, 15), (13, 15)):
            ui.put(im, x0, y0, "azure")
            if y0 < 15:
                ui.put(im, x0 + 1, y0, "sky"); ui.put(im, x0, y0 + 1, "sky"); ui.put(im, x0 + 1, y0 + 1, "white")
    return im


def _pcells(rows, ox=0, oy=0):
    return ui.cells_from_rows(rows, "X", ox, oy)


def season(kind):
    im = ui.new(16, 16)
    if kind == "Spring":   # cherry blossom: 5 round petals + gold centre
        cells = set()
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            cells |= ui.disc_cells(8 + 3.5 * math.cos(a), 8.3 + 3.5 * math.sin(a), 2.5)
        ui.shade_cells(im, cells, "pink", "pinkl", "pinkd", deep=True)
        for k in range(5):  # petal notch lines
            a = -math.pi / 2 + k * 2 * math.pi / 5 + math.pi / 5
            ui.put(im, round(7.5 + 5.6 * math.cos(a)), round(7.8 + 5.6 * math.sin(a)), "pinkd")
        ui.fill_cells(im, ui.disc_cells(8, 8.3, 1.9), "gold")
        ui.put(im, 7, 7, "goldl"); ui.put(im, 9, 9, "goldd")
        return ui.outline_img(im, ui.H("#8f2a58"))
    if kind == "Summer":  # lush green leaf (diagonal, tip up-right) with midrib + veins
        cells = set()
        c = math.sqrt(.5)
        for y in range(16):
            for x in range(16):
                dx, dy = x + .5 - 8.2, 8.0 - (y + .5)
                u, v = (dx + dy) * c, (dy - dx) * c
                if abs(u) <= 7.6 and abs(v) <= 4.6 * (1 - (u / 7.6) ** 2):
                    cells.add((x, y))
        ui.shade_cells(im, cells, "green", "greenl", "greend", deep=True)
        for i in range(-7, 8):    # midrib
            x, y = round(8.2 + i * c - .5), round(8.0 - i * c - .5)
            if (x, y) in cells:
                ui.put(im, x, y, "limel" if i > 0 else "lime")
        for (i, side) in ((-3, 1), (-3, -1), (0, 1), (0, -1), (3, 1), (3, -1)):   # side veins
            u, v = i, side * 1.0
            x, y = round(8.2 + (u - v) * c - .5), round(8.0 - (u + v) * c - .5)
            if (x, y) in cells:
                ui.put(im, x, y, "greend")
        ui.put(im, 2, 14, "leafd"); ui.put(im, 1, 15, "leafd")
        return ui.outline_img(im, "greeno")
    if kind == "Autumn":  # maple leaf
        rows = [
            ".......X.......",
            "......XXX......",
            "..X..XXXXX..X..",
            "..XX.XXXXX.XX..",
            "..XXXXXXXXXXX..",
            "...XXXXXXXXX...",
            ".XXXXXXXXXXXXX.",
            "..XXXXXXXXXXX..",
            "...XXXXXXXXX...",
            "....XXXXXXX....",
            ".....XXXXX.....",
            ".......X.......",
            ".......X.......",
        ]
        cells = _pcells(rows, 0, 1)
        ui.shade_cells(im, cells, "orange", "orangel", "red", deep=True)
        for y in range(5, 13):
            ui.put(im, 7, y, "oranged") if (7, y) in cells else None
        for (x, y) in ((7, 11), (7, 12)):
            ui.put(im, x, y, "oranged")
        ui.put(im, 7, 13, "brownd") if False else None
        return ui.outline_img(im, "redo")
    # Winter: snowflake (cardinal + diagonal arms) on a soft blue disc so it reads on cream panels
    disc = ui.disc_cells(8, 8, 7.0)
    ui.shade_cells(im, disc, "sky", "sky2", "azure", deep=True)
    flake = ["....XX....",
             ".X..XX..X.",
             "..X.XX.X..",
             "...XXXX...",
             "XXXXXXXXXX",
             "XXXXXXXXXX",
             "...XXXX...",
             "..X.XX.X..",
             ".X..XX..X.",
             "....XX...."]
    ui.fill_cells(im, ui.cells_from_rows(flake, "X", 3, 3), "white")
    ui.put(im, 7, 7, "ice"); ui.put(im, 8, 8, "ice")
    return ui.outline_img(im, "navy2")


def tab_family():
    im = ui.new(16, 16)
    wall = ui.rect_cells(3, 8, 10, 7)
    ui.shade_cells(im, wall, "cream", "creamh", "creams", deep=True)
    roof = {(x, y) for y in range(1, 9) for x in range(1, 15) if abs(x - 7.5) <= (y - 1) * 1.05 + 0.6}
    ui.shade_cells(im, roof, "red", "redl", "redd", deep=True)
    for x in range(1, 15):
        ui.put(im, x, 8, "redd")
    heart = ui.cells_from_rows(["XX..XX", "XXXXXX", "XXXXXX", ".XXXX.", "..XX.."], "X", 5, 9)
    ui.fill_cells(im, heart, "pinkd" if False else "red")
    ui.put(im, 5, 10, "redl"); ui.put(im, 6, 9, "redl")
    for (x, y) in ((10, 11), (11, 11), (10, 12), (11, 12)):
        pass
    ui.fill_cells(im, ui.rect_cells(3, 14, 10, 1), "creamd")
    return ui.outline_img(im, "outw")


def ring_small():
    """Propose-button icon: smaller ring with a tiny blue gem (diagonal, sparkle)."""
    im = ui.new(16, 16)
    band = ui.disc_cells(8, 10.2, 4.2) - ui.disc_cells(8, 10.2, 2.2)
    ui.shade_cells(im, band, "gold", "goldl", "goldd", deep=True)
    gem = ui.cells_from_rows([".X.", "XXX", ".X."], "X", 7, 3)
    ui.shade_cells(im, gem, "azure", "sky", "blue", deep=True)
    ui.put(im, 8, 4, "sky2")
    ui.put(im, 7, 6, "gold"); ui.put(im, 8, 6, "gold"); ui.put(im, 9, 6, "gold")
    ui.outline_img(im, "outw")
    for (x, y) in ((2, 2), (13, 3)):  # sparkle ticks
        ui.put(im, x, y, "goldl"); ui.put(im, x - 1, y, "goldd") if False else None
    ui.put(im, 12, 1, "white"); ui.put(im, 13, 2, "gold"); ui.put(im, 11, 2, "gold"); ui.put(im, 12, 3, "gold")
    return im


# ============================================================================================
# 5. FX
# ============================================================================================
def rain_drop():
    im = Image.new("RGBA", (2, 6), (0, 0, 0, 0))
    for (x, y, k) in ((1, 0, "x"), (1, 1, "v"), (1, 2, "t"), (0, 3, "t"), (0, 4, "p"), (0, 5, "p")):
        im.putpixel((x, y), CP[k])
    return im


def snow_flake():
    f0 = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    for (x, y, k) in ((1, 0, "z"), (2, 0, "z"), (0, 1, "z"), (1, 1, "V"), (2, 1, "V"), (3, 1, "z"),
                      (0, 2, "z"), (1, 2, "V"), (2, 2, "V"), (3, 2, "z"), (1, 3, "z"), (2, 3, "z")):
        f0.putpixel((x, y), CP[k])
    f1 = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    for (x, y, k) in ((1, 0, "x"), (2, 1, "V"), (1, 1, "V"), (0, 1, "z"), (3, 1, "z"),
                      (1, 2, "V"), (2, 2, "V"), (1, 3, "x"), (2, 0, "z"), (2, 3, "z"), (0, 2, "z"), (3, 2, "z")):
        f1.putpixel((x, y), CP[k])
    for (x, y) in ((0, 0), (3, 0), (0, 3), (3, 3)):
        f1.putpixel((x, y), (0, 0, 0, 0))
    # frame 1: sparkle cross (thin arms) instead of the round flake
    f1 = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    for (x, y, k) in ((1, 0, "z"), (2, 0, "V"), (0, 1, "z"), (1, 1, "V"), (2, 1, "V"), (3, 1, "z"),
                      (1, 2, "V"), (2, 2, "V"), (1, 3, "V"), (2, 3, "z")):
        f1.putpixel((x, y), CP[k])
    return strip([f0, f1])


def lamp_glow():
    S = 32
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = (S - 1) / 2
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - c, y - c) / (S / 2)
            if r >= 1:
                continue
            t = (1 - r) ** 2.0
            a = round(190 * t / 8) * 8            # banded alpha keeps it pixel-art soft
            col = (255, round(214 + 28 * t), round(96 + 90 * t))
            if a > 0:
                im.putpixel((x, y), (*col, min(a, 255)))
    return im


def _heart_cells(rows, ox, oy):
    return {(x + ox, y + oy) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "X"}


HEART7 = ["XX.XX", "XXXXX", "XXXXX", ".XXX.", "..X.."]    # 5x5 mid heart
HEART5 = ["X.X", "XXX", ".X."]                              # 3x3 mini heart


def wedding_hearts():
    frames = []
    conf = [(1, 3, "I"), (14, 5, "m"), (3, 10, "x"), (12, 12, "l"), (7, 1, "B"), (9, 8, "o")]
    for k in range(4):
        fr = ui.new(16, 16)
        # big pink heart rising, mini heart rising out of phase
        by, bx = 9 - 3 * k, 5 + (1 if k in (1, 2) else 0)
        cells = _heart_cells(HEART7, bx, by)
        cells = {(x, y) for (x, y) in cells if 0 <= y < 16}
        ui.shade_cells(fr, cells, "red", "redl", "redd", deep=True)
        if (bx + 1, by + 1) in cells:
            ui.put(fr, bx + 1, by + 1, "white")
        ui.outline_img(fr, "outw")
        my, mx = (14 - 3 * k) % 15, 11 + (1 if k % 2 else 0)
        mc = {(x, y) for (x, y) in _heart_cells(HEART5, mx, my) if 0 <= y < 16 and x < 16}
        ui.shade_cells(fr, mc, "pink", "pinkl", "pinkd")
        # second mini heart (left)
        ly, lx = (6 - 3 * k) % 14, 1 + (1 if k % 2 == 0 else 0)
        lc = {(x, y) for (x, y) in _heart_cells(HEART5, lx, ly) if 0 <= y < 16}
        ui.shade_cells(fr, lc, "pinkl", "white", "pink")
        # confetti: drifts down 3px/frame (wraps), alternating sideways
        for (cx, cy, col) in conf:
            y = (cy + 3 * k) % 16
            x = (cx + (1 if (k + cx) % 2 else 0)) % 16
            if fr.getpixel((x, y))[3] == 0:
                ui.put(fr, x, y, {"I": "gold", "m": "pink", "x": "sky", "l": "greenl", "B": "red", "o": "orange"}[col])
        frames.append(fr)
    return strip(frames)


# ============================================================================================
def main():
    n = 0
    # --- children
    for key in "ABC":
        for d in DIRS:
            save(child_sheet(key, d, "walk"), f"characters/children/CHAR_006_Child_{key}_{d}_Walk_v01.png")
            save(child_sheet(key, d, "idle"), f"characters/children/CHAR_006_Child_{key}_{d}_Idle_v01.png")
            n += 2
        save(child_portrait(key), f"characters/children/CHAR_006_Child_{key}_Portrait_v01.png")
        n += 1
    # --- elder
    for outfit in ("Default", "Outfit2"):
        for d in DIRS:
            for mode, tag in (("walk", "Walk"), ("idle", "Idle")):
                save(elder_sheet(d, mode, outfit), f"characters/player/elder/CHAR_007_Player_Elder_{outfit}_{d}_{tag}_v01.png")
                n += 1
    # --- props
    save(crib(), "objects/furniture/BLD_006_Crib_v01.png")
    save(double_bed(), "objects/furniture/BLD_006_DoubleBed_v01.png")
    save(ring_icon(), "objects/products/OBJ_004_Ring_v01.png")
    n += 3
    # --- HUD
    for k in ("Sunny", "Cloudy", "Rain", "Snow"):
        save(weather(k), f"ui/hud/UI_014_Weather_{k}_v01.png")
    for k in ("Spring", "Summer", "Autumn", "Winter"):
        save(season(k), f"ui/hud/UI_015_Season_{k}_v01.png")
    save(tab_family(), "ui/hud/UI_007_Tab_Family_v01.png")
    save(ring_small(), "ui/hud/UI_016_Ring_v01.png")
    n += 10
    # --- FX
    save(rain_drop(), "effects/weather/FX_006_RainDrop_v01.png")
    save(snow_flake(), "effects/weather/FX_006_SnowFlake_v01.png")
    save(lamp_glow(), "effects/weather/FX_007_LampGlow_v01.png")
    save(wedding_hearts(), "effects/weather/FX_008_Hearts_Wedding_v01.png")
    n += 4
    print(f"family/weather: wrote {n} files")


if __name__ == "__main__":
    main()
