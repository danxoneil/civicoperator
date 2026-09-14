#!/usr/bin/env python3
"""Generate /llms.txt and /llms-full.txt from the committed HTML tree.

`llms.txt` is the emerging convention for handing an AI agent a clean, curated
map of a site instead of making it crawl and guess. Cloudflare's AI-crawler log
showed agents probing /llms.txt and /llms-full.txt and getting 404s, alongside
the rest of the discovery surface.

Two files are produced:

  llms.txt       an index: one line per page with its title and description,
                 grouped into sections. Small enough to drop into a prompt.
  llms-full.txt  the whole reference layer inlined, built from the Markdown
                 companions that scripts/generate_markdown.py already writes.

URL rules match scripts/generate_sitemap.py exactly (trailing-slash directory
forms, redirect stubs skipped), so the three files never disagree.

Run from the repo root:  python scripts/generate_llms_txt.py
Re-run whenever pages are added or removed (the nightly state build does).
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

BASE = "https://www.civicoperator.com"

EXCLUDE_DIRS = {
    ".git", ".github", "old-site", "state-spending-monitor",
    "pdf-find-parse", "scripts", "worker", "css", "img",
}

# Slugs under work/rht/states/ that are cross-state reference tables, not a
# single state's profile.
CLUSTER_SLUGS = {"agencies", "rural-definitions", "outlays", "methodology", "test-run-pilot"}

REFRESH_RE = re.compile(r'http-equiv=["\']?refresh', re.IGNORECASE)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
# The backreference matters: the attribute delimiter must close the match, or an
# apostrophe inside a double-quoted description truncates it ("Arizona's" -> "Arizona").
DESC_RE = re.compile(
    r"""<meta[^>]+name=([\"'])description\1[^>]+content=([\"'])(.*?)\2""",
    re.IGNORECASE | re.DOTALL,
)
# Every page title ends with the site name; it's noise repeated 70+ times.
SUFFIX_RE = re.compile(r"\s*(?:&middot;|·|\||—|–|-)\s*Civic Operator\s*$", re.IGNORECASE)

SUMMARY = (
    "Civic Operator publishes an independent reference layer for the CMS Rural "
    "Health Transformation Program (RHTP) — the $50B state-awarded program "
    "created by Section 71401 of the One Big Beautiful Bill Act. For all 50 "
    "states it records the exact Year-1 federal award, the administering "
    "agency, how each state defines \"rural\", the performance metrics each "
    "state committed to CMS, official .gov sources, and a dated activity log."
)

NOTES = [
    "Every page has a clean Markdown companion at the same URL with `index.md` "
    "appended, or via `Accept: text/markdown` content negotiation.",
    "Figures are transcribed from state project narratives and CMS award "
    "documents; each state page cites its official .gov sources.",
    "State award amounts are CMS Year-1 obligated figures unless stated otherwise.",
]


def is_redirect_stub(path: Path) -> bool:
    try:
        return bool(REFRESH_RE.search(path.read_text(encoding="utf-8", errors="ignore")[:2048]))
    except OSError:
        return False


def url_for(rel: Path) -> str:
    parts = rel.as_posix()
    if parts == "index.html":
        return f"{BASE}/"
    if parts.endswith("/index.html"):
        return f"{BASE}/{parts[:-len('index.html')]}"
    return f"{BASE}/{parts}"


def clean(raw: str) -> str:
    """Collapse whitespace and decode entities from a title/description."""
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def meta_for(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    tm, dm = TITLE_RE.search(text), DESC_RE.search(text)
    title = SUFFIX_RE.sub("", clean(tm.group(1))) if tm else path.parent.name
    return title, clean(dm.group(3)) if dm else ""


def section_for(rel: Path) -> str:
    parts = rel.as_posix()
    if parts == "index.html":
        return "Start here"
    if parts.startswith("work/rht/states/"):
        slug = parts.split("/")[3]
        if slug.endswith(".html"):
            return "Rural Health Transformation Program"
        return "RHTP cross-state reference" if slug in CLUSTER_SLUGS else "RHTP state profiles"
    if parts.startswith("work/rht"):
        return "Rural Health Transformation Program"
    return "Other pages"


# Sections render in this order; anything unlisted follows, sorted.
SECTION_ORDER = [
    "Start here",
    "Rural Health Transformation Program",
    "RHTP cross-state reference",
    "RHTP state profiles",
    "Other pages",
]


def collect(root: Path) -> list[tuple[str, str, str, str, Path]]:
    """Return (section, url, title, description, path), deduped and sorted."""
    rows = []
    seen = set()
    for path in sorted(root.rglob("*.html")):
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or is_redirect_stub(path):
            continue
        url = url_for(rel)
        if url in seen:
            continue
        seen.add(url)
        title, desc = meta_for(path)
        rows.append((section_for(rel), url, title, desc, path))
    return rows


def render_index(rows) -> str:
    out = ["# Civic Operator", "", f"> {SUMMARY}", ""]
    for note in NOTES:
        out.append(f"- {note}")
    out.append("")
    for section in SECTION_ORDER + sorted({r[0] for r in rows} - set(SECTION_ORDER)):
        entries = [r for r in rows if r[0] == section]
        if not entries:
            continue
        out.append(f"## {section}")
        out.append("")
        for _, url, title, desc, _p in sorted(entries, key=lambda r: r[2].lower()):
            out.append(f"- [{title}]({url})" + (f": {desc}" if desc else ""))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_full(rows, root: Path) -> str:
    out = [
        "# Civic Operator — full reference text",
        "",
        f"> {SUMMARY}",
        "",
        "Generated from the Markdown companions of every public page.",
        "",
    ]
    for _section, url, title, _desc, path in sorted(rows, key=lambda r: r[1]):
        companion = path.with_suffix(".md")
        if not companion.exists():
            continue
        body = companion.read_text(encoding="utf-8", errors="ignore").strip()
        if not body:
            continue
        out += ["---", "", f"# {title}", "", f"Source: {url}", "", body, ""]
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    rows = collect(root)
    if not rows:
        print("No pages found — refusing to write empty llms.txt", file=sys.stderr)
        return 1

    index = root / "llms.txt"
    index.write_text(render_index(rows), encoding="utf-8")
    print(f"Wrote llms.txt with {len(rows)} pages")

    full = root / "llms-full.txt"
    text = render_full(rows, root)
    full.write_text(text, encoding="utf-8")
    print(f"Wrote llms-full.txt ({len(text) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
