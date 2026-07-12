#!/usr/bin/env python3
"""
Petal SEO Engine — Automatic SEO for every page.

Generates meta tags, Open Graph, Twitter Cards, JSON-LD structured data,
sitemap.xml, and robots.txt — all automatically from your Petal config
and page frontmatter.
"""


class SEOConfig:
    """Global SEO configuration from petal.config."""

    def __init__(self, site_name="", site_url="", site_description="",
                 author="", language="en", twitter_handle=""):
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")
        self.site_description = site_description
        self.author = author
        self.language = language
        self.twitter_handle = twitter_handle


class PageSEO:
    """SEO data for a single page."""

    def __init__(self, title="", description="", keywords=None, image="",
                 page_type="website", canonical="", noindex=False,
                 structured_data=None):
        self.title = title
        self.description = description
        self.keywords = keywords or []
        self.image = image
        self.page_type = page_type  # website, article, blog, product
        self.canonical = canonical
        self.noindex = noindex
        self.structured_data = structured_data  # dict for JSON-LD


class SEOGenerator:
    """Generates HTML meta tags from SEO configuration."""

    def __init__(self, config):
        self.config = config

    def generate_meta_tags(self, page_seo, page_url=""):
        """Generate all meta tags for a page."""
        tags = []
        c = self.config
        p = page_seo

        # Build full title
        if p.title and c.site_name:
            full_title = f"{p.title} | {c.site_name}"
        elif p.title:
            full_title = p.title
        elif c.site_name:
            full_title = c.site_name
        else:
            full_title = "Untitled"

        description = p.description or c.site_description
        full_url = f"{c.site_url}{page_url}" if c.site_url else page_url
        image_url = p.image
        if image_url and not image_url.startswith("http"):
            image_url = f"{c.site_url}{image_url}" if c.site_url else image_url

        # Basic meta tags
        tags.append(f'<title>{_escape(full_title)}</title>')
        if description:
            tags.append(f'<meta name="description" content="{_escape(description)}">')
        if p.keywords:
            tags.append(f'<meta name="keywords" content="{_escape(", ".join(p.keywords))}">')
        if c.author or True:
            author = c.author or ""
            if author:
                tags.append(f'<meta name="author" content="{_escape(author)}">')

        # Canonical URL
        canonical = p.canonical or full_url
        if canonical:
            tags.append(f'<link rel="canonical" href="{_escape(canonical)}">')

        # Robots
        if p.noindex:
            tags.append('<meta name="robots" content="noindex, nofollow">')

        # Viewport (always)
        tags.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
        tags.append('<meta charset="utf-8">')

        # Open Graph tags
        tags.append(f'<meta property="og:title" content="{_escape(p.title or full_title)}">')
        if description:
            tags.append(f'<meta property="og:description" content="{_escape(description)}">')
        tags.append(f'<meta property="og:type" content="{_escape(p.page_type)}">')
        if full_url:
            tags.append(f'<meta property="og:url" content="{_escape(full_url)}">')
        if image_url:
            tags.append(f'<meta property="og:image" content="{_escape(image_url)}">')
        if c.site_name:
            tags.append(f'<meta property="og:site_name" content="{_escape(c.site_name)}">')
        tags.append(f'<meta property="og:locale" content="{_escape(c.language)}">')

        # Twitter Card tags
        tags.append(f'<meta name="twitter:card" content="{"summary_large_image" if image_url else "summary"}">')
        tags.append(f'<meta name="twitter:title" content="{_escape(p.title or full_title)}">')
        if description:
            tags.append(f'<meta name="twitter:description" content="{_escape(description)}">')
        if image_url:
            tags.append(f'<meta name="twitter:image" content="{_escape(image_url)}">')
        if c.twitter_handle:
            tags.append(f'<meta name="twitter:site" content="{_escape(c.twitter_handle)}">')

        return "\n    ".join(tags)

    def generate_jsonld(self, page_seo, page_url=""):
        """Generate JSON-LD structured data."""
        import json
        c = self.config
        p = page_seo
        full_url = f"{c.site_url}{page_url}" if c.site_url else page_url

        if p.structured_data:
            return f'<script type="application/ld+json">\n{json.dumps(p.structured_data, indent=2)}\n</script>'

        # Auto-generate based on page type
        data = {"@context": "https://schema.org"}

        if p.page_type == "article":
            data["@type"] = "Article"
            data["headline"] = p.title
            if p.description:
                data["description"] = p.description
            if c.author:
                data["author"] = {"@type": "Person", "name": c.author}
            if full_url:
                data["url"] = full_url
            if p.image:
                img = p.image if p.image.startswith("http") else f"{c.site_url}{p.image}"
                data["image"] = img
        else:
            data["@type"] = "WebPage"
            data["name"] = p.title or c.site_name
            if p.description:
                data["description"] = p.description
            if full_url:
                data["url"] = full_url

        return f'<script type="application/ld+json">\n{json.dumps(data, indent=2)}\n</script>'


class SitemapGenerator:
    """Generates sitemap.xml from all pages."""

    def __init__(self, config):
        self.config = config

    def generate(self, pages):
        """Generate sitemap.xml content.
        
        Args:
            pages: list of dicts with 'url', optional 'lastmod', 'priority', 'changefreq'
        """
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for page in pages:
            full_url = f"{self.config.site_url}{page['url']}" if self.config.site_url else page['url']
            lines.append("  <url>")
            lines.append(f"    <loc>{_escape(full_url)}</loc>")
            if "lastmod" in page:
                lines.append(f"    <lastmod>{page['lastmod']}</lastmod>")
            priority = page.get("priority", "0.5")
            lines.append(f"    <priority>{priority}</priority>")
            changefreq = page.get("changefreq", "weekly")
            lines.append(f"    <changefreq>{changefreq}</changefreq>")
            lines.append("  </url>")

        lines.append("</urlset>")
        return "\n".join(lines)


class RobotsGenerator:
    """Generates robots.txt."""

    def __init__(self, config):
        self.config = config

    def generate(self, disallow=None):
        """Generate robots.txt content."""
        lines = ["User-agent: *", "Allow: /"]
        if disallow:
            for path in disallow:
                lines.append(f"Disallow: {path}")
        if self.config.site_url:
            lines.append(f"Sitemap: {self.config.site_url}/sitemap.xml")
        return "\n".join(lines)


def _escape(text):
    """Escape HTML special characters."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))


def seo_builtin(title="", description="", keywords=None, image="",
                page_type="website", noindex=False):
    """Built-in seo() function available in Petal frontmatter.
    
    Returns a PageSEO object that the template engine picks up.
    """
    return PageSEO(
        title=title,
        description=description,
        keywords=keywords or [],
        image=image,
        page_type=page_type,
        noindex=noindex,
    )
