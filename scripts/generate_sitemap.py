#!/usr/bin/env python3
"""Generate /sitemap.xml from the committed HTML tree.

The site is static GitHub Pages served at https://www.civicoperator.com.
This walks the repo, keeps only real public pages, and writes a canonical
sitemap per https://www.sitemaps.org/protocol.html.

URL rules (match what the live site actually serves without a redirect):
  - foo/index.html      -> https://www.civicoperator.com/foo/   (trailing slash)
  - index.html (root)   -> https://www.civicoperator.com/
  - foo.html            -> https://www.civicoperator.com/foo.html
  - redirect stubs (files with <meta http-equiv="refresh">) are skipped,
    because their URL 301/refreshes elsewhere and the target is listed instead.

Run from the repo root:  python scripts/generate_sitemap.py
Re-run whenever pages are added or removed (e.g. in the nightly state build).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = "https://www.civicoperator.com"

# Directories that are not part of the public site (tooling, data, archives).
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "old-site",
    "state-spending-monitor",
    "pdf-find-parse",
    "scripts",
    "css",
    "img",
}

REFRESH_RE = re.compile(r'http-equiv=["\']?refresh', re.IGNORECASE)


def is_redirect_stub(path: Path) -> bool:
    """True if the file is a client-side redirect (meta refresh) rather than a page."""
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:2048]
    except OSError:
        return False
    return bool(REFRESH_RE.search(head))


def url_for(rel: Path) -> str:
    """Map a repo-relative .html path to its canonical public URL."""
    parts = rel.as_posix()
    if parts == "index.html":
        return f"{BASE}/"
    if parts.endswith("/index.html"):
        return f"{BASE}/{parts[:-len('index.html')]}"  # keeps trailing slash
    return f"{BASE}/{parts}"


def collect(root: Path) -> list[str]:
    urls: set[str] = set()
    for path in root.rglob("*.html"):
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if is_redirect_stub(path):
            continue
        urls.add(url_for(rel))
    # Sort with the homepage first, then lexicographically.
    return sorted(urls, key=lambda u: (u != f"{BASE}/", u))


def render(urls: list[str]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{u}</loc></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    urls = collect(root)
    out = root / "sitemap.xml"
    out.write_text(render(urls), encoding="utf-8")
    print(f"Wrote {out.relative_to(root)} with {len(urls)} URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
