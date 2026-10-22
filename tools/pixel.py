"""Shared pixel-art helpers. All generator scripts import this so palette and output stay consistent."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

TILE = 16            # map tile size (px)
CHAR_W, CHAR_H = 16, 24   # character frame size; feet anchored at bottom-center
ICON = 16            # UI / item icon size
PORTRAIT = 48        # dialogue portrait size

# Fixed project palette (16-bit style). Only use these keys.
P = {
    "_": (0, 0, 0, 0),            # transparent
    "k": (24, 20, 37, 255),       # outline / near-black
    "K": (58, 50, 74, 255),       # dark gray-purple
    "g": (110, 105, 128, 255),    # gray
    "G": (170, 166, 184, 255),    # light gray
    "w": (244, 240, 232, 255),    # white
    "s": (240, 196, 160, 255),    # skin light
    "S": (204, 146, 112, 255),    # skin shade
    "t": (160, 104, 72, 255),     # skin tan
    "T": (112, 68, 48, 255),      # skin dark
    "r": (214, 64, 64, 255),      # red
    "R": (140, 36, 52, 255),      # dark red
    "o": (236, 136, 52, 255),     # orange
    "y": (248, 212, 80, 255),     # yellow
    "Y": (196, 152, 40, 255),     # gold
    "l": (140, 204, 80, 255),     # light green
    "e": (72, 156, 72, 255),      # green
    "E": (36, 96, 60, 255),       # dark green
    "c": (96, 200, 220, 255),     # cyan
    "b": (64, 120, 208, 255),     # blue
    "B": (40, 64, 128, 255),      # dark blue
    "p": (156, 92, 196, 255),     # purple
    "m": (236, 128, 172, 255),    # pink
    "n": (156, 108, 64, 255),     # brown
    "N": (96, 64, 40, 255),       # dark brown
    "u": (208, 172, 120, 255),    # sand / beige
    "a": (124, 124, 132, 255),    # asphalt
    "A": (88, 88, 98, 255),       # asphalt dark
}


def from_rows(rows, palette=P):
    """Build an RGBA image from a list of equal-length strings of palette keys."""
    h, w = len(rows), len(rows[0])
    img = Image.new("RGBA", (w, h))
    for y, row in enumerate(rows):
        assert len(row) == w, f"row {y} width {len(row)} != {w}"
        for x, ch in enumerate(row):
            img.putpixel((x, y), palette[ch])
    return img


def recolor(img, mapping):
    """Swap palette colors: mapping is {old_key: new_key}."""
    src = {P[k]: P[v] for k, v in mapping.items()}
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            if px[x, y] in src:
                px[x, y] = src[px[x, y]]
    return out


def strip(frames):
    """Horizontal sprite sheet; frame order left -> right."""
    w, h = frames[0].size
    sheet = Image.new("RGBA", (w * len(frames), h))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    return sheet


def save(img, relpath):
    """Save under assets/ at native resolution (scale in engine with nearest-neighbor)."""
    path = ASSETS / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path
