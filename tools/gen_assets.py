#!/usr/bin/env python3
"""
Novayclient asset generator.

Every texture shipped in pack/ is generated here, so the pack's artwork is
original, reproducible and reviewable. Vanilla files are never copied into the
repository; only dimensions, nine-slice sidecar values and the crosshair atlas
cell were taken from the Minecraft 1.19.50.2 source tree (docs/REFERENCES.md).

Usage:
    python3 -m venv .venv && .venv/bin/pip install pillow
    .venv/bin/python tools/gen_assets.py

Outputs:
    pack/textures/ui/*.png      HUD + menu artwork
    pack/textures/gui/icons.png crosshair atlas
    pack/pack_icon.png          pack icon
    docs/preview/*.png          review contact sheets
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
UI = PACK / "textures" / "ui"
GUI = PACK / "textures" / "gui"
PREVIEW = ROOT / "docs" / "preview"

# ---------------------------------------------------------------------------
# Theme: single source of truth, mirrored in pack/ui/_novay_theme.json
# ---------------------------------------------------------------------------
INK = (0x0A, 0x0D, 0x13)
PANEL = (0x11, 0x16, 0x20)
PANEL_HI = (0x18, 0x1F, 0x2C)
LINE = (0x22, 0x2D, 0x41)
STEEL = (0x3D, 0x4B, 0x66)
STEEL_HI = (0x5A, 0x6D, 0x8D)
MUTED = (0x8C, 0x9B, 0xB4)
TEXT = (0xE6, 0xEB, 0xF4)
ACCENT = (0x4C, 0xD9, 0xFF)
ACCENT_DK = (0x1B, 0x7E, 0x9E)
SHADOW = (0x03, 0x05, 0x08)
GOLD = (0xF5, 0xC2, 0x54)

TRANSPARENT = (0, 0, 0, 0)


def C(color, alpha=255):
    """Tint helper: RGB tuple -> RGBA, or override alpha."""
    return (color[0], color[1], color[2], alpha)


def rrect(d, box, fill, radius=2, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def border(img, box, color):
    """Draw a 1px border in-place inside box."""
    x0, y0, x1, y1 = box
    ImageDraw.Draw(img).rectangle(box, outline=C(color))


# ===========================================================================
# 1. Crosshair atlas
#    1.19.50 has no font-atlas crosshair and no JSON UI control for it: the
#    first-person reticle is the (0,0)-(15,15) cell of textures/gui/icons.png.
#    A 16x16 atlas keeps the override minimal.
# ===========================================================================
CROSSHAIR_SHAPES = ("classic", "plus", "dot", "bracket")

# The reticle that ships in the pack. Change this to any name in
# CROSSHAIR_SHAPES ("classic", "plus", "dot", "bracket") and re-run this
# script + tools/build.py to switch styles. 1.19.50 has no in-game switch,
# so this is a build-time choice (documented in docs/FEATURES.md).
CROSSHAIR_SHAPE = "classic"


def crosshair(shape="classic", color=ACCENT, outline=SHADOW):
    cell = Image.new("RGBA", (16, 16), TRANSPARENT)
    d = ImageDraw.Draw(cell)
    o, c = C(outline), C(color)
    if shape == "classic":
        # 1px arms from 3..12 on both rows/cols, 2px centre gap
        for x in (3, 4, 5, 6, 9, 10, 11, 12):
            d.point((x, 7), o)
            d.point((x, 8), o)
        for y in (3, 4, 5, 6, 9, 10, 11, 12):
            d.point((7, y), o)
            d.point((8, y), o)
        for x in (4, 5, 6, 9, 10, 11):
            d.point((x, 7), c)
            d.point((x, 8), c)
        for y in (4, 5, 6, 9, 10, 11):
            d.point((7, y), c)
            d.point((8, y), c)
    elif shape == "plus":
        d.rectangle((4, 6, 11, 9), fill=o)
        d.rectangle((6, 4, 9, 11), fill=o)
        d.rectangle((5, 7, 10, 8), fill=c)
        d.rectangle((7, 5, 8, 10), fill=c)
    elif shape == "dot":
        d.rectangle((6, 6, 9, 9), fill=o)
        d.rectangle((7, 7, 8, 8), fill=c)
    elif shape == "bracket":
        # four 3px corner ticks around an open centre, 2px core dot
        for (cx, cy, sx, sy) in ((4, 4, 1, 1), (11, 4, -1, 1), (4, 11, 1, -1), (11, 11, -1, -1)):
            for i in (0, 1, 2):
                d.point((cx + sx * i, cy), o)
                d.point((cx, cy + sy * i), o)
            for i in (1, 2):
                d.point((cx + sx * i, cy), c)
                d.point((cx, cy + sy * i), c)
            d.point((cx, cy), c)
        d.rectangle((7, 7, 8, 8), fill=o)
        d.point((7, 7), c)
        d.point((8, 8), c)
    else:
        raise ValueError(shape)
    return cell


def icons_atlas(shape="classic", color=ACCENT):
    atlas = Image.new("RGBA", (16, 16), TRANSPARENT)
    atlas.alpha_composite(crosshair(shape, color), (0, 0))
    return atlas


# ===========================================================================
# 2. Hotbar (20x22 HUD slot, 24x24 selection frame, 1x22 caps)
# ===========================================================================
def hotbar_slot(corner_accent=True):
    img = Image.new("RGBA", (20, 22), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.rectangle((1, 2, 18, 20), fill=C(PANEL))
    border(img, (1, 2, 18, 20), LINE)
    d.rectangle((2, 3, 17, 19), fill=C(INK))
    d.line((2, 3, 17, 3), fill=C(STEEL, 110))
    if corner_accent:
        for (x, y) in ((1, 2), (16, 2), (1, 17), (16, 17)):
            d.rectangle((x, y, x + 1, y + 1), fill=C(ACCENT_DK))
    return img


def hotbar_selected():
    img = Image.new("RGBA", (24, 24), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 23, 23), outline=C(ACCENT))
    d.rectangle((1, 1, 22, 22), outline=C(ACCENT_DK))
    for (x, y, dx, dy) in ((0, 0, 1, 1), (23, 0, -1, 1), (0, 23, 1, -1), (23, 23, -1, -1)):
        d.line((x, y, x + 3 * dx, y), fill=C(TEXT))
        d.line((x, y, x, y + 3 * dy), fill=C(TEXT))
    return img


def hotbar_cap():
    img = Image.new("RGBA", (1, 22), TRANSPARENT)
    for y in range(2, 21):
        img.putpixel((0, y), C(STEEL))
    return img


# ===========================================================================
# 3. Hearts / hunger / armor
#    Vanilla canvas is 9x9 for every HUD status sprite. Shapes are original but
#    follow the classic silhouette families so the HUD still reads instantly.
# ===========================================================================
# Full heart, 9x9. Each row is a list of (x_start, x_end) inclusive runs.
HEART_ROWS = [
    [(1, 2), (6, 7)],
    [(0, 3), (5, 8)],
    [(0, 8)],
    [(0, 8)],
    [(0, 8)],
    [(1, 7)],
    [(2, 6)],
    [(3, 5)],
    [(4, 4)],
]
# Ham shank, 9x9. Meat on the left, bone tip to the lower right.
HUNGER_ROWS = [
    [(1, 4), (6, 7)],
    [(0, 4), (5, 7)],
    [(0, 3)],
    [(0, 3)],
    [(1, 3)],
    [(2, 3), (5, 5)],
    [(3, 3), (4, 5)],
    [(4, 5)],
    [(5, 5)],
]
# Chestplate, 9x9.
ARMOR_ROWS = [
    [(1, 7)],
    [(0, 8)],
    [(0, 1), (3, 5), (7, 8)],
    [(0, 1), (3, 5), (7, 8)],
    [(0, 1), (3, 5), (7, 8)],
    [(0, 1), (3, 5), (7, 8)],
    [(1, 7)],
    [(2, 6)],
    [(3, 5)],
]


def mask_from(rows, size=9):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    for y, runs in enumerate(rows):
        for x0, x1 in runs:
            d.line((x0, y, x1, y), fill=255)
    return m


def outline_mask(mask, grow=1):
    return mask.filter(ImageFilter.MaxFilter(grow * 2 + 1))


def sprite(rows, fill, shade, *, outline=SHADOW, shine=None, half=None,
           empty=False, bg_only=False, extra_shine=None):
    """
    Build a 9x9 icon from an ASCII-style run mask.

    half:  'right' keeps the left half filled, 'left' keeps the right half.
    empty: draw only the dark background version of the shape.
    """
    m = mask_from(rows)
    shadow = outline_mask(m)
    img = Image.new("RGBA", (9, 9), TRANSPARENT)
    img.paste(C(outline, 215), (0, 0), shadow)

    inner = Image.new("RGBA", (9, 9), TRANSPARENT)
    d = ImageDraw.Draw(inner)
    for y in range(9):
        for x in range(9):
            if not m.getpixel((x, y)):
                continue
            if half == "right" and x > 4:
                continue
            if half == "left" and x < 4:
                continue
            if bg_only:
                d.point((x, y), C((0x24, 0x2C, 0x3B), 245))
            elif y >= 6:
                d.point((x, y), C(shade))
            else:
                d.point((x, y), C(fill))
    if not bg_only and not empty:
        shine_pts = shine if shine is not None else [(1, 1), (2, 1)]
        for (x, y) in shine_pts:
            if m.getpixel((x, y)) and (half is None or (half == "right" and x <= 4) or (half == "left" and x >= 4)):
                d.point((x, y), C((0xFA, 0xFD, 0xFF), 225))
        for (x, y) in (extra_shine or []):
            if m.getpixel((x, y)):
                d.point((x, y), C(fill, 255))
    img.alpha_composite(inner)
    if half:
        # darken the emptied side so a half icon still reads as a full slot
        dark = Image.new("RGBA", (9, 9), TRANSPARENT)
        dd = ImageDraw.Draw(dark)
        for y in range(9):
            for x in range(9):
                if not m.getpixel((x, y)):
                    continue
                if (half == "right" and x > 4) or (half == "left" and x < 4):
                    dd.point((x, y), C((0x1A, 0x21, 0x2D), 235))
        img.alpha_composite(dark)
    return img


def heart(fill, shade, **kw):
    return sprite(HEART_ROWS, fill, shade, shine=[(1, 1), (2, 1), (1, 2)], **kw)


def hunger(fill, shade, **kw):
    return sprite(HUNGER_ROWS, fill, shade, shine=[(1, 1), (1, 2)], **kw)


def armor(fill, shade, **kw):
    return sprite(ARMOR_ROWS, fill, shade, shine=[(1, 1), (2, 1)], **kw)


def water_bubble(full=True):
    img = Image.new("RGBA", (9, 9), TRANSPARENT)
    d = ImageDraw.Draw(img)
    if full:
        d.ellipse((1, 1, 7, 7), fill=C((0x4E, 0xB6, 0xE8), 240))
        d.ellipse((2, 2, 6, 6), fill=C((0x9A, 0xE2, 0xFF), 250))
        d.point((3, 2), C((255, 255, 255), 235))
        d.point((2, 3), C((255, 255, 255), 200))
    else:
        d.ellipse((1, 1, 7, 7), outline=C(STEEL, 230))
    return img


def xp_strip(kind):
    if kind == "empty":
        img = Image.new("RGBA", (13, 5), C((0x0B, 0x10, 0x19)))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 12, 4), outline=C(LINE))
        return img
    if kind == "full":
        img = Image.new("RGBA", (13, 5), C(ACCENT_DK))
        d = ImageDraw.Draw(img)
        for y in (0, 4):
            d.line((0, y, 12, y), fill=C(ACCENT))
        d.line((0, 1, 12, 1), fill=C((0x86, 0xE8, 0xFF)))
        d.line((0, 2, 12, 2), fill=C(ACCENT_DK))
        return img
    if kind == "nub":
        img = Image.new("RGBA", (11, 5), TRANSPARENT)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 1, 10, 3), fill=C(TEXT))
        return img
    raise ValueError(kind)


# ===========================================================================
# 4. Inventory / menu surfaces (exact vanilla canvas sizes)
# ===========================================================================
def cell_image(kind="normal"):
    palette = {
        "normal": (PANEL_HI, LINE),
        "darkgrey": (PANEL, LINE),
        "invert": (STEEL, STEEL_HI),
        "red": ((0x2B, 0x11, 0x16), (0xFF, 0x5A, 0x6E)),
        "lock": ((0x19, 0x15, 0x0F), (0x6B, 0x54, 0x27)),
    }
    fill, edge = palette[kind]
    img = Image.new("RGBA", (5, 5), C(fill))
    border(img, (0, 0, 4, 4), edge)
    return img


def highlight_slot():
    return Image.new("RGBA", (1, 1), C(ACCENT, 170))


def dialog_surface():
    img = Image.new("RGBA", (16, 16), C(PANEL))
    d = ImageDraw.Draw(img)
    border(img, (0, 0, 15, 15), LINE)
    d.line((1, 1, 14, 1), fill=C(PANEL_HI))
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)):
        d.point((x, y), C(ACCENT_DK))
    return img


def pause_border():
    img = Image.new("RGBA", (5, 5), C(PANEL))
    border(img, (0, 0, 4, 4), LINE)
    return img


def tip_background():
    img = Image.new("RGBA", (6, 6), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 5, 5), fill=C(INK, 205))
    d.rectangle((0, 0, 5, 5), outline=C(LINE))
    return img



def bubble_strip(full):
    """12x30 rotating bubble texture (vanilla size)."""
    img = Image.new("RGBA", (12, 30), TRANSPARENT)
    src = water_bubble(full)
    for i in range(3):
        img.alpha_composite(src, (1, i * 10 + 1))
    return img


# ===========================================================================
# 5. Branding
# ===========================================================================
def pack_icon(size=256):
    img = Image.new("RGBA", (size, size), C(INK))
    d = ImageDraw.Draw(img)
    rrect(d, (6, 6, size - 7, size - 7), C((0x0E, 0x12, 0x1A)), radius=28, outline=C(LINE), width=2)
    for (x, y, sx, sy) in ((22, 22, 1, 1), (size - 23, 22, -1, 1), (22, size - 23, 1, -1), (size - 23, size - 23, -1, -1)):
        d.line((x, y, x + 40 * sx, y), fill=C(ACCENT_DK), width=2)
        d.line((x, y, x, y + 40 * sy), fill=C(ACCENT_DK), width=2)
        d.point((x + 3 * sx, y + 3 * sy), C(ACCENT))
    # N monogram: two vertical strokes, diagonal, cyan
    d.line((72, 188, 72, 76), fill=C(TEXT), width=18)
    d.line((184, 188, 184, 76), fill=C(TEXT), width=18)
    d.line((72, 78, 184, 186), fill=C(ACCENT), width=18)
    d.rectangle((70, 208, 186, 214), fill=C(ACCENT_DK))
    return img


# 3x5 pixel font used for the wordmark (each glyph is 3 wide, 5 tall).
FONT_3x5 = {
    "N": ["X.X", "XXX", "XXX", "X.X", "X.X"],
    "O": [".X.", "X.X", "X.X", "X.X", ".X."],
    "V": ["X.X", "X.X", "X.X", ".X.", ".X."],
    "A": [".X.", "X.X", "XXX", "X.X", "X.X"],
    "Y": ["X.X", "X.X", ".X.", ".X.", ".X."],
    "C": [".XX", "X..", "X..", "X..", ".XX"],
    "L": ["X..", "X..", "X..", "X..", "XXX"],
    "I": ["XXX", ".X.", ".X.", ".X.", "XXX"],
    "E": ["XXX", "X..", "XXX", "X..", "XXX"],
    "T": ["XXX", ".X.", ".X.", ".X.", ".X."],
}


def draw_pixel_text(d, text, x0, y0, scale=2, fill=TEXT, accent_letters=""):
    """Draw text with the built-in 3x5 font; returns the x cursor after drawing."""
    x = x0
    for ch in text:
        glyph = FONT_3x5.get(ch)
        if glyph is None:
            x += 4 * scale
            continue
        color = ACCENT if ch in accent_letters else fill
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "X":
                    d.rectangle((x + gx * scale, y0 + gy * scale,
                                 x + gx * scale + scale - 1, y0 + gy * scale + scale - 1),
                                fill=C(color))
        x += 4 * scale
    return x


def logo(w=90, h=21):
    """Wordmark plate: 45x10.5 UI units drawn at 2x (90x21 px)."""
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), C(INK, 228), radius=4, outline=C(ACCENT_DK))
    # chevron mark
    d.line((5, 5, 8, 10), fill=C(ACCENT))
    d.line((5, 15, 8, 10), fill=C(ACCENT))
    d.line((4, 10, 10, 10), fill=C(ACCENT_DK))
    end = draw_pixel_text(d, "NOVAYCLIENT", 14, 4, scale=1, fill=TEXT, accent_letters="N")
    d.line((14, 16, end - 2, 16), fill=C(ACCENT_DK))
    return img


# ===========================================================================
# 6. Low-fire asset
# ===========================================================================
def low_fire_from_vanilla(src: Path, out: Path, keep=0.55):
    """
    Shorten each 16x16 frame of a 16x512 flame strip and soften it.

    The source strip must be supplied by the developer from their own copy of
    the game (see docs/FEATURES.md); it is not redistributed. The reduced strip
    stays 16x512 so the vanilla flipbook definition still applies.
    """
    src_img = Image.open(src).convert("RGBA")
    w, h = src_img.size
    frames = h // 16
    out_img = Image.new("RGBA", (w, h), TRANSPARENT)
    for i in range(frames):
        frame = src_img.crop((0, i * 16, 16, i * 16 + 16))
        bbox = frame.getbbox()
        if not bbox:
            continue
        keep_from = bbox[1] + int((bbox[3] - bbox[1]) * (1 - keep))
        region = frame.crop((0, keep_from, 16, bbox[3]))
        region.putalpha(region.getchannel("A").point(lambda v: int(v * 0.72)))
        out_img.paste(region, (0, i * 16 + (16 - region.height)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out)
    print(f"  {out.relative_to(ROOT)}  {out_img.size[0]}x{out_img.size[1]}")


# ===========================================================================
# Build
# ===========================================================================
def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def build_all():
    print("Novayclient asset build")

    # --- crosshair ------------------------------------------------------
    save(icons_atlas(CROSSHAIR_SHAPE), GUI / "icons.png")
    print("  crosshair atlas 16x16")
    for shape in CROSSHAIR_SHAPES:
        save(crosshair(shape), PREVIEW / f"crosshair_{shape}.png")

    # --- hotbar ---------------------------------------------------------
    for i in range(9):
        save(hotbar_slot(), UI / f"hotbar_{i}.png")
    save(hotbar_selected(), UI / "selected_hotbar_slot.png")
    save(hotbar_cap(), UI / "hotbar_start_cap.png")
    save(hotbar_cap(), UI / "hotbar_end_cap.png")
    print("  hotbar 9 slots + selection + caps")

    # --- hearts ---------------------------------------------------------
    heart_sets = {
        "heart": ((0xFF, 0x4D, 0x5E), (0xC8, 0x22, 0x3C)),
        "heart_flash": ((0xFF, 0x92, 0x9C), (0xE2, 0x4C, 0x60)),
        "heart_blink": ((0x93, 0xA2, 0xBA), (0x5C, 0x68, 0x7E)),
        "heart_new": ((0xFF, 0x4D, 0x5E), (0xC8, 0x22, 0x3C)),
        "poison_heart": ((0xA6, 0xE0, 0x74), (0x5F, 0xA8, 0x3A)),
        "wither_heart": ((0x55, 0x55, 0x5E), (0x2C, 0x2C, 0x32)),
        "absorption_heart": ((0xF5, 0xC2, 0x54), (0xC0, 0x8E, 0x28)),
        "freeze_heart": ((0x93, 0xCC, 0xF2), (0x4B, 0x8C, 0xBE)),
        "freeze_heart_flash": ((0xD3, 0xF1, 0xFF), (0x7F, 0xB8, 0xD8)),
    }
    for name, (f, s) in heart_sets.items():
        save(heart(f, s), UI / f"{name}.png")
        if name not in ("heart", "heart_new"):
            save(heart(f, s, half="left"), UI / f"{name}_half.png")
    save(heart((0xFF, 0x4D, 0x5E), (0xC8, 0x22, 0x3C), half="left"), UI / "heart_half.png")
    save(sprite(HEART_ROWS, None, None, bg_only=True), UI / "heart_background.png")
    print("  hearts (9 state variants + halves)")

    # --- hunger ---------------------------------------------------------
    hunger_sets = {
        "hunger_full": ((0xD8, 0x9B, 0x5A), (0x99, 0x5E, 0x2C), "full"),
        "hunger_half": ((0xD8, 0x9B, 0x5A), (0x99, 0x5E, 0x2C), "half"),
        "hunger_blink": ((0xAA, 0xB6, 0xC8), (0x6E, 0x7A, 0x8C), "full"),
        "hunger_flash_full": ((0xF2, 0xBA, 0x78), (0xB8, 0x7C, 0x3C), "full"),
        "hunger_flash_half": ((0xF2, 0xBA, 0x78), (0xB8, 0x7C, 0x3C), "half"),
        "hunger_effect_full": ((0xA6, 0xE0, 0x74), (0x5F, 0xA8, 0x3A), "full"),
        "hunger_effect_half": ((0xA6, 0xE0, 0x74), (0x5F, 0xA8, 0x3A), "half"),
        "hunger_effect_flash_full": ((0xC4, 0xF2, 0x96), (0x7C, 0xC0, 0x4C), "full"),
        "hunger_effect_flash_half": ((0xC4, 0xF2, 0x96), (0x7C, 0xC0, 0x4C), "half"),
    }
    for name, (f, s, half) in hunger_sets.items():
        save(hunger(f, s, half="left" if half == "half" else None), UI / f"{name}.png")
    save(sprite(HUNGER_ROWS, None, None, bg_only=True), UI / "hunger_background.png")
    save(sprite(HUNGER_ROWS, None, None, bg_only=True), UI / "hunger_effect_background.png")
    print("  hunger (9 state variants)")

    # --- armor ----------------------------------------------------------
    save(armor((0xD3, 0xDD, 0xEA), (0x7E, 0x8C, 0xA4)), UI / "armor_full.png")
    save(armor((0xD3, 0xDD, 0xEA), (0x7E, 0x8C, 0xA4), half="left"), UI / "armor_half.png")
    save(sprite(ARMOR_ROWS, None, None, bg_only=True), UI / "armor_empty.png")

    # --- air / xp -------------------------------------------------------
    save(water_bubble(True), UI / "bubble.png")
    save(bubble_strip(True), UI / "bubbles_full.png")
    save(bubble_strip(False), UI / "bubbles_empty.png")
    save(xp_strip("empty"), UI / "experiencebarempty.png")
    save(xp_strip("full"), UI / "experiencebarfull.png")
    save(xp_strip("nub"), UI / "experiencenub.png")
    save(xp_strip("empty"), UI / "experience_bar_empty_blue.png")
    save(xp_strip("full"), UI / "experience_bar_full_blue.png")
    save(xp_strip("full"), UI / "experience_bar_full_white.png")

    # --- effect + misc hud ---------------------------------------------
    save(tip_background(), UI / "hud_tip_text_background.png")

    # --- inventory / menu surfaces -------------------------------------
    for kind in ("normal", "darkgrey", "invert", "red", "lock"):
        save(cell_image(kind), UI / f"cell_image_{kind}.png")
    save(cell_image("normal"), UI / "cell_image.png")
    save(highlight_slot(), UI / "highlight_slot.png")
    save(dialog_surface(), UI / "dialog_background_opaque.png")
    save(pause_border(), UI / "pause_screen_border.png")
    print("  inventory + menu surfaces")

    # --- branding -------------------------------------------------------
    save(pack_icon(), PACK / "pack_icon.png")
    save(logo(), UI / "novay_logo.png")
    print("  pack icon + wordmark")

    build_preview()
    print("done")


def build_preview():
    PREVIEW.mkdir(parents=True, exist_ok=True)
    scale = 9
    items = [
        ("crosshair", GUI / "icons.png", 16, 16),
        ("hotbar", UI / "hotbar_0.png", 20, 22),
        ("selected", UI / "selected_hotbar_slot.png", 24, 24),
        ("heart", UI / "heart.png", 9, 9),
        ("half", UI / "heart_half.png", 9, 9),
        ("heart bg", UI / "heart_background.png", 9, 9),
        ("poison", UI / "poison_heart.png", 9, 9),
        ("absorption", UI / "absorption_heart.png", 9, 9),
        ("hunger", UI / "hunger_full.png", 9, 9),
        ("hunger bg", UI / "hunger_background.png", 9, 9),
        ("armor full", UI / "armor_full.png", 9, 9),
        ("armor empty", UI / "armor_empty.png", 9, 9),
        ("bubble", UI / "bubble.png", 9, 9),
        ("xp full", UI / "experiencebarfull.png", 13, 5),
        ("xp empty", UI / "experiencebarempty.png", 13, 5),
        ("cell", UI / "cell_image.png", 5, 5),
        ("dialog", UI / "dialog_background_opaque.png", 16, 16),
        ("tip", UI / "hud_tip_text_background.png", 6, 6),
    ]
    pad, top = 12, 14
    w = sum(i[2] * scale + pad for i in items) + pad
    h = max(i[3] * scale for i in items) + top * 2
    sheet = Image.new("RGBA", (w, h), (0x14, 0x18, 0x20, 255))
    x = pad
    for _, path, iw, ih in items:
        im = Image.open(path).convert("RGBA").resize((iw * scale, ih * scale), Image.NEAREST)
        sheet.alpha_composite(im, (x, top))
        x += iw * scale + pad
    sheet.save(PREVIEW / "hud_art.png")

    # combined "in game" mock strip: hearts + hunger + hotbar row
    mock_w, mock_h = 420, 96
    mock = Image.new("RGBA", (mock_w, mock_h), (0x2A, 0x3A, 0x2A, 255))
    d = ImageDraw.Draw(mock)
    for i in range(10):
        mock.alpha_composite(Image.open(UI / "heart.png"), (10 + i * 10, 12))
        mock.alpha_composite(Image.open(UI / "hunger_full.png").transpose(Image.FLIP_LEFT_RIGHT), (330 + i * 9, 12))
    for i in range(9):
        mock.alpha_composite(Image.open(UI / "hotbar_0.png"), (110 + i * 20, 62))
    mock.alpha_composite(Image.open(UI / "selected_hotbar_slot.png"), (110 + 4 * 20 - 2, 60))
    mock.alpha_composite(Image.open(GUI / "icons.png"), ((mock_w - 16) // 2, 40))
    mock.resize((mock_w * 2, mock_h * 2), Image.NEAREST).save(PREVIEW / "hud_mock.png")

    icon = Image.open(PACK / "pack_icon.png")
    brand = Image.new("RGBA", (icon.width + 40, icon.height + 140), (0x0A, 0x0D, 0x13, 255))
    brand.alpha_composite(icon, (20, 20))
    brand.alpha_composite(logo().resize((480, 112), Image.NEAREST), (20, 300))
    brand.save(PREVIEW / "branding.png")
    print("  preview sheets -> docs/preview/")


if __name__ == "__main__":
    build_all()
