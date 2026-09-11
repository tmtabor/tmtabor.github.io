#!/usr/bin/env python3
"""Generate a 1200x630 share image for a post, styled like the rest of the site.

    python3 scripts/make_og_image.py content/articles/2026-07-28-module-toolkit.md

Reads Title, Summary and Date from the post's metadata, writes
content/images/og-<slug>.png, and prints the `Image:` line to paste into the
post. Fonts are fetched once into .cache/fonts/ (gitignored).

Requires Pillow: the system python3 on macOS usually has it. If not,
`uv run --with pillow python3 scripts/make_og_image.py ...` works too.
"""
import pathlib
import re
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / ".cache" / "fonts"
FONTS = {
    "RobotoSlab.ttf": "https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf",
    "Inter.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
}

W, H = 1200, 630
GROUND, CARD, BORDER = "#e9edf2", "#ffffff", "#e2e8f0"
SLATE900, SLATE600, RED900 = "#0f172a", "#475569", "#7f1d1d"
PAD_X, TOP = 112, 112


def ensure_fonts():
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FONTS.items():
        dest = FONT_DIR / name
        if not dest.exists():
            print(f"fetching {name}...")
            urllib.request.urlretrieve(url, dest)
    return FONT_DIR


def load(name, size, weight):
    """Variable fonts: pick a weight along the wght axis."""
    f = ImageFont.truetype(str(FONT_DIR / name), size)
    f.set_variation_by_axes([weight])
    return f


def meta(md, key, default=""):
    m = re.search(rf"^{key}:\s*(.+)$", md, re.M)
    return m.group(1).strip() if m else default


def tracked(draw, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track


def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main(post_path):
    post = pathlib.Path(post_path)
    md = post.read_text()
    title = meta(md, "Title")
    summary = meta(md, "Summary")
    slug = meta(md, "Slug") or post.stem
    date = meta(md, "Date")[:10]
    if not title:
        sys.exit(f"no Title: found in {post}")

    ensure_fonts()
    img = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 40, W - 40, H - 40], radius=24, fill=CARD, outline=BORDER, width=1)

    f_kicker = load("Inter.ttf", 20, 600)
    f_title = load("RobotoSlab.ttf", 62, 700)
    f_sum = load("Inter.ttf", 26, 400)
    f_foot = load("Inter.ttf", 20, 500)
    maxw = W - 2 * PAD_X

    y = TOP
    tracked(d, (PAD_X, y), "THORIN TABOR", f_kicker, RED900, 3.2)
    y += 60

    title_lines = wrap(d, title, f_title, maxw)
    if len(title_lines) > 3:
        sys.exit(f"title wraps to {len(title_lines)} lines; shorten it or drop the title size")
    for line in title_lines:
        d.text((PAD_X, y), line, font=f_title, fill=SLATE900)
        y += 72
    y += 16

    for line in wrap(d, summary, f_sum, maxw)[:3]:
        d.text((PAD_X, y), line, font=f_sum, fill=SLATE600)
        y += 38

    d.text((PAD_X, H - 132), f"tmtabor.io  ·  {date}", font=f_foot, fill=RED900)

    out = ROOT / "content" / "images" / f"og-{slug}.png"
    img.save(out, "PNG")
    print(f"\nwrote {out.relative_to(ROOT)} — {W}x{H}, {out.stat().st_size // 1024}KB")
    print(f"\nadd this to {post.name}:\n\n    Image: images/og-{slug}.png\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
