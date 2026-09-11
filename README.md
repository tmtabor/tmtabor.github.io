# tmtabor.io

Personal site, built with [Pelican](https://getpelican.com/).

## Develop

```sh
uv run pelican --autoreload --listen -s pelicanconf.py
```

Serves at http://localhost:8000/.

## Build

```sh
uv run pelican content -o output -s publishconf.py
```

Deployment to GitHub Pages happens automatically via `.github/workflows/pages.yml` on push to `main`.

## Styles

Tailwind is compiled ahead of time into `theme/static/css/main.css`, which is
**committed** — the deploy workflow has no frontend build step and cannot
generate it. Adding a utility class to a template is therefore only half the
change: regenerate and commit the CSS too, or the class will silently do
nothing in production.

```sh
python3 scripts/build_css.py
```

The script fetches the Tailwind standalone CLI once into `.cache/tailwind/`
(gitignored) and checksum-verifies it against the release's `sha256sums.txt`.
It is a single self-contained binary — no Node, no npm, no `node_modules`.

It builds the site to `.cache/css-scan/` first so the CLI scans generated HTML
as well as templates, catching classes that only Markdown or Pelican produce.

Two other modes:

```sh
python3 scripts/build_css.py --watch   # rebuild as you edit templates
python3 scripts/build_css.py --check   # exit non-zero if main.css is stale
```

`--watch` is worth running in a second terminal alongside the dev server when
doing design work, so new classes appear without a manual regen.

Custom CSS that Tailwind does not generate — the card animations, nav
underlines, project status badges, article body styles — lives in the inline
`<style>` block in `theme/templates/base.html` and needs no regeneration.
Pinned Tailwind version: `VERSION` in `scripts/build_css.py`.

### Fonts

Inter and Roboto Slab are **self-hosted** from `theme/static/fonts/` rather
than loaded from Google Fonts, so the site makes no third-party requests for
them. The `@font-face` rules live in `scripts/tailwind/input.css` and compile
into `main.css`; `base.html` preloads the two latin subsets.

These are variable fonts — one file per family per subset covers every weight,
so the whole site costs two font requests. The `latin-ext` files are committed
but only downloaded if a page actually contains those characters, which
`unicode-range` decides; they are insurance for names with Central or Eastern
European diacritics and cost nothing until used.

To refresh or change weights:

```sh
python3 scripts/fetch_fonts.py   # re-download the subsets
python3 scripts/build_css.py     # recompile main.css
```

Licenses ship alongside the files: Inter is OFL-1.1, Roboto Slab Apache-2.0.

## Writing a post

Posts live in `content/articles/` as Markdown with a metadata header:

```
Title: Building the GenePattern Module Toolkit
Date: 2026-07-28
Slug: genepattern-module-toolkit
Tags: genepattern, agentic-ai
Summary: One sentence, used for the meta description, the feed and link previews.
Image: images/og-module-toolkit.png
```

`Image:` is optional and sets the post's share image for Open Graph, Twitter
cards and the `BlogPosting` JSON-LD. Give a path relative to the site root or a
full URL; without it, posts fall back to `images/og-default.png`.

**Share images must be 1200x630** — `base.html` declares those dimensions to
crawlers, so an image of another size will be described incorrectly. Put them
in `content/images/`, which is copied to `/images/` at build time.

To generate one in the site's style, point the script at the post:

```sh
python3 scripts/make_og_image.py content/articles/2026-07-28-module-toolkit.md
```

It reads the post's Title, Summary and Date, writes
`content/images/og-<slug>.png`, and prints the `Image:` line to paste back in.
Fonts are fetched once into `.cache/fonts/`.
