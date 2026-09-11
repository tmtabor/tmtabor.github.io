#!/usr/bin/env python3
"""Download the self-hosted webfont subsets into theme/static/fonts/.

    python3 scripts/fetch_fonts.py

The site self-hosts its fonts rather than linking Google Fonts, so the files in
theme/static/fonts/ are committed. This script records where they came from and
makes refreshing them repeatable -- it is not part of the build.

It asks the Google Fonts API for the same families and weights the site used to
request, then keeps the latin and latin-ext subsets. Those are variable fonts:
one file per family per subset covers every weight.

After running this, regenerate the stylesheet so the @font-face rules in
scripts/tailwind/input.css still match:

    python3 scripts/build_css.py
"""
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "theme" / "static" / "fonts"

# The exact request base.html used to make, before the fonts were self-hosted.
CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Inter:wght@300;400;500;600"
    "&family=Roboto+Slab:wght@400;600;700"
    "&display=swap"
)
# A modern desktop UA, or the API serves legacy ttf instead of woff2.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# Latin covers every character the site renders today; latin-ext is insurance
# for names with Central/Eastern European diacritics. unicode-range means an
# unused subset is never downloaded by a visitor.
SUBSETS = {"latin", "latin-ext"}


def fetch_css():
    req = urllib.request.Request(CSS_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.read().decode()


def main():
    css = fetch_css()
    blocks = re.findall(r"/\* (\S+) \*/\s*@font-face \{(.*?)\}", css, re.S)
    if not blocks:
        sys.exit("could not parse the Google Fonts stylesheet; the format may have changed")

    DEST.mkdir(parents=True, exist_ok=True)
    seen = set()
    for subset, block in blocks:
        if subset not in SUBSETS:
            continue
        family = re.search(r"font-family: '([^']+)'", block).group(1)
        if (family, subset) in seen:
            continue  # same variable file is declared once per weight
        seen.add((family, subset))

        url = re.search(r"url\((\S+?)\)", block).group(1)
        name = f"{family.lower().replace(' ', '-')}-{subset}.woff2"
        out = DEST / name
        urllib.request.urlretrieve(url, out)
        print(f"  {out.stat().st_size:>7,}B  {name}")

        rng = re.search(r"unicode-range: ([^;]+);", block).group(1).strip()
        if rng not in (ROOT / "scripts" / "tailwind" / "input.css").read_text():
            print(f"    ! unicode-range for {family}/{subset} differs from input.css -- update it")

    print(f"\nwrote {len(seen)} files to {DEST.relative_to(ROOT)}")
    print("now run: python3 scripts/build_css.py")


if __name__ == "__main__":
    main()
