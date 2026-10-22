"""Extra pixel art: hairstyles (CHAR-004), character creation UI (UI-010), area unlock (UI-013),
cafe work tools (MINI-006) and relationship stage icons (EVT-002).

Run: python3 tools/gen_extras.py   -> writes PNGs under assets/ (see assets/SPEC.md).

Grids use '.' for empty and palette keys from tools/pixel.py otherwise. Helpers come from gen_ui.
Hair overlays are drawn for the Down-facing bald base head built from the player's walk frame 0.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from pixel import P, ASSETS, from_rows, save  # noqa: E402
from gen_ui import (EMPTY, add_outline, blank_wh, button_image, disc_rows, nine_rows,  # noqa: E402
                    panel_frame, stretch, to_image)

INV = {v: k for k, v in P.items()}


# ----------------------------------------------------------------- helpers

def put(canvas, rows, x0, y0):
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != EMPTY:
                canvas[y0 + y][x0 + x] = ch


def sprite(rows, W=16, H=16, outline=True):
    """Centre a char grid in a W x H canvas and add the 1px 'k' outline."""
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


def load_player():
    return Image.open(ASSETS / "characters/player/walk/CHAR_001_Player_Down_Walk_v01.png").convert("RGBA").crop((0, 0, 16, 24))


# ----------------------------------------------------------------- CHAR-004 hairstyles

def bald_base():
    """Player Down walk frame 0 with the hair removed (skin dome instead)."""
    pl = load_player()
    rows = ["".join(INV[pl.getpixel((x, y))] for x in range(16)) for y in range(24)]
    dome = [
        "________________",
        "____kkkkkkkk____",
        "___k" + "s" * 8 + "k___",
        "__k" + "s" * 10 + "k__",
    ]
    rows[0:4] = dome
    for y in range(4, 9):                       # sideburns / fringe -> skin
        rows[y] = rows[y].replace("N", "s").replace("n", "s")
    return from_rows(rows)


# fills: row -> 16 chars ('.' empty, N main, n highlight, r tie). Outline is added automatically.
HAIR = {
    "Spiky": ({
        1: "...N.N.NN.N.N...",
        2: "..NNNNNNNNNNNN..",
        3: "..NNNNNNNNNNNN..",
        4: "..NNNN.NN.NNNN..",
        5: "..NN..N..N..NN..",
        6: "...N........N...",
        7: "...N........N...",
    }, [(5, 2), (6, 2), (4, 3), (5, 3), (7, 1)]),
    "Short": ({
        1: ".....NNNNNN.....",
        2: "....NNNNNNNN....",
        3: "...NNNNNNNNNN...",
        4: "...NNNN..NNNN...",
        5: "...N........N...",
        6: "...N........N...",
        7: "...N........N...",
    }, [(6, 1), (7, 1), (5, 2), (4, 3)]),
    "Long": ({
        1: "....NNNNNNNN....",
        2: "...NNNNNNNNNN...",
        3: "..NNNNNNNNNNNN..",
        4: ".NNNNNNN..NNNNN.",
        5: ".NNN........NNN.",
        6: ".NNN........NNN.",
        7: ".NNN........NNN.",
        8: ".NNN........NNN.",
        9: ".NNN........NNN.",
        10: ".NNN........NNN.",
        11: ".NNN........NNN.",
        12: ".NN..........NN.",
        13: ".NN..........NN.",
    }, [(5, 1), (6, 1), (4, 2), (1, 6), (1, 7), (14, 9)]),
    "Bob": ({
        1: "....NNNNNNNN....",
        2: "...NNNNNNNNNN...",
        3: "..NNNNNNNNNNNN..",
        4: "..NNNNNNNNNNNN..",
        5: "..NN........NN..",
        6: "..NN........NN..",
        7: "..NN........NN..",
        8: "..NN........NN..",
        9: "..NN........NN..",
        10: "..NN........NN..",
    }, [(5, 1), (6, 1), (4, 2), (2, 6), (2, 7)]),
    "Ponytail": ({
        1: ".....NNNNNN.....",
        2: "....NNNNNNNN....",
        3: "...NNNNNNNNNN...",
        4: "...NNNN..NNNNrN.",
        5: "...N........NNN.",
        6: "...N........NNN.",
        7: "...N........NNN.",
        8: "...N........NNN.",
        9: ".............NN.",
        10: "..............N.",
    }, [(6, 1), (7, 1), (5, 2), (4, 3), (14, 6)]),
    "Buzz": ({
        2: "....NNNNNNNN....",
        3: "...NNNNNNNNNN...",
        4: "...NN......NN...",
    }, []),
}


def hair_overlay(style):
    fills, hl = HAIR[style]
    bald = bald_base()
    mask = set()                                  # skin pixels of the bald head (never outlined)
    for y in range(0, 12):
        for x in range(16):
            px = bald.getpixel((x, y))
            if px[3] and px != P["k"]:
                mask.add((x, y))
    g = blank_wh(16, 24)
    for y, row in fills.items():
        assert len(row) == 16, (style, y)
        for x, ch in enumerate(row):
            if ch != ".":
                g[y][x] = ch
    for x, y in hl:
        assert g[y][x] == "N", (style, x, y)
        g[y][x] = "n"
    if style == "Buzz":                           # stubble texture
        for y in range(2, 5):
            for x in range(16):
                if g[y][x] == "N" and (x + y) % 2:
                    g[y][x] = "n"
    ring = []
    for y in range(24):
        for x in range(16):
            if g[y][x] != EMPTY or (x, y) in mask:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < 16 and 0 <= ny < 24 and g[ny][nx] != EMPTY:
                    ring.append((x, y))
                    break
    for x, y in ring:
        g[y][x] = "k"
    return to_image(g)


def hair_preview(overlays):
    W, H = 6 * 16 + 7 * 4, 24 + 8
    out = panel_frame(W, H).convert("RGBA")
    bald = bald_base()
    for i, ov in enumerate(overlays):
        cell = bald.copy()
        cell.alpha_composite(ov)
        out.alpha_composite(cell, (4 + i * 20, 4))
    return out


# ----------------------------------------------------------------- UI-010 character creation

CREATE_DEPTH = "kBbBBBYk"      # navy band, light-blue line, gold inner trim


def arrow(direction):
    rows = []
    for y in range(11):
        d = abs(y - 5)
        line = ""
        for x in range(7):
            if x >= d:
                c = "y" if y <= 5 else "Y"
                if x == d and y <= 5:
                    c = "w"
                line += c
            else:
                line += EMPTY
        rows.append(line)
    if direction == "Right":
        rows = [r[::-1] for r in rows]
    return sprite(rows)


def swatch_frame():
    rows = []
    for y in range(12):
        line = ""
        for x in range(12):
            if (x, y) in ((0, 0), (11, 0), (0, 11), (11, 11)):
                line += "_"
            elif x in (0, 11) or y in (0, 11):
                line += "k"
            elif x in (1, 10) or y in (1, 10):
                line += "w" if (x, y) == (1, 1) else "B"
            else:
                line += "_"
        rows.append(line)
    return from_rows(rows)


def name_field():
    W, H = 96, 16
    rows = []
    for y in range(H):
        line = ""
        for x in range(W):
            if (x in (0, W - 1)) and (y in (0, H - 1)):
                line += "_"
            elif x in (0, W - 1) or y in (0, H - 1):
                line += "k"
            elif x in (1, W - 2) or y in (1, H - 2):
                line += "B"
            elif y == 2:
                line += "G"            # inset shadow along the top
            else:
                line += "w"
        rows.append(line)
    return from_rows(rows)


def create_preview(swatch, arrows, field, hair_ov):
    W, H = 160, 120
    img = from_rows(stretch(nine_rows(CREATE_DEPTH, "w"), W, H)).convert("RGBA")
    img.alpha_composite(field, (32, 12))
    # character on a soft shadow, drawn at 3x
    sh = Image.new("RGBA", (W, H))
    for y in range(8):
        for x in range(36):
            if ((x + .5 - 18) / 18) ** 2 + ((y + .5 - 4) / 4) ** 2 <= 1:
                sh.putpixel((22 + x, 98 + y), P["G"])
    img.alpha_composite(sh)
    img.alpha_composite(load_player().resize((48, 72), Image.NEAREST), (16, 30))
    # selector rows: arrows + content between
    rows_y = (34, 54, 74)
    for y in rows_y:
        img.alpha_composite(arrows[0], (68, y))
        img.alpha_composite(arrows[1], (132, y))
    thumb = bald_base()
    thumb.alpha_composite(hair_ov)
    img.alpha_composite(thumb.crop((0, 0, 16, 16)), (100, rows_y[0]))
    for row, cols in zip(rows_y[1:], (("s", "t", "T"), ("N", "y", "R"))):
        for i, key in enumerate(cols):
            x = 86 + i * 16
            img.paste(Image.new("RGBA", (8, 8), P[key]), (x + 2, row + 4))
            img.alpha_composite(swatch, (x, row + 2))
    # confirm button with a green tick
    btn = button_image("normal").convert("RGBA")
    for x, y in ((20, 8), (21, 9), (22, 10), (23, 9), (24, 8), (25, 7), (26, 6), (27, 5)):
        for dy in (0, 1):
            btn.putpixel((x, y + dy), P["e"])
    img.alpha_composite(btn, (84, 94))
    return img


# ----------------------------------------------------------------- UI-013 area unlock

def unlock_banner():
    W, H = 128, 32
    c = blank_wh(W, H)
    # ribbon tails (behind), with swallow-tail notch
    for x in range(0, 20):
        for y in range(10, 28):
            notch = 6 - abs(y - 18.5) * 0.75
            for side in (0, 1):
                xx = x if side == 0 else W - 1 - x
                if x < notch:
                    continue
                c[y][xx] = "Y" if y >= 25 else "y"
    # main band
    for y in range(4, 24):
        for x in range(12, W - 12):
            c[y][x] = "w" if y == 4 else ("Y" if y >= 22 else "y")
    for y in (7, 20):                              # dashed stitching
        for x in range(18, W - 18):
            if x % 2 == 0:
                c[y][x] = "Y" if y == 7 else "o"
    # folds under the band ends
    for y in range(24, 28):
        for x in range(12, 20):
            if x - 12 >= y - 24:
                for xx in (x, W - 1 - x):
                    c[y][xx] = "N"
    # corner sparkles
    for cx, cy in ((26, 14), (W - 27, 14)):
        for d in (-1, 0, 1):
            c[cy + d][cx] = "w"
            c[cy][cx + d] = "w"
    add_outline(c)
    return to_image(c)


LOCKED = [
    "..gggggg..",
    ".gg....gg.",
    ".g......g.",
    ".g......g.",
    "wwwwwwwwww",
    "wGGGGGGGGg",
    "wGGGkkGGGg",
    "wGGGkkGGGg",
    "wGGGGkGGGg",
    "wGGGGGGGGg",
    "gggggggggg",
]

UNLOCKED = [
    "......GGGG..",
    ".....GG..GG.",
    ".....G....G.",
    ".....G....G.",
    "....G.......",
    "wwwwwwwwwwww",
    "wyyyyyyyyyyY",
    "wyyyykkyyyyY",
    "wyyyykkyyyyY",
    "wyyyyykyyyyY",
    "wyyyyyyyyyyY",
    "YYYYYYYYYYYY",
]


def map_pin_new():
    c = blank_wh(16, 16)
    cx, cy, r = 5.5, 6.0, 4.6
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            disc = dx * dx + dy * dy <= r * r
            tip = dy > 0 and abs(dx) <= (r + 4.0 - dy) * 0.55 and dy <= r + 4.0 and abs(dx) <= r
            if disc or tip:
                c[y][x] = "R" if (dx + dy > 2.0) else "r"
    for y in range(16):
        for x in range(16):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= 2.2 ** 2:
                c[y][x] = "w"
    for x, y in ((3, 3), (4, 2)):
        if c[y][x] == "r":
            c[y][x] = "m"
    # "new" sparkle badge top right
    sx, sy = 12, 3
    for d in (-2, -1, 1, 2):
        c[sy + d][sx] = "y"
        c[sy][sx + d] = "y"
    c[sy][sx] = "w"
    add_outline(c)
    return to_image(c)


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

HEART7 = [".mm.mm.", "mmmmmmm", "mmmmmmm", ".mmmmm.", "..mmm..", "...m..."]
HEART9 = [".mmm.mmm.", "mmmmmmmmm", "mmmmmmmmm", "mmmmmmmmm", ".mmmmmmm.", "..mmmmm..", "...mmm...", "....m...."]
HEART11 = [".mmmm.mmmm.", "mmmmmmmmmmm", "mmmmmmmmmmm", "mmmmmmmmmmm", "mmmmmmmmmmm", ".mmmmmmmmm.",
           "..mmmmmmm..", "...mmmmm...", "....mmm....", ".....m....."]


def heart_shaded(rows, hi, lo, mid):
    """Recolour a one-colour heart: highlight top-left, shade lower part."""
    out = []
    n = len(rows)
    for y, row in enumerate(rows):
        line = ""
        for x, ch in enumerate(row):
            if ch == EMPTY:
                line += ch
            elif y <= 1 and 1 <= x <= 2:
                line += "w"
            elif y >= n * 0.55:
                line += lo
            else:
                line += mid
        out.append(line)
    return out


def layer(canvas_rows, rows, x0, y0):
    g = [list(r) for r in canvas_rows]
    put(g, rows, x0, y0)
    return ["".join(r) for r in g]


def empty_rows(w=16, h=16):
    return [EMPTY * w] * h


STRANGER = [
    "...GGGGGG...",
    "..GGGGGGGG..",
    ".GGGgggGGGG.",
    ".GGGGGGGgGG.",
    ".GGGGGGgGGG.",
    ".GGGGGgGGGG.",
    ".GGGGGgGGGG.",
    ".GGGGGGGGGG.",
    ".GGGGGgGGGG.",
    "..GGGGGGGG..",
    "...GGGGGG...",
]

def hs_rows():
    """Handshake 14x6: left sleeve blue, right sleeve green, clasped hands in the middle."""
    return [
        "....ssss......",
        "bbbssSssssseee",
        "bbbsSsssSssee.",
        "bbbssSsssseeee",
        "bbb.ssssss.eee",
        ".....SSSS.....",
    ]


def stage_icons():
    out = {}
    out["Stranger"] = sprite(STRANGER)
    out["Acquaintance"] = sprite(hs_rows())
    # Friend: handshake with a small heart above
    g = layer(empty_rows(14, 14), heart_shaded(HEART7, "w", "r", "m"), 3, 0)
    g = layer(g, hs_rows(), 0, 8)
    out["Friend"] = sprite(g)
    # CloseFriend: one pink heart with sparkle
    g = layer(empty_rows(14, 13), heart_shaded(HEART9, "w", "r", "m"), 2, 3)
    g = layer(g, ["..y..", ".yyy.", "..y.."], 9, 0)
    out["CloseFriend"] = sprite(g)
    # Crush: red heart with flutter marks
    g = layer(empty_rows(14, 14), heart_shaded(HEART11, "w", "R", "r"), 2, 2)
    g = layer(g, ["y", "y"], 0, 3)
    g = layer(g, ["y"], 13, 1)
    out["Crush"] = sprite(g)
    # Partner: small pink heart behind a big red heart, gold sparkle
    g = layer(empty_rows(14, 14), heart_shaded(HEART7, "w", "r", "m"), 6, 0)
    g = layer(g, heart_shaded(HEART11, "w", "R", "r"), 0, 3)
    g = layer(g, ["y"], 13, 9)
    out["Partner"] = sprite(g)
    return out


def stage_bar():
    W, H = 96, 12
    c = blank_wh(W, H)
    for y in range(H):
        for x in range(W):
            if (x in (0, W - 1)) and (y in (0, H - 1)):
                continue
            if x in (0, W - 1) or y in (0, H - 1):
                c[y][x] = "k"
            elif x in (1, W - 2) or y in (1, H - 2):
                c[y][x] = "B"
            else:
                c[y][x] = "w" if y > 2 else "G"
    seg = (W - 2) / 6
    for i in range(1, 6):
        x = round(1 + seg * i)
        for y in range(2, H - 2):
            c[y][x] = "B"
    pips = ["G", "c", "l", "y", "m", "r"]
    for i, key in enumerate(pips):
        cx = round(1 + seg * (i + 0.5)) - 1
        for dx in (0, 1):
            for dy in (0, 1):
                c[5 + dy][cx + dx] = key
    return to_image(c)


# ----------------------------------------------------------------- build

def build():
    out = []

    def w(img, rel):
        out.append(save(img, rel))

    # CHAR-004
    overlays = []
    for style in ("Spiky", "Short", "Long", "Bob", "Ponytail", "Buzz"):
        ov = hair_overlay(style)
        overlays.append(ov)
        w(ov, f"characters/player/hair/CHAR_004_Hair_{style}_Down_v01.png")
    w(hair_preview(overlays), "characters/player/hair/CHAR_004_Hair_Preview_v01.png")
    w(bald_base(), "characters/player/hair/CHAR_004_BaseHead_Down_v01.png")

    # UI-010
    w(from_rows(nine_rows(CREATE_DEPTH, "w")), "ui/menus/UI_010_CreatePanel_v01.png")
    la, ra = arrow("Left"), arrow("Right")
    w(la, "ui/menus/UI_010_Arrow_Left_v01.png")
    w(ra, "ui/menus/UI_010_Arrow_Right_v01.png")
    sw, nf = swatch_frame(), name_field()
    w(sw, "ui/menus/UI_010_ColorSwatch_Frame_v01.png")
    w(nf, "ui/menus/UI_010_NameField_v01.png")
    w(create_preview(sw, (la, ra), nf, overlays[1]), "ui/menus/UI_010_Preview_v01.png")

    # UI-013
    w(unlock_banner(), "ui/menus/UI_013_UnlockBanner_v01.png")
    w(sprite(LOCKED), "ui/menus/UI_013_Lock_Locked_v01.png")
    w(sprite(UNLOCKED), "ui/menus/UI_013_Lock_Unlocked_v01.png")
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
