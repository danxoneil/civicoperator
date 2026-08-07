#!/usr/bin/env python3
"""Generate clean Markdown companions for each public HTML page.

For every public page `foo/index.html` this writes `foo/index.md`, and for a
leaf page `bar.html` it writes `bar.md`. GitHub Pages serves those files
directly, and the Cloudflare Worker (see worker/markdown-negotiation.js) maps
`Accept: text/markdown` requests on the canonical URL to the companion .md.

Chrome (nav, breadcrumbs, footer, scripts, styles, SVG) is stripped so agents
get formatting-stripped content, not the full page scaffold.

Run from the repo root:  python scripts/generate_markdown.py
Requires: beautifulsoup4, markdownify  (pip install beautifulsoup4 markdownify)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = "https://www.civicoperator.com"

EXCLUDE_DIRS = {
    ".git", ".github", "old-site", "state-spending-monitor",
    "pdf-find-parse", "scripts", "worker", "css", "img",
}

# Elements that are page scaffold, not content.
STRIP_SELECTORS = [
    "script", "style", "noscript", "svg", "iframe", "canvas", "template",
    "nav", "footer", ".navbar", ".sitebar", ".site-footer", ".crumbs",
    "[class*=subnav]",
]

REFRESH_RE = re.compile(r'http-equiv=["\']?refresh', re.IGNORECASE)


def is_redirect_stub(path: Path) -> bool:
    try:
        return bool(REFRESH_RE.search(path.read_text(encoding="utf-8", errors="ignore")[:2048]))
    except OSError:
        return False


def canonical_url(rel: Path) -> str:
    parts = rel.as_posix()
    if parts == "index.html":
        return f"{BASE}/"
    if parts.endswith("/index.html"):
        return f"{BASE}/{parts[:-len('index.html')]}"
    return f"{BASE}/{parts}"


def html_to_markdown(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title and soup.title.string:
        # Drop the " · Civic Operator" / " — Civic Operator" site suffix.
        title = re.split(r"\s+[·—|]\s+Civic Operator", soup.title.string)[0].strip()

    body = soup.body or soup
    for sel in STRIP_SELECTORS:
        for el in body.select(sel):
            el.decompose()

    has_h1 = body.find("h1") is not None

    content = md(str(body), heading_style="ATX", bullets="-", strip=["img"]).strip()
    # Collapse 3+ blank lines that markdownify can leave behind.
    content = re.sub(r"\n{3,}", "\n\n", content)

    # Only synthesize a title heading when the page has no <h1> of its own,
    # so we don't emit a redundant second top-level heading.
    header = f"# {title}\n\n" if title and not has_h1 else ""
    return f"{header}{content}\n\n---\nSource: {url}\n"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    # Allow generating for a single file (used for quick review): pass a path arg.
    if len(sys.argv) > 1:
        targets = [root / sys.argv[1]]
    else:
        targets = [
            p for p in root.rglob("*.html")
            if not any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts)
            and not is_redirect_stub(p)
        ]

    written = 0
    for path in targets:
        rel = path.relative_to(root)
        url = canonical_url(rel)
        out = path.with_suffix(".md")
        out.write_text(html_to_markdown(path.read_text(encoding="utf-8"), url), encoding="utf-8")
        written += 1
    print(f"Wrote {written} Markdown companion file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
