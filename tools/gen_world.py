#!/usr/bin/env python3
"""Generate world assets: tilesets, blockers, urban objects, buildings, interiors, furniture, food, products, demo scene.
Deterministic (fixed seeds). Usage: python3 tools/gen_world.py"""
import sys, json, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image
from pixel import P, TILE, ASSETS, save, strip

T = TILE
FILES = []


# ------------------------------------------------------------------ helpers
def new(w, h):
    return Image.new("RGBA", (w, h), P["_"])


def px(im, x, y, k):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), P[k])


def rect(im, x0, y0, x1, y1, k):  # inclusive corners
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(im, x, y, k)


def outline(im, k="k"):
    src = im.copy()
    sp, op = src.load(), im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            if sp[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and sp[nx, ny][3]:
                        op[x, y] = P[k]
                        break
    return im


def mask_of(ells):
    m = set()
    for cx, cy, rx, ry in ells:
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1:
                    m.add((x, y))
    return m


def shade(im, mask, c, tones, rng, noise=0.12, fleck=None):
    cx, cy, rx, ry = c
    light, mid, dark = tones
    for x, y in sorted(mask):
        v = -((x + .5 - cx) / rx) * .55 - ((y + .5 - cy) / ry) * .75 + rng.uniform(-noise, noise)
        k = light if v > .38 else dark if v < -.25 else mid
        if fleck and k == mid and rng.random() < fleck[1]:
            k = fleck[0]
        px(im, x, y, k)


def out(img, rel):
    save(img, rel)
    FILES.append(rel)


def out_json(obj, rel):
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    FILES.append(rel)


def grid_img(g):
    im = new(len(g[0]), len(g))
    for y, row in enumerate(g):
        for x, k in enumerate(row):
            px(im, x, y, k)
    return im


def noise_grid(seed, base, specks):
    r = random.Random(seed)
    g = [[base] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            v, acc = r.random(), 0
            for k, p in specks:
                acc += p
                if v < acc:
                    g[y][x] = k
                    break
    return g


def copy(g):
    return [row[:] for row in g]


# ------------------------------------------------------------------ ground grids
GRASS_A = noise_grid(1, "l", [("e", .08), ("E", .02), ("y", .015)])
GRASS_B = noise_grid(2, "l", [("e", .06), ("E", .02), ("y", .02)])
for (x, y) in ((3, 4), (10, 11), (12, 3)):
    GRASS_B[y][x] = "e"; GRASS_B[y - 1][x - 1] = "e"; GRASS_B[y - 1][x + 1] = "e"; GRASS_B[y + 1][x] = "E"
for (x, y, c) in ((5, 12, "w"), (13, 8, "y")):
    GRASS_B[y][x] = c; GRASS_B[y][x + 1 if x < 14 else x - 1] = "y" if c == "w" else "w"
DIRT = noise_grid(3, "n", [("N", .08), ("u", .06)])
ASPH = noise_grid(4, "a", [("A", .07)])


def sidewalk_grid():
    r = random.Random(5)
    g = [["G"] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            band = y // 8
            jx = (x % 8 == 7) if band == 0 else (x % 8 == 3)
            if y % 8 == 7 or jx:
                g[y][x] = "g"
            elif r.random() < .04:
                g[y][x] = "w"
    return g


SIDE = sidewalk_grid()


def wood_grid():
    r = random.Random(6)
    g = [["n"] * T for _ in range(T)]
    for y in range(T):
        b = y // 4
        for x in range(T):
            if y % 4 == 3:
                g[y][x] = "N"
            elif x in ((b * 5) % 16, (b * 5 + 8) % 16):
                g[y][x] = "N"
            elif r.random() < .07:
                g[y][x] = "u"
    return g


def floor_tile_grid():
    r = random.Random(7)
    g = [["w"] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            if x % 8 == 7 or y % 8 == 7:
                g[y][x] = "G"
            elif r.random() < .04:
                g[y][x] = "G"
    return g


WOOD, FLOOR = wood_grid(), floor_tile_grid()


def curb_tile(edges):
    g = copy(SIDE)
    for y in range(T):
        for x in range(T):
            best = None
            for e in edges:
                d = {"t": y, "b": T - 1 - y, "l": x, "r": T - 1 - x}[e]
                face = 2 if e == "b" else 1
                if d < face:
                    cand = (d, "g")
                elif d < face + 2:
                    cand = (d, "w")
                else:
                    continue
                if best is None or cand[0] < best[0]:
                    best = cand
            if best:
                g[y][x] = best[1]
    return grid_img(g)


# ------------------------------------------------------------------ road tiles
ARMS = {"N": (7, 2, 8, 8), "S": (7, 7, 8, 13), "W": (2, 7, 8, 8), "E": (7, 7, 13, 8)}


def road_tile(arms=()):
    g = copy(ASPH)
    im = grid_img(g)
    for a in arms:
        x0, y0, x1, y1 = ARMS[a]
        rect(im, x0, y0, x1, y1, "y")
    return im


def crosswalk(horizontal_road):
    im = grid_img(ASPH)
    for i in range(4):
        o = 1 + i * 4
        if horizontal_road:
            rect(im, 2, o, 13, o + 1, "w")
        else:
            rect(im, o, 2, o + 1, 13, "w")
    return im


DT = [3, 3, 2, 2, 3, 3, 3, 2, 2, 2, 3, 3, 2, 2, 3, 3]


def path_tile(sides):
    grass = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            if ("t" in sides and y < DT[x]) or ("b" in sides and y >= T - DT[(x + 5) % 16]) \
               or ("l" in sides and x < DT[y]) or ("r" in sides and x >= T - DT[(y + 5) % 16]):
                grass[y][x] = True
    g = copy(DIRT)
    for y in range(T):
        for x in range(T):
            if grass[y][x]:
                g[y][x] = GRASS_A[y][x]
    for y in range(T):
        for x in range(T):
            if grass[y][x]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < T and 0 <= ny < T and not grass[ny][nx]:
                        g[y][x] = "E"
    return grid_img(g)


# ------------------------------------------------------------------ blockers
def brick_wall():
    r = random.Random(8)
    im = new(T, T)
    for x in range(T):
        px(im, x, 0, "k"); px(im, x, 1, "w"); px(im, x, 2, "G"); px(im, x, 3, "G"); px(im, x, 4, "g"); px(im, x, 5, "k")
        for y in range(6, 14):
            band = 0 if y < 10 else 1
            mortar = (y in (9, 13)) or ((band == 0 and x in (3, 11)) or (band == 1 and x in (7, 15)))
            c = "g" if mortar else "R"
            if not mortar and (y in (6, 10)) and r.random() < .6:
                c = "r"
            px(im, x, y, c)
        px(im, x, 14, "K"); px(im, x, 15, "k")
    return im


def fence_h():
    im = new(T, T)
    for x in range(T):
        for y0 in (6, 11):
            px(im, x, y0, "u"); px(im, x, y0 + 1, "n")
    rect(im, 6, 3, 9, 14, "n"); rect(im, 6, 3, 9, 4, "u"); rect(im, 6, 3, 6, 14, "u"); rect(im, 9, 5, 9, 14, "N")
    return outline(im)


def fence_v():
    im = new(T, T)
    for y in range(T):
        px(im, 7, y, "u"); px(im, 8, y, "n")
    for y0 in (1, 9):
        rect(im, 5, y0, 10, y0 + 5, "n"); rect(im, 5, y0, 10, y0 + 1, "u"); rect(im, 10, y0 + 2, 10, y0 + 5, "N")
    return outline(im)


def hedge():
    r = random.Random(9)
    im = new(T, T)
    for y in range(T):
        for x in range(T):
            c = "e"
            if y < 5:
                c = "l" if r.random() < .35 else "e"
            elif y > 10:
                c = "E" if r.random() < .5 else "e"
            elif r.random() < .12:
                c = "E"
            px(im, x, y, c)
    for (x, y) in ((3, 8), (9, 7), (12, 9), (6, 11)):
        rect(im, x, y, x + 1, y + 1, "l")
    for x in range(T):
        px(im, x, 0, "k"); px(im, x, 15, "k")
    for x in range(T):
        if x % 4 == 1:
            px(im, x, 1, "e")
    return im


def water(frame):
    im = new(T, T)
    r = random.Random(10)
    for y in range(T):
        for x in range(T):
            px(im, x, y, "B" if r.random() < .06 else "b")
    dashes = [(2, 3), (9, 7), (4, 11), (12, 14)] if frame == 0 else [(6, 3), (13, 7), (8, 11), (0, 14)]
    for (x, y) in dashes:
        for i in range(3):
            px(im, (x + i) % T, y, "c")
    sx, sy = (10, 2) if frame == 0 else (3, 9)
    px(im, sx, sy, "w")
    return im


# ------------------------------------------------------------------ nature & decorations
def tree():
    r = random.Random(11)
    im = new(32, 32)
    rect(im, 14, 20, 17, 30, "n"); rect(im, 16, 20, 17, 30, "N"); rect(im, 13, 29, 18, 30, "N"); px(im, 14, 24, "u")
    ells = [(16, 12, 10, 9), (8.5, 14.5, 6.5, 6), (23.5, 14.5, 6.5, 6), (16, 7.5, 8, 6.5)]
    shade(im, mask_of(ells), (16, 11, 13, 11), ("l", "e", "E"), r, noise=.14, fleck=("l", .08))
    return outline(im)


def bush():
    r = random.Random(12)
    im = new(16, 16)
    ells = [(5, 9.5, 4, 3.5), (11, 9.5, 4, 3.5), (8, 7.5, 5, 4.5)]
    shade(im, mask_of(ells), (8, 8, 7, 6), ("l", "e", "E"), r, fleck=("l", .1))
    for (x, y) in ((5, 9), (10, 7), (8, 11)):
        px(im, x, y, "r")
    return outline(im)


def flowers():
    im = new(16, 16)
    for (x, y, c) in ((4, 4, "m"), (11, 3, "y"), (12, 9, "r"), (6, 8, "w"), (3, 12, "y"), (9, 13, "m")):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px(im, x + dx, y + dy, c)
        px(im, x, y, "y" if c != "y" else "o")
        px(im, x, y + 2, "e"); px(im, x - 1, y + 3, "E")
        if y + 3 < 16: px(im, x, y + 3, "e")
    return im


def rock():
    r = random.Random(13)
    im = new(16, 16)
    ells = [(8, 9.5, 6.5, 4.5), (5, 10.5, 3.5, 3)]
    shade(im, mask_of(ells), (8, 9, 7, 5), ("G", "g", "K"), r, noise=.1)
    px(im, 9, 8, "K"); px(im, 10, 9, "K"); px(im, 5, 9, "G"); px(im, 6, 8, "w")
    return outline(im)


def streetlamp():
    im = new(16, 32)
    rect(im, 5, 29, 10, 30, "K"); rect(im, 7, 9, 8, 29, "g"); rect(im, 8, 9, 8, 29, "K")
    rect(im, 4, 3, 11, 8, "K"); rect(im, 5, 4, 10, 8, "y"); rect(im, 5, 1, 10, 2, "K"); px(im, 6, 5, "w"); px(im, 6, 6, "w")
    rect(im, 9, 4, 10, 8, "Y")
    return outline(im)


def bench():
    im = new(32, 16)
    rect(im, 3, 6, 4, 14, "K"); rect(im, 27, 6, 28, 14, "K")
    rect(im, 2, 2, 29, 3, "u"); rect(im, 2, 4, 29, 5, "n")
    rect(im, 1, 8, 30, 8, "u"); rect(im, 1, 9, 30, 10, "n")
    return outline(im)


def trashcan():
    im = new(16, 16)
    rect(im, 4, 5, 11, 14, "G"); rect(im, 10, 5, 11, 14, "g")
    for x in (6, 8): rect(im, x, 7, x, 13, "g")
    rect(im, 3, 3, 12, 4, "g"); rect(im, 3, 3, 12, 3, "G"); rect(im, 7, 2, 8, 2, "K")
    return outline(im)


def signboard():
    im = new(16, 16)
    rect(im, 7, 9, 8, 14, "N")
    rect(im, 2, 1, 13, 9, "n"); rect(im, 3, 2, 12, 8, "w")
    for y, x1 in ((3, 11), (5, 9), (7, 11)):
        rect(im, 4, y, x1, y, "K")
    return outline(im)


def mailbox():
    im = new(16, 16)
    rect(im, 7, 9, 8, 14, "N")
    rect(im, 3, 3, 12, 9, "b"); rect(im, 3, 9, 12, 9, "B"); rect(im, 11, 4, 12, 8, "B"); rect(im, 3, 4, 4, 8, "B"); px(im, 6, 4, "c")
    rect(im, 12, 1, 13, 5, "r")
    return outline(im)


def trafficsign():
    im = new(16, 32)
    rect(im, 5, 30, 10, 30, "K"); rect(im, 7, 12, 8, 30, "G"); rect(im, 8, 12, 8, 30, "g")
    for (cx, cy, rx, ry, c) in ((8, 7, 6.5, 6.5, "w"), (8, 7, 5, 5, "r")):
        for (x, y) in mask_of([(cx, cy, rx, ry)]):
            px(im, x, y, c)
    rect(im, 5, 6, 10, 8, "w")
    return outline(im)


# ------------------------------------------------------------------ buildings
def window(im, x0, y0, x1, y1, frame="N", glass="c"):
    rect(im, x0, y0, x1, y1, frame)
    rect(im, x0 + 1, y0 + 1, x1 - 1, y1 - 1, glass)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    rect(im, mx, y0 + 1, mx, y1 - 1, frame); rect(im, x0 + 1, my, x1 - 1, my, frame)
    px(im, x0 + 1, y0 + 1, "w"); px(im, x0 + 2, y0 + 1, "w"); px(im, x0 + 1, y0 + 2, "w")


def door(im, x0, y0, body="n", frame="N"):
    rect(im, x0, y0, x0 + 15, y0 + 15, frame)
    rect(im, x0 + 2, y0 + 2, x0 + 13, y0 + 15, body)
    rect(im, x0 + 4, y0 + 4, x0 + 11, y0 + 8, "c"); px(im, x0 + 4, y0 + 4, "w"); px(im, x0 + 5, y0 + 4, "w")
    rect(im, x0 + 7, y0 + 4, x0 + 7, y0 + 8, frame)
    rect(im, x0 + 4, y0 + 10, x0 + 11, y0 + 14, "N" if body == "n" else "K")
    rect(im, x0 + 5, y0 + 11, x0 + 10, y0 + 14, body)
    px(im, x0 + 11, y0 + 9, "y")
    rect(im, x0, y0 + 15, x0 + 15, y0 + 15, "G")  # threshold


def make_house():
    im = new(48, 48)
    rect(im, 4, 20, 43, 47, "w")
    for y in range(24, 44, 4):
        rect(im, 4, y, 43, y, "G")
    rect(im, 4, 44, 43, 47, "g"); rect(im, 4, 44, 43, 44, "G")
    for y in range(3, 20):
        inset = round(8 * (19 - y) / 16)
        for x in range(1 + inset, 47 - inset):
            row = (y - 3) // 3
            c = "r"
            if (y - 3) % 3 == 2: c = "R"
            elif (x + (row % 2) * 3) % 6 == 0: c = "R"
            px(im, x, y, c)
    rect(im, 4, 20, 43, 21, "g")
    rect(im, 33, 0, 38, 9, "K"); rect(im, 33, 0, 34, 9, "g"); rect(im, 33, 0, 38, 1, "G")  # chimney
    window(im, 6, 26, 13, 37); window(im, 34, 26, 41, 37)
    for x0 in (6, 34):
        rect(im, x0 - 1, 38, x0 + 8, 39, "N")
        for i, c in enumerate("mryme"[:5]):
            px(im, x0 + i * 2 - 0, 37, c if i % 2 == 0 else "e")
    door(im, 16, 32)
    return outline(im)


FONT = {
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
}


def sign_board(im, text, bg, fg):
    rect(im, 18, 3, 44, 13, "k"); rect(im, 19, 4, 43, 12, bg)
    for i, ch in enumerate(text):
        for y, row in enumerate(FONT[ch]):
            for x, b in enumerate(row):
                if b == "1":
                    px(im, 20 + i * 6 + x, 5 + y, fg)


def storefront(wall, wall2, para, awn_a, awn_b, text, board_bg, board_fg, items, right):
    im = new(64, 48)
    rect(im, 1, 18, 62, 47, wall)
    for y in range(21, 46, 4):
        rect(im, 1, y, 62, y, wall2)
    rect(im, 1, 1, 62, 17, para); rect(im, 1, 1, 62, 1, "G"); rect(im, 1, 16, 62, 17, "g")
    rect(im, 4, 8, 15, 8, "g"); rect(im, 48, 8, 59, 8, "g")
    for x in range(2, 62):
        c = awn_a if ((x - 2) // 4) % 2 == 0 else awn_b
        for y in range(22, 31):
            px(im, x, y, c)
        if (x - 2) % 4 in (1, 2):
            px(im, x, 31, c)
        px(im, x, 22, "G")
    rect(im, 2, 32, 61, 33, wall2)
    rect(im, 1, 45, 62, 47, "g"); rect(im, 1, 45, 62, 45, "G")
    window(im, 5, 35, 28, 44, frame="N")
    rect(im, 6, 41, 27, 41, "N")
    for (x, y, w, h, c) in items:
        rect(im, x, y, x + w - 1, y + h - 1, c); rect(im, x, y, x + w - 1, y, "w") if h > 2 else None
    right(im)
    door(im, 32, 32, body="K", frame="N")
    rect(im, 36, 41, 43, 42, "r")  # open sign
    sign_board(im, text, board_bg, board_fg)
    return outline(im)


def shop_right(im):
    window(im, 51, 35, 58, 44)
    rect(im, 52, 40, 57, 43, "w"); rect(im, 53, 41, 56, 42, "m")


def cafe_right(im):
    rect(im, 50, 34, 59, 45, "N"); rect(im, 51, 35, 58, 44, "K")
    for y in (37, 39, 41):
        rect(im, 52, y, 56 if y != 39 else 54, y, "w")
    px(im, 57, 43, "y"); px(im, 55, 42, "m")
    rect(im, 49, 45, 60, 46, "N")


def sign_icon(kind):
    im = new(16, 16)
    rect(im, 1, 0, 14, 15, "k"); rect(im, 0, 1, 15, 14, "k")
    rect(im, 1, 1, 14, 14, "y" if kind == "shop" else "w"); rect(im, 1, 1, 14, 1, "w" if kind == "shop" else "G")
    fg = new(16, 16)
    if kind == "shop":
        rect(fg, 4, 6, 11, 12, "r"); rect(fg, 4, 12, 11, 12, "R"); rect(fg, 10, 6, 11, 12, "R")
        for (x, y) in ((6, 5), (6, 4), (7, 3), (8, 3), (9, 4), (9, 5)):
            px(fg, x, y, "R")
        px(fg, 6, 8, "w")
        outline(fg)
    else:
        rect(fg, 4, 7, 10, 11, "w"); rect(fg, 5, 12, 9, 12, "w"); rect(fg, 9, 8, 10, 11, "G")
        rect(fg, 11, 8, 12, 10, "w"); px(fg, 12, 9, "_")
        rect(fg, 5, 7, 9, 7, "N")
        outline(fg)
        px(fg, 6, 4, "G"); px(fg, 7, 3, "G"); px(fg, 6, 2, "G"); px(fg, 9, 4, "G"); px(fg, 8, 3, "G")
    im.alpha_composite(fg)
    return im


def gazebo():
    im = new(48, 48)
    # floor platform
    rect(im, 2, 38, 45, 47, "u")
    for y in (41, 44): rect(im, 2, y, 45, y, "n")
    rect(im, 2, 44, 45, 47, "g"); rect(im, 2, 44, 45, 44, "G"); rect(im, 16, 44, 31, 47, "G"); rect(im, 16, 46, 31, 46, "g")
    # back area
    rect(im, 9, 26, 38, 37, "K")
    for x in range(10, 38, 3): rect(im, x, 27, x, 36, "k")
    # posts + railings
    for x0 in (6, 39):
        rect(im, x0, 24, x0 + 2, 43, "w"); rect(im, x0 + 2, 24, x0 + 2, 43, "G")
    rect(im, 9, 34, 15, 34, "w"); rect(im, 32, 34, 38, 34, "w")
    for x in range(10, 16, 2): rect(im, x, 35, x, 42, "G")
    for x in range(33, 39, 2): rect(im, x, 35, x, 42, "G")
    rect(im, 9, 43, 15, 43, "g"); rect(im, 32, 43, 38, 43, "g")
    # roof cone
    for y in range(2, 24):
        half = 1 + (y - 2) * 22 / 21
        for x in range(int(24 - half), int(24 + half) + 1):
            u = (x + .5 - 24) / half
            seg = int((u + 1) * 3)
            px(im, x, y, "r" if seg % 2 == 0 else "R")
    rect(im, 1, 22, 46, 23, "R"); rect(im, 4, 24, 43, 25, "K")
    rect(im, 23, 0, 24, 3, "Y")
    return outline(im)


# ------------------------------------------------------------------ interiors / furniture / items
def interior_wall(variant):
    im = new(T, T)
    for y in range(T):
        for x in range(T):
            if variant == 0:
                if y == 0: c = "K"
                elif y < 11: c = "w" if x % 8 in (2, 3) else "u"
                elif y == 11: c = "N"
                elif y < 15: c = "N" if x % 4 == 0 else "n"
                else: c = "N"
            else:
                if y == 0: c = "K"
                elif y < 11: c = "c" if (x % 8 == 3 and y % 4 == 2) or (x % 8 == 7 and y % 4 == 0) else "b"
                elif y == 11: c = "w"
                elif y < 15: c = "G" if x % 4 == 0 else "w"
                else: c = "g"
            px(im, x, y, c)
    return im


def bed():
    im = new(16, 32)
    rect(im, 1, 1, 14, 30, "N"); rect(im, 2, 2, 13, 4, "n"); rect(im, 2, 5, 13, 29, "w")
    rect(im, 4, 6, 11, 11, "G"); rect(im, 4, 6, 11, 10, "w")
    rect(im, 2, 14, 13, 29, "b"); rect(im, 2, 14, 13, 15, "c"); rect(im, 10, 16, 13, 29, "B")
    for y in (20, 25): rect(im, 3, y, 9, y, "B")
    return outline(im)


def table():
    im = new(16, 16)
    rect(im, 2, 13, 3, 14, "N"); rect(im, 12, 13, 13, 14, "N")
    rect(im, 1, 11, 14, 12, "N"); rect(im, 1, 2, 14, 10, "n"); rect(im, 1, 2, 14, 3, "u"); rect(im, 2, 6, 6, 6, "u")
    return outline(im)


def chair():
    im = new(16, 16)
    rect(im, 4, 12, 5, 14, "N"); rect(im, 10, 12, 11, 14, "N")
    rect(im, 4, 7, 11, 11, "n"); rect(im, 4, 7, 11, 7, "u")
    rect(im, 4, 2, 11, 6, "N"); rect(im, 5, 3, 10, 5, "n")
    return outline(im)


def counter():
    im = new(32, 16)
    rect(im, 1, 8, 30, 14, "n"); rect(im, 1, 3, 30, 8, "u"); rect(im, 1, 8, 30, 8, "Y")
    for x in range(3, 30, 6): rect(im, x, 10, x + 3, 13, "N")
    rect(im, 20, 1, 28, 6, "g"); rect(im, 21, 1, 24, 2, "c"); rect(im, 21, 4, 27, 5, "G"); rect(im, 26, 1, 28, 2, "K")
    rect(im, 4, 4, 9, 6, "w"); px(im, 5, 5, "y"); px(im, 7, 5, "r")
    return outline(im)


def shelf():
    im = new(16, 32)
    rect(im, 1, 1, 14, 30, "N"); rect(im, 2, 2, 13, 29, "n")
    for y in (10, 20): rect(im, 2, y, 13, y + 1, "N")
    cols = ["r", "b", "y", "e", "m", "o", "c", "p"]
    r = random.Random(14)
    for y0 in (3, 12, 22):
        x = 3
        while x < 12:
            w = r.choice([2, 3]); h = r.choice([4, 5])
            rect(im, x, y0 + 7 - h, min(x + w - 1, 12), y0 + 6, r.choice(cols)); x += w + 1
    return outline(im)


def lamp():
    im = new(16, 16)
    rect(im, 7, 8, 8, 13, "K"); rect(im, 5, 13, 10, 14, "K")
    for y, (x0, x1) in enumerate([(5, 10), (4, 11), (4, 11), (3, 12), (3, 12), (3, 12)]):
        rect(im, x0, 2 + y, x1, 2 + y, "y")
    rect(im, 3, 7, 12, 7, "Y"); rect(im, 5, 3, 6, 4, "w"); rect(im, 11, 3, 12, 7, "Y")
    return outline(im)


def coffee():
    im = new(16, 16)
    rect(im, 3, 7, 10, 12, "w"); rect(im, 4, 13, 9, 13, "w"); rect(im, 9, 8, 10, 12, "G")
    rect(im, 11, 8, 13, 11, "w"); px(im, 12, 9, "_"); px(im, 12, 10, "_")
    rect(im, 4, 7, 9, 8, "N"); rect(im, 5, 7, 6, 7, "n")
    rect(im, 2, 14, 12, 14, "G")
    outline(im)
    for (x, y) in ((5, 4), (6, 3), (5, 2), (8, 4), (9, 3), (8, 2)):
        px(im, x, y, "G")
    return im


def bread():
    r = random.Random(15)
    im = new(16, 16)
    shade(im, mask_of([(8, 9.5, 6.5, 4.5)]), (8, 9, 7, 5), ("y", "Y", "n"), r, noise=.08)
    for x in (5, 8, 11):
        px(im, x, 7, "u"); px(im, x + 1, 8, "u")
    return outline(im)


def apple():
    r = random.Random(16)
    im = new(16, 16)
    shade(im, mask_of([(8, 9.5, 5.5, 5)]), (8, 9, 6, 5.5), ("m", "r", "R"), r, noise=.06)
    px(im, 5, 7, "w"); px(im, 5, 8, "w"); rect(im, 7, 3, 8, 5, "N"); rect(im, 9, 3, 11, 4, "e"); px(im, 11, 3, "l")
    px(im, 8, 5, "R")
    return outline(im)


def bento():
    im = new(16, 16)
    rect(im, 1, 3, 14, 13, "N"); rect(im, 2, 4, 13, 12, "K")
    rect(im, 2, 4, 7, 12, "w"); px(im, 3, 6, "G"); px(im, 5, 9, "G"); px(im, 6, 5, "G"); px(im, 4, 11, "G"); px(im, 4, 7, "k")
    rect(im, 8, 4, 8, 12, "N")
    rect(im, 9, 4, 12, 6, "y"); rect(im, 10, 5, 11, 5, "o")
    rect(im, 9, 8, 12, 9, "o"); rect(im, 9, 11, 12, 12, "e"); px(im, 10, 11, "l"); px(im, 12, 8, "r")
    return outline(im)


def sandwich():
    im = new(16, 16)
    rect(im, 2, 4, 13, 6, "u"); rect(im, 3, 3, 12, 3, "u"); rect(im, 2, 4, 13, 4, "y")
    rect(im, 1, 7, 14, 7, "l"); rect(im, 2, 8, 13, 8, "r"); rect(im, 1, 9, 14, 9, "y"); rect(im, 2, 10, 13, 10, "m")
    rect(im, 2, 11, 13, 13, "u"); rect(im, 2, 13, 13, 13, "Y")
    return outline(im)


def shirt():
    im = new(16, 16)
    rect(im, 4, 4, 11, 13, "b"); rect(im, 1, 4, 3, 7, "b"); rect(im, 12, 4, 14, 7, "b")
    rect(im, 6, 4, 9, 4, "_"); rect(im, 5, 5, 10, 5, "B"); rect(im, 6, 5, 9, 5, "c")
    rect(im, 10, 6, 11, 13, "B"); rect(im, 13, 5, 14, 7, "B"); rect(im, 1, 7, 3, 7, "B")
    px(im, 5, 8, "c"); px(im, 5, 9, "c")
    return outline(im)


def flower_item():
    im = new(16, 16)
    pts = ((8, 4, "m"), (4, 6, "r"), (12, 6, "y"))
    for (x, y, c) in pts:
        for (px_, py_) in mask_of([(x, y, 2.6, 2.6)]):
            px(im, px_, py_, c)
        px(im, x, y, "y" if c != "y" else "o")
    for x0 in (8, 5, 11):
        for y in range(7, 10): px(im, x0 + (8 - x0) * (y - 7) // 4, y, "e")
    for y in range(9, 15):
        half = (y - 8) * 6 // 6 + 1
        rect(im, 8 - half, y, 7 + half, y, "w")
    rect(im, 5, 11, 6, 11, "G"); rect(im, 3, 13, 12, 14, "G"); rect(im, 8, 10, 8, 14, "m")
    return outline(im)


def book():
    im = new(16, 16)
    rect(im, 2, 2, 12, 13, "r"); rect(im, 2, 2, 3, 13, "R"); rect(im, 13, 3, 14, 13, "w"); rect(im, 3, 13, 14, 13, "w")
    rect(im, 2, 13, 12, 13, "R"); rect(im, 5, 5, 10, 6, "y"); rect(im, 5, 8, 9, 8, "y"); rect(im, 13, 5, 14, 5, "G")
    return outline(im)


def gift():
    im = new(16, 16)
    rect(im, 2, 7, 13, 14, "r"); rect(im, 2, 13, 13, 14, "R"); rect(im, 1, 5, 14, 8, "m"); rect(im, 1, 8, 14, 8, "R")
    rect(im, 7, 5, 8, 14, "y")
    rect(im, 4, 2, 6, 4, "y"); rect(im, 9, 2, 11, 4, "y"); px(im, 5, 3, "_"); px(im, 10, 3, "_"); rect(im, 7, 4, 8, 4, "Y")
    return outline(im)


# ------------------------------------------------------------------ build outputs
def build():
    # --- MAP_001 ground
    ground = [("GrassA", grid_img(GRASS_A)), ("GrassB", grid_img(GRASS_B)), ("Dirt", grid_img(DIRT)),
              ("Sidewalk", grid_img(SIDE)), ("FloorWood", grid_img(WOOD)), ("FloorTile", grid_img(FLOOR))]
    out(strip([i for _, i in ground]), "maps/tilesets/MAP_001_Ground_Tileset_v01.png")
    for n, i in ground:
        out(i, f"maps/tilesets/MAP_001_{n}_Tile_v01.png")
    out_json({"tile_size": T, "columns": len(ground), "tiles": {str(i): n.lower() for i, (n, _) in enumerate(ground)}},
             "maps/tilesets/MAP_001_Ground_Tileset_v01.json")

    # --- MAP_002 road
    rt = {}
    rt["road_h"] = road_tile("WE"); rt["road_v"] = road_tile("NS")
    rt["corner_es"] = road_tile("ES"); rt["corner_sw"] = road_tile("SW")
    rt["corner_ne"] = road_tile("NE"); rt["corner_nw"] = road_tile("NW")
    for n in ("t_nes", "t_esw", "t_nsw", "t_new", "crossroad"):
        rt[n] = road_tile()
    rt["crosswalk_h"] = crosswalk(True); rt["crosswalk_v"] = crosswalk(False)
    rt["curb_top"] = curb_tile("t"); rt["curb_bottom"] = curb_tile("b")
    rt["curb_left"] = curb_tile("l"); rt["curb_right"] = curb_tile("r")
    rt["curb_corner_tl"] = curb_tile("tl"); rt["curb_corner_tr"] = curb_tile("tr")
    rt["curb_corner_bl"] = curb_tile("bl"); rt["curb_corner_br"] = curb_tile("br")
    rt["path_edge_top"] = path_tile("t"); rt["path_edge_bottom"] = path_tile("b")
    rt["path_edge_left"] = path_tile("l"); rt["path_edge_right"] = path_tile("r")
    rt["path_corner_tl"] = path_tile("tl"); rt["path_corner_tr"] = path_tile("tr")
    rt["path_corner_bl"] = path_tile("bl"); rt["path_corner_br"] = path_tile("br")
    rt["path_h"] = path_tile("tb"); rt["path_v"] = path_tile("lr")
    cols = 8
    rows = (len(rt) + cols - 1) // cols
    sheet = new(cols * T, rows * T)
    for i, im in enumerate(rt.values()):
        sheet.paste(im, ((i % cols) * T, (i // cols) * T))
    out(sheet, "maps/tilesets/MAP_002_Road_Tileset_v01.png")
    out_json({"tile_size": T, "columns": cols, "rows": rows,
              "note": "t_xxx = open sides; curb_<side> = sidewalk tile with its curb on that side (road lies beyond it); "
                      "path_edge_<side> = dirt tile with grass on that side; path_h/path_v = 1-tile-wide dirt path",
              "tiles": {str(i): n for i, n in enumerate(rt)}}, "maps/tilesets/MAP_002_Road_Tileset_v01.json")

    # --- MAP_010 blockers
    bl = [("brick_wall", brick_wall()), ("fence_h", fence_h()), ("fence_v", fence_v()), ("hedge", hedge()),
          ("water_0", water(0)), ("water_1", water(1))]
    out(strip([i for _, i in bl]), "maps/tilesets/MAP_010_Blockers_v01.png")
    out_json({"tile_size": T, "columns": len(bl), "impassable": True,
              "note": "fence tiles have transparent background (draw over grass); water_0/water_1 are animation frames",
              "tiles": {str(i): n for i, (n, _) in enumerate(bl)}}, "maps/tilesets/MAP_010_Blockers_v01.json")
    for n, i in bl:
        pass

    # --- MAP_005 / MAP_006
    obj = {}
    obj["tree"] = tree(); obj["bush"] = bush(); obj["flowers"] = flowers(); obj["rock"] = rock()
    for n, f in (("tree", "Tree"), ("bush", "Bush"), ("flowers", "FlowerPatch"), ("rock", "Rock")):
        out(obj[n], f"maps/urban/MAP_005_Nature_{f}_v01.png")
    for n, f, fn in (("lamp", "Streetlamp", streetlamp), ("bench", "Bench", bench), ("trash", "TrashCan", trashcan),
                     ("signboard", "Signboard", signboard), ("mailbox", "Mailbox", mailbox),
                     ("trafficsign", "TrafficSign", trafficsign)):
        obj[n] = fn()
        out(obj[n], f"maps/urban/MAP_006_Deco_{f}_v01.png")

    # --- buildings
    sh_sign, cf_sign = sign_icon("shop"), sign_icon("cafe")
    out(sh_sign, "buildings/shops/BLD_005_Sign_Shop_v01.png")
    out(cf_sign, "buildings/workplaces/BLD_005_Sign_Cafe_v01.png")
    house = make_house()
    shop = storefront("u", "n", "K", "r", "w", "SHOP", "r", "w",
                      [(7, 38, 3, 3, "r"), (12, 37, 3, 4, "y"), (17, 38, 3, 3, "m"), (22, 36, 4, 5, "e")], shop_right)
    cafe = storefront("n", "N", "n", "o", "w", "CAFE", "N", "w",
                      [(8, 39, 3, 2, "w"), (13, 39, 3, 2, "w"), (18, 39, 3, 2, "w"), (23, 38, 3, 3, "u")], cafe_right)
    gaz = gazebo()
    out(house, "buildings/houses/BLD_001_House_v01.png")
    out(shop, "buildings/shops/BLD_002_Shop_v01.png")
    out(cafe, "buildings/workplaces/BLD_003_Cafe_v01.png")
    out(gaz, "buildings/social/BLD_004_Park_Gazebo_v01.png")

    def col(w, h, door_x):
        rows_ = ["#" * w for _ in range(h)]
        rows_[-1] = "#" * door_x + "D" + "#" * (w - door_x - 1)
        return rows_
    binfo = {}
    for name, path, im, dx in (("BLD_001_House", "houses/BLD_001_House_v01.png", house, 1),
                               ("BLD_002_Shop", "shops/BLD_002_Shop_v01.png", shop, 2),
                               ("BLD_003_Cafe", "workplaces/BLD_003_Cafe_v01.png", cafe, 2),
                               ("BLD_004_Park_Gazebo", "social/BLD_004_Park_Gazebo_v01.png", gaz, 1)):
        w, h = im.width // T, im.height // T
        binfo[name] = {"image": path, "size_px": [im.width, im.height], "footprint_tiles": [w, h],
                       "door_tile": [dx, h - 1], "entry_tile": [dx, h],
                       "collision": col(w, h, dx)}
    out_json({"tile_size": T, "anchor": "bottom-left of footprint; tile offsets are (col,row) from footprint top-left",
              "legend": {"#": "blocked", "D": "door/entry trigger (walk from entry_tile north into it)"},
              "buildings": binfo}, "buildings/collision.json")

    # --- interiors / furniture / food / products
    w0, w1 = interior_wall(0), interior_wall(1)
    out(w0, "maps/interiors/MAP_007_Interior_Wall_A_v01.png")
    out(w1, "maps/interiors/MAP_007_Interior_Wall_B_v01.png")
    out(strip([w0, w1]), "maps/interiors/MAP_007_Interior_Wall_v01.png")
    for n, fn in (("Bed", bed), ("Table", table), ("Chair", chair), ("Counter", counter), ("Shelf", shelf), ("Lamp", lamp)):
        out(fn(), f"objects/furniture/BLD_006_{n}_v01.png")
    for n, fn in (("Coffee", coffee), ("Bread", bread), ("Apple", apple), ("Bento", bento), ("Sandwich", sandwich)):
        out(fn(), f"objects/food/OBJ_003_{n}_v01.png")
    for n, fn in (("Shirt", shirt), ("Flower", flower_item), ("Book", book), ("Gift", gift)):
        out(fn(), f"objects/products/OBJ_004_{n}_v01.png")

    return rt, bl, obj, house, shop, cafe, gaz


def demo(rt, bl, obj, house, shop, cafe, gaz):
    W, H = 20, 15
    cv = new(W * T, H * T)
    rng = random.Random(21)
    g_a, g_b = grid_img(GRASS_A), grid_img(GRASS_B)
    place = {}

    def put(c, r, name):
        place[(c, r)] = name
    for r in range(H):
        for c in range(W):
            put(c, r, "grassb" if rng.random() < .25 else "grassa")
    for c in range(W):
        put(c, 10, "road_h"); put(c, 11, "curb_top")
        if c != 10: put(c, 9, "curb_bottom")
        put(c, 12, "hedge"); put(c, 14, "wall")
    for r in range(0, 10): put(10, r, "road_v")
    put(10, 8, "crosswalk_v"); put(8, 10, "crosswalk_h"); put(10, 10, "t_new")
    for r in range(0, 9):
        put(9, r, "curb_right"); put(11, r, "curb_left")
    put(9, 9, "curb_corner_br"); put(11, 9, "curb_corner_bl")
    for c in range(W):
        pass
    put(10, 12, "path_v"); put(10, 13, "path_v"); put(10, 14, "path_v")
    # house yard
    put(2, 7, "path_v"); put(2, 8, "path_v")
    for c in (0, 1, 3, 4): put(c, 8, "fence_h")
    for r in range(4, 8): put(0, r, "fence_v")
    for r in range(5, 8): put(4, r, "fence_v")
    # gazebo plaza
    put(5, 7, "path_corner_tl"); put(6, 7, "path_edge_top"); put(7, 7, "path_corner_tr")
    put(5, 8, "path_edge_left"); put(6, 8, "dirt"); put(7, 8, "path_edge_right")
    # pond
    for r in (0, 1):
        for c in (2, 3, 4): put(c, r, "water")
    tiles = {"grassa": g_a, "grassb": g_b, "dirt": grid_img(DIRT), "hedge": bl[3][1], "wall": bl[0][1],
             "water": bl[4][1]}
    tiles.update(rt)
    # fences/hedge/wall: fences need grass under
    for (c, r), n in sorted(place.items()):
        if n.startswith("fence"):
            cv.paste(g_a, (c * T, r * T))
            cv.alpha_composite(bl[1][1] if n == "fence_h" else bl[2][1], (c * T, r * T))
        else:
            cv.paste(tiles[n], (c * T, r * T))
    # pond rim: 1px darker inner edge + sand outer ring
    wm = {(c, r) for (c, r), n in place.items() if n == "water"}
    pxs = cv.load()
    def inwater(x, y): return (x // T, y // T) in wm
    snap = [(x, y) for y in range(H * T) for x in range(W * T)]
    for (x, y) in snap:
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= x + dx < W * T and 0 <= y + dy < H * T]
        if inwater(x, y) and any(not inwater(a, b) for a, b in nb):
            pxs[x, y] = P["B"]
    for (x, y) in snap:
        if not inwater(x, y):
            nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < W * T and 0 <= y + dy < H * T]
            if any(inwater(a, b) for a, b in nb):
                pxs[x, y] = P["u"]

    objs = []  # (col, bottom_row, image)

    def add(c, r, im): objs.append((c, r, im))
    add(1, 6, house); add(5, 6, gaz); add(12, 8, shop); add(16, 8, cafe)
    for c, r in ((6, 1), (13, 3), (17, 2), (18, 5), (1, 13), (6, 13), (16, 13)): add(c, r, obj["tree"])
    for c, r in ((5, 2), (13, 5), (8, 4), (3, 13), (12, 13)): add(c, r, obj["bush"])
    for c, r in ((1, 7), (3, 7), (8, 8), (14, 4), (4, 13), (15, 13), (19, 3)): add(c, r, obj["flowers"])
    for c, r in ((1, 1), (5, 1), (15, 2), (9, 13)): add(c, r, obj["rock"])
    add(9, 3, obj["lamp"]); add(11, 6, obj["lamp"]); add(11, 9, obj["trafficsign"])
    add(3, 9, obj["bench"]); add(12, 9, obj["bench"]); add(1, 9, obj["mailbox"])
    add(15, 9, obj["signboard"]); add(19, 9, obj["trash"]); add(6, 11, obj["lamp"]) if False else None
    objs.sort(key=lambda o: (o[1], o[0]))
    for c, r, im in objs:
        cv.alpha_composite(im, (c * T, (r + 1) * T - im.height))
    out(cv, "maps/MAP_DEMO_StarterBlock_v01.png")
    return cv


if __name__ == "__main__":
    rt, bl, obj, house, shop, cafe, gaz = build()
    cv = demo(rt, bl, obj, house, shop, cafe, gaz)
    print(f"files written: {len(FILES)}")
