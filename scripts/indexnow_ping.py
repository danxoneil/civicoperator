#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver...) which pages changed.

IndexNow is a push protocol: instead of waiting for a crawler to notice a
change, we POST the changed URLs once and every participating engine shares
the notification. Bing's index also feeds Copilot and DuckDuckGo answers.

The key below is PUBLIC BY DESIGN -- IndexNow verifies ownership by fetching
https://www.civicoperator.com/<KEY>.txt, which is committed at the repo root.
It is not a secret and needs no GitHub secret.

Which URLs are sent:
  --since <git rev>   pages whose .html changed between <rev> and HEAD
  --all               every URL in sitemap.xml (one-off backfill only)
Either way, only URLs listed in sitemap.xml are sent, so redirect stubs and
non-public files never go out.

--wait-for-pages polls the GitHub Pages build API until HEAD is deployed, so
engines that fetch immediately see the new page, not the old one. It needs
GITHUB_TOKEN and GITHUB_REPOSITORY (set automatically in Actions).

This script never exits non-zero: a failed ping must not fail a site build.

Run from the repo root:  python scripts/indexnow_ping.py --since HEAD~1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://www.civicoperator.com"
HOST = "www.civicoperator.com"
KEY = "721d1cfc2dd93d3a6f415cbc5028e9d4"
KEY_LOCATION = f"{BASE}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10000  # protocol limit per request


def log(msg: str) -> None:
    print(msg)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(msg + "\n")


def sitemap_urls() -> set[str]:
    text = Path("sitemap.xml").read_text(encoding="utf-8")
    return set(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text))


def url_for(rel: str) -> str:
    """Same mapping as scripts/generate_sitemap.py."""
    if rel == "index.html":
        return f"{BASE}/"
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-len('index.html')]}"
    return f"{BASE}/{rel}"


def changed_urls(since: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", since, "HEAD", "--", "*.html"],
        capture_output=True, text=True, check=True,
    ).stdout
    return sorted({url_for(p.strip()) for p in out.splitlines() if p.strip()})


def head_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()


def wait_for_pages(sha: str, timeout: int = 600) -> bool:
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not (token and repo):
        log("No GITHUB_TOKEN/GITHUB_REPOSITORY; not waiting for Pages.")
        return False
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pages/builds/latest",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"},
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                build = json.load(resp)
            if build.get("commit") == sha and build.get("status") == "built":
                return True
            if build.get("commit") == sha and build.get("status") == "errored":
                log("Pages build for HEAD errored; pinging anyway.")
                return False
        except (urllib.error.URLError, ValueError) as exc:
            log(f"Pages status check failed ({exc}); retrying.")
        time.sleep(20)
    log(f"Pages did not report {sha[:7]} built within {timeout}s; pinging anyway.")
    return False


def ping(urls: list[str]) -> None:
    payload = json.dumps({
        "host": HOST, "key": KEY, "keyLocation": KEY_LOCATION,
        "urlList": urls[:MAX_URLS],
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=payload, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            code = resp.status
    except urllib.error.HTTPError as exc:
        code = exc.code
    except urllib.error.URLError as exc:
        log(f"IndexNow request failed: {exc.reason}")
        return
    meaning = {
        200: "accepted", 202: "accepted (key validation pending)",
        400: "bad request", 403: "key not valid -- is the key file live?",
        422: "URLs do not match host/key", 429: "rate limited",
    }.get(code, "unexpected response")
    log(f"IndexNow: HTTP {code} {meaning} for {len(urls)} URL(s).")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--since", help="git rev; send pages changed since it")
    group.add_argument("--all", action="store_true", help="send every sitemap URL")
    ap.add_argument("--wait-for-pages", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print URLs, send nothing")
    args = ap.parse_args()

    try:
        allowed = sitemap_urls()
        urls = sorted(allowed) if args.all else [u for u in changed_urls(args.since) if u in allowed]
    except (OSError, subprocess.CalledProcessError) as exc:
        log(f"IndexNow skipped: could not work out changed pages ({exc}).")
        return 0

    if not urls:
        log("IndexNow: no changed public pages to send.")
        return 0
    if args.dry_run:
        print("\n".join(urls))
        log(f"IndexNow dry run: {len(urls)} URL(s) would be sent.")
        return 0
    if args.wait_for_pages:
        wait_for_pages(head_sha())
    ping(urls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
