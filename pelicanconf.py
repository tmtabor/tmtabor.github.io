from datetime import datetime

AUTHOR = "Thorin Tabor"
SITENAME = "Thorin Tabor"
SITEURL = ""

PATH = "content"
THEME = "theme"

TIMEZONE = "America/Los_Angeles"
DEFAULT_LANG = "en"

# Content locations
ARTICLE_PATHS = ["articles"]
PAGE_PATHS = ["pages"]

STATIC_PATHS = ["images", "extra/CNAME"]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
}

# Routing: /blog/<slug>/ for posts, /blog/ for the full index, hand-built
# templates for / and /bio/ via TEMPLATE_PAGES.
ARTICLE_URL = "blog/{slug}/"
ARTICLE_SAVE_AS = "blog/{slug}/index.html"

DIRECT_TEMPLATES = ["archives"]
ARCHIVES_URL = "blog/"
ARCHIVES_SAVE_AS = "blog/index.html"

TEMPLATE_PAGES = {
    "index.html": "index.html",
    "bio.html": "bio/index.html",
}

JINJA_GLOBALS = {
    "current_year": datetime.now().year,
}

DEFAULT_PAGINATION = False

# Single-author, single-category site — no per-author/category/tag pages needed.
AUTHOR_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
TAG_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
TAGS_SAVE_AS = ""

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_DATE_FORMAT = "%b %-d, %Y"
