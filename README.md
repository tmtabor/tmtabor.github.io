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
