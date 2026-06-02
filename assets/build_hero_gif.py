#!/usr/bin/env python3
"""
DEV-ONLY asset generator — builds assets/hero.gif (the animated README hero).

This is NOT part of the rangey skill and is NOT a runtime dependency. The skill
scripts in scripts/ stay zero-dependency. This file just needs Pillow to render
a small terminal-style animation (a stand-in until a real screen recording).

    python3 -m venv /tmp/gifvenv
    /tmp/gifvenv/bin/pip install pillow
    /tmp/gifvenv/bin/python assets/build_hero_gif.py
"""

from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersample, then downscale for crisp text
W, H = 820, 500
OUT = "assets/hero.gif"

BG     = (13, 17, 23)
BORDER = (48, 54, 61)
LINE   = (33, 38, 45)
GRAY   = (173, 187, 200)
DIM    = (118, 131, 144)
FAINT  = (86, 96, 107)
WHITE  = (230, 237, 243)
GREEN  = (63, 185, 80)
ORANGE = (240, 136, 62)
BLUE   = (56, 139, 253)


def _font(size, index=0):
    for path in ("/System/Library/Fonts/Menlo.ttc",
                 "/System/Library/Fonts/Monaco.ttf",
                 "/System/Library/Fonts/SFNSMono.ttf"):
        try:
            return ImageFont.truetype(path, size * S, index=index)
        except Exception:
            continue
    return ImageFont.load_default()


F_T = _font(14)   # title bar
F_B = _font(15)   # body
F_D = _font(13)   # detail


def sc(v):
    return int(v * S)


def seg(d, x, y, parts, font):
    """parts = [(text, color), ...] drawn left-to-right; returns end x (unscaled)."""
    for text, color in parts:
        d.text((sc(x), sc(y)), text, font=font, fill=color)
        x += d.textlength(text, font=font) / S
    return x


ROWS = [
    dict(label="Putting",     val="3.0", vcol=ORANGE, w=345, bcol=ORANGE,
         detail="37 putts vs ~34 for your level"),
    dict(label="Off the tee", val="1.0", vcol=GRAY,   w=115, bcol=BLUE,
         detail="7/14 fairways (50%) vs ~45%, 1 penalty"),
    dict(label="Short game",  val="0.8", vcol=GRAY,   w=92,  bcol=BLUE,
         detail="3/12 up-and-downs (25%) vs ~33%"),
    dict(label="Approach",    val="0.0", vcol=FAINT,  w=6,   bcol=FAINT,
         detail="6/18 greens (33%) vs ~30%"),
]
ROW_Y = [166, 220, 274, 328]


def scene(bars, details, leak, trend):
    img = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([sc(1), sc(1), sc(W - 2), sc(H - 2)],
                        radius=sc(14), outline=BORDER, width=S)

    # title bar
    for i, c in enumerate([(255, 95, 86), (254, 188, 46), (40, 200, 64)]):
        x = 22 + 22 * i
        d.ellipse([sc(x), sc(21), sc(x + 12), sc(33)], fill=c)
    seg(d, 100, 22, [("rangey", DIM), ("   ·   scorecard read", FAINT)], F_T)
    d.line([(0, sc(54)), (sc(W), sc(54))], fill=LINE, width=S)

    seg(d, 28, 84, [("> ", GREEN),
                    ("here's my scorecard — what should I work on?", GRAY)], F_B)
    seg(d, 28, 124, [("WHERE YOUR STROKES GO", WHITE),
                     ("    (mid · round of 92)", DIM)], F_B)

    for r, ry in zip(ROWS, ROW_Y):
        w = max(2, int(r["w"] * bars))
        d.rounded_rectangle([sc(250), sc(ry + 4), sc(250 + w), sc(ry + 24)],
                            radius=sc(3), fill=r["bcol"])
        d.text((sc(30), sc(ry)), r["label"], font=F_B, fill=GRAY)
        d.text((sc(182), sc(ry)), r["val"], font=F_B, fill=r["vcol"])
        if details:
            d.text((sc(250), sc(ry + 28)), "└ " + r["detail"], font=F_D, fill=DIM)

    if leak:
        d.rounded_rectangle([sc(24), sc(388), sc(590), sc(420)],
                            radius=sc(6), outline=ORANGE, width=S)
        d.ellipse([sc(40), sc(398), sc(52), sc(410)], outline=ORANGE, width=S)
        d.ellipse([sc(44), sc(402), sc(48), sc(406)], fill=ORANGE)
        seg(d, 64, 396, [("Biggest leak: ", WHITE), ("Putting", ORANGE),
                         ("   (~3.0 strokes vs your level)", DIM)], F_B)

    if trend:
        seg(d, 30, 448, [("after practicing it:   ", FAINT), ("92", DIM),
                         (" -> ", FAINT), ("86", GREEN),
                         ("    -6 strokes (the leak shrank)", GREEN)], F_D)

    return img.resize((W, H), Image.LANCZOS)


FRAMES = [
    (scene(0.0, False, False, False), 750),
    (scene(0.25, False, False, False), 130),
    (scene(0.5, False, False, False), 130),
    (scene(0.75, False, False, False), 130),
    (scene(1.0, False, False, False), 200),
    (scene(1.0, True, False, False), 550),
    (scene(1.0, True, True, False), 850),
    (scene(1.0, True, True, True), 2600),
]

imgs = [f[0] for f in FRAMES]
durs = [f[1] for f in FRAMES]
pal = imgs[-1].convert("P", palette=Image.ADAPTIVE, colors=128)
imgs_p = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
imgs_p[0].save(OUT, save_all=True, append_images=imgs_p[1:],
               duration=durs, loop=0, optimize=True, disposal=2)
print(f"wrote {OUT}  ({len(imgs_p)} frames)")
