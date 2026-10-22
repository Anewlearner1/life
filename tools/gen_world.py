#!/usr/bin/env python3
"""Generate world assets (art v2, concept-sheet style): tilesets, blockers, urban objects, buildings, interiors,
furniture, food, products, demo scene. Deterministic (fixed seeds). Usage: python3 tools/gen_world.py

Colors come from the concept palette CP (see assets/reference/concept_palette.png) plus a few exact extras sampled from
the concept sheet (roofs/awnings/brick).  Single-char keys: see Q below."""
import sys, json, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image
from pixel import CP, TILE, ASSETS, save, strip

T = TILE
FILES = []

# Concept palette + a few sampled extras
Q = dict(CP)
Q.update({
    "!": (240, 116, 65, 255),    # orange (cafe roof / awning)
    "@": (250, 136, 78, 255),    # light orange
    "#": (182, 85, 56, 255),     # roof / brick mid
    "$": (122, 58, 42, 255),     # roof / brick dark
    "%": (168, 101, 98, 255),    # cafe board
    "&": (138, 74, 62, 255),     # brick dark
})
# Cheat sheet:
# grays 0 (outline) 1 2 3 4 5 6 7 8 9(white) | browns A(darkest) D E F G H J L M N(cream) | yellow K I
# red B C | greens T U R S O(pale) | blues c d e f g h j l o p t v x z (light) | extras ! @ # $ % &


# ------------------------------------------------------------------ helpers
def new(w, h):
    return Image.new("RGBA", (w, h), Q["_"])


def px(im, x, y, k):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), Q[k])


def rect(im, x0, y0, x1, y1, k):  # inclusive corners
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(im, x, y, k)


