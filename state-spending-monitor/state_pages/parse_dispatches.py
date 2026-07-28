#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Substack export -> per-state dispatch index (dispatch_index.json).

Scans a Substack export folder, extracts every <h1> story headline, maps the
leading token(s) to a US state, and records a Substack heading deep-anchor
(the confirmed  §<slug>  format) + the live post URL.

Run wherever the export is reachable (the machine/CI that has the Google Drive
export synced). Writes dispatch_index.json next to this script.

    EXPORT_ROOT env  -> folder holding dated export subfolders
                        (default: the RHT "Substack Exports" Drive path below)
    Picks the newest dated subfolder that contains files/posts.csv.
"""
import csv, html, json, os, re, sys

EXPORT_ROOT = os.environ.get("EXPORT_ROOT", r"G:/My Drive/RHT/Substack Exports")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dispatch_index.json")

STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
"Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas",
"Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota",
"Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
"New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas",
"Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
STATES_BY_LEN = sorted(STATES, key=len, reverse=True)   # "West Virginia" before "Virginia"

def find_latest_export(root):
    best = None
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "files", "posts.csv")):
            best = p
    return best

def slugify(text):
    """Replica of Substack's heading anchor slug (caller prepends §)."""
    t = html.unescape(text).replace("&", " and ").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def leading_state(headline):
    for st in STATES_BY_LEN:
        if re.match(rf"^{re.escape(st)}(?![a-zA-Z])", headline):
            return st
    return None

def main():
    export = find_latest_export(EXPORT_ROOT)
    if not export:
        print(f"No export with files/posts.csv under {EXPORT_ROOT}", file=sys.stderr)
        sys.exit(1)
    base_url = "https://www.ruralhealthtransformation.life"
    man = os.path.join(export, "manifest.json")
    if os.path.isfile(man):
        base_url = json.load(open(man, encoding="utf-8")).get("base_url", base_url)

    meta = {}
    with open(os.path.join(export, "files", "posts.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            meta[row["post_id"]] = row

    posts_dir = os.path.join(export, "files", "posts")
    h1_re = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
    by_state = {}
    for fn in os.listdir(posts_dir):
        if not fn.endswith(".html"):
            continue
        post_id = fn[:-5]
        slug = post_id.split(".", 1)[1] if "." in post_id else post_id
        m = meta.get(post_id, {})
        if m.get("is_published") != "true":
            continue
        date = (m.get("post_date") or "")[:10]
        title = m.get("title") or ""
        body = open(os.path.join(posts_dir, fn), encoding="utf-8").read()
        for raw in h1_re.findall(body):
            headline = strip_tags(raw)
            st = leading_state(headline) if headline else None
            if not st:
                continue
            by_state.setdefault(st, []).append({
                "date": date, "post_title": title, "headline": headline[:180],
                "url": f"{base_url}/p/{slug}#\u00a7{slugify(headline)}",
                "audience": m.get("audience") or "",
            })
    for st in by_state:
        by_state[st].sort(key=lambda x: x["date"], reverse=True)

    json.dump(by_state, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Parsed {os.path.basename(export)}: {len(by_state)} states, "
          f"{sum(len(v) for v in by_state.values())} headlines -> {OUT}")

if __name__ == "__main__":
    main()
