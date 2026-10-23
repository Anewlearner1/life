"""UI, minigame and effect pixel art (HUD, buttons, panels, icons, rhythm, FX) - art direction v2.

Run: python3 tools/gen_ui.py   -> writes PNGs under assets/ (see assets/SPEC.md).

Everything is redrawn on a clean pixel grid, matching the look of the concept sheet
(assets/reference/ArtDirection_ConceptSheet_v01.png, sections 05-08): navy-blue framed panels with
cream interiors and softly rounded corners, glossy blue speed buttons, round coloured arrow cues,
chunky outlined judge words, red heart / orange bread / blue-pink smiley need icons, gold $ coin.
Colours below are sampled from the concept (see UP). File names and pixel sizes are unchanged.

Toolkit (also imported by gen_extras.py): grid(), shade_cells(), outline_img(), rrect_panel(),
nine_stretch(), disc_cells(), heart_cells(), ...
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image  # noqa: E402
from pixel import P, from_rows, save, ASSETS, ICON  # noqa: E402,F401

EMPTY = "."


def H(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


# ---------------------------------------------------------------- palette (sampled from the concept sheet)
UP = {
    "out": H("#1a2d4a"),      # navy outline
    "outw": H("#4a2a1e"),     # warm dark outline (bread, coin, bag...)
    "navy": H("#2a4862"),     # panel frame navy
    "navy2": H("#1e3b70"),
    "navyd": H("#142d5e"),
    "blue": H("#3675af"),
    "blue2": H("#5187c5"),
    "azure": H("#1d99de"),
    "sky": H("#73cef5"),
    "sky2": H("#8ddaf6"),
    "ice": H("#cde1f3"),
    "ice2": H("#e1effa"),
    "teal": H("#0ea6c9"),
    "teald": H("#0d89ae"),
    "tealL": H("#63cae1"),
    "cream": H("#fdf7e8"),
    "creamh": H("#fffdf4"),
    "creams": H("#ecdcb8"),
    "creamd": H("#d9c79c"),
    "white": H("#f8fafa"),
    "snow": H("#eff6f7"),
    "mist": H("#cad9e3"),
    "fog": H("#a0c0d7"),
    "fogd": H("#80a4bf"),
    "gray": H("#999991"),
    "grayl": H("#c9c2be"),
    "grayd": H("#6b6c6c"),
    "grayk": H("#535354"),
    "gold": H("#fdc72d"),
    "goldl": H("#fde88a"),
    "goldd": H("#ce9134"),
    "orange": H("#e8872f"),
    "orangel": H("#f5b25e"),
    "oranged": H("#b4571f"),
    "red": H("#d63a2c"),
    "redl": H("#f0705a"),
    "redd": H("#8f2220"),
    "pink": H("#ec80ac"),
    "pinkl": H("#f7aecd"),
    "pinkd": H("#c24f86"),
    "green": H("#3fb066"),
    "greenl": H("#7fdc9a"),
    "greend": H("#136f43"),
    "lime": H("#9fbf43"),
    "limel": H("#d2ea8a"),
    "purple": H("#7a3fd0"),
    "purplel": H("#b080f4"),
    "purpled": H("#52209d"),
    "brown": H("#9d6949"),
    "brownl": H("#c9936a"),
    "brownd": H("#5f3a2c"),
    "skin": H("#f3c9a0"),
    "skind": H("#d5a07a"),
    "hair": H("#9d5a36"),
    "hairl": H("#c07a4c"),
    "leaf": H("#7ba14c"),
    "leafd": H("#2f5c32"),
    "ink": H("#14263f"),
    "greeno": H("#0c3a22"),
    "redo": H("#4a0f12"),
}


def new(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def grid(rows, legend, w=None, h=None, ox=0, oy=0):
    """Char grid -> RGBA image. '.' is empty; legend maps char -> UP key (or an rgba tuple)."""
    w = w or max(len(r) for r in rows)
    h = h or len(rows)
    im = new(w, h)
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            c = legend[ch]
            px[x + ox, y + oy] = UP[c] if isinstance(c, str) else c
    return im


def put(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), UP[c] if isinstance(c, str) else c)


def cells_of(im):
    px = im.load()
    return {(x, y) for y in range(im.height) for x in range(im.width) if px[x, y][3] > 0}


def paste(dst, src, x, y):
    dst.alpha_composite(src, (x, y))
    return dst


def outline_img(im, color="out", diag=False):
    """1px outline on empty pixels that touch a filled one (4-neighbour, optionally 8)."""
    col = UP[color] if isinstance(color, str) else color
    px = im.load()
    w, h = im.size
    ring = []
    nb = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diag:
        nb += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                continue
            for dx, dy in nb:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3]:
                    ring.append((x, y))
                    break
    for x, y in ring:
        px[x, y] = col
    return im


# ---------------------------------------------------------------- shapes
def disc_cells(cx, cy, r):
    return {(x, y) for y in range(int(cy - r - 2), int(cy + r + 3)) for x in range(int(cx - r - 2), int(cx + r + 3))
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r}


def ellipse_cells(cx, cy, rx, ry):
    return {(x, y) for y in range(int(cy - ry - 2), int(cy + ry + 3)) for x in range(int(cx - rx - 2), int(cx + rx + 3))
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}


def rect_cells(x0, y0, w, h):
    return {(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)}


def rr_inside(x, y, w, h, r):
    """Is pixel (x, y) inside a w x h rounded rectangle with corner radius r?"""
    cx = min(max(x + 0.5, r), w - r)
    cy = min(max(y + 0.5, r), h - r)
    return (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r + 0.15


def rr_cells(x0, y0, w, h, r):
    return {(x0 + x, y0 + y) for y in range(h) for x in range(w) if rr_inside(x, y, w, h, r)}


def cells_from_rows(rows, ch="X", ox=0, oy=0):
    return {(x + ox, y + oy) for y, row in enumerate(rows) for x, c in enumerate(row) if c == ch}


def shade_cells(im, cells, base, light, dark, deep=False):
    """Fill cells with base colour; top/left rim pixels light, bottom/right rim pixels dark."""
    for (x, y) in cells:
        lit = (x - 1, y) not in cells or (x, y - 1) not in cells
        shd = (x + 1, y) not in cells or (x, y + 1) not in cells
        if deep and (x + 1, y + 1) not in cells:
            shd = True
        c = base
        if shd and not lit:
            c = dark
        elif lit and not shd:
            c = light
        put(im, x, y, c)
    return im


def fill_cells(im, cells, c):
    for (x, y) in cells:
        put(im, x, y, c)
    return im


def vgrad(c0, c1, t):
    a, b = UP[c0] if isinstance(c0, str) else c0, UP[c1] if isinstance(c1, str) else c1
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


HEART13 = [
    "..XXX...XXX..",
    ".XXXXX.XXXXX.",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    ".XXXXXXXXXXX.",
    "..XXXXXXXXX..",
    "...XXXXXXX...",
    "....XXXXX....",
    ".....XXX.....",
    "......X......",
]
HEART11 = [
    ".XXX...XXX.",
    "XXXXX.XXXXX",
    "XXXXXXXXXXX",
    "XXXXXXXXXXX",
    ".XXXXXXXXX.",
    "..XXXXXXX..",
    "...XXXXX...",
    "....XXX....",
    ".....X.....",
]
HEART9 = [
    ".XX...XX.",
    "XXXX.XXXX",
    "XXXXXXXXX",
    "XXXXXXXXX",
    ".XXXXXXX.",
    "..XXXXX..",
    "...XXX...",
    "....X....",
]
HEART7 = [
    ".XX.XX.",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    "...X...",
]


def heart_img(rows, base="red", light="redl", dark="redd", outline="outw", size=16, hl=True, gloss=None):
    cells = cells_from_rows(rows)
    w, h = max(x for x, _ in cells) + 1, max(y for _, y in cells) + 1
    ox, oy = (size - w) // 2, (size - h) // 2 + (0 if h >= 10 else 0)
    cells = {(x + ox, y + oy) for x, y in cells}
    im = new(size, size)
    shade_cells(im, cells, base, light, dark, deep=True)
    if hl:
        hx, hy = ox + 2, oy + 1
        for dx, dy in (gloss or ((0, 0), (-1, 1), (0, 1))):
            if (hx + dx, hy + dy) in cells:
                put(im, hx + dx, hy + dy, "white")
    return outline_img(im, outline)


# ---------------------------------------------------------------- panels
def layered_panel(w, h, r, layers):
    """Rounded multi-ring panel. layers: [(inset, colour | (top_left, bottom_right) | fn(x, y))] outside-in."""
    im = new(w, h)
    px = im.load()
    for inset, col in layers:
        rr = max(r - inset, 0.5)
        iw, ih = w - 2 * inset, h - 2 * inset
        for y in range(ih):
            for x in range(iw):
                if not rr_inside(x, y, iw, ih, rr):
                    continue
                gx, gy = x + inset, y + inset
                if callable(col):
                    c = col(gx, gy)
                elif isinstance(col, tuple) and len(col) == 2 and isinstance(col[0], str):
                    tl, br = col
                    c = br if (gx - inset >= iw - 1 - 0 or gy - inset >= ih - 1) else tl
                else:
                    c = col
                px[gx, gy] = UP[c] if isinstance(c, str) else c
    return im


def frame24(frame="navy", line="sky", interior="cream", thick=3):
    """24x24 nine-slice panel (8px borders): navy frame, light inner line, cream interior."""
    size = 24
    cream_fn = lambda gx, gy: UP["cream"]  # noqa: E731
    layers = [(0, "out"), (1, frame), (1 + thick, line), (2 + thick, "out" if False else interior)]
    im = layered_panel(size, size, 5, layers)
    px = im.load()
    # soft top highlight on the frame, darker bottom edge
    for x in range(3, size - 3):
        px[x, 1] = UP["blue2"] if frame == "navy" else px[x, 1]
        px[x, size - 2] = UP["navyd"]
    for y in range(3, size - 3):
        px[1, y] = UP["blue"] if frame == "navy" else px[1, y]
        px[size - 2, y] = UP["navyd"]
    # interior inner shade (top + left row) to give the cream a recessed feel
    ix0, ix1 = 2 + thick, size - 3 - thick
    for i in range(ix0, ix1 + 1):
        px[i, ix0] = UP["creams"]
        px[ix0, i] = UP["creams"]
    return im


def dialog24():
    """24x24 dialogue box: thin navy outline, cream interior, soft rounded corners (as the concept)."""
    size = 24
    layers = [(0, "out"), (1, "creamh"), (2, "cream")]
    im = layered_panel(size, size, 5, layers)
    px = im.load()
    for x in range(3, size - 3):
        px[x, size - 2] = UP["creams"]
        px[x, size - 3] = UP["creams"]
    for y in range(3, size - 3):
        px[size - 2, y] = UP["creams"]
    return im


def nine_stretch(src, W, H, b=8):
    """Nine-slice stretch of an RGBA image with fixed b-pixel borders (nearest-neighbour)."""
    sw, sh = src.size
    out = new(W, H)
    sp, op = src.load(), out.load()

    def m(i, D, S):
        if i < b:
            return i
        if i >= D - b:
            return S - (D - i)
        return b + (i - b) * (S - 2 * b) // (D - 2 * b)

    for y in range(H):
        for x in range(W):
            op[x, y] = sp[m(x, W, sw), m(y, H, sh)]
    return out


# ---------------------------------------------------------------- legacy char-grid helpers (gen_extras MINI-006 still uses these)
def add_outline(canvas, color="k"):
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


def blank_wh(w, h):
    return [[EMPTY] * w for _ in range(h)]


def to_image(canvas):
    rows = ["".join(r).replace(EMPTY, "_") for r in canvas]
    for row in rows:
        for ch in row:
            assert ch in P, f"{ch!r} is not a palette key"
    return from_rows(rows)


# ================================================================= HUD (16x16)
def need_energy():
    """Red heart (stamina)."""
    return heart_img(HEART13, "red", "redl", "redd", "outw")


def need_fullness():
    """Orange bread loaf (hunger)."""
    im = new(16, 16)
    body = ellipse_cells(8, 8.6, 6.5, 4.4) | rect_cells(3, 8, 10, 3)
    body = {(x, y) for (x, y) in body if 3 <= y <= 12}
    shade_cells(im, body, "orange", "orangel", "oranged", deep=True)
    # scoring slashes
    for sx in (4, 7, 10):
        for k, (dx, dy) in enumerate(((0, 0), (1, 0), (1, 1), (2, 1))):
            x, y = sx + dx, 5 + dy
            if (x, y) in body:
                put(im, x, y, "goldl")
        for dx, dy in ((0, 1), (1, 2)):
            if (sx + dx, 5 + dy) in body:
                put(im, sx + dx, 5 + dy, "oranged")
    return outline_img(im, "outw")


def need_mood():
    """Blue smiley with pink cheeks (mood)."""
    im = new(16, 16)
    body = disc_cells(8, 8, 6.4)
    shade_cells(im, body, "blue", "sky", "navy2", deep=True)
    for x, y in ((5, 6), (5, 7), (10, 6), (10, 7)):
        put(im, x, y, "ink")
    for x, y in ((3, 8), (4, 8), (11, 8), (12, 8)):
        put(im, x, y, "pink")
    for x, y in ((5, 10), (6, 11), (7, 11), (8, 11), (9, 11), (10, 10)):
        put(im, x, y, "white")
    for x, y in ((4, 3), (5, 2), (4, 4)):
        put(im, x, y, "sky2")
    return outline_img(im, "out")


DOLLAR = [
    "..X..",
    ".XXXX",
    "X.X..",
    ".XXX.",
    "..XX.",
    "..X.X",
    "XXXX.",
    "..X..",
]


def coin(size=16, d=13.6):
    im = new(size, size)
    c = size / 2
    body = disc_cells(c, c, d / 2)
    shade_cells(im, body, "gold", "goldl", "goldd", deep=True)
    gx, gy = int(c) - 2, int(c) - 4
    for (x, y) in cells_from_rows(DOLLAR):
        put(im, gx + x, gy + y, "white")
    return outline_img(im, "outw")


def clock_icon():
    """Alarm clock: red body, white face, bells and feet."""
    im = new(16, 16)
    body = disc_cells(8, 9, 6.2)
    shade_cells(im, body, "red", "redl", "redd", deep=True)
    fill_cells(im, disc_cells(8, 9, 4.3), "cream")
    for (x, y) in disc_cells(8, 9, 4.3):
        if (x + y) > 18:
            put(im, x, y, "creams")
    # bells
    for bx in (2, 11):
        fill_cells(im, rect_cells(bx, 1, 3, 2), "gold")
        put(im, bx, 1, "goldl")
        put(im, bx + 2, 2, "goldd")
    # feet
    for x, y in ((4, 15), (11, 15)):
        put(im, x, y, "redd")
    # hands + ticks
    for y in range(6, 10):
        put(im, 8, y, "ink")
    for x in (9, 10):
        put(im, x, 9, "ink")
    put(im, 8, 9, "red")
    put(im, 8, 6 - 0, "ink")
    for x, y in ((8, 5), (11, 9), (8, 12), (5, 9)):
        if (x, y) in disc_cells(8, 9, 4.3):
            put(im, x, y, "grayl")
    return outline_img(im, "outw")


def calendar_icon():
    im = new(16, 16)
    page = rect_cells(2, 3, 12, 11)
    shade_cells(im, page, "cream", "white", "creams")
    fill_cells(im, rect_cells(2, 3, 12, 3), "red")
    for x in range(2, 14):
        put(im, x, 3, "redl")
    for x in range(2, 14):
        put(im, x, 5, "redd")
    for x in (4, 11):
        for y in (1, 2, 3):
            put(im, x, y, "grayk" if y < 3 else "white")
    for gy in (8, 11):
        for gx in (4, 7, 10):
            fill_cells(im, rect_cells(gx, gy, 2, 2), "blue" if (gx, gy) != (10, 11) else "red")
    return outline_img(im, "out")


def clock_frame():
    """64x20 clock / date panel: pale-blue gradient with a navy outline (concept 'time & date' panel)."""
    W, Hh = 64, 20
    layers = [
        (0, "out"),
        (1, lambda gx, gy: UP["white"] if (gy == 1 or gx == 1) else UP["navy2"] if False else UP["mist"]),
        (2, lambda gx, gy: vgrad("ice2", "ice", (gy - 2) / (Hh - 4))),
    ]
    im = layered_panel(W, Hh, 4, layers)
    px = im.load()
    for x in range(3, W - 3):
        px[x, Hh - 2] = UP["fog"]
    return im


def needbar_frame():
    """48x8 gauge frame (interior transparent; the fill is drawn by code underneath/above)."""
    W, Hh = 48, 8
    im = new(W, Hh)
    px = im.load()
    for y in range(Hh):
        for x in range(W):
            if not rr_inside(x, y, W, Hh, 3):
                continue
            edge = x in (0, W - 1) or y in (0, Hh - 1) or not rr_inside(x - 1, y - 1, W - 2, Hh - 2, 2.2) if (0 < x < W - 1 and 0 < y < Hh - 1) else True
            if edge:
                px[x, y] = UP["out"]
    return im


def needbar_fill():
    """1x6 vertical gradient (white -> grey) so the per-need tint gets a glossy top and darker base."""
    im = new(1, 6)
    for y, v in enumerate((255, 255, 238, 222, 204, 186)):
        im.putpixel((0, y), (v, v, v, 255))
    return im


# ================================================================= time controls (16x16), glossy blue
def time_button(kind):
    """Glossy blue rounded button (14x14 body + outline) with a white glyph."""
    im = new(16, 16)
    px = im.load()
    for y in range(14):
        for x in range(14):
            if not rr_inside(x, y, 14, 14, 4):
                continue
            t = y / 13
            px[x + 1, y + 1] = vgrad("sky", "azure", t * 2) if t < 0.5 else vgrad("azure", "navy2", (t - 0.5) * 2)
    for y in range(2, 6):                       # gloss band
        for x in range(3, 13):
            if rr_inside(x - 2, y - 2, 10, 5, 2.5):
                a = px[x, y]
                px[x, y] = tuple(min(255, int(a[i] + (255 - a[i]) * 0.32)) for i in range(3)) + (255,)
    glyph = new(16, 16)
    g = glyph.load()
    if kind == "pause":
        for y in range(4, 12):
            for x in (5, 6, 9, 10):
                g[x, y] = UP["white"]
    elif kind == "play":
        for i in range(6):
            for y in range(4 + i, 12 - i):
                if 4 + i < 12 - i:
                    g[5 + i, y] = UP["white"]
    else:  # fast: two triangles
        for off in (3, 8):
            for i in range(4):
                for y in range(5 + i, 11 - i):
                    if 5 + i < 11 - i:
                        g[off + i, y] = UP["white"]
    sh = new(16, 16)
    sp = sh.load()
    for (x, y) in cells_of(glyph):
        if y + 1 < 16:
            sp[x, y + 1] = UP["navy2"]
    paste(im, sh, 0, 0)
    paste(im, glyph, 0, 0)
    return outline_img(im, "out")


# ================================================================= buttons (48x16, nine-slice 4px)
def button_image(role):
    W, Hh = 48, 16
    if role == "normal":
        layers = [(0, "out"),
                  (1, lambda gx, gy: UP["white"] if gy <= 2 else UP["mist"] if gy >= Hh - 3 else UP["snow"]),
                  (2, lambda gx, gy: UP["white"] if gy <= 3 else UP["mist"] if gy >= Hh - 4 else UP["snow"])]
        im = layered_panel(W, Hh, 4, layers)
        px = im.load()
        for x in range(2, W - 2):
            px[x, Hh - 2] = UP["fog"]
        return im
    if role == "pressed":
        layers = [(0, "out"),
                  (1, lambda gx, gy: UP["tealL"] if gy <= 2 else UP["teald"] if gy >= Hh - 3 else UP["teal"]),
                  (2, lambda gx, gy: UP["teal"] if gy < Hh - 4 else UP["teald"])]
        return layered_panel(W, Hh, 4, layers)
    if role == "selected":
        layers = [(0, "out"),
                  (1, "azure"),
                  (2, lambda gx, gy: UP["white"] if gy <= 3 else UP["ice"] if gy >= Hh - 4 else UP["ice2"])]
        return layered_panel(W, Hh, 4, layers)
    layers = [(0, "fogd"), (1, lambda gx, gy: UP["fog"])]  # disabled
    im = layered_panel(W, Hh, 4, layers)
    px = im.load()
    for x in range(2, W - 2):
        px[x, 1] = H("#b4cde0")
    return im


# ================================================================= panels
DIALOG_PREVIEW_TEXT = ("gray", (14, 14, 114), (14, 24, 94), (14, 34, 60))


def dialog_preview():
    W, Hh = 160, 48
    im = nine_stretch(dialog24(), W, Hh)
    for (x, y, w) in ((12, 12, 130), (12, 22, 108), (12, 32, 64)):
        for yy in (y, y + 1):
            for xx in range(x, x + w):
                put(im, xx, yy, "navy")
    # tail + advance mark
    for i in range(4):
        for xx in range(i, 8 - i):
            put(im, 142 + xx - 1, 39 + i + 1, "out") if False else None
    for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (3, 1), (2, 2)):
        put(im, 144 + dx, 36 + dy, "teal")
    return im


# ================================================================= tab / notice icons
def tab_character():
    im = new(16, 16)
    # shoulders / shirt
    shirt = {(x, y) for y in range(11, 15) for x in range(3, 13) if (y > 11 or 4 <= x <= 11)}
    shade_cells(im, shirt, "blue", "sky", "navy2")
    # head
    head = ellipse_cells(8, 6.2, 4.2, 4.4)
    shade_cells(im, head, "skin", "creamh", "skind")
    # hair
    hair = {(x, y) for (x, y) in head if y <= 4 or (y == 5 and (x <= 4 or x >= 11))} | {(4, 4), (11, 4)}
    hair = {(x, y) for (x, y) in hair if 1 <= y}
    shade_cells(im, hair, "hair", "hairl", "brownd")
    put(im, 6, 7, "ink")
    put(im, 10, 7, "ink")
    put(im, 8, 9, "pinkd")
    return outline_img(im, "outw")


def tab_bag():
    """Brown backpack (concept)."""
    im = new(16, 16)
    # handle
    for x, y in ((6, 1), (7, 1), (8, 1), (9, 1), (5, 2), (10, 2)):
        put(im, x, y, "brownd")
    body = rr_cells(3, 2, 10, 13, 3)
    shade_cells(im, body, "brown", "brownl", "brownd", deep=True)
    pocket = rr_cells(4, 8, 8, 5, 2)
    shade_cells(im, pocket, "brownl", H("#dcae84"), "brown")
    for x in range(4, 12):
        put(im, x, 8, "brownd")
    # buckle
    fill_cells(im, rect_cells(7, 7, 2, 3), "cream")
    put(im, 7, 9, "goldd")
    put(im, 8, 9, "goldd")
    # top flap seam
    for x in range(4, 12):
        put(im, x, 5, "brownd") if x not in (7, 8) else None
    return outline_img(im, "outw")


def tab_map():
    """Folded map: green land, blue river, red marker."""
    im = new(16, 16)
    cols = ["leaf", "lime", "leaf"]
    for i, (x0, x1) in enumerate(((1, 5), (6, 10), (11, 14))):
        top = 3 + (1 if i == 1 else 0)
        bot = 12 + (1 if i == 1 else 0)
        for y in range(top, bot + 1):
            for x in range(x0, x1 + 1):
                c = cols[i]
                if y == top:
                    c = "limel"
                elif y == bot:
                    c = "leafd"
                put(im, x, y, c)
        if i != 2:
            for y in range(top, bot + 1):
                put(im, x1, y, "leafd")
    # river
    for x, y in ((3, 4), (3, 5), (4, 6), (4, 7), (4, 8), (3, 9), (3, 10), (8, 5), (8, 6), (9, 7), (9, 8), (9, 9), (8, 10)):
        put(im, x, y, "sky")
    # marker
    for x, y in ((7, 8), (8, 8), (7, 9), (8, 9)):
        put(im, x, y, "red")
    put(im, 7, 8, "pinkl")
    return outline_img(im, "out")


def tab_work():
    """Brown briefcase with a cyan clasp (concept)."""
    im = new(16, 16)
    for x, y in ((5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (5, 3), (10, 3), (5, 4), (10, 4)):
        put(im, x, y, "brownd")
    body = rr_cells(1, 4, 14, 10, 2)
    shade_cells(im, body, "brown", "brownl", "brownd", deep=True)
    for x in range(2, 14):
        put(im, x, 8, "brownd")
        put(im, x, 9, "brownl") if False else None
    fill_cells(im, rect_cells(7, 7, 2, 4), "cream")
    put(im, 7, 10, "tealL")
    put(im, 8, 10, "tealL")
    put(im, 7, 7, "white")
    return outline_img(im, "outw")


def tab_relationship():
    return heart_img(HEART13, "red", "redl", "redd", "outw")


def tab_settings():
    im = new(16, 16)
    cells = set()
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            tooth = (math.cos(ang * 8) > 0.1)
            if d <= 5.3 or (d <= 7.0 and tooth):
                cells.add((x, y))
    cells -= disc_cells(8, 8, 2.4)
    shade_cells(im, cells, "fog", "snow", "fogd", deep=True)
    for (x, y) in disc_cells(8, 8, 2.4):
        put(im, x, y, "ink")
    return outline_img(im, "out")


def notice_warning():
    im = new(16, 16)
    tri = set()
    for y in range(2, 14):
        half = (y - 2) * 0.55 + 0.5
        for x in range(16):
            if abs(x + 0.5 - 8) <= half:
                tri.add((x, y))
    shade_cells(im, tri, "gold", "goldl", "goldd", deep=False)
    for y in range(6, 10):
        put(im, 7, y, "ink")
        put(im, 8, y, "ink")
    put(im, 7, 11, "ink")
    put(im, 8, 11, "ink")
    return outline_img(im, "outw")


def notice_info():
    im = new(16, 16)
    shade_cells(im, disc_cells(8, 8, 6.4), "azure", "sky", "navy2", deep=True)
    put(im, 7, 4, "white")
    put(im, 8, 4, "white")
    for y in range(7, 12):
        put(im, 7, y, "white")
        put(im, 8, y, "white")
    put(im, 6, 7, "white")
    put(im, 6, 11, "white")
    put(im, 9, 11, "white")
    return outline_img(im, "out")


def notice_saveok():
    im = new(16, 16)
    shade_cells(im, disc_cells(8, 8, 6.4), "green", "greenl", "greend", deep=True)
    for x, y in ((4, 8), (5, 9), (6, 10), (7, 9), (8, 8), (9, 7), (10, 6), (11, 5)):
        put(im, x, y, "white")
        put(im, x, y + 1, "white")
    return outline_img(im, "out")


def padlock(open_=False, body="gold", light="goldl", dark="goldd"):
    im = new(16, 16)
    shackle = [(5, 3), (6, 2), (7, 2), (8, 2), (9, 2), (10, 3), (5, 4), (5, 5), (10, 4), (10, 5)] if not open_ else \
              [(8, 1), (9, 1), (10, 1), (11, 2), (11, 3), (11, 4), (5, 4), (5, 5)]
    for x, y in shackle:
        put(im, x, y, "grayl")
        put(im, x + 1 if (x, y) in ((10, 3), (10, 4), (10, 5), (11, 2), (11, 3), (11, 4)) and False else x, y, "grayl")
    bodyc = rr_cells(3, 6, 10, 8, 2)
    shade_cells(im, bodyc, body, light, dark, deep=True)
    put(im, 8, 9, "ink")
    put(im, 8, 10, "ink")
    put(im, 7, 9, "ink")
    put(im, 7, 10, "ink")
    put(im, 8, 11, "ink")
    return outline_img(im, "outw")


def unlock_icon():
    return padlock(open_=True)


# ================================================================= save / load / hearts / audio
def floppy(error=False):
    im = new(16, 16)
    body = rect_cells(2, 2, 12, 12) - {(13, 2), (12, 2), (13, 3)}
    shade_cells(im, body, "azure", "sky", "navy2", deep=True)
    fill_cells(im, rect_cells(5, 2, 6, 4), "mist")      # shutter
    fill_cells(im, rect_cells(8, 3, 2, 2), "grayk")
    fill_cells(im, rect_cells(4, 8, 8, 6), "white")      # label
    for x in range(5, 11):
        put(im, x, 10, "mist")
        put(im, x, 12, "mist")
    if error:
        for i in range(5):
            put(im, 5 + i, 8 + i, "red")
            put(im, 9 - i, 8 + i, "red")
    return outline_img(im, "out")


def load_icon():
    im = new(16, 16)
    tray = rr_cells(1, 10, 14, 5, 2)
    shade_cells(im, tray, "sky", "sky2", "azure")
    fill_cells(im, rect_cells(4, 11, 8, 2), "navy2")
    for y in range(1, 6):
        for x in (6, 7, 8, 9):
            put(im, x, y, "sky2")
    for i in range(5):
        for x in range(3 + i, 13 - i):
            put(im, x, 6 + i - 0, "sky2") if i < 4 else None
    return outline_img(im, "out")


def heart_state(kind):
    if kind == "full":
        return heart_img(HEART13, "red", "redl", "redd", "outw")
    if kind == "empty":
        return heart_img(HEART13, "gray", "grayl", "grayd", "grayk", hl=False)
    # half: left red, right grey
    full = heart_img(HEART13, "red", "redl", "redd", "outw")
    empty = heart_img(HEART13, "gray", "grayl", "grayd", "grayk", hl=False)
    out = empty.copy()
    for y in range(16):
        for x in range(8):
            out.putpixel((x, y), full.getpixel((x, y)))
    for y in range(3, 14):
        put(out, 8, y, "outw") if out.getpixel((8, y))[3] else None
    return out


def interact_bubble():
    im = new(16, 16)
    body = disc_cells(8, 7.2, 6.3)
    shade_cells(im, body, "ice2", "white", "ice", deep=True)
    for x, y in ((4, 13), (5, 13), (4, 12), (5, 12), (3, 14), (4, 14)):
        put(im, x, y, "ice2")
    for y in range(3, 9):
        put(im, 7, y, "azure")
        put(im, 8, y, "azure")
    put(im, 7, 10, "azure")
    put(im, 8, 10, "azure")
    put(im, 7, 11 - 0, "azure") if False else None
    return outline_img(im, "out")


def talk_bubble():
    im = new(16, 16)
    body = rr_cells(1, 2, 14, 10, 3)
    shade_cells(im, body, "white", "creamh", "ice")
    for x, y in ((4, 12), (5, 12), (4, 13), (3, 14), (4, 14)):
        put(im, x, y, "white")
    put(im, 3, 14, "white")
    for x in (5, 8, 11):
        put(im, x, 7, "navy")
        put(im, x + 1, 7, "navy")
    return outline_img(im, "out")


def speaker(on=True):
    im = new(16, 16)
    cone = {(x, y) for y in range(5, 12) for x in range(2, 5)} | \
           {(x, y) for y in range(2, 15) for x in range(5, 8) if abs(y - 8) <= (x - 4) * 2 + 0.5}
    shade_cells(im, cone, "fog", "snow", "fogd")
    if on:
        for x, y in ((9, 6), (9, 7), (9, 8), (9, 9), (10, 5), (10, 10), (11, 4), (11, 11), (12, 3), (12, 12), (12, 5), (12, 10)):
            put(im, x, y, "sky")
        put(im, 11, 6, "sky")
        put(im, 11, 9, "sky")
        put(im, 11, 7, "sky")
        put(im, 11, 8, "sky")
    else:
        for i in range(5):
            put(im, 9 + i, 5 + i, "red")
            put(im, 13 - i, 5 + i, "red")
    return outline_img(im, "out")


# ================================================================= rhythm cues / judge / track
ARROW_UP = [
    "....XX....",
    "...XXXX...",
    "..XXXXXX..",
    ".XXXXXXXX.",
    "XXXXXXXXXX",
    "...XXXX...",
    "...XXXX...",
    "...XXXX...",
]


def rhythm_cue(base, light, dark, turns):
    im = new(16, 16)
    body = disc_cells(8, 8, 6.9)
    shade_cells(im, body, base, light, dark, deep=True)
    # inner glossy highlight (upper-left)
    for (x, y) in ((4, 3), (5, 3), (6, 2), (3, 4), (3, 5)):
        put(im, x, y, light)
    arrow = cells_from_rows(ARROW_UP)
    ar = new(16, 16)
    for (x, y) in arrow:
        put(ar, x + 3, y + 4, "white")
    ar = ar.rotate(-90 * turns)
    sh = new(16, 16)
    for (x, y) in cells_of(ar):
        put(sh, x + (1 if turns in (0, 1, 2, 3) else 0), y + 1, dark)
    paste(im, sh, 0, 0)
    paste(im, ar, 0, 0)
    return outline_img(im, "ink")


FONT = {
    "P": ["1110", "1001", "1001", "1110", "1000", "1000", "1000"],
    "E": ["1111", "1000", "1000", "1110", "1000", "1000", "1111"],
    "R": ["1110", "1001", "1001", "1110", "1010", "1001", "1001"],
    "F": ["1111", "1000", "1000", "1110", "1000", "1000", "1000"],
    "C": ["0111", "1000", "1000", "1000", "1000", "1000", "0111"],
    "T": ["1111", "0110", "0110", "0110", "0110", "0110", "0110"],
    "G": ["0111", "1000", "1000", "1011", "1001", "1001", "0111"],
    "O": ["0110", "1001", "1001", "1001", "1001", "1001", "0110"],
    "D": ["1110", "1001", "1001", "1001", "1001", "1001", "1110"],
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
    "S": ["0111", "1000", "1000", "0110", "0001", "0001", "1110"],
}

FONT5 = {   # chunkier 5x7 face for the short words (GOOD / MISS)
    "G": ["01110", "11001", "11000", "11011", "11001", "11001", "01110"],
    "O": ["01110", "11011", "11011", "11011", "11011", "11011", "01110"],
    "D": ["11110", "11011", "11011", "11011", "11011", "11011", "11110"],
    "M": ["11011", "11111", "11111", "11111", "11011", "11011", "11011"],
    "I": ["1111", "0110", "0110", "0110", "0110", "0110", "1111"],
    "S": ["01111", "11000", "11000", "01110", "00011", "00011", "11110"],
}

JUDGE_W, JUDGE_H = 40, 12


def judge_word(text, top, mid, bot, outline, bold):
    im = new(JUDGE_W, JUDGE_H)
    glyphs = []
    for ch in text:
        glyphs.append(FONT5[ch] if bold else FONT[ch])
    gap = 1
    total = sum(len(g[0]) for g in glyphs) + gap * (len(glyphs) - 1)
    x = (JUDGE_W - total) // 2
    y0 = 2
    for g in glyphs:
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == "1":
                    c = top if ry <= 1 else (bot if ry >= 5 else mid)
                    put(im, x + rx, y0 + ry, c)
        x += len(g[0]) + gap
    outline_img(im, outline)
    # drop shadow: one extra row under the outline
    px = im.load()
    for yy in range(JUDGE_H - 2, -1, -1):
        for xx in range(JUDGE_W):
            if px[xx, yy][3] and px[xx, yy][:3] == UP[outline][:3] and not px[xx, yy + 1][3]:
                px[xx, yy + 1] = UP[outline]
    return im


def hitzone():
    im = new(24, 24)
    px = im.load()
    for y in range(24):
        for x in range(24):
            d = math.hypot(x + 0.5 - 12, y + 0.5 - 12)
            if 9.0 <= d < 11.0:
                px[x, y] = UP["sky2"]
            elif 7.9 <= d < 9.0 or 11.0 <= d < 12.0:
                px[x, y] = UP["out"]
    # glossy tick marks (N E S W) like the concept's glowing gem lane
    for i in range(-1, 2):
        for k in (3, 4):
            px[12 + i, k] = UP["white"] if i == 0 else UP["sky"]
            px[12 + i, 23 - k] = UP["white"] if i == 0 else UP["sky"]
            px[k, 12 + i] = UP["white"] if i == 0 else UP["sky"]
            px[23 - k, 12 + i] = UP["white"] if i == 0 else UP["sky"]
    for x, y in ((11, 12), (12, 12), (11, 11), (12, 11)):
        px[x, y] = UP["sky2"] if (x + y) % 2 else UP["white"]
    return im


def track(rail="#498aa8", edge="navy2", lo="navy2", hi="navyd", rung="blue", rung2="#22578e", side="#3a73a8",
          line1="sky2", line2="sky"):
    """128x24 lane: navy panel with glowing cyan grid, centre line and edge rails (colour args: farm variant)."""
    W, Hh = 128, 24
    im = new(W, Hh)
    px = im.load()
    col = lambda v: H(v) if v.startswith("#") else UP[v]  # noqa: E731
    for y in range(Hh):
        for x in range(W):
            if y in (0, Hh - 1):
                c = UP["ink"] if rail == "#498aa8" else UP["outw"]
            elif y in (1, Hh - 2):
                c = col(rail)
            elif y in (2, Hh - 3):
                c = col(edge)
            else:
                t = abs(y - 11.5) / 9.5
                c = vgrad(lo, hi, min(1, t))
                if x % 16 == 8:
                    c = vgrad(rung, lo, t)           # grid rungs
                if (x % 16) in (7, 9) and 4 <= y <= 19:
                    c = vgrad(lo, col(rung2), 1 - t)
                if y in (11, 12):
                    c = UP[line1] if y == 11 else UP[line2]  # glowing centre line
                elif y in (10, 13):
                    c = col(side)
            px[x, y] = c
    # rounded end caps (clip the four corners)
    for x, y in ((0, 0), (W - 1, 0), (0, Hh - 1), (W - 1, Hh - 1)):
        px[x, y] = (0, 0, 0, 0)
    return im


def track_farm():
    """Earthy furrow lane: dark soil, leaf-green rails, lime centre line."""
    return track(rail="leaf", edge="leafd", lo=H("#4a2f22"), hi=H("#2e1c14"), rung="brown", rung2="#6b4630",
                 side="#5f3a2c", line1="limel", line2="lime")


def crop_cue(kind):
    """16x16 round-ish crop icon for the farm rhythm lane (carrot / cabbage / pumpkin), warm dark outline."""
    im = new(16, 16)
    if kind == "carrot":
        body = {(x, y) for y in range(5, 15) for x in range(16)
                if abs(x + 0.5 - (8.5 - (y - 5) * 0.12)) <= 4.3 * (14.8 - y) / 9.8}
        shade_cells(im, body, "orange", "orangel", "oranged", deep=True)
        for (x, y) in ((6, 8), (7, 8), (9, 11), (10, 11), (7, 13)):   # growth rings
            if (x, y) in body:
                put(im, x, y, "oranged")
        for (x, y) in ((6, 6), (7, 6)):
            put(im, x, y, "orangel")
        leaf = ["..G....G....G...",
                "..gG...gG..Gg...",
                "...gG..gG.Gg....",
                "....gGgggGgd....",
                ".....dgggdd....."]
        paste(im, grid(leaf, {"G": "greenl", "g": "green", "d": "greend"}, 16, 5, 0, 0), 0, 1)
    elif kind == "cabbage":
        body = disc_cells(8, 8.5, 6.6)
        shade_cells(im, body, "lime", "limel", "green", deep=True)
        for (x, y) in ((8, 4), (8, 5), (8, 6), (7, 7), (6, 8), (9, 7), (10, 8), (5, 11), (6, 12), (10, 12), (11, 11)):
            put(im, x, y, "green")
        for (x, y) in ((5, 4), (6, 3), (4, 5), (7, 4)):
            put(im, x, y, "white")
    else:  # pumpkin
        body = ellipse_cells(8, 9.2, 6.9, 5.4)
        shade_cells(im, body, "orange", "orangel", "oranged", deep=True)
        for x in (4, 8, 12):
            for y in range(6, 14):
                if (x, y) in body:
                    put(im, x, y, "oranged" if x != 8 else "orangel")
        for (x, y) in ((5, 7), (6, 6)):
            put(im, x, y, "goldl")
        for (x, y) in ((7, 3), (8, 3), (7, 4), (8, 4), (8, 5)):
            put(im, x, y, "greend" if y > 3 else "green")
        put(im, 9, 4, "green"); put(im, 10, 4, "greenl")
    return outline_img(im, "outw")


# ================================================================= effects (16x16 frames)
def exclaim_frame(dy):
    im = new(16, 16)
    for y in range(3, 10):
        for x in (7, 8):
            put(im, x, y, "gold")
        put(im, 7, y, "goldl")
        put(im, 8, y, "gold")
    for y in range(8, 10):
        put(im, 8, y, "orange")
    for x in (7, 8):
        for y in (12, 13):
            put(im, x, y, "gold")
    put(im, 8, 13, "orange")
    put(im, 7, 12, "goldl")
    outline_img(im, "outw")
    # sparkle accents
    for x, y in ((3, 7), (12, 6)):
        put(im, x, y, "goldl")
    out = new(16, 16)
    out.paste(im, (0, dy))
    return out


def coin_pop_frame(rx):
    im = new(16, 16)
    cells = ellipse_cells(8, 8, rx, 6.2)
    shade_cells(im, cells, "gold", "goldl", "goldd", deep=True)
    if rx >= 4:
        gx, gy = 8 - 2, 5
        for (x, y) in cells_from_rows(DOLLAR):
            if (gx + x, gy + y) in cells:
                put(im, gx + x + 1, gy + y + 1, "goldd") if (gx + x + 1, gy + y + 1) in cells else None
        for (x, y) in cells_from_rows(DOLLAR):
            if (gx + x, gy + y) in cells:
                put(im, gx + x, gy + y, "white")
    return outline_img(im, "outw")


def sparkle_frame(arm, centre="white", ray="gold", edge="orange", inner="goldl", diag=None):
    im = new(16, 16)
    cx = cy = 8
    if diag:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            put(im, cx + dx, cy + dy, diag)
    for i in range(1, arm + 1):
        col = edge if (i == arm and arm > 1) else (inner if i == 1 else ray)
        for dx, dy in ((i, 0), (-i, 0), (0, i), (0, -i)):
            put(im, cx + dx, cy + dy, col)
    if arm >= 4:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(im, cx + dx * 2 + dy, cy + dy * 2 + dx, ray) if False else None
    put(im, cx, cy, centre)
    return im


STAR = [
    "......XX......",
    "......XX......",
    ".....XXXX.....",
    "XXXXXXXXXXXXXX",
    ".XXXXXXXXXXXX.",
    "..XXXXXXXXXX..",
    "...XXXXXXXX...",
    "...XXXXXXXX...",
    "..XXXX..XXXX..",
    "..XXX....XXX..",
]


def star_frame():
    im = new(16, 16)
    cells = cells_from_rows(STAR, "X", 1, 3)
    shade_cells(im, cells, "gold", "goldl", "orange", deep=True)
    put(im, 7, 8, "white")
    put(im, 8, 8, "white")
    put(im, 7, 9, "white")
    return outline_img(im, "outw")


def lowneed_frame(body, light, dark):
    im = new(16, 16)
    shade_cells(im, disc_cells(8, 8, 6.4), body, light, dark, deep=True)
    for y in list(range(4, 9)) + [10, 11]:
        for x in (7, 8):
            put(im, x, y, "white")
    return outline_img(im, "ink")


# ================================================================= title banner (key art, untouched)
def title_banner():
    src = Image.open(ASSETS / "reference" / "ArtDirection_ConceptSheet_v01.png").convert("RGBA")
    return src.crop((0, 0, 1024, 190))


# ================================================================= build
def build():
    out = []

    def put_(img, rel):
        out.append(save(img, rel))

    # HUD
    put_(need_energy(), "ui/hud/UI_001_Need_Energy_v01.png")
    put_(need_fullness(), "ui/hud/UI_001_Need_Fullness_v01.png")
    put_(need_mood(), "ui/hud/UI_001_Need_Mood_v01.png")
    put_(coin(), "ui/hud/UI_002_Money_v01.png")
    put_(clock_icon(), "ui/hud/UI_003_Clock_v01.png")
    put_(calendar_icon(), "ui/hud/UI_003_Calendar_v01.png")
    put_(clock_frame(), "ui/hud/UI_003_ClockFrame_v01.png")
    put_(needbar_frame(), "ui/hud/UI_001_NeedBar_Frame_v01.png")
    put_(needbar_fill(), "ui/hud/UI_001_NeedBar_Fill_v01.png")

    # Buttons
    put_(time_button("pause"), "ui/buttons/UI_004_TimeControl_Pause_v01.png")
    put_(time_button("play"), "ui/buttons/UI_004_TimeControl_Normal_v01.png")
    put_(time_button("fast"), "ui/buttons/UI_004_TimeControl_Fast_v01.png")
    for role, name in (("normal", "Normal"), ("pressed", "Pressed"), ("disabled", "Disabled"), ("selected", "Selected")):
        put_(button_image(role), f"ui/buttons/UI_006_Button_{name}_v01.png")

    # Panels
    put_(dialog24(), "ui/panels/UI_005_DialogBox_v01.png")
    put_(dialog_preview(), "ui/panels/UI_005_DialogBox_Preview_v01.png")
    put_(frame24("navy", "sky", "cream"), "ui/panels/UI_009_ShopPanel_v01.png")

    # Tabs
    put_(tab_character(), "ui/icons/UI_007_Tab_Character_v01.png")
    put_(tab_bag(), "ui/icons/UI_007_Tab_Bag_v01.png")
    put_(tab_map(), "ui/icons/UI_007_Tab_Map_v01.png")
    put_(tab_work(), "ui/icons/UI_007_Tab_Work_v01.png")
    put_(tab_relationship(), "ui/icons/UI_007_Tab_Relationship_v01.png")
    put_(tab_settings(), "ui/icons/UI_007_Tab_Settings_v01.png")

    # Notices
    put_(notice_warning(), "ui/icons/UI_008_Notice_Warning_v01.png")
    put_(notice_info(), "ui/icons/UI_008_Notice_Info_v01.png")
    put_(unlock_icon(), "ui/icons/UI_008_Notice_Unlock_v01.png")
    put_(notice_saveok(), "ui/icons/UI_008_Notice_SaveOk_v01.png")

    # Save / load
    put_(floppy(), "ui/icons/UI_012_Save_v01.png")
    put_(load_icon(), "ui/icons/UI_012_Load_v01.png")
    put_(floppy(error=True), "ui/icons/UI_012_SaveError_v01.png")

    # Hearts
    for k, n in (("full", "Full"), ("half", "Half"), ("empty", "Empty")):
        put_(heart_state(k), f"ui/icons/UI_011_Heart_{n}_v01.png")

    # Object hints
    put_(interact_bubble(), "ui/icons/OBJ_001_Interact_v01.png")
    put_(talk_bubble(), "ui/icons/OBJ_001_Talk_v01.png")

    # Audio
    put_(speaker(True), "ui/icons/AUDIO_001_Volume_On_v01.png")
    put_(speaker(False), "ui/icons/AUDIO_001_Volume_Off_v01.png")

    # Minigames (rhythm)
    put_(frame24("navy", "sky2", "cream"), "minigames/rhythm/MINI_001_Panel_v01.png")
    put_(rhythm_cue("green", "greenl", "greend", 0), "minigames/rhythm/MINI_002_RhythmCue_Tap_v01.png")
    put_(rhythm_cue("blue", "sky", "navy2", 1), "minigames/rhythm/MINI_002_RhythmCue_Hold_v01.png")
    put_(track(), "minigames/rhythm/MINI_003_Track_v01.png")
    put_(hitzone(), "minigames/rhythm/MINI_003_HitZone_v01.png")
    put_(track_farm(), "minigames/rhythm/MINI_003_Track_Farm_v01.png")
    for kind, name in (("carrot", "Carrot"), ("cabbage", "Cabbage"), ("pumpkin", "Pumpkin")):
        put_(crop_cue(kind), f"minigames/rhythm/MINI_002_RhythmCue_Crop_{name}_v01.png")
    put_(judge_word("PERFECT", "goldl", "gold", "orange", "outw", False), "minigames/rhythm/MINI_004_Judge_Perfect_v01.png")
    put_(judge_word("GOOD", "limel", "greenl", "green", "greeno", True), "minigames/rhythm/MINI_004_Judge_Good_v01.png")
    put_(judge_word("MISS", "redl", "red", "redd", "redo", True), "minigames/rhythm/MINI_004_Judge_Miss_v01.png")
    put_(frame24("navy2", "sky", "cream", thick=4), "minigames/rhythm/MINI_005_ResultPanel_v01.png")

    # Effects
    strip = lambda frames: _strip(frames)  # noqa: E731
    put_(strip([exclaim_frame(dy) for dy in (0, -2, -3, -1)]), "effects/interaction/FX_001_InteractPulse_v01.png")
    put_(strip([coin_pop_frame(rx) for rx in (5.5, 3.6, 1.4, 3.6)]), "effects/rewards/FX_002_CoinPop_v01.png")
    base_heart = heart_img(HEART11, "red", "redl", "redd", "outw")
    frames = []
    for dy in (2, 1, 0, -1):
        f = new(16, 16)
        f.paste(base_heart, (0, dy))
        frames.append(f)
    put_(strip(frames), "effects/rewards/FX_003_HeartUp_v01.png")
    put_(strip([sparkle_frame(2), sparkle_frame(5, diag="goldl"), star_frame(), sparkle_frame(2, centre="goldl", ray="goldd", edge="goldd", inner="goldd")]),
         "effects/unlocks/FX_004_Sparkle_v01.png")
    put_(strip([lowneed_frame("red", "redl", "redd"), lowneed_frame("redd", "red", H("#5c1414"))]), "effects/interaction/FX_005_LowNeed_v01.png")

    # Title banner (concept key art, cropped, not repainted)
    put_(title_banner(), "ui/title/UI_000_TitleBanner_v01.png")
    return out


def _strip(frames):
    w, h = frames[0].size
    sheet = new(w * len(frames), h)
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    return sheet


if __name__ == "__main__":
    paths = build()
    print(f"wrote {len(paths)} files")