def outline(im, k="0"):
    src = im.copy()
    sp, op = src.load(), im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            if sp[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and sp[nx, ny][3]:
                        op[x, y] = Q[k]
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
    """3-tone ellipse shading, light from the top-left."""
    cx, cy, rx, ry = c
    light, mid, dark = tones
    for x, y in sorted(mask):
        v = -((x + .5 - cx) / rx) * .55 - ((y + .5 - cy) / ry) * .75 + rng.uniform(-noise, noise)
        k = light if v > .38 else dark if v < -.25 else mid
        if fleck and k == mid and rng.random() < fleck[1]:
            k = fleck[0]
        px(im, x, y, k)


def clump(im, cx, cy, rx, ry, rng, tones="OSRUT", fleck=.1):
    """Leafy blob: highlight top-left, shadow bottom, darkest rim underneath (layered-green look)."""
    hi, base, mid, dark, deep = tones
    m = mask_of([(cx, cy, rx, ry)])
    for (x, y) in sorted(m):
        v = -((x + .5 - cx) / rx) * .45 - ((y + .5 - cy) / ry) * .85 + rng.uniform(-.1, .1)
        if (x, y + 1) not in m:
            k = deep
        elif v > .72:
            k = hi
        elif v > .28:
            k = base
        elif v > -.3:
            k = mid
        else:
            k = dark
        if k == base and rng.random() < fleck:
            k = hi
        elif k == mid and rng.random() < fleck:
            k = dark
        elif k == dark and rng.random() < fleck:
            k = mid
        px(im, x, y, k)
    return m


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
GRASS_A = noise_grid(1, "S", [("O", .07), ("R", .06), ("U", .012)])
GRASS_B = noise_grid(2, "S", [("O", .05), ("R", .05), ("U", .015)])
for (x, y) in ((3, 4), (10, 11), (12, 3)):   # little grass tufts
    GRASS_B[y][x] = "R"; GRASS_B[y - 1][x - 1] = "R"; GRASS_B[y - 1][x + 1] = "R"; GRASS_B[y + 1][x] = "U"
for (x, y, c) in ((5, 12, "9"), (13, 8, "I")):   # tiny flowers
    GRASS_B[y][x] = c; GRASS_B[y][x + 1 if x < 14 else x - 1] = "I" if c == "9" else "9"
DIRT = noise_grid(3, "G", [("F", .09), ("H", .07), ("J", .03), ("E", .02)])
ASPH = noise_grid(4, "3", [("2", .06), ("4", .05)])


def sidewalk_grid():
    """Light gray cobblestones, 8x8 stones laid in offset rows, 1px dark joints, top-left stone highlight."""
    r = random.Random(5)
    g = [["6"] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            band = y // 8
            jx = (x % 8 == 7) if band == 0 else (x % 8 == 3)
            if y % 8 == 7 or jx:
                g[y][x] = "4"
            elif y % 8 == 0 or (x % 8 == 0 and band == 0) or (x % 8 == 4 and band == 1):
                g[y][x] = "8"
            elif r.random() < .07:
                g[y][x] = "7"
            elif r.random() < .04:
                g[y][x] = "5"
    return g


SIDE = sidewalk_grid()


def wood_grid():
    r = random.Random(6)
    g = [["G"] * T for _ in range(T)]
    for y in range(T):
        b = y // 4
        for x in range(T):
            if y % 4 == 3:
                g[y][x] = "E"
            elif y % 4 == 0:
                g[y][x] = "H"
            elif x in ((b * 5) % 16, (b * 5 + 8) % 16):
                g[y][x] = "F"
            elif r.random() < .07:
                g[y][x] = "J"
    return g


def floor_tile_grid():
    r = random.Random(7)
    g = [["L"] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            if x % 8 == 7 or y % 8 == 7:
                g[y][x] = "J"
            elif x % 8 == 0 or y % 8 == 0:
                g[y][x] = "M"
            elif r.random() < .05:
                g[y][x] = "M"
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
                    cand = (d, "2")
                elif d < face + 2:
                    cand = (d, "8")
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
    im = grid_img(ASPH)
    for a in arms:
        x0, y0, x1, y1 = ARMS[a]
        rect(im, x0, y0, x1, y1, "I")
        if y0 == y1 - 1 and x1 - x0 > 1:   # horizontal arm: light top row
            rect(im, x0, y0, x1, y0, "K")
        elif x1 == x0 + 1:
            rect(im, x0, y0, x0, y1, "K")
    return im


def crosswalk(horizontal_road):
    im = grid_img(ASPH)
    for i in range(4):
        o = 1 + i * 4
        if horizontal_road:
            rect(im, 2, o, 13, o + 1, "9"); rect(im, 2, o + 1, 13, o + 1, "7")
        else:
            rect(im, o, 2, o + 1, 13, "9"); rect(im, o + 1, 2, o + 1, 13, "7")
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
                        g[y][x] = "U"
    return grid_img(g)


# ------------------------------------------------------------------ blockers
def brick_wall():
    """Gray stone wall: light cap, two brick courses, dark base."""
    r = random.Random(8)
    im = new(T, T)
    for x in range(T):
        px(im, x, 0, "0"); px(im, x, 1, "9"); px(im, x, 2, "8"); px(im, x, 3, "7"); px(im, x, 4, "4"); px(im, x, 5, "0")
        for y in range(6, 14):
            band = 0 if y < 10 else 1
            mortar = (y in (9, 13)) or ((band == 0 and x in (3, 11)) or (band == 1 and x in (7, 15)))
            c = "3" if mortar else "5"
            if not mortar and y in (6, 10):
                c = "6"
            elif not mortar and r.random() < .12:
                c = "4"
            px(im, x, y, c)
        px(im, x, 14, "2"); px(im, x, 15, "0")
    return im


def fence_h():
    im = new(T, T)
    for x in range(T):
        for y0 in (5, 10):
            px(im, x, y0, "J"); px(im, x, y0 + 1, "G"); px(im, x, y0 + 2, "E")
    # post
    rect(im, 6, 2, 9, 14, "G"); rect(im, 6, 2, 9, 3, "J"); rect(im, 6, 2, 6, 14, "H"); rect(im, 9, 4, 9, 14, "E")
    px(im, 7, 2, "L")
    return outline(im, "A")


def fence_v():
    im = new(T, T)
    for y in range(T):
        px(im, 6, y, "J"); px(im, 7, y, "G"); px(im, 8, y, "G"); px(im, 9, y, "E")
    for y0 in (1, 9):
        rect(im, 4, y0, 11, y0 + 5, "G"); rect(im, 4, y0, 11, y0 + 1, "J"); rect(im, 11, y0 + 2, 11, y0 + 5, "E")
        rect(im, 4, y0 + 2, 4, y0 + 5, "H")
    return outline(im, "A")


def hedge():
    r = random.Random(9)
    im = new(T, T)
    for y in range(T):
        for x in range(T):
            if y < 5:
                c = "S" if r.random() < .55 else "R"
            elif y < 11:
                c = "R" if r.random() < .75 else "U"
            else:
                c = "U" if r.random() < .75 else "T"
            px(im, x, y, c)
    for (x, y) in ((3, 2), (10, 3), (6, 7), (13, 8)):
        rect(im, x, y, x + 1, y + 1, "O")
    for x in range(T):
        px(im, x, 0, "0"); px(im, x, 15, "0")
        if x % 4 in (0, 3):
            px(im, x, 1, "T") if False else None
    for x in range(T):
        px(im, x, 14, "T")
    return im


def water(frame):
    im = new(T, T)
    r = random.Random(10)
    for y in range(T):
        for x in range(T):
            px(im, x, y, "l" if r.random() < .08 else "o" if r.random() < .5 else "p")
    dashes = [(2, 3), (9, 7), (4, 11), (12, 14)] if frame == 0 else [(6, 3), (13, 7), (8, 11), (0, 14)]
    for (x, y) in dashes:
        for i in range(3):
            px(im, (x + i) % T, y, "x")
    sx, sy = (10, 2) if frame == 0 else (3, 9)
    px(im, sx, sy, "9"); px(im, sx + 1, sy, "z")
    return im


# ------------------------------------------------------------------ nature & decorations
TG = "SRUTT"   # tree greens (mid-green dominant, like the concept)
TH = "OSRUT"   # highlight clump


def tree():
    """32x40 round chunky tree: layered clumps, short trunk with roots (footprint 2x2, image extends above)."""
    r = random.Random(11)
    im = new(32, 40)
    # trunk + roots
    rect(im, 13, 28, 18, 37, "F"); rect(im, 13, 28, 14, 37, "H"); rect(im, 17, 28, 18, 37, "E"); rect(im, 15, 30, 15, 36, "G")
    rect(im, 11, 36, 20, 38, "E"); rect(im, 12, 36, 14, 36, "F"); rect(im, 11, 38, 20, 38, "D"); rect(im, 16, 35, 16, 35, "E")
    rect(im, 12, 37, 12, 37, "F")
    clump(im, 16, 14, 14.5, 12, r, TG)                     # back crown
    clump(im, 8.5, 19, 8.5, 7.5, r, TG)                    # left
    clump(im, 23.5, 19, 8.5, 7.5, r, TG)                   # right
    clump(im, 14, 9.5, 8.5, 6.5, r, TH)                    # top highlight cluster
    clump(im, 16, 23, 11, 6.5, r, TG)                      # front-low
    return outline(im)


def bush():
    r = random.Random(12)
    im = new(16, 16)
    rect(im, 7, 12, 8, 14, "E"); px(im, 7, 12, "F")
    clump(im, 8, 8.5, 7, 5.5, r, TH)
    clump(im, 4.5, 10, 4.5, 3.8, r, TG)
    clump(im, 11.5, 10, 4.5, 3.8, r, TG)
    return outline(im)


def flowers():
    im = new(16, 16)
    r = random.Random(17)
    for (x, y) in ((3, 11), (8, 12), (12, 10), (6, 8), (11, 6)):   # leaf tufts
        for dx, dy, k in ((0, 0, "U"), (-1, 1, "R"), (1, 1, "R"), (0, 1, "T"), (-1, 2, "T"), (1, 2, "T")):
            px(im, x + dx, y + dy + 1, k)
    for (x, y, c) in ((4, 5, "C"), (10, 3, "9"), (13, 8, "C"), (7, 8, "I"), (2, 9, "9"), (9, 10, "H")):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px(im, x + dx, y + dy, c)
        px(im, x, y, "I" if c != "I" else "C")
    return outline(im, "T")


def rock():
    r = random.Random(13)
    im = new(16, 16)
    ells = [(8, 9.5, 6.5, 4.8), (5, 10.5, 3.6, 3.2)]
    shade(im, mask_of(ells), (8, 9, 7, 5), ("L", "J", "G"), r, noise=.1)
    for (x, y) in ((9, 8), (10, 9), (10, 10)):
        px(im, x, y, "F")
    for (x, y) in ((4, 11), (5, 12), (6, 12), (11, 12)):
        px(im, x, y, "F")
    px(im, 6, 8, "N"); px(im, 7, 8, "N"); px(im, 5, 9, "N")
    return outline(im, "A")


def streetlamp():
    """16x40 dark iron lamp post with yellow lantern."""
    im = new(16, 40)
    # base flare
    rect(im, 4, 36, 11, 39, "2"); rect(im, 5, 33, 10, 35, "2"); rect(im, 6, 31, 9, 32, "2")
    rect(im, 4, 36, 5, 39, "3"); rect(im, 4, 36, 11, 36, "4")
    # pole
    rect(im, 7, 13, 8, 31, "2"); rect(im, 7, 13, 7, 31, "4"); rect(im, 8, 13, 8, 31, "1")
    rect(im, 6, 21, 9, 21, "3"); rect(im, 6, 15, 9, 15, "3")
    # lantern
    rect(im, 4, 5, 11, 13, "1"); rect(im, 5, 6, 10, 12, "K")
    rect(im, 5, 6, 6, 8, "N"); rect(im, 9, 6, 10, 12, "I"); rect(im, 7, 6, 8, 12, "K"); rect(im, 5, 12, 10, 12, "I")
    rect(im, 3, 4, 12, 4, "2"); rect(im, 3, 13, 12, 13, "2")
    rect(im, 5, 3, 10, 3, "2"); rect(im, 6, 2, 9, 2, "2"); rect(im, 7, 0, 8, 1, "3")
    return outline(im)


def bench():
    im = new(32, 16)
    # back rest
    rect(im, 2, 1, 29, 2, "J"); rect(im, 2, 3, 29, 4, "H"); rect(im, 2, 5, 29, 5, "E")
    rect(im, 2, 7, 29, 7, "J"); rect(im, 2, 8, 29, 9, "H"); rect(im, 2, 10, 29, 10, "E")
    # supports
    rect(im, 3, 5, 4, 7, "D"); rect(im, 27, 5, 28, 7, "D")
    rect(im, 3, 11, 4, 14, "D"); rect(im, 27, 11, 28, 14, "D"); rect(im, 3, 11, 3, 14, "E"); rect(im, 27, 11, 27, 14, "E")
    return outline(im, "A")


def trashcan():
    im = new(16, 16)
    rect(im, 4, 4, 11, 14, "F"); rect(im, 4, 4, 5, 14, "H"); rect(im, 10, 4, 11, 14, "E")
    for y in (7, 11):
        rect(im, 4, y, 11, y, "E")
    rect(im, 3, 2, 12, 5, "G"); rect(im, 4, 3, 11, 4, "A"); rect(im, 3, 2, 12, 2, "H")
    rect(im, 7, 8, 8, 10, "x"); px(im, 7, 8, "9")
    return outline(im, "A")


def signboard():
    """Standing poster board."""
    im = new(16, 16)
    rect(im, 7, 10, 8, 14, "3")
    rect(im, 2, 1, 13, 10, "J"); rect(im, 3, 2, 12, 9, "N")
    rect(im, 5, 3, 7, 5, "C"); rect(im, 6, 2, 6, 2, "I"); rect(im, 8, 4, 11, 4, "o"); rect(im, 8, 6, 11, 6, "3")
    rect(im, 4, 7, 9, 8, "o"); rect(im, 10, 7, 11, 8, "I")
    rect(im, 2, 10, 13, 10, "G")
    return outline(im, "1")


def mailbox():
    im = new(16, 16)
    rect(im, 7, 9, 8, 13, "B"); rect(im, 5, 14, 10, 14, "$"); rect(im, 6, 13, 9, 13, "B")
    rect(im, 3, 2, 12, 9, "B"); rect(im, 4, 1, 11, 1, "B"); rect(im, 3, 2, 4, 8, "C"); rect(im, 11, 3, 12, 9, "$")
    rect(im, 5, 4, 10, 5, "9"); rect(im, 5, 5, 10, 5, "6"); rect(im, 5, 7, 10, 7, "$")
    px(im, 4, 1, "C")
    return outline(im)


def trafficsign():
    im = new(16, 32)
    rect(im, 5, 30, 10, 31, "2"); rect(im, 7, 13, 8, 30, "5"); rect(im, 8, 13, 8, 30, "3"); rect(im, 7, 13, 7, 30, "7")
    for (x, y) in mask_of([(8, 7, 6.8, 6.8)]):
        px(im, x, y, "9")
    for (x, y) in mask_of([(8, 7, 5.2, 5.2)]):
        px(im, x, y, "B")
    rect(im, 4, 6, 11, 8, "9"); rect(im, 4, 8, 11, 8, "7")
    for (x, y) in ((4, 3), (5, 2), (6, 2), (3, 4), (3, 5)):
        px(im, x, y, "C")
    return outline(im)


# ------------------------------------------------------------------ farm field (rural crops)
def soil_grid(seed=21):
    """Tilled soil: two horizontal ridges per tile (period 8, tiles seamlessly in both directions)."""
    r = random.Random(seed)
    prof = "DEFGFEED"
    g = [[prof[y % 8]] * T for y in range(T)]
    for y in range(T):
        for x in range(T):
            v = r.random()
            if v < .07:
                g[y][x] = "D" if y % 8 in (2, 3, 4) else "G"
            elif v < .10:
                g[y][x] = "H"
    return g


def tile_soil():
    return grid_img(soil_grid())


def tile_cabbage_row():
    """Soil with two staggered rows of round cabbage heads (one per ridge, wraps seamlessly sideways)."""
    r = random.Random(22)
    im = grid_img(soil_grid(23))
    for cy, xs in ((4.5, (4, 12)), (12.5, (0, 8, 16))):
        for cx in xs:
            clump(im, cx, cy, 4.3, 3.7, r, "OSRUT", fleck=.05)
            px(im, cx - 1, int(cy) - 1, "M"); px(im, cx, int(cy) - 2, "O"); px(im, cx - 2, int(cy), "O")
    return im


def tile_wheat_row():
    """Soil with ripe golden wheat: fanned bunches on two ridges, heads in three golds (back row first)."""
    r = random.Random(24)
    im = grid_img(soil_grid(25))
    for base, xs in ((9, (2, 6, 10, 14)), (16, (0, 4, 8, 12))):
        for cx in xs:
            for dx, h in ((-1, 6), (0, 8), (1, 6)):
                x = cx + dx
                top = base - h - r.randint(0, 1)
                for y in range(top + 3, base + 1):
                    px(im, x, y, "G" if dx else "J")
                px(im, x, top, "K"); px(im, x, top + 1, "K"); px(im, x, top + 2, "I"); px(im, x, top + 3, "H")
                px(im, x + dx, top + 1, "I"); px(im, x - dx, top + 2, "H") if dx else None
            px(im, cx, base, "E"); px(im, cx - 1, base, "D"); px(im, cx + 1, base, "D")
    return im


def crop_cabbage():
    r = random.Random(31)
    im = new(16, 16)
    mask_of_soil = mask_of([(8, 13, 6.5, 2.2)])
    for (x, y) in sorted(mask_of_soil):
        px(im, x, y, "E" if (x + y) % 3 else "D")
    clump(im, 8, 8.5, 6.4, 5.6, r, "OSRUT", fleck=.05)
    clump(im, 8, 7.5, 3.4, 3, r, "MOSRU", fleck=0)
    for (x, y) in ((8, 4), (8, 5), (7, 6), (9, 6)):      # leaf veins
        px(im, x, y, "O")
    for (x, y) in ((3, 9), (4, 10), (12, 9), (11, 10), (8, 11)):
        px(im, x, y, "T")
    return outline(im, "T")


def crop_pumpkin():
    r = random.Random(32)
    im = new(16, 16)
    for (x, y) in sorted(mask_of([(8, 13.5, 6.5, 2)])):
        px(im, x, y, "E" if (x + y) % 3 else "D")
    m = mask_of([(8, 9.5, 7, 5.2)])
    shade(im, m, (8, 9.5, 7, 5.2), ("I", "!", "#"), r, noise=.05)
    for x in (4, 8, 12):                                   # ribs
        for y in range(6, 14):
            if (x, y) in m:
                px(im, x, y, "#" if x != 8 else "@")
    for (x, y) in ((5, 7), (6, 6)):
        px(im, x, y, "K")
    rect(im, 7, 3, 8, 5, "T"); px(im, 7, 3, "R"); rect(im, 9, 4, 10, 4, "U")   # stem + curl
    return outline(im, "$")


def crop_wheat():
    """A tied sheaf of wheat standing in the field."""
    im = new(16, 16)
    for (x, y) in sorted(mask_of([(8, 14, 5.5, 1.6)])):
        px(im, x, y, "E" if (x + y) % 3 else "D")
    for i, x in enumerate((4, 6, 8, 10, 12)):
        top = (2, 1, 0, 1, 2)[i]
        for y in range(top + 3, 14):
            px(im, x, y, "G" if i % 2 == 0 else "J")
        px(im, x, top, "K"); px(im, x, top + 1, "I"); px(im, x, top + 2, "I")
        px(im, x - 1, top + 2, "H"); px(im, x + 1, top + 1, "K")
    rect(im, 3, 9, 13, 10, "B"); rect(im, 3, 9, 13, 9, "C")         # red tie
    rect(im, 2, 13, 14, 14, "G")                                    # cut stalk ends
    rect(im, 2, 14, 14, 14, "E")
    return outline(im, "A")


def scarecrow():
    """16x32 scarecrow on a post: straw hat, sack face, red patched shirt, straw hands."""
    im = new(16, 32)
    rect(im, 7, 15, 8, 30, "F"); rect(im, 7, 15, 7, 30, "H"); rect(im, 8, 17, 8, 30, "E")     # post
    rect(im, 5, 30, 10, 31, "D"); rect(im, 6, 30, 9, 30, "F")                                   # base mound
    rect(im, 1, 14, 14, 15, "F"); rect(im, 1, 14, 14, 14, "H"); rect(im, 1, 15, 14, 15, "E")    # arms
    for x in (0, 15):                                                                           # straw hands
        for y in (12, 13, 15, 16):
            px(im, x, y, "K")
        px(im, x, 14, "I")
    rect(im, 4, 12, 11, 22, "B"); rect(im, 4, 12, 5, 22, "C"); rect(im, 10, 12, 11, 22, "$")   # shirt
    rect(im, 6, 18, 9, 20, "b" if False else "M"); rect(im, 6, 18, 9, 18, "L"); px(im, 7, 19, "G")  # patch
    for x in (4, 6, 9, 11):                                                                     # straw at hem
        rect(im, x, 23, x, 25, "K"); px(im, x, 25, "I")
    rect(im, 5, 5, 10, 11, "L"); rect(im, 5, 5, 6, 11, "M"); rect(im, 10, 5, 10, 11, "J")     # sack head
    px(im, 6, 7, "0"); px(im, 9, 7, "0"); rect(im, 6, 10, 9, 10, "D"); px(im, 7, 9, "S" if False else "H")
    px(im, 6, 10, "0"); px(im, 9, 10, "0")
    rect(im, 2, 4, 13, 5, "I"); rect(im, 2, 4, 13, 4, "K"); rect(im, 2, 5, 13, 5, "Y" if False else "H")   # hat brim
    rect(im, 5, 0, 10, 3, "I"); rect(im, 5, 0, 7, 0, "K"); rect(im, 5, 3, 10, 3, "H")                   # hat crown
    rect(im, 5, 3, 10, 3, "B")
    return outline(im, "A")


# ------------------------------------------------------------------ buildings
def window(im, x0, y0, x1, y1, frame="E", glass="p", sill=True):
    rect(im, x0, y0, x1, y1, "D")
    rect(im, x0 + 1, y0 + 1, x1 - 1, y1 - 1, frame)
    rect(im, x0 + 2, y0 + 2, x1 - 2, y1 - 2, glass)
    mx = (x0 + x1) // 2
    rect(im, mx, y0 + 1, mx, y1 - 1, frame)
    if y1 - y0 >= 9:
        my = (y0 + y1) // 2
        rect(im, x0 + 1, my, x1 - 1, my, frame)
    # glass shine
    rect(im, x0 + 2, y0 + 2, x0 + 2, y0 + 3, "x"); px(im, x0 + 3, y0 + 2, "z")
    px(im, mx + 1, y0 + 2, "x") if mx + 1 < x1 - 1 else None
    rect(im, x0 + 2, y1 - 2, x1 - 2, y1 - 2, "t") if glass == "p" and y1 - y0 > 4 else None
    if sill:
        rect(im, x0 - 1, y1 + 1, x1 + 1, y1 + 1, "J")


def flowerbox(im, x0, x1, y):
    rect(im, x0, y, x1, y + 3, "T"); rect(im, x0, y, x1, y, "U")
    for i, x in enumerate(range(x0 + 1, x1, 2)):
        px(im, x, y - 1, ("C", "I", "9", "B")[i % 4]); px(im, x, y, "S")


def bush_clump(im, cx, cy, rx, ry, rng, flowers=True):
    clump(im, cx, cy, rx, ry, rng)
    if flowers:
        for _ in range(3):
            x = int(cx + rng.uniform(-rx * .6, rx * .6)); y = int(cy + rng.uniform(-ry * .5, ry * .5))
            px(im, x, y, rng.choice("CIB9"))


def make_house():
    """48x64: hipped red-orange roof, cream walls, wooden door, flower boxes. Door tile = footprint col 1."""
    r = random.Random(31)
    im = new(48, 64)
    # chimney
    rect(im, 31, 0, 37, 14, "#"); rect(im, 31, 0, 37, 1, "5"); rect(im, 36, 2, 37, 14, "$"); rect(im, 31, 0, 31, 1, "7")
    for y in (5, 9, 13): rect(im, 31, y, 37, y, "$")
    # walls
    rect(im, 5, 29, 42, 60, "M"); rect(im, 5, 29, 42, 31, "L"); rect(im, 38, 32, 42, 60, "L")
    rect(im, 5, 56, 42, 60, "6"); rect(im, 5, 56, 42, 56, "8"); rect(im, 5, 60, 42, 60, "4")
    for x in range(8, 42, 6): rect(im, x, 57, x, 59, "4")
    # roof (hipped trapezoid)
    for y in range(3, 30):
        t = (y - 3) / 26
        half = 6 + t * 16.5
        x0, x1 = int(round(24 - half)), int(round(24 + half)) - 1
        course = (y - 3) // 3
        for x in range(x0, x1 + 1):
            k = "C"
            if x >= 24 + (x1 - 24) * .55: k = "#" if (x1 - x) < 6 else "B"
            if (y - 3) % 3 == 2: k = "B" if k in ("C",) else "$"
            elif (x + course * 3) % 6 == 0 and (y - 3) % 3 == 0: k = "B" if k == "C" else "$"
            if x - x0 <= 1 and y > 4: k = "@" if k == "C" else k
            px(im, x, y, k)
    rect(im, 2, 28, 45, 29, "$"); rect(im, 3, 28, 44, 28, "B")
    # windows
    window(im, 7, 33, 17, 45); window(im, 31, 33, 41, 45)
    flowerbox(im, 7, 17, 48); flowerbox(im, 31, 41, 48)
    # door
    rect(im, 19, 49, 28, 61, "D"); rect(im, 20, 50, 27, 61, "F"); rect(im, 20, 50, 20, 61, "H")
    rect(im, 21, 52, 22, 55, "p"); rect(im, 25, 52, 26, 55, "p"); px(im, 21, 52, "x"); px(im, 25, 52, "x")
    rect(im, 21, 57, 26, 60, "E"); rect(im, 22, 58, 25, 59, "G"); px(im, 26, 56, "K")
    rect(im, 18, 48, 29, 48, "J")
    # step + path
    rect(im, 16, 61, 31, 63, "6"); rect(im, 16, 61, 31, 61, "8"); rect(im, 17, 63, 30, 63, "4")
    # bushes
    bush_clump(im, 8, 58, 6.5, 5, r); bush_clump(im, 40, 58, 6.5, 5, r)
    clump(im, 14, 61, 3.5, 2.8, r); clump(im, 34, 61, 3.5, 2.8, r)
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


def draw_text(im, text, x0, y0, fg="9", sh="$", pitch=6):
    for i, ch in enumerate(text):
        for y, row in enumerate(FONT[ch]):
            for x, b in enumerate(row):
                if b == "1":
                    px(im, x0 + i * pitch + x + 1, y0 + y + 1, sh)
    for i, ch in enumerate(text):
        for y, row in enumerate(FONT[ch]):
            for x, b in enumerate(row):
                if b == "1":
                    px(im, x0 + i * pitch + x, y0 + y, fg)


def awning(im, x0, x1, y0, ca, cb, shade_a, shade_b, h=10, sw=6):
    """Striped awning with scalloped hem."""
    for x in range(x0, x1 + 1):
        s = (x - x0) // sw
        c, d = (ca, shade_a) if s % 2 == 0 else (cb, shade_b)
        local = (x - x0) % sw
        bump = 1 if 1 <= local <= sw - 2 else 0
        if local in (2, 3) and sw >= 6: bump = 2
        for y in range(y0, y0 + h + bump):
            k = c
            if y >= y0 + h - 2 + bump - 1: k = d
            if y == y0: k = d if c != "9" else "8"
            px(im, x, y, k)


def make_shop():
    """64x64: red SHOP sign, red/white striped awning, wooden double door. Door tile = footprint col 2."""
    r = random.Random(32)
    im = new(64, 64)
    # wall
    rect(im, 2, 24, 61, 59, "M"); rect(im, 2, 24, 61, 25, "L")
    rect(im, 2, 56, 61, 59, "6"); rect(im, 2, 56, 61, 56, "8"); rect(im, 2, 59, 61, 59, "4")
    for x in range(5, 61, 6): rect(im, x, 57, x, 58, "4")
    # orange wood parapet
    rect(im, 2, 13, 61, 25, "H"); rect(im, 2, 13, 61, 14, "J"); rect(im, 2, 24, 61, 25, "G")
    for x in range(5, 61, 5): rect(im, x, 15, x, 23, "G")
    # sign
    rect(im, 13, 0, 50, 19, "0"); rect(im, 14, 1, 49, 18, "$"); rect(im, 15, 2, 48, 17, "B"); rect(im, 15, 2, 48, 3, "C")
    rect(im, 15, 2, 15, 17, "C"); rect(im, 48, 3, 48, 17, "$"); rect(im, 15, 17, 48, 17, "$")
    draw_text(im, "SHOP", 21, 6, "9", "$", 6)
    # awning
    awning(im, 2, 61, 26, "B", "9", "$", "7", h=11, sw=6)
    # windows
    window(im, 5, 44, 27, 55); window(im, 50, 44, 58, 55)
    for (x, y, w, h, c) in ((8, 50, 3, 3, "C"), (12, 49, 3, 4, "I"), (16, 50, 3, 3, "U"), (20, 48, 5, 5, "o")):
        rect(im, x, y, x + w - 1, y + h - 1, c); px(im, x, y, "9")
    rect(im, 52, 50, 56, 53, "N"); rect(im, 53, 51, 55, 52, "C")
    # door
    rect(im, 33, 42, 46, 62, "D"); rect(im, 34, 43, 45, 62, "F"); rect(im, 39, 43, 40, 62, "D")
    rect(im, 35, 44, 38, 51, "p"); rect(im, 41, 44, 44, 51, "p"); px(im, 35, 44, "x"); px(im, 41, 44, "x")
    rect(im, 35, 53, 38, 61, "E"); rect(im, 41, 53, 44, 61, "E"); rect(im, 36, 54, 37, 60, "G"); rect(im, 42, 54, 43, 60, "G")
    px(im, 38, 57, "K"); px(im, 41, 57, "K")
    rect(im, 32, 42, 47, 42, "J")
    rect(im, 30, 60, 49, 63, "6"); rect(im, 30, 60, 49, 60, "8"); rect(im, 31, 63, 48, 63, "4")
    # side bushes
    clump(im, 3, 59, 3.6, 4.5, r); clump(im, 60, 59, 3.6, 4.5, r)
    return outline(im)


def make_cafe():
    """64x64: orange awning + CAFE board, brick/wood walls, small orange-roofed annex. Door tile = footprint col 2."""
    r = random.Random(33)
    im = new(64, 64)
    # annex tower (left) with orange roof
    rect(im, 2, 18, 17, 59, "H"); rect(im, 2, 18, 3, 59, "J"); rect(im, 14, 20, 17, 59, "G")
    for y in range(4, 19):
        t = (y - 4) / 14
        half = 5 + t * 6
        for x in range(int(round(10 - half)), int(round(10 + half))):
            k = "!"
            if (y - 4) % 3 == 2: k = "#"
            elif x > 10 + half * .3: k = "#" if (y - 4) % 3 else "$"
            elif x < 10 - half * .5 and (y - 4) % 3 == 0: k = "@"
            px(im, x, y, k)
    rect(im, 1, 18, 18, 19, "$")
    window(im, 5, 26, 12, 37, frame="E")
    rect(im, 2, 46, 17, 49, "J")
    # main block with brick CAFE board
    rect(im, 17, 15, 62, 59, "G")
    rect(im, 17, 12, 62, 38, "%")
    for y in range(13, 38):
        for x in range(18, 62):
            if y % 4 == 3: px(im, x, y, "&")
            elif (x + (y // 4) * 4) % 8 == 0: px(im, x, y, "&")
            elif y % 4 == 0 and r.random() < .35: px(im, x, y, "#") if False else None
    rect(im, 17, 12, 62, 13, "J"); rect(im, 17, 14, 62, 14, "$")
    # board
    rect(im, 23, 18, 56, 34, "A"); rect(im, 24, 19, 55, 33, "%"); rect(im, 24, 19, 55, 20, "C"); rect(im, 24, 19, 24, 33, "C")
    rect(im, 55, 20, 55, 33, "&"); rect(im, 24, 33, 55, 33, "&")
    draw_text(im, "CAFE", 29, 22, "9", "$", 6)
    # awning (orange / white)
    awning(im, 17, 62, 36, "!", "9", "#", "7", h=10, sw=6)
    # wood lower wall
    rect(im, 17, 47, 62, 59, "F")
    for x in range(20, 62, 4): rect(im, x, 47, x, 59, "E")
    rect(im, 17, 47, 62, 47, "H")
    rect(im, 17, 57, 62, 59, "6"); rect(im, 17, 57, 62, 57, "8"); rect(im, 17, 59, 62, 59, "4")
    # windows + door
    window(im, 20, 44, 31, 55); window(im, 50, 44, 60, 55)
    for x in (23, 27): rect(im, x, 51, x + 2, 53, "9"); rect(im, x, 53, x + 2, 53, "7")
    rect(im, 53, 50, 57, 53, "I"); rect(im, 54, 51, 56, 52, "C")
    rect(im, 33, 42, 46, 62, "D"); rect(im, 34, 43, 45, 62, "E"); rect(im, 39, 43, 40, 62, "D")
    rect(im, 35, 44, 38, 52, "p"); rect(im, 41, 44, 44, 52, "p"); px(im, 35, 44, "x"); px(im, 41, 44, "x")
    rect(im, 35, 54, 38, 61, "F"); rect(im, 41, 54, 44, 61, "F"); px(im, 38, 57, "K"); px(im, 41, 57, "K")
    rect(im, 32, 42, 47, 42, "J")
    rect(im, 30, 60, 49, 63, "6"); rect(im, 30, 60, 49, 60, "8"); rect(im, 31, 63, 48, 63, "4")
    # bushes + flowers
    clump(im, 3, 59, 3.4, 4.5, r); clump(im, 61, 59, 2.8, 4.5, r)
    for (x, y, c) in ((19, 61, "I"), (21, 62, "C"), (53, 62, "I"), (57, 61, "C")):
        px(im, x, y, c); px(im, x, y + 1, "U")
    return outline(im)


def sign_icon(kind):
    im = new(16, 16)
    rect(im, 1, 0, 14, 15, "0"); rect(im, 0, 1, 15, 14, "0")
    rect(im, 1, 1, 14, 14, "I" if kind == "shop" else "N"); rect(im, 1, 1, 14, 1, "K" if kind == "shop" else "8")
    fg = new(16, 16)
    if kind == "shop":
        rect(fg, 4, 6, 11, 12, "B"); rect(fg, 4, 12, 11, 12, "$"); rect(fg, 10, 6, 11, 12, "$")
        for (x, y) in ((6, 5), (6, 4), (7, 3), (8, 3), (9, 4), (9, 5)):
            px(fg, x, y, "$")
        px(fg, 6, 8, "C"); px(fg, 6, 9, "C")
        outline(fg)
    else:
        rect(fg, 4, 7, 10, 11, "9"); rect(fg, 5, 12, 9, 12, "9"); rect(fg, 9, 8, 10, 11, "7")
        rect(fg, 11, 8, 12, 10, "9"); px(fg, 12, 9, "_")
        rect(fg, 5, 7, 9, 7, "D")
        outline(fg)
        px(fg, 6, 4, "6"); px(fg, 7, 3, "6"); px(fg, 6, 2, "6"); px(fg, 9, 4, "6"); px(fg, 8, 3, "6")
    im.alpha_composite(fg)
    return im


def gazebo():
    """48x64 park gazebo: hex red roof, white posts, wood floor, bushes. Door tile = footprint col 1."""
    r = random.Random(34)
    im = new(48, 64)
    # floor
    rect(im, 3, 54, 44, 59, "J"); rect(im, 3, 54, 44, 54, "M")
    for y in (56, 58): rect(im, 3, y, 44, y, "G")
    rect(im, 3, 60, 44, 62, "6"); rect(im, 3, 60, 44, 60, "8"); rect(im, 3, 62, 44, 62, "4")
    rect(im, 17, 60, 30, 63, "7"); rect(im, 17, 60, 30, 60, "9"); rect(im, 17, 63, 30, 63, "5")
    # back wall (dark lattice)
    rect(im, 9, 32, 38, 53, "E")
    for x in range(10, 38, 3): rect(im, x, 33, x, 52, "D")
    for y in (38, 46): rect(im, 9, y, 38, y, "D")
    # posts
    for x0 in (5, 40):
        rect(im, x0, 28, x0 + 2, 59, "9"); rect(im, x0 + 2, 28, x0 + 2, 59, "7"); rect(im, x0, 28, x0, 59, "8")
    # railings
    for xa, xb in ((8, 15), (32, 39)):
        rect(im, xa, 46, xb, 47, "9"); rect(im, xa, 47, xb, 47, "7")
        for x in range(xa + 1, xb, 2): rect(im, x, 48, x, 56, "8")
        rect(im, xa, 57, xb, 57, "6")
    # roof (cone)
    for y in range(4, 30):
        half = 2 + (y - 4) * 21.5 / 25
        for x in range(int(round(24 - half)), int(round(24 + half))):
            u = (x + .5 - 24) / half
            seg = int((u + 1) * 3)
            k = ("C", "B", "C", "B", "C", "B")[min(seg, 5)]
            if seg in (0, 1): k = "C" if seg == 0 else "B"
            if y % 4 == 3: k = "$" if k == "B" else "B"
            if (y - 4) < 2: k = "C"
            px(im, x, y, k)
    for y in range(4, 30):   # left rim highlight
        half = 2 + (y - 4) * 21.5 / 25
        px(im, int(round(24 - half)), y, "@")
    rect(im, 1, 28, 46, 30, "$"); rect(im, 1, 28, 46, 28, "B"); rect(im, 3, 31, 44, 32, "A")
    rect(im, 23, 0, 24, 5, "I"); px(im, 23, 0, "K")
    # bushes
    clump(im, 4, 59, 4.5, 4, r); clump(im, 43, 59, 4.5, 4, r)
    return outline(im)


# ------------------------------------------------------------------ interiors / furniture / items
def interior_wall(variant):
    im = new(T, T)
    for y in range(T):
        for x in range(T):
            if variant == 0:    # cream wallpaper + wood wainscot (house / shop)
                if y == 0: c = "A"
                elif y < 11: c = "M" if x % 8 in (2, 3) else "L"
                elif y == 11: c = "D"
                elif y < 15: c = "F" if x % 4 else "E"
                else: c = "D"
            else:               # brown wood panels (cafe / workplace)
                if y == 0: c = "A"
                elif y < 11: c = "G" if x % 5 else "F"
                elif y == 11: c = "D"
                elif y < 15: c = "E" if x % 4 else "D"
                else: c = "A"
            px(im, x, y, c)
    return im


def bed():
    im = new(16, 32)
    rect(im, 1, 1, 14, 30, "E"); rect(im, 2, 1, 13, 4, "G"); rect(im, 2, 1, 13, 1, "J")
    rect(im, 2, 5, 13, 29, "N"); rect(im, 4, 6, 11, 11, "9"); rect(im, 4, 11, 11, 11, "7"); rect(im, 4, 6, 5, 10, "9")
    rect(im, 2, 14, 13, 29, "o"); rect(im, 2, 14, 13, 16, "x"); rect(im, 2, 16, 13, 16, "t")
    rect(im, 10, 17, 13, 29, "l"); rect(im, 2, 22, 9, 22, "l"); rect(im, 4, 19, 6, 19, "v"); rect(im, 5, 25, 8, 25, "j")
    rect(im, 2, 29, 13, 30, "E"); rect(im, 2, 29, 13, 29, "G")
    return outline(im, "A")


def table():
    im = new(16, 16)
    rect(im, 2, 12, 3, 14, "E"); rect(im, 12, 12, 13, 14, "E"); rect(im, 2, 12, 2, 14, "F")
    rect(im, 1, 10, 14, 11, "F"); rect(im, 1, 2, 14, 9, "H"); rect(im, 1, 2, 14, 3, "J"); rect(im, 1, 2, 1, 9, "J")
    rect(im, 14, 4, 14, 9, "G"); rect(im, 3, 6, 8, 6, "J"); rect(im, 9, 7, 12, 7, "G")
    return outline(im, "A")


def chair():
    im = new(16, 16)
    rect(im, 4, 12, 5, 14, "E"); rect(im, 10, 12, 11, 14, "E")
    rect(im, 3, 8, 12, 11, "H"); rect(im, 3, 8, 12, 8, "J"); rect(im, 3, 11, 12, 11, "G")
    rect(im, 4, 1, 11, 7, "G"); rect(im, 4, 1, 11, 1, "J"); rect(im, 5, 3, 6, 6, "E"); rect(im, 9, 3, 10, 6, "E")
    rect(im, 7, 2, 8, 6, "H")
    return outline(im, "A")


def counter():
    im = new(32, 16)
    rect(im, 1, 8, 30, 14, "F"); rect(im, 1, 4, 30, 8, "J"); rect(im, 1, 8, 30, 8, "H"); rect(im, 1, 4, 30, 4, "L")
    for x in range(3, 30, 7): rect(im, x, 10, x + 4, 13, "E"); rect(im, x + 1, 11, x + 3, 12, "G")
    # espresso machine
    rect(im, 20, 0, 28, 6, "5"); rect(im, 21, 0, 24, 2, "t"); rect(im, 21, 4, 27, 5, "7"); rect(im, 26, 0, 28, 2, "1")
    rect(im, 4, 2, 9, 4, "9"); px(im, 5, 3, "I"); px(im, 7, 3, "C")
    return outline(im, "A")


def shelf():
    im = new(16, 32)
    rect(im, 1, 1, 14, 30, "D"); rect(im, 2, 2, 13, 29, "G")
    for y in (10, 20): rect(im, 2, y, 13, y + 1, "E"); rect(im, 2, y, 13, y, "J")
    cols = ["B", "o", "I", "U", "C", "H", "x", "9"]
    r = random.Random(14)
    for y0 in (3, 12, 22):
        x = 3
        while x < 12:
            w = r.choice([2, 3]); h = r.choice([4, 5])
            c = r.choice(cols)
            rect(im, x, y0 + 7 - h, min(x + w - 1, 12), y0 + 6, c); px(im, x, y0 + 7 - h, "9" if c != "9" else "N")
            x += w + 1
    return outline(im, "A")


def lamp():
    im = new(16, 16)
    rect(im, 7, 8, 8, 13, "E"); rect(im, 5, 13, 10, 14, "D")
    for y, (x0, x1) in enumerate([(5, 10), (4, 11), (4, 11), (3, 12), (3, 12), (3, 12)]):
        rect(im, x0, 2 + y, x1, 2 + y, "K")
    rect(im, 3, 7, 12, 7, "I"); rect(im, 5, 3, 6, 4, "N"); rect(im, 11, 3, 12, 7, "I")
    return outline(im, "A")


def interior_trim():
    """Dark wood border (side / bottom walls seen from above): planks with a lit top edge."""
    r = random.Random(15)
    im = new(T, T)
    for y in range(T):
        for x in range(T):
            if y in (0, 15): c = "A"
            elif y == 1: c = "E"
            elif x % 8 == 0: c = "A"
            elif x % 8 == 1: c = "E"
            elif r.random() < .04: c = "E"
            else: c = "D"
            px(im, x, y, c)
    return im


def door_mat():
    """Wood floor with a red doormat (walkable exit tile in the bottom wall)."""
    im = grid_img(WOOD)
    rect(im, 2, 1, 13, 14, "B"); rect(im, 3, 2, 12, 13, "C")
    for y in (4, 7, 10):
        rect(im, 4, y, 11, y, "I")
    rect(im, 3, 2, 12, 2, "@"); rect(im, 2, 1, 13, 1, "A"); rect(im, 2, 14, 13, 14, "A")
    return im


def interior_window():
    """Wall decoration: framed window with curtains, drawn over an interior wall tile."""
    im = new(T, T)
    window(im, 2, 1, 13, 10, frame="E", glass="p", sill=True)
    rect(im, 2, 2, 3, 9, "C"); rect(im, 12, 2, 13, 9, "C"); rect(im, 2, 2, 3, 2, "@"); rect(im, 12, 2, 13, 2, "@")
    rect(im, 3, 5, 3, 9, "B"); rect(im, 12, 5, 12, 9, "B")
    return im


def rug():
    """3x2 tile rug: red border, cream stripes, fringe."""
    im = new(48, 32)
    rect(im, 2, 3, 45, 28, "B"); rect(im, 3, 4, 44, 27, "C"); rect(im, 5, 6, 42, 25, "N"); rect(im, 6, 7, 41, 24, "C")
    rect(im, 3, 4, 44, 4, "@")
    for x in range(10, 40, 6):
        rect(im, x, 11, x + 2, 13, "I"); rect(im, x + 3, 18, x + 5, 20, "N")
    for x in range(3, 45, 3):
        px(im, x, 2, "N"); px(im, x, 29, "N")
    return outline(im, "A")


def coffee():
    im = new(16, 16)
    rect(im, 3, 7, 10, 12, "9"); rect(im, 4, 13, 9, 13, "9"); rect(im, 9, 8, 10, 12, "7"); rect(im, 4, 13, 9, 13, "8")
    rect(im, 11, 8, 13, 11, "9"); px(im, 12, 9, "_"); px(im, 12, 10, "_")
    rect(im, 4, 7, 9, 8, "D"); rect(im, 5, 7, 6, 7, "F")
    rect(im, 2, 14, 12, 14, "6")
    outline(im)
    for (x, y) in ((5, 4), (6, 3), (5, 2), (8, 4), (9, 3), (8, 2)):
        px(im, x, y, "7")
    return im


def bread():
    r = random.Random(15)
    im = new(16, 16)
    shade(im, mask_of([(8, 9.5, 6.5, 4.5)]), (8, 9, 7, 5), ("K", "H", "F"), r, noise=.08)
    for x in (5, 8, 11):
        px(im, x, 7, "L"); px(im, x + 1, 8, "L")
    return outline(im, "A")


def apple():
    r = random.Random(16)
    im = new(16, 16)
    shade(im, mask_of([(8, 9.5, 5.5, 5)]), (8, 9, 6, 5.5), ("C", "B", "$"), r, noise=.06)
    px(im, 5, 7, "9"); px(im, 5, 8, "9"); rect(im, 7, 3, 8, 5, "D"); rect(im, 9, 3, 11, 4, "U"); px(im, 11, 3, "S")
    px(im, 8, 5, "$")
    return outline(im, "A")


def bento():
    im = new(16, 16)
    rect(im, 1, 3, 14, 13, "D"); rect(im, 2, 4, 13, 12, "A")
    rect(im, 2, 4, 7, 12, "9"); px(im, 3, 6, "7"); px(im, 5, 9, "7"); px(im, 6, 5, "7"); px(im, 4, 11, "7"); px(im, 4, 7, "0")
    rect(im, 8, 4, 8, 12, "D")
    rect(im, 9, 4, 12, 6, "I"); rect(im, 10, 5, 11, 5, "C")
    rect(im, 9, 8, 12, 9, "C"); rect(im, 9, 11, 12, 12, "U"); px(im, 10, 11, "S"); px(im, 12, 8, "B")
    return outline(im)


def sandwich():
    im = new(16, 16)
    rect(im, 2, 4, 13, 6, "J"); rect(im, 3, 3, 12, 3, "J"); rect(im, 2, 4, 13, 4, "L")
    rect(im, 1, 7, 14, 7, "S"); rect(im, 2, 8, 13, 8, "B"); rect(im, 1, 9, 14, 9, "I"); rect(im, 2, 10, 13, 10, "C")
    rect(im, 2, 11, 13, 13, "J"); rect(im, 2, 13, 13, 13, "G")
    return outline(im, "A")


def shirt():
    im = new(16, 16)
    rect(im, 4, 4, 11, 13, "o"); rect(im, 1, 4, 3, 7, "o"); rect(im, 12, 4, 14, 7, "o")
    rect(im, 6, 4, 9, 4, "_"); rect(im, 5, 5, 10, 5, "l"); rect(im, 6, 5, 9, 5, "x")
    rect(im, 10, 6, 11, 13, "l"); rect(im, 13, 5, 14, 7, "l"); rect(im, 1, 7, 3, 7, "l")
    px(im, 5, 8, "v"); px(im, 5, 9, "v"); px(im, 2, 5, "v")
    return outline(im)


def flower_item():
    im = new(16, 16)
    pts = ((8, 4, "C"), (4, 6, "I"), (12, 6, "9"))
    for (x, y, c) in pts:
        for (px_, py_) in mask_of([(x, y, 2.6, 2.6)]):
            px(im, px_, py_, c)
        px(im, x, y, "I" if c != "I" else "C")
    for x0 in (8, 5, 11):
        for y in range(7, 10): px(im, x0 + (8 - x0) * (y - 7) // 4, y, "U")
    for y in range(9, 15):
        half = (y - 8) * 6 // 6 + 1
        rect(im, 8 - half, y, 7 + half, y, "N")
    rect(im, 5, 11, 6, 11, "6"); rect(im, 3, 13, 12, 14, "6"); rect(im, 8, 10, 8, 14, "C")
    return outline(im, "A")


def book():
    im = new(16, 16)
    rect(im, 2, 2, 12, 13, "B"); rect(im, 2, 2, 3, 13, "$"); rect(im, 13, 3, 14, 13, "N"); rect(im, 3, 13, 14, 13, "N")
    rect(im, 2, 13, 12, 13, "$"); rect(im, 5, 5, 10, 6, "K"); rect(im, 5, 8, 9, 8, "K"); rect(im, 13, 5, 14, 5, "8")
    px(im, 4, 3, "C"); px(im, 5, 3, "C")
    return outline(im, "A")


def gift():
    im = new(16, 16)
    rect(im, 2, 7, 13, 14, "B"); rect(im, 2, 13, 13, 14, "$"); rect(im, 1, 5, 14, 8, "C"); rect(im, 1, 8, 14, 8, "$")
    rect(im, 7, 5, 8, 14, "I")
    rect(im, 4, 2, 6, 4, "I"); rect(im, 9, 2, 11, 4, "I"); px(im, 5, 3, "_"); px(im, 10, 3, "_"); rect(im, 7, 4, 8, 4, "H")
    return outline(im, "A")


# ------------------------------------------------------------------ build outputs
# footprints (tiles) stay fixed: images may extend above their footprint.
FOOT = {"house": (3, 3), "shop": (4, 3), "cafe": (4, 3), "gazebo": (3, 3)}


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

    # --- MAP_011 farm field tiles + MAP_008 rural crop props (tilled soil, cabbage row, wheat row)
    farm = [("soil", tile_soil()), ("cabbage_row", tile_cabbage_row()), ("wheat_row", tile_wheat_row())]
    out(strip([i for _, i in farm]), "maps/tilesets/MAP_011_Farm_Tileset_v01.png")
    out_json({"tile_size": T, "columns": len(farm), "tiles": {str(i): n for i, (n, _) in enumerate(farm)},
              "note": "soil is walkable (tilled path between rows); cabbage_row and wheat_row are crop rows (impassable)"},
             "maps/tilesets/MAP_011_Farm_Tileset_v01.json")
    for n, f, fn in (("cabbage", "Cabbage", crop_cabbage), ("pumpkin", "Pumpkin", crop_pumpkin),
                     ("wheat", "Wheat", crop_wheat), ("scarecrow", "Scarecrow", scarecrow)):
        out(fn(), f"maps/rural/MAP_008_Farm_{f}_v01.png")

    # --- buildings
    sh_sign, cf_sign = sign_icon("shop"), sign_icon("cafe")
    out(sh_sign, "buildings/shops/BLD_005_Sign_Shop_v01.png")
    out(cf_sign, "buildings/workplaces/BLD_005_Sign_Cafe_v01.png")
    house, shop, cafe, gaz = make_house(), make_shop(), make_cafe(), gazebo()
    out(house, "buildings/houses/BLD_001_House_v01.png")
    out(shop, "buildings/shops/BLD_002_Shop_v01.png")
    out(cafe, "buildings/workplaces/BLD_003_Cafe_v01.png")
    out(gaz, "buildings/social/BLD_004_Park_Gazebo_v01.png")

    def col(w, h, door_x):
        rows_ = ["#" * w for _ in range(h)]
        rows_[-1] = "#" * door_x + "D" + "#" * (w - door_x - 1)
        return rows_
    binfo = {}
    for name, path, im, dx, fk in (("BLD_001_House", "houses/BLD_001_House_v01.png", house, 1, "house"),
                                   ("BLD_002_Shop", "shops/BLD_002_Shop_v01.png", shop, 2, "shop"),
                                   ("BLD_003_Cafe", "workplaces/BLD_003_Cafe_v01.png", cafe, 2, "cafe"),
                                   ("BLD_004_Park_Gazebo", "social/BLD_004_Park_Gazebo_v01.png", gaz, 1, "gazebo")):
        w, h = FOOT[fk]
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
    out(rug(), "objects/furniture/BLD_006_Rug_v01.png")
    out(interior_window(), "maps/interiors/MAP_007_Interior_Window_v01.png")
    # interior tileset: wall A, wall B, side/bottom trim, door mat (frames 0..3)
    it = [("wall_a", w0), ("wall_b", w1), ("trim", interior_trim()), ("door_mat", door_mat())]
    out(strip([i for _, i in it]), "maps/interiors/MAP_007_Interior_Tileset_v01.png")
    out_json({"tile_size": T, "columns": len(it), "tiles": {str(i): n for i, (n, _) in enumerate(it)},
              "note": "wall_a/wall_b/trim are impassable; door_mat is the walkable exit tile in the bottom wall"},
             "maps/interiors/MAP_007_Interior_Tileset_v01.json")
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
    for (c, r), n in sorted(place.items()):
        if n.startswith("fence"):
            cv.paste(g_a, (c * T, r * T))
            cv.alpha_composite(bl[1][1] if n == "fence_h" else bl[2][1], (c * T, r * T))
        else:
            cv.paste(tiles[n], (c * T, r * T))
    # pond rim: dark blue inner edge + sand outer ring
    wm = {(c, r) for (c, r), n in place.items() if n == "water"}
    pxs = cv.load()

    def inwater(x, y): return (x // T, y // T) in wm
    snap = [(x, y) for y in range(H * T) for x in range(W * T)]
    for (x, y) in snap:
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= x + dx < W * T and 0 <= y + dy < H * T]
        if inwater(x, y) and any(not inwater(a, b) for a, b in nb):
            pxs[x, y] = Q["l"]
    for (x, y) in snap:
        if not inwater(x, y):
            nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < W * T and 0 <= y + dy < H * T]
            if any(inwater(a, b) for a, b in nb):
                pxs[x, y] = Q["J"]

    objs = []  # (col, bottom_row, image)

    def add(c, r, im): objs.append((c, r, im))
    add(1, 6, house); add(5, 6, gaz); add(12, 8, shop); add(16, 8, cafe)
    for c, r in ((6, 1), (13, 3), (17, 2), (18, 5), (1, 13), (6, 13), (16, 13)): add(c, r, obj["tree"])
    for c, r in ((5, 2), (13, 5), (8, 4), (3, 13), (12, 13)): add(c, r, obj["bush"])
    for c, r in ((1, 7), (3, 7), (8, 8), (14, 4), (4, 13), (15, 13), (19, 3)): add(c, r, obj["flowers"])
    for c, r in ((1, 1), (5, 1), (15, 2), (9, 13)): add(c, r, obj["rock"])
    add(9, 3, obj["lamp"]); add(11, 6, obj["lamp"]); add(11, 9, obj["trafficsign"])
    add(3, 9, obj["bench"]); add(12, 9, obj["bench"]); add(1, 9, obj["mailbox"])
    add(15, 9, obj["signboard"]); add(19, 9, obj["trash"])
    objs.sort(key=lambda o: (o[1], o[0]))
    for c, r, im in objs:
        cv.alpha_composite(im, (c * T, (r + 1) * T - im.height))
    out(cv, "maps/MAP_DEMO_StarterBlock_v01.png")
    return cv


if __name__ == "__main__":
    rt, bl, obj, house, shop, cafe, gaz = build()
    cv = demo(rt, bl, obj, house, shop, cafe, gaz)
    print(f"files written: {len(FILES)}")
