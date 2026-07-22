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
