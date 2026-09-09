import json
from datetime import datetime

JINJA_FILTERS = {"tojson": lambda value: json.dumps(value).replace("</", "<\\/")}

AUTHOR = "Thorin Tabor"
SITENAME = "Thorin Tabor"
SITESUBTITLE = (
    "Staff Software Engineer building agentic AI systems — RAG, MCP and "
    "multi-agent pipelines. Notes on making agents reliable."
)
SITEURL = ""

PATH = "content"
THEME = "theme"

TIMEZONE = "America/Los_Angeles"
DEFAULT_LANG = "en"

# Content locations
ARTICLE_PATHS = ["articles"]
PAGE_PATHS = ["pages"]

STATIC_PATHS = [
    "images",
    "extra/CNAME",
    "extra/robots.txt",
    "extra/favicon.ico",
    "extra/favicon-16x16.png",
    "extra/favicon-32x32.png",
    "extra/apple-touch-icon.png",
]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/favicon.ico": {"path": "favicon.ico"},
    "extra/favicon-16x16.png": {"path": "favicon-16x16.png"},
    "extra/favicon-32x32.png": {"path": "favicon-32x32.png"},
    "extra/apple-touch-icon.png": {"path": "apple-touch-icon.png"},
}

# Routing: /blog/<slug>/ for posts, /blog/ for the full index, hand-built
# templates for / and /bio/ via TEMPLATE_PAGES.
ARTICLE_URL = "blog/{slug}/"
ARTICLE_SAVE_AS = "blog/{slug}/index.html"

TAG_URL = "tags/{slug}/"
TAG_SAVE_AS = "tags/{slug}/index.html"
TAGS_URL = "tags/"
TAGS_SAVE_AS = "tags/index.html"

DIRECT_TEMPLATES = ["archives", "tags"]
ARCHIVES_URL = "blog/"
ARCHIVES_SAVE_AS = "blog/index.html"

TEMPLATE_PAGES = {
    "index.html": "index.html",
    "bio.html": "bio/index.html",
    "sitemap.xml": "sitemap.xml",
    "llms.txt": "llms.txt",
    "404.html": "404.html",
}

JINJA_GLOBALS = {
    "current_year": datetime.now().year,
}

DEFAULT_PAGINATION = False

# Single-author, single-category site — no per-author/category pages needed.
AUTHOR_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""

FEED_ALL_ATOM = "feeds/all.atom.xml"
FEED_ALL_RSS = "feeds/all.rss.xml"
FEED_DOMAIN = SITEURL
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_DATE_FORMAT = "%b %-d, %Y"

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.codehilite": {"css_class": "highlight"},
        "markdown.extensions.fenced_code": {},
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
    },
    "output_format": "html5",
}
