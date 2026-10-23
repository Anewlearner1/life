"""Extra pixel art (art direction v2): character creation UI (UI-010), area unlock (UI-013),
cafe work tools (MINI-006) and relationship stage icons (EVT-002).

The CHAR-004 hairstyles are no longer generated here (owned by tools/gen_player.py).

Run: python3 tools/gen_extras.py   -> writes PNGs under assets/ (see assets/SPEC.md).

UI pieces use the concept-sheet toolkit from gen_ui (navy frames, cream interiors, soft rounded corners,
glossy blue controls). Cafe tools are legacy char grids keyed to tools/pixel.py's palette P.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image  # noqa: E402
from pixel import P, ASSETS, from_rows, save  # noqa: E402,F401
from gen_ui import (EMPTY, HEART7, HEART9, HEART11, HEART13, UP, add_outline, blank_wh, button_image,  # noqa: E402
                    cells_from_rows, cells_of, disc_cells, ellipse_cells, fill_cells, frame24, heart_img, new,
                    nine_stretch, outline_img, paste, put, rr_cells, rr_inside, shade_cells, tab_character, to_image,
                    layered_panel, vgrad, rect_cells)

INV = {v: k for k, v in P.items()}


# ----------------------------------------------------------------- helpers

def put_rows(canvas, rows, x0, y0):
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != EMPTY:
                canvas[y0 + y][x0 + x] = ch


def sprite(rows, W=16, H=16, outline=True):
    """Centre a char grid in a W x H canvas and add the 1px 'k' outline (legacy P palette)."""
    w = {len(r) for r in rows}
    assert len(w) == 1, f"ragged rows {sorted(w)}"
    cells = {(x, y): ch for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != EMPTY}
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    assert bw <= W - 2 and bh <= H - 2, f"sprite {bw}x{bh} too big for {W}x{H}"
    ox, oy = (W - bw) // 2 - min(xs), (H - bh) // 2 - min(ys)
    canvas = blank_wh(W, H)
    for (x, y), ch in cells.items():
        canvas[y + oy][x + ox] = ch
    if outline:
        add_outline(canvas)
    return to_image(canvas)


def sprite_up(im, W=16, H=16, outline="out"):
    """Centre a UP-coloured RGBA sprite on a W x H canvas and outline it."""
    cells = cells_of(im)
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    x0, y0 = min(xs), min(ys)
    bw, bh = max(xs) - x0 + 1, max(ys) - y0 + 1
    assert bw <= W - 2 and bh <= H - 2, f"sprite {bw}x{bh} too big for {W}x{H}"
    out = new(W, H)
    out.alpha_composite(im.crop((x0, y0, x0 + bw, y0 + bh)), ((W - bw) // 2, (H - bh) // 2))
    return outline_img(out, outline)


# ----------------------------------------------------------------- UI-010 character creation

def arrow(direction):
    """Glossy blue chevron-triangle (concept arrows), 16x16."""
    im = new(16, 16)
    cells = set()
    for y in range(2, 14):
        d = abs(y - 7.5)
        for x in range(3, 13):
            if d <= 5.6 and x >= 3 + d * 1.5 - 0.2:
                cells.add((x, y))
    shade_cells(im, cells, "blue2", "sky", "navy2", deep=True)
    for x, y in ((6, 7), (7, 6), (7, 7), (6, 8)):
        put(im, x, y, "white")
    im = outline_img(im, "out")
    return im.transpose(Image.FLIP_LEFT_RIGHT) if direction == "Right" else im


def swatch_frame():
    """12x12 selection ring (interior transparent): navy outline, white inner line."""
    im = new(12, 12)
    px = im.load()
    for y in range(12):
        for x in range(12):
            if not rr_inside(x, y, 12, 12, 3):
                continue
            if x in (0, 11) or y in (0, 11) or not rr_inside(x - 1, y - 1, 10, 10, 2):
                px[x, y] = UP["out"]
            elif not rr_inside(x - 2, y - 2, 8, 8, 1.2) or x in (1, 10) or y in (1, 10):
                px[x, y] = UP["white"]
    return im


def name_field():
    """96x16 text field: cream, navy outline, recessed top shadow."""
    W, Hh = 96, 16
    layers = [(0, "out"), (1, "blue2"),
              (2, lambda gx, gy: UP["creams"] if gy == 2 else UP["cream"])]
    return layered_panel(W, Hh, 3, layers)


def create_preview(swatch, arrows, field):
    W, Hh = 160, 120
    img = nine_stretch(frame24("navy", "sky", "cream"), W, Hh)
    img.alpha_composite(field, (32, 12))
    # stand-in avatar (bust icon at 3x) on a soft shadow
    for y in range(8):
        for x in range(36):
            if ((x + .5 - 18) / 18) ** 2 + ((y + .5 - 4) / 4) ** 2 <= 1:
                img.putpixel((22 + x, 98 + y), UP["creams"])
    img.alpha_composite(tab_character().resize((48, 48), Image.NEAREST), (16, 46))
    rows_y = (34, 54, 74)
    for y in rows_y:
        img.alpha_composite(arrows[0], (68, y))
        img.alpha_composite(arrows[1], (132, y))
    for row, cols in zip(rows_y, (("hair", "brownd", "gold"), ("skin", "brownl", "brownd"), ("blue", "red", "green"))):
        for i, key in enumerate(cols):
            x = 86 + i * 16
            fill_cells(img, rect_cells(x + 2, row + 4, 8, 8), key)
            img.alpha_composite(swatch, (x, row + 2))
    btn = button_image("normal")
    for x, y in ((20, 8), (21, 9), (22, 10), (23, 9), (24, 8), (25, 7), (26, 6), (27, 5)):
        for dy in (0, 1):
            put(btn, x, y + dy, "green")
    img.alpha_composite(btn, (84, 94))
    return img


# ----------------------------------------------------------------- UI-013 area unlock

def unlock_banner():
    """128x32 gold ribbon with swallow-tail ends, navy-brown outline and corner sparkles."""
    W, Hh = 128, 32
    im = new(W, Hh)
    px = im.load()
    for x in range(0, 20):                      # ribbon tails (behind), notched
        for y in range(10, 28):
            notch = 6 - abs(y - 18.5) * 0.75
            if x < notch:
                continue
            for xx in (x, W - 1 - x):
                px[xx, y] = UP["goldd"] if y >= 25 else UP["orange"]
    for y in range(4, 24):                      # main band
        for x in range(12, W - 12):
            c = UP["gold"]
            if y <= 5:
                c = UP["goldl"]
            elif y >= 21:
                c = UP["goldd"]
            px[x, y] = c
    for y in (8, 19):                           # stitching
        for x in range(18, W - 18):
            if x % 2 == 0:
                px[x, y] = UP["goldd"] if y == 8 else UP["orange"]
    for y in range(24, 28):                     # folds under the band ends
        for x in range(12, 20):
            if x - 12 >= y - 24:
                for xx in (x, W - 1 - x):
                    px[xx, y] = UP["oranged"]
    for cx, cy in ((26, 14), (W - 27, 14)):      # sparkles
        for d in (-2, -1, 1, 2):
            px[cx + d, cy] = UP["white"]
            px[cx, cy + d] = UP["white"]
        px[cx, cy] = UP["cream"]
    return outline_img(im, "outw")


def lock_icon(open_):
    from gen_ui import padlock
    if open_:
        return padlock(open_=True)
    return padlock(open_=False, body="grayl", light="white", dark="grayd")


def map_pin_new():
    im = new(16, 16)
    cx, cy, r = 6.0, 6.2, 4.8
    cells = disc_cells(cx, cy, r)
    for y in range(16):
        for x in range(16):
            dy = y + 0.5 - cy
            if 0 < dy <= r + 4.2 and abs(x + 0.5 - cx) <= (r + 4.2 - dy) * 0.6:
                cells.add((x, y))
    shade_cells(im, cells, "red", "redl", "redd", deep=True)
    fill_cells(im, disc_cells(cx, cy, 2.1), "white")
    # "new" sparkle badge, top right
    sx, sy = 12, 3
    for d in (-2, -1, 1, 2):
        put(im, sx + d, sy, "gold")
        put(im, sx, sy + d, "gold")
    put(im, sx, sy, "white")
    return outline_img(im, "outw")


# ----------------------------------------------------------------- MINI-006 cafe tools

ESPRESSO = [
    ".GGGGGGGGGGGG.",
    "GwwwwwwwwwwwwG",
    "GrrrrrrrrrrrrG",
    "GrwwwrrrrrrrrG",
    "GrwkwrrrrrryrG",
    "GrwwwrrrrrryrG",
    "GrrrrrrrrrrrrG",
    "GRRRRRRRRRRRRG",
    "GGGGGGGGGGGGGG",
    "....GGGGGG....",
    "....KKKKKKnnn.",
    "....gKKKKg....",
    "......KK......",
    "....wwwwww....",
    "....wnnnnw....",
    "....wwwwwwGG..",
    ".....wwwwG....",
    "gGGGGGGGGGGGGg",
    "KgKgKgKgKgKgKg",
]

GRINDER = [
    "..wwwwwwww..",
    "..wNNNNNNw..",
    "..wNnNNnNw..",
    "...wNNNNw...",
    "....wNNw....",
    "...KKKKKK...",
    "..KKKKKKKK..",
    "..KKrrKKKK..",
    "..KKrrKKKK..",
    "..KKKKKKKK..",
    "..KKKggKKK..",
    "..KKKggKKK..",
    ".GGGGGGGGGG.",
]

CUP = [
    "...G...G......",
    "....G...G.....",
    "..wwwwwwwwww..",
    ".wnnnnnnnnnnw.",
    ".wnnnwwnnnnnw.",
    ".wwwwwwwwwwww.",
    "..wwwwwwwwwwGG",
    "..wwwwwwwwwG.G",
    "..wwwwwwwwwG.G",
    "...wwwwwwwwGG.",
    "....wwwwwwG...",
    ".GGGGGGGGGGGGG",
    "..gggggggggggg",
]

MILK = [
    "..bbbb..",
    ".bbbbbb.",
    "bbbbbbbb",
    "wwwwwwwG",
    "wwwbwwwG",
    "wwbbbwwG",
    "wwbbbwwG",
    "wwwbwwwG",
    "wwwwwwwG",
    "wwwwwwwG",
    "GGGGGGGg",
]

TRAY = [
    "..wwww........",
    "..wnnw..yyyy..",
    "..wwww.yyyyyy.",
    "..wwww.oooooo.",
    "GGGGGGGGGGGGGG",
    "GwwwwwwwwwwwwG",
    ".GGGGGGGGGGGG.",
]

MENU = [
    "nnnnnnnnnnnnnn",
    "nKKKKKKKKKKKKn",
    "nKwwwwwwwwwKKn",
    "nKKKKKKKKKKKKn",
    "nKwwwwwwKyyKKn",
    "nKKKKKKKKKKKKn",
    "nKwwwwwKKyyKKn",
    "nKKKKKKKKKKKKn",
    "nKwwwwwwKyyKKn",
    "nKKKKKKKKKKKKn",
    "nNNNNNNNNNNNNn",
    "NNNNNNNNNNNNNN",
    ".nN........nN.",
    ".nN........nN.",
    ".nN........nN.",
    ".nN........nN.",
    ".NN........NN.",
    "NNNN......NNNN",
]

APRON = [
    "....wwwwww....",
    "...w......w...",
    "...w......w...",
    "...eeeeeeee...",
    "...eeeeeeee...",
    "..eeeeeeeeee..",
    "wwEEEEEEEEEEww",
    "..eeeeeeeeee..",
    "..eeeeeeeeee..",
    "..eewwwwwwee..",
    "..eewGGGGwee..",
    "..eewwwwwwee..",
    "..eeeeeeeeee..",
    "..EEEEEEEEEE..",
]


# ----------------------------------------------------------------- EVT-002 relationship stages

def hearts_up(rows, base, light, dark, outline="outw"):
    cells = cells_from_rows(rows)
    im = new(max(x for x, _ in cells) + 1, max(y for _, y in cells) + 1)
    shade_cells(im, cells, base, light, dark, deep=True)
    if len(rows[0]) >= 9:
        put(im, 2, 1, "white")
        put(im, 1, 2, "white")
    return im


def handshake():
    """Handshake 14x7: blue sleeve, green sleeve, clasped hands."""
    rows = [
        "....hhhh......",
        "bbbhhHhhhhhggg",
        "bbbhHhhhHhhgg.",
        "bbbhhHhhhhgggg",
        "bbb.hhhhhh.ggg",
        ".....HHHH.....",
    ]
    legend = {"h": "skin", "H": "skind", "b": "blue", "g": "green"}
    from gen_ui import grid
    return grid(rows, legend)


def combine(parts, W, Hh):
    out = new(W, Hh)
    for img, x, y in parts:
        paste(out, img, x, y)
    return out


def stage_icons():
    out = {}
    stranger = new(12, 11)
    shade_cells(stranger, ellipse_cells(6, 5.5, 5.5, 5.2), "grayl", "white", "gray", deep=True)
    for x, y in ((6, 3), (7, 3), (8, 4), (7, 5), (6, 6)):
        put(stranger, x - 1, y, "grayk")
    put(stranger, 5, 8, "grayk")
    out["Stranger"] = sprite_up(stranger, outline="grayk")
    out["Acquaintance"] = sprite_up(handshake())
    friend = combine([(hearts_up(HEART7, "pink", "pinkl", "pinkd"), 3, 0), (handshake(), 0, 8)], 14, 14)
    out["Friend"] = sprite_up(friend)
    close = combine([(hearts_up(HEART9, "pink", "pinkl", "pinkd"), 2, 3)], 14, 13)
    for dx, dy in ((0, 0), (-1, 1), (1, 1), (0, 2), (0, 1)):
        put(close, 11 + dx, 1 + dy, "gold")
    out["CloseFriend"] = sprite_up(close)
    crush = combine([(hearts_up(HEART11, "red", "redl", "redd"), 2, 2)], 14, 14)
    put(crush, 0, 3, "gold"); put(crush, 0, 4, "gold"); put(crush, 13, 1, "gold"); put(crush, 13, 2, "gold")
    out["Crush"] = sprite_up(crush)
    partner = combine([(hearts_up(HEART7, "pink", "pinkl", "pinkd"), 6, 0), (hearts_up(HEART11, "red", "redl", "redd"), 0, 3)], 14, 14)
    put(partner, 13, 9, "gold"); put(partner, 13, 10, "gold")
    out["Partner"] = sprite_up(partner)
    return out


def stage_bar():
    """96x12 six-segment bar with coloured pips (stranger .. partner)."""
    W, Hh = 96, 12
    layers = [(0, "out"), (1, "blue2"), (2, lambda gx, gy: UP["creams"] if gy == 2 else UP["cream"])]
    im = layered_panel(W, Hh, 3, layers)
    seg = (W - 2) / 6
    for i in range(1, 6):
        x = round(1 + seg * i)
        for y in range(2, Hh - 2):
            put(im, x, y, "blue2")
    pips = ["gray", "sky", "greenl", "gold", "pink", "red"]
    for i, key in enumerate(pips):
        cx = round(1 + seg * (i + 0.5)) - 1
        for dx in (0, 1):
            for dy in (0, 1):
                put(im, cx + dx, 5 + dy, key)
    return im


# ----------------------------------------------------------------- build

def build():
    out = []

    def w(img, rel):
        out.append(save(img, rel))

    # UI-010
    w(frame24("navy", "gold", "cream"), "ui/menus/UI_010_CreatePanel_v01.png")
    la, ra = arrow("Left"), arrow("Right")
    w(la, "ui/menus/UI_010_Arrow_Left_v01.png")
    w(ra, "ui/menus/UI_010_Arrow_Right_v01.png")
    sw, nf = swatch_frame(), name_field()
    w(sw, "ui/menus/UI_010_ColorSwatch_Frame_v01.png")
    w(nf, "ui/menus/UI_010_NameField_v01.png")
    w(create_preview(sw, (la, ra), nf), "ui/menus/UI_010_Preview_v01.png")

    # UI-013
    w(unlock_banner(), "ui/menus/UI_013_UnlockBanner_v01.png")
    w(lock_icon(False), "ui/menus/UI_013_Lock_Locked_v01.png")
    w(lock_icon(True), "ui/menus/UI_013_Lock_Unlocked_v01.png")
    w(map_pin_new(), "ui/menus/UI_013_MapPin_New_v01.png")

    # MINI-006
    tools = [("EspressoMachine", ESPRESSO, 16, 24), ("Grinder", GRINDER, 16, 16), ("Cup", CUP, 16, 16),
             ("Milk", MILK, 16, 16), ("Tray", TRAY, 16, 16), ("MenuBoard", MENU, 16, 24),
             ("Apron", APRON, 16, 16)]
    for name, rows, W, H in tools:
        w(sprite(rows, W, H), f"objects/work_tools/MINI_006_{name}_v01.png")

    # EVT-002
    for name, img in stage_icons().items():
        w(img, f"ui/icons/EVT_002_Stage_{name}_v01.png")
    w(stage_bar(), "ui/icons/EVT_002_StageBar_v01.png")
    return out


if __name__ == "__main__":
    paths = build()
    print(f"wrote {len(paths)} files")
