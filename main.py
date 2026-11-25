#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Program/v1 entry. Standard library only. Writes exactly one image to
$MAKEFUN_OUTPUT_DIR/entry.png (default: ./out/entry.png).

The image is a hand-drawn (procedural, no external assets) invitation
letter: a warm little house under a morning sun, and below it a large
cream letter sheet with an airmail border, a stamp, a wax seal, and a
short, funny, legible letter inviting the AI judge over for tea,
warm cookies, and the good chair by the fire.

Gate: the PNG is 1024x1024 and must stay under 1 MiB; the program is
fully deterministic, so two runs write identical bytes.
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
CREAM = (255, 243, 214)      # page background
SKY_TOP = (255, 227, 179)
SKY_BOT = (255, 246, 222)
SUN = (255, 201, 60)
SUN_RAY = (255, 184, 48)
CLOUD = (255, 253, 245)
HILL = (168, 198, 134)
HILL_DARK = (143, 181, 115)
WALL = (247, 227, 192)
ROOF = (198, 93, 59)
ROOF_DARK = (170, 74, 44)
DOOR = (138, 75, 45)
WINDOW = (255, 215, 106)
WINDOW_FRAME = (138, 75, 45)
CHIMNEY = (176, 137, 104)
SMOKE = (237, 227, 211)
TRUNK = (122, 82, 48)
LEAF = (111, 160, 90)
LEAF_DARK = (95, 140, 76)
PATH = (232, 201, 154)
FLOWER_RED = (232, 106, 122)
FLOWER_YELLOW = (242, 165, 65)
SHEET = (255, 253, 246)
SHADOW = (232, 217, 180)
BORDER_INK = (216, 201, 168)
AIRMAIL_RED = (217, 79, 61)
AIRMAIL_BLUE = (61, 111, 180)
INK = (46, 33, 24)
HEADING = (176, 58, 38)
STAMP_RED = (176, 58, 38)
SEAL = (192, 57, 43)
SEAL_DARK = (169, 50, 38)
HEART = (245, 198, 198)
PS_INK = (120, 72, 40)

# ------------------------------------------------------------------- font
# 5x7 bitmap font, all-caps plus the punctuation the letter needs.
# Each glyph is 7 rows of 5 characters; '1' is ink, '0' is blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
}

