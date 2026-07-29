#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Substack export -> dispatch_sources.json : per-state grounding text for the
weekly re-authoring routine.

For each state, the most-recent dispatch sections (date, headline, body text)
that led with that state's name. This is the in-repo grounding the Sunday
re-author routine reads (the cloud runner can't reach the Google Drive export),
so it is committed and refreshed here wherever the Drive export is synced
(same place parse_dispatches.py runs).

    EXPORT_ROOT env  -> folder with dated export subfolders
    MAX_SECTIONS     -> per state (default 30)
    BODY_CHARS       -> per section (default 1600)
"""
import csv, html, json, os, re, sys

EXPORT_ROOT = os.environ.get("EXPORT_ROOT", r"G:/My Drive/RHT/Substack Exports")
MAX_SECTIONS = int(os.environ.get("MAX_SECTIONS", "30"))
BODY_CHARS = int(os.environ.get("BODY_CHARS", "1600"))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dispatch_sources.json")

STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
"Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas",
"Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota",
"Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
"New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas",
"Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
BYLEN = sorted(STATES, key=len, reverse=True)

def strip_tags(s): return re.sub(r"[ \t]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
def lead_state(h):
    for st in BYLEN:
        if re.match(rf"^{re.escape(st)}(?![a-zA-Z])", h): return st
    return None

def find_latest(root):
    best = None
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "files", "posts.csv")): best = p
    return best

def main():
    export = find_latest(EXPORT_ROOT)
    if not export:
        print(f"No export under {EXPORT_ROOT}", file=sys.stderr); sys.exit(1)
    meta = {}
    with open(os.path.join(export, "files", "posts.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f): meta[row["post_id"]] = row
    posts = os.path.join(export, "files", "posts")
    secs = {s: [] for s in STATES}
    for fn in os.listdir(posts):
        if not fn.endswith(".html"): continue
        m = meta.get(fn[:-5], {})
        if m.get("is_published") != "true": continue
        date = (m.get("post_date") or "")[:10]
        body = open(os.path.join(posts, fn), encoding="utf-8").read()
        for part in re.split(r"(?=<h1\b)", body):
            hm = re.match(r"<h1\b[^>]*>(.*?)</h1>(.*)", part, re.S)
            if not hm: continue
            headline = strip_tags(hm.group(1))
            st = lead_state(headline) if headline else None
            if not st: continue
            secs[st].append({"date": date, "headline": headline,
                             "body": strip_tags(hm.group(2))[:BODY_CHARS]})
    out = {}
    for s in STATES:
        rows = sorted(secs[s], key=lambda x: x["date"], reverse=True)[:MAX_SECTIONS]
        if rows: out[s] = rows
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kb = os.path.getsize(OUT) // 1024
    print(f"Wrote {OUT} ({kb} KB) — {len(out)} states, "
          f"{sum(len(v) for v in out.values())} sections")

if __name__ == "__main__":
    main()
