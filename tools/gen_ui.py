"""UI, minigame and effect pixel art (HUD, buttons, panels, icons, rhythm, FX).

Run: python3 tools/gen_ui.py   -> writes PNGs under assets/ (see assets/SPEC.md).

Icons are hand-drawn character grids: '.' = empty, every other char is a key of
the shared palette P in tools/pixel.py. Icons are centred in 16x16 and get a 1px
outline (k by default, blue B for light buttons). Panels are 24x24 nine-slices
with 8px borders. Effects are horizontal strips built with pixel.strip().
Art direction follows assets/reference/ArtDirection_ConceptSheet_v01.png.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa: F401,F403  (P, from_rows, strip, save, ICON)

EMPTY = "."
OUTLINE = "k"


# ----------------------------------------------------------------- core helpers

def centred(rows, size=ICON):
    """Put the tight bounding box of a char grid in the middle of a size x size canvas."""
    cells = {(x, y): ch for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != EMPTY}
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    x0, y0 = min(xs), min(ys)
    bw, bh = max(xs) - x0 + 1, max(ys) - y0 + 1
    assert bw <= size - 2 and bh <= size - 2, f"sprite {bw}x{bh} leaves no room for outline"
    ox, oy = (size - bw) // 2 - x0, (size - bh) // 2 - y0
    canvas = blank(size)
    for (x, y), ch in cells.items():
        canvas[y + oy][x + ox] = ch
    return canvas


def add_outline(canvas, color=OUTLINE):
    """1px outline on empty cells that touch (4-neighbour) a filled cell."""
    h, w = len(canvas), len(canvas[0])
    ring = []
    for y in range(h):
        for x in range(w):
            if canvas[y][x] != EMPTY:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and canvas[ny][nx] != EMPTY:
                    ring.append((x, y))
                    break
    for x, y in ring:
        canvas[y][x] = color
    return canvas


def blank(size=ICON):
    return [[EMPTY] * size for _ in range(size)]


def to_image(canvas):
    rows = ["".join(r).replace(EMPTY, "_") for r in canvas]
    for row in rows:
        for ch in row:
            assert ch in P, f"{ch!r} is not a palette key"
    return from_rows(rows)


def icon(rows, outline=OUTLINE):
    canvas = add_outline(centred(rows), outline)
    return to_image(canvas)


def paint(cells, ch, size=ICON):
    """Absolute-coordinate grid with `ch` at each (x, y) in cells."""
    g = blank(size)
    for x, y in cells:
        g[y][x] = ch
    return ["".join(r) for r in g]


def shift(canvas, dy):
    h = len(canvas)
    out = blank(len(canvas[0]))
    for y in range(h):
        if 0 <= y + dy < h:
            out[y + dy] = list(canvas[y])
    return out


def recolor_rows(rows, mapping):
    return ["".join(mapping.get(ch, ch) for ch in r) for r in rows]


def disc_rows(d, fn):
    """d x d grid of a filled disc; fn(x, y) returns the char for inside pixels."""
    r = d / 2
    rows = []
    for y in range(d):
        line = ""
        for x in range(d):
            inside = (x + 0.5 - r) ** 2 + (y + 0.5 - r) ** 2 <= r * r
            line += fn(x, y) if inside else EMPTY
        rows.append(line)
    return rows


def nine_rows(depth, interior, size=24):
    """Nine-slice grid: `depth` gives the colour of each border ring (outside in), rest is interior."""
    n = size
    rows = []
    for y in range(n):
        line = ""
        for x in range(n):
            if x in (0, n - 1) and y in (0, n - 1):
                line += "_"
                continue
            d = min(x, y, n - 1 - x, n - 1 - y)
            line += depth[d] if d < len(depth) else interior
        rows.append(line)
    return rows


def stretch(rows, W, H, b=8):
    """Nine-slice stretch of a char grid with fixed b-pixel borders."""
    sw, sh = len(rows[0]), len(rows)

    def src(i, D, S):
        if i < b:
            return i
        if i >= D - b:
            return S - (D - i)
        return b + (i - b) * (S - 2 * b) // (D - 2 * b)

    return ["".join(rows[src(y, H, sh)][src(x, W, sw)] for x in range(W)) for y in range(H)]


# ----------------------------------------------------------------- HUD (16x16)

# Energy: red/orange heart-like icon (art direction update).
ENERGY_SHAPE = [
    "..hhhhh..hhhhh..",
    ".hHHhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "...hhhhhhhhhh...",
    "....hhhhhhhh....",
    ".....hhhhhh.....",
    "......hhhh......",
    ".......hh.......",
]

# Fullness: drumstick (orange meat, white bone).
DRUM = [
    "....ooooo.......",
    "...yyoooon......",
    "..yyoooooon.....",
    "..yooooooon.....",
    "..oooooooon.....",
    "..oooooooon.....",
    "..ooooooonn.....",
    "...oonnnnn......",
    "....nnnnnww.....",
    "..........ww....",
    "...........ww...",
    "............www.",
    ".............wG.",
]

# Mood: blue smiley with pink cheeks.
MOOD = [
    ".....bbbbbb.....",
    "...bcbbbbbbbb...",
    "..bcbbbbbbbbbb..",
    "..bcbkbbbbkbbb..",
    "..bbbkbbbbkbbb..",
    "..brbbbbbbbbrb..",
    "..bbkbbbbbbkbb..",
    "..bbbkkkkkkbbb..",
    "..bbbbbbbbbbbb..",
    "...bbbbbbbbbb...",
    ".....bbbbbb.....",
]

# Gold coin with a '$' (dark brown glyph for contrast on yellow).
COIN = [
    ".....wyyyyY.....",
    "...wyyyyyyyyY...",
    "..wyyyyyyyyyYY..",
    "..wyyyyyyyyyyY..",
    "..yyyyyyyyyyyY..",
    "..yyyyyyyyyyyY..",
    "..yyyyyyyyyyyY..",
    "..yyyyyyyyyyYY..",
    "..yyyyyyyyyYYY..",
    "...yyyyyYYYYY...",
    ".....YYYYYY.....",
]
DOLLAR = [  # 5 wide x 7 tall, drawn on the coin face
    "..#..",
    ".####",
    "#.#..",
    ".###.",
    "..#.#",
    "####.",
    "..#..",
]

CLOCK = [
    ".....wwwwww.....",
    "...wwwwwwwwwG...",
    "..wwwwwkwwwwwG..",
    "..wwwwwkwwwwwG..",
    "..wwwwwkwwwwwG..",
    "..wwwwwkkkkwwG..",
    "..wwwwwwwwwwGG..",
    "..wwwwwwwwwGGG..",
    "..wwwwwwwwGGGG..",
    "...GGGGGGGGGG...",
    ".....GGGGGG.....",
]

CAL = [
    ".....K....K.....",
    ".....K....K.....",
    "..rrrrrrrrrrrr..",
    "..RRRRRRRRRRRR..",
    "..wwwwwwwwwwww..",
    "..wwwwwwwwwwww..",
    "..wwgwwgwwgwww..",
    "..wwwwwwwwwwww..",
    "..wwwwwwwwwwww..",
    "..wwgwwgwwgwww..",
    "..GGGGGGGGGGGG..",
]


def panel_frame(w, h, outer="k", ring="B", inner="w"):
    rows = []
    for y in range(h):
        line = ""
        for x in range(w):
            if (x, y) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
                c = "_"
            elif x in (0, w - 1) or y in (0, h - 1):
                c = outer
            elif x in (1, w - 2) or y in (1, h - 2):
                c = ring
            else:
                c = inner
            line += c
        rows.append(line)
    return from_rows(rows)


def needbar_frame():
    rows = []
    for y in range(8):
        rows.append("".join("k" if (y in (0, 7) or x in (0, 47)) else "_" for x in range(48)))
    return from_rows(rows)


# ----------------------------------------------------------------- time control (16x16)

def _body_rows():
    g = blank(16)
    for y in range(2, 12):
        for x in range(2, 14):
            if (x, y) in ((2, 2), (13, 2), (2, 11), (13, 11)):
                continue
            g[y][x] = "G" if (y == 11 or x == 13) else "w"
    return ["".join(r) for r in g]


def time_button(glyph_cells, glyph_color):
    g = [list(r) for r in _body_rows()]
    for x, y in glyph_cells:
        g[y][x] = glyph_color
    return icon(["".join(r) for r in g], outline="B")


def pause_cells():
    return [(x, y) for y in range(5, 11) for x in (5, 6, 9, 10)]


def play_cells():
    return [(x, y) for y in range(4, 13) for x in range(6, 6 + 5 - abs(y - 8))]


def fast_cells():
    cells = []
    for y in range(5, 12):
        w = 4 - abs(y - 8)
        cells += [(x, y) for x in range(4, 4 + w)]
        cells += [(x, y) for x in range(9, 9 + w)]
    return cells


# ----------------------------------------------------------------- buttons (48x16)

# Role -> palette key. Outline is blue (B) for light buttons, per concept sheet.
BUTTON_ROLES = {
    "normal":   {"k": "B", "h": "w", "b": "w", "l": "G", "e": "B"},
    "pressed":  {"k": "B", "h": "c", "b": "b", "l": "B", "e": "B"},
    "disabled": {"k": "g", "h": "G", "b": "G", "l": "g", "e": "g"},
    "selected": {"k": "B", "h": "w", "b": "c", "l": "b", "e": "B"},
}


def button_image(role, pressed_shift=False):
    m = BUTTON_ROLES[role]
    base = (
        ["_" + "k" * 46 + "_", "k" + "h" * 46 + "k"]
        + ["k" + "b" * 46 + "k"] * 11
        + ["k" + "l" * 46 + "k", "k" + "e" * 46 + "k", "_" + "k" * 46 + "_"]
    )
    rows = recolor_rows(base, m)
    if pressed_shift:  # pressed: content moves down 1px, bottom edge drops away
        rows = ["_" * 48] + rows[:15]
    return from_rows(rows)


# ----------------------------------------------------------------- panels (24x24 nine-slice)

DIALOG_DEPTH = "kBbBBBBk"   # outer k, navy band, light-blue inner line
SHOP_DEPTH = "kBcBBBBk"     # alt: cyan inner line
RESULT_DEPTH = "kBbBBBBk"
MINI_PANEL_DEPTH = "kBbBBBBk"


def dialog_preview():
    rows = [list(r) for r in stretch(nine_rows(DIALOG_DEPTH, "w"), 160, 48)]
    for y0, length in ((16, 112), (22, 80), (28, 48)):
        for y in (y0, y0 + 1):
            for x in range(24, 24 + length):
                rows[y][x] = "K"
    return from_rows(["".join(r) for r in rows])


# ----------------------------------------------------------------- tabs / icons (16x16)

TAB_CHAR = [
    "......NNNN......",
    ".....NNNNNN.....",
    ".....NssssN.....",
    ".....NsKsKN.....",
    ".....SssssS.....",
    "......SSSS......",
    ".......ss.......",
    "..bbbbbbbbbbbb..",
    "..bbbbbbbbbbbb..",
    "..bbbbbbbbbbbb..",
    "..BBBBBBBBBBBB..",
]

TAB_BAG = [
    "......KKKK......",
    "....K......K....",
    "....K......K....",
    "..nnnnnnnnnnnn..",
    "..nnnnnnnnnnNN..",
    "..nnnnuuuunnNN..",
    "..nnnnuuuunnNN..",
    "..nnnnnnnnnnNN..",
    "..nnnnnnnnnnNN..",
    "...NNNNNNNNNN...",
]

TAB_MAP = [
    "..uuuunuuunuuu..",
    "..uuuunuuunuuu..",
    "..uuuunurunuuu..",
    "..uuuunurunuuu..",
    "..uuuunuRunuuu..",
    "..uuuunuuunuuu..",
    "..uuuunuuunuuu..",
    "..uuuunuuunuuu..",
    "..nnnnnnnnnnnn..",
]

# Cup (rows 3..10 of WORK) is reused by the Work tab (with steam) and nothing else.
WORK = [
    ".....G..G.......",
    "......G..G......",
    ".....G..G.......",
    "...wwwwwwwww....",
    "....nnnnnnn.....",
    "...wwwwwwwwGww..",
    "...wwwwwwwwG..w.",
    "...wwwwwwwwG..w.",
    "....wwwwwwG.ww..",
    ".....GGGGG......",
    "..gggggggggggg..",
]


def heart_rows(variant):
    shape = [
        ".." + "h" * 5 + ".." + "h" * 5 + "..",
        "." + "hHH" + "h" * 11 + ".",
        "." + "h" * 14 + ".",
        ".." + "h" * 12 + "..",
        ".." + "h" * 12 + "..",
        "..." + "h" * 10 + "...",
        "...." + "h" * 8 + "....",
        "....." + "h" * 6 + ".....",
        "......" + "h" * 4 + "......",
        "......." + "h" * 2 + ".......",
    ]
    out = []
    for y, row in enumerate(shape):
        line = ""
        for x, ch in enumerate(row):
            if ch == "H":
                c = "w"
            elif ch == "h":
                low = y >= 6
                if variant == "full":
                    c = "R" if low else "r"
                elif variant == "pink":
                    c = "r" if low else "m"
                elif variant == "half":
                    c = ("r" if x < 8 else "G") if not low else ("R" if x < 8 else "g")
                else:  # empty
                    c = "g" if low else "G"
            else:
                c = EMPTY
            line += c
        out.append(line)
    return out


def energy_rows():
    """Red/orange heart-like Energy icon: orange upper lobes, red lower body, pale highlight."""
    rows = heart_rows("full")
    return [("".join("o" if (ch == "r" and y < 6) else ("y" if ch == "w" else ch) for ch in row))
            for y, row in enumerate(rows)]


def coin_rows():
    """Gold coin with a dark-brown '$' painted on the face."""
    g = [list(r) for r in COIN]
    for r, row in enumerate(DOLLAR):
        for c, ch in enumerate(row):
            if ch == "#":
                g[3 + r][4 + c] = "N"
    return ["".join(r) for r in g]


WARNING_TRI_H = 13


def warning_rows():
    rows = [["."] * 16 for _ in range(WARNING_TRI_H)]
    for y in range(WARNING_TRI_H):
        half = max(0, round((y + 1) * 6 / WARNING_TRI_H))
        left, right = 6 - half, 7 + half
        for x in range(left, right + 1):
            rows[y][x] = "Y" if (x == right or y == WARNING_TRI_H - 1) else "y"
    for y in list(range(4, 9)) + [10, 11]:
        for x in (6, 7):
            rows[y][x] = "k"
    return ["".join(r) for r in rows]


def info_rows():
    def f(x, y):
        if x in (5, 6) and (2 <= y <= 3 or 5 <= y <= 9):
            return "w"
        if x <= 2 and y <= 3:
            return "c"
        if x + y >= 17:
            return "B"
        return "b"
    return disc_rows(12, f)


def saveok_rows():
    check = {(3, 6), (4, 7), (5, 8), (6, 7), (7, 6), (8, 5), (9, 4)}
    thick = check | {(x, y + 1) for x, y in check}

    def f(x, y):
        if (x, y) in thick:
            return "w"
        if x + y >= 17:
            return "E"
        return "e"
    return disc_rows(12, f)


UNLOCK = [
    ".....GGGGGG.....",
    ".....G....G.....",
    ".....G....G.....",
    ".....G..........",
    "...yyyyyyyyyy...",
    "...yyyyyyyyyY...",
    "...yyyykkyyyY...",
    "...yyyykkyyyY...",
    "...yyyyyyyyyY...",
    "...YYYYYYYYYY...",
]


def gear_rows():
    rows = []
    for y in range(16):
        line = ""
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            d = math.hypot(dx, dy)
            tooth = False
            for k in range(8):
                ang = k * math.pi / 4
                ux, uy = math.cos(ang), math.sin(ang)
                along = dx * ux + dy * uy
                perp = abs(-dx * uy + dy * ux)
                if 3.2 <= along <= 6.6 and perp <= 1.25:
                    tooth = True
            if d <= 1.9:
                c = EMPTY
            elif d <= 4.7:
                c = "w" if dx + dy < -2.5 else ("g" if dx + dy > 2.5 else "G")
            elif tooth:
                c = "G"
            else:
                c = EMPTY
            line += c
        rows.append(line)
    return rows


def bubble_rows(glyph):
    g = blank(16)
    for y in range(2, 11):
        for x in range(1, 14):
            if (x, y) in ((1, 2), (13, 2), (1, 10), (13, 10)):
                continue
            g[y][x] = "G" if y == 10 else "w"
    for x, y in ((3, 11), (4, 11), (5, 11), (3, 12), (4, 12), (3, 13)):
        g[y][x] = "w"
    for (x, y), ch in glyph.items():
        g[y][x] = ch
    return ["".join(r) for r in g]


def interact_bubble():
    g = {}
    for y in range(3, 7):
        for x in (7, 8):
            g[(x, y)] = "r"
    for y in (8, 9):
        for x in (7, 8):
            g[(x, y)] = "r"
    return icon(bubble_rows(g))


def talk_bubble():
    g = {}
    for y in (5, 6):
        for x in (4, 5, 7, 8, 10, 11):
            g[(x, y)] = "K"
    return icon(bubble_rows(g))


def speaker_rows(on):
    c = blank(16)
    for y in range(5, 9):
        for x in range(2, 5):
            c[y][x] = "G"
    for x, (y0, y1) in zip((5, 6, 7), ((4, 9), (3, 10), (2, 11))):
        for y in range(y0, y1 + 1):
            c[y][x] = "g" if x == 7 else "G"
    if on:
        for y in (5, 6, 7, 8):
            c[y][10] = "c"
        for y in range(3, 11):
            c[y][12] = "c"
    else:
        for i in range(5):
            c[4 + i][9 + i] = "r"
            c[4 + i][13 - i] = "r"
    return ["".join(r) for r in c]


def floppy_rows(error=False):
    g = [["b"] * 12 for _ in range(12)]
    for y in range(0, 4):
        for x in range(2, 9):
            g[y][x] = "G"
    for y in range(0, 3):
        for x in (6, 7):
            g[y][x] = "K"
    for y in range(6, 11):
        for x in range(2, 10):
            g[y][x] = "w"
    for x in range(12):
        g[11][x] = "B"
    for y in range(12):
        g[y][11] = "B"
    if error:
        for i in range(5):
            g[6 + i][3 + i] = "r"
            g[6 + i][7 - i] = "r"
    return ["".join(r) for r in g]


LOAD_ROWS = [
    ".....cccc.....",
    ".....cccc.....",
    ".....cccc.....",
    ".....cccc.....",
    ".....cccc.....",
    "..cccccccccc..",
    "...cccccccc...",
    "....cccccc....",
    "..............",
    "bbbbbbbbbbbbbb",
    "bbbbbbbbbbbbbb",
]


# ----------------------------------------------------------------- rhythm cues / judge

ARROW_UP = [(5, 2), (6, 2), (4, 3), (5, 3), (6, 3), (7, 3), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4),
            (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5),
            (5, 6), (6, 6), (5, 7), (6, 7), (5, 8), (6, 8), (5, 9), (6, 9)]


def _rotate(cells, turns):
    """Rotate arrow pixels on the 12x12 disc: turns quarter-turns clockwise."""
    out = cells
    for _ in range(turns):
        out = [(11 - y, x) for x, y in out]
    return out


def rhythm_cue(body, shade, turns):
    arrow = set(_rotate(ARROW_UP, turns))

    def f(x, y):
        if (x, y) in arrow:
            return "w"
        if x + y >= 17:
            return shade
        return body
    return icon(disc_rows(12, f))


FONT3x5 = {
    "P": ["111", "101", "111", "100", "100"],
    "E": ["111", "100", "110", "100", "111"],
    "R": ["110", "101", "110", "101", "101"],
    "F": ["111", "100", "110", "100", "100"],
    "C": ["011", "100", "100", "100", "011"],
    "T": ["111", "010", "010", "010", "010"],
    "G": ["011", "100", "101", "101", "011"],
    "O": ["111", "101", "101", "101", "111"],
    "D": ["110", "101", "101", "101", "110"],
    "M": ["10001", "11011", "10101", "10001", "10001"],
    "I": ["111", "010", "010", "010", "111"],
    "S": ["011", "100", "010", "001", "110"],
}


JUDGE_W, JUDGE_H = 40, 12   # wide enough for PERFECT with 2px letter gaps


def judge_word(text, fill, bottom):
    canvas = blank_wh(JUDGE_W, JUDGE_H)
    gap = 2                                    # 2px gap between glyphs (outline keeps letters apart)
    total = sum(len(FONT3x5[ch][0]) for ch in text) + gap * (len(text) - 1)
    x = (JUDGE_W - total) // 2
    y0 = 3
    cells = {}
    for ch in text:
        for ry, row in enumerate(FONT3x5[ch]):
            for rx, bit in enumerate(row):
                if bit == "1":
                    cells[(x + rx, y0 + ry)] = fill if ry < 4 else bottom
        x += len(FONT3x5[ch][0]) + gap
    for (x, y), c in cells.items():
        canvas[y][x] = c
    add_outline(canvas)
    return to_image(canvas)


def blank_wh(w, h):
    return [[EMPTY] * w for _ in range(h)]


def hitzone():
    rows = []
    for y in range(24):
        line = ""
        for x in range(24):
            d = math.hypot(x + 0.5 - 12, y + 0.5 - 12)
            if d < 2.0:
                c = "y"
            elif 8.5 <= d < 10.5:
                c = "w"
            elif 7.5 <= d < 8.5 or 10.5 <= d < 11.5:
                c = "k"
            else:
                c = "_"
            line += c
        rows.append(line)
    return from_rows(rows)


def track():
    rows = []
    for y in range(24):
        line = ""
        for x in range(128):
            if y in (0, 23):
                c = "k"
            elif y in (1, 22):
                c = "g"
            elif y in (11, 12):
                c = "G"
            elif x % 16 == 8 and 4 <= y <= 19:
                c = "g"
            else:
                c = "K"
            line += c
        rows.append(line)
    return from_rows(rows)


# ----------------------------------------------------------------- effects

def interact_pulse_frame(dy):
    c = blank(16)
    for y in list(range(5, 11)) + [12, 13]:
        for x in (7, 8):
            c[y][x] = "r"
    add_outline(c)
    return to_image(shift(c, dy))


def coin_pop_frame(rx):
    c = blank(16)
    for y in range(16):
        for x in range(16):
            px, py = x + 0.5 - 8, y + 0.5 - 8
            if (px / rx) ** 2 + (py / 5.0) ** 2 <= 1.0:
                c[y][x] = "Y" if px > 0 else "y"
                if rx >= 5 and px < -2 and py < -1:
                    c[y][x] = "w"
    add_outline(c)
    return to_image(c)


def sparkle_frame(arm, centre="w", ray=None, diag=None, edge=None, inner=None):
    """Cross sparkle. `inner` colours the first ray pixel, `edge` the outermost one."""
    c = blank(16)
    cx = cy = 8
    if diag:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            c[cy + dy][cx + dx] = diag
    if ray:
        for i in range(1, arm + 1):
            col = edge if (edge and i == arm and arm > 1) else (inner if (inner and i == 1) else ray)
            for dx, dy in ((i, 0), (-i, 0), (0, i), (0, -i)):
                c[cy + dy][cx + dx] = col
    if centre:
        c[cy][cx] = centre
    return to_image(c)


def lowneed_frame(body):
    c = blank(16)
    for y in range(16):
        for x in range(16):
            if (x + 0.5 - 8) ** 2 + (y + 0.5 - 8) ** 2 <= 36:
                c[y][x] = body
    for y in list(range(4, 9)) + [10, 11]:
        for x in (7, 8):
            c[y][x] = "w"
    add_outline(c)
    return to_image(c)


# ----------------------------------------------------------------- build

def build():
    out = []

    def put(img, rel):
        out.append(save(img, rel))

    # HUD
    put(icon(energy_rows()), "ui/hud/UI_001_Need_Energy_v01.png")
    put(icon(DRUM), "ui/hud/UI_001_Need_Fullness_v01.png")
    put(icon(MOOD), "ui/hud/UI_001_Need_Mood_v01.png")
    put(icon(coin_rows()), "ui/hud/UI_002_Money_v01.png")
    put(icon(CLOCK), "ui/hud/UI_003_Clock_v01.png")
    put(icon(CAL), "ui/hud/UI_003_Calendar_v01.png")
    put(panel_frame(64, 20, outer="k", ring="B", inner="w"), "ui/hud/UI_003_ClockFrame_v01.png")
    put(needbar_frame(), "ui/hud/UI_001_NeedBar_Frame_v01.png")
    put(from_rows(["w"] * 6), "ui/hud/UI_001_NeedBar_Fill_v01.png")

    # Buttons
    put(time_button(pause_cells(), "B"), "ui/buttons/UI_004_TimeControl_Pause_v01.png")
    put(time_button(play_cells(), "e"), "ui/buttons/UI_004_TimeControl_Normal_v01.png")
    put(time_button(fast_cells(), "e"), "ui/buttons/UI_004_TimeControl_Fast_v01.png")
    put(button_image("normal"), "ui/buttons/UI_006_Button_Normal_v01.png")
    put(button_image("pressed", pressed_shift=True), "ui/buttons/UI_006_Button_Pressed_v01.png")
    put(button_image("disabled"), "ui/buttons/UI_006_Button_Disabled_v01.png")
    put(button_image("selected"), "ui/buttons/UI_006_Button_Selected_v01.png")

    # Panels
    put(from_rows(nine_rows(DIALOG_DEPTH, "w")), "ui/panels/UI_005_DialogBox_v01.png")
    put(dialog_preview(), "ui/panels/UI_005_DialogBox_Preview_v01.png")
    put(from_rows(nine_rows(SHOP_DEPTH, "w")), "ui/panels/UI_009_ShopPanel_v01.png")

    # Tabs
    put(icon(TAB_CHAR), "ui/icons/UI_007_Tab_Character_v01.png")
    put(icon(TAB_BAG), "ui/icons/UI_007_Tab_Bag_v01.png")
    put(icon(recolor_rows(TAB_MAP, {"u": "l", "n": "e"})), "ui/icons/UI_007_Tab_Map_v01.png")
    put(icon(WORK), "ui/icons/UI_007_Tab_Work_v01.png")
    put(icon(heart_rows("pink")), "ui/icons/UI_007_Tab_Relationship_v01.png")
    put(icon(gear_rows()), "ui/icons/UI_007_Tab_Settings_v01.png")

    # Notices
    put(icon(warning_rows()), "ui/icons/UI_008_Notice_Warning_v01.png")
    put(icon(info_rows()), "ui/icons/UI_008_Notice_Info_v01.png")
    put(icon(UNLOCK), "ui/icons/UI_008_Notice_Unlock_v01.png")
    put(icon(saveok_rows()), "ui/icons/UI_008_Notice_SaveOk_v01.png")

    # Save / load
    put(icon(floppy_rows()), "ui/icons/UI_012_Save_v01.png")
    put(icon(LOAD_ROWS), "ui/icons/UI_012_Load_v01.png")
    put(icon(floppy_rows(error=True)), "ui/icons/UI_012_SaveError_v01.png")

    # Hearts
    put(icon(heart_rows("full")), "ui/icons/UI_011_Heart_Full_v01.png")
    put(icon(heart_rows("half")), "ui/icons/UI_011_Heart_Half_v01.png")
    put(icon(heart_rows("empty")), "ui/icons/UI_011_Heart_Empty_v01.png")

    # Object hints
    put(interact_bubble(), "ui/icons/OBJ_001_Interact_v01.png")
    put(talk_bubble(), "ui/icons/OBJ_001_Talk_v01.png")

    # Audio
    put(icon(speaker_rows(True)), "ui/icons/AUDIO_001_Volume_On_v01.png")
    put(icon(speaker_rows(False)), "ui/icons/AUDIO_001_Volume_Off_v01.png")

    # Minigames (rhythm)
    put(from_rows(nine_rows(MINI_PANEL_DEPTH, "w")), "minigames/rhythm/MINI_001_Panel_v01.png")
    put(rhythm_cue("e", "E", 0), "minigames/rhythm/MINI_002_RhythmCue_Tap_v01.png")
    put(rhythm_cue("b", "B", 1), "minigames/rhythm/MINI_002_RhythmCue_Hold_v01.png")
    put(track(), "minigames/rhythm/MINI_003_Track_v01.png")
    put(hitzone(), "minigames/rhythm/MINI_003_HitZone_v01.png")
    put(judge_word("PERFECT", "y", "o"), "minigames/rhythm/MINI_004_Judge_Perfect_v01.png")
    put(judge_word("GOOD", "l", "e"), "minigames/rhythm/MINI_004_Judge_Good_v01.png")
    put(judge_word("MISS", "r", "R"), "minigames/rhythm/MINI_004_Judge_Miss_v01.png")
    put(from_rows(nine_rows(RESULT_DEPTH, "w")), "minigames/rhythm/MINI_005_ResultPanel_v01.png")

    # Effects
    put(strip([interact_pulse_frame(dy) for dy in (0, -2, -3, -1)]),
        "effects/interaction/FX_001_InteractPulse_v01.png")
    put(strip([coin_pop_frame(rx) for rx in (5, 3, 1.2, 3)]),
        "effects/rewards/FX_002_CoinPop_v01.png")
    base_heart = add_outline(centred(heart_rows("full")))
    put(strip([to_image(shift(base_heart, dy)) for dy in (2, 1, 0, -1)]),
        "effects/rewards/FX_003_HeartUp_v01.png")
    # small -> large -> medium -> fade; every frame has a visible cross
    put(strip([sparkle_frame(2, "w", "y", None, "Y", "w"),
               sparkle_frame(5, "w", "y", "y", "Y", "w"),
               sparkle_frame(3, "w", "y", "Y", "Y"),
               sparkle_frame(2, None, "Y", None)]),
        "effects/unlocks/FX_004_Sparkle_v01.png")
    put(strip([lowneed_frame("r"), lowneed_frame("R")]),
        "effects/interaction/FX_005_LowNeed_v01.png")
    return out


if __name__ == "__main__":
    paths = build()
    print(f"wrote {len(paths)} files")