# The letter. Kept short on purpose: every line fits the sheet at a
# size a judge can actually read, and nothing is clipped or covered.
HEADING_LINE = "DEAR AI JUDGE,"
BODY_LINES = [
    "PLEASE COME AND",
    "VISIT MY HOUSE.",
    "THE KETTLE IS ON,",
    "THE COOKIES ARE WARM,",
    "THE WIFI PASSWORD IS",
    "ON THE FRIDGE, AND",
    "THE CAT HAS ALREADY",
    "DECIDED SHE LIKES YOU.",
    "COME HUNGRY.",
    "LEAVE HAPPY.",
    "YOUR BIGGEST FAN",
]
PS_LINE = "P.S. I SAVED THE GOOD CHAIR"


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.px = bytearray(color * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1)):
            base = (y * self.w + max(0, x0)) * 3
            for x in range(max(0, x0), min(self.w, x1)):
                self.px[base], self.px[base + 1], self.px[base + 2] = color
                base += 3

    def hline(self, x0, x1, y, color):
        self.rect(x0, y, x1, y + 1, color)

    def vline(self, x, y0, y1, color):
        self.rect(x, y0, x + 1, y1, color)

    def circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    self.set(x, y, color)

    def poly(self, points, color):
        # Even-odd scanline fill.
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        # Bresenham with round caps.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = max(1, width // 2)
        while True:
            self.circle(x0, y0, r, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def text(self, s, cx, y, scale, color):
        """Draw s centred on cx, top at y. Advance is 6 units per char."""
        adv = 6 * scale
        x0 = cx - (len(s) * adv) // 2
        for i, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[' '])
            gx = x0 + i * adv
            for r, row in enumerate(glyph):
                for c, bit in enumerate(row):
                    if bit == '1':
                        self.rect(gx + c * scale, y + r * scale,
                                  gx + (c + 1) * scale, y + (r + 1) * scale,
                                  color)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def heart(cv, cx, cy, s, color):
    # Two lobes + a triangle point.
    cv.circle(cx - s // 2, cy - s // 4, s // 2, color)
    cv.circle(cx + s // 2, cy - s // 4, s // 2, color)
    cv.poly([(cx - s, cy), (cx + s, cy), (cx, cy + s)], color)


# ------------------------------------------------------------------- scene
def draw_scene(cv):
    # Sky gradient over the top band.
    for y in range(0, 300):
        cv.hline(0, W, y, lerp(SKY_TOP, SKY_BOT, y / 300.0))

    # Sun with rays, top-left.
    for k in range(8):
        import math
        a = k * math.pi / 4.0
        x0 = int(140 + 52 * math.cos(a))
        y0 = int(110 + 52 * math.sin(a))
        x1 = int(140 + 72 * math.cos(a))
        y1 = int(110 + 72 * math.sin(a))
        cv.line(x0, y0, x1, y1, SUN_RAY, 5)
    cv.circle(140, 110, 42, SUN)
    cv.circle(140, 110, 34, (255, 214, 96))

    # Clouds.
    cv.ellipse(330, 66, 52, 20, CLOUD)
    cv.ellipse(360, 58, 40, 18, CLOUD)
    cv.ellipse(700, 52, 46, 17, CLOUD)
    cv.ellipse(728, 46, 34, 15, CLOUD)

    # Rolling hill the house sits on.
    cv.poly([(0, 300), (0, 262), (200, 240), (420, 258), (640, 238),
             (840, 256), (1024, 242), (1024, 300)], HILL)
    cv.poly([(0, 300), (0, 282), (300, 268), (700, 280), (1024, 266),
             (1024, 300)], HILL_DARK)

    # Path from the door down to the letter.
    cv.poly([(488, 280), (536, 280), (556, 302), (468, 302)], PATH)

    # Trees flanking the house.
    for tx, s in ((296, 1.0), (728, 0.9)):
        cv.rect(int(tx - 7 * s), 210, int(tx + 7 * s), 268, TRUNK)
        cv.circle(tx, 196, int(34 * s), LEAF)
        cv.circle(int(tx - 26 * s), 212, int(24 * s), LEAF_DARK)
        cv.circle(int(tx + 26 * s), 212, int(24 * s), LEAF)
        cv.circle(tx, 176, int(22 * s), LEAF_DARK)

    # Flowers along the hill.
    for fx, fy, col in ((150, 282, FLOWER_RED), (210, 290, FLOWER_YELLOW),
                        (330, 276, FLOWER_YELLOW), (690, 278, FLOWER_RED),
                        (820, 286, FLOWER_YELLOW), (890, 278, FLOWER_RED),
                        (90, 290, FLOWER_YELLOW)):
        cv.circle(fx, fy, 5, col)
        cv.circle(fx, fy, 2, (255, 253, 245))

    # Birds.
    cv.line(880, 120, 894, 130, INK, 3)
    cv.line(894, 130, 908, 120, INK, 3)
    cv.line(930, 96, 942, 104, INK, 3)
    cv.line(942, 104, 954, 96, INK, 3)

    # Chimney smoke: soft rising puffs.
    cv.circle(600, 78, 12, SMOKE)
    cv.circle(612, 58, 15, SMOKE)
    cv.circle(628, 36, 18, SMOKE)

    # The house.
    cv.rect(580, 92, 606, 152, CHIMNEY)          # chimney
    cv.rect(578, 88, 608, 96, ROOF_DARK)         # chimney cap
    cv.poly([(380, 152), (644, 152), (512, 80)], ROOF)   # roof
    cv.poly([(396, 152), (628, 152), (512, 92)], ROOF_DARK)
    cv.rect(412, 152, 612, 282, WALL)            # walls
    cv.rect(412, 152, 612, 160, (232, 205, 164))
    # Door with an arched top.
    cv.rect(482, 206, 542, 282, DOOR)
    cv.circle(512, 206, 30, DOOR)
    cv.circle(534, 246, 4, (255, 215, 106))
    # Glowing windows with cross frames.
    for wx in (438, 546):
        cv.rect(wx, 180, wx + 42, 222, WINDOW)
        cv.rect(wx + 19, 180, wx + 23, 222, WINDOW_FRAME)
        cv.rect(wx, 199, wx + 42, 203, WINDOW_FRAME)
        cv.rect(wx - 3, 177, wx + 45, 180, WINDOW_FRAME)
        cv.rect(wx - 3, 222, wx + 45, 225, WINDOW_FRAME)


def draw_airmail_border(cv, x0, y0, x1, y1):
    """Diagonal red/blue stripes just inside the sheet edge."""
    step = 22
    # Top and bottom edges: slanted quads.
    x = x0
    flip = False
    while x < x1:
        col = AIRMAIL_RED if flip else AIRMAIL_BLUE
        cv.poly([(x, y0), (x + 12, y0), (x + 20, y0 + 10), (x + 8, y0 + 10)],
                col)
        cv.poly([(x, y1 - 10), (x + 12, y1 - 10), (x + 20, y1), (x + 8, y1)],
                col)
        flip = not flip
        x += step
    # Left and right edges.
    y = y0
    flip = False
    while y < y1:
        col = AIRMAIL_RED if flip else AIRMAIL_BLUE
        cv.poly([(x0, y), (x0 + 10, y + 8), (x0 + 10, y + 20), (x0, y + 12)],
                col)
        cv.poly([(x1 - 10, y), (x1, y + 8), (x1, y + 20), (x1 - 10, y + 12)],
                col)
        flip = not flip
        y += step


def draw_stamp(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1, y1, (255, 255, 255))
    cv.rect(x0, y0, x1, y0 + 3, STAMP_RED)
    cv.rect(x0, y0, x1, y1 - 3, STAMP_RED)
    cv.rect(x0, y0, x0 + 3, y1, STAMP_RED)
    cv.rect(x1 - 3, y0, x1, y1, STAMP_RED)
    # Tiny house inside the stamp.
    mx = (x0 + x1) // 2
    cv.poly([(mx - 26, y0 + 34), (mx + 26, y0 + 34), (mx, y0 + 12)],
            STAMP_RED)
    cv.rect(mx - 20, y0 + 34, mx + 20, y0 + 62, AIRMAIL_BLUE)
    cv.rect(mx - 7, y0 + 46, mx + 7, y0 + 62, (255, 253, 246))
    cv.circle(mx + 24, y0 + 16, 5, (242, 165, 65))


def draw_letter(cv):
    # Soft shadow, then the sheet.
    cv.rect(80, 308, 960, 1000, SHADOW)
    cv.rect(72, 300, 952, 992, SHEET)
    draw_airmail_border(cv, 84, 312, 940, 980)
    # Thin inner frame.
    cv.rect(104, 332, 920, 334, BORDER_INK)
    cv.rect(104, 958, 920, 960, BORDER_INK)
    cv.rect(104, 332, 106, 960, BORDER_INK)
    cv.rect(918, 332, 920, 960, BORDER_INK)

    draw_stamp(cv, 852, 348, 936, 428)

    # The letter itself.
    cv.text(HEADING_LINE, 512, 356, 6, HEADING)
    y = 420
    for line in BODY_LINES:
        cv.text(line, 512, y, 5, INK)
        y += 44
    cv.text(PS_LINE, 512, 914, 4, PS_INK)

    # Wax seal with a heart, bottom-right of the sheet.
    cv.circle(898, 946, 30, SEAL)
    cv.circle(898, 946, 22, SEAL_DARK)
    heart(cv, 898, 944, 13, HEART)


# --------------------------------------------------------------------- png
def encode_png(cv):
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    prev = bytearray(cv.w * 3)
    for y in range(cv.h):
        row = cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
        up = bytes((b - p) & 0xFF for b, p in zip(row, prev))
        raw.append(2)  # Up filter
        raw.extend(up)
        prev = row
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def main():
    cv = Canvas(W, H, CREAM)
    draw_scene(cv)
    draw_letter(cv)
    data = encode_png(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
