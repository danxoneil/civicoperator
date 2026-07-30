#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build per-state hero thumbnails from the Drive screenshot archive.

For each state, find the most-recent full-page capture in
`STATES_ROOT/<State>-RHT/`, crop the top (header/hero band), downscale, and save
an optimized WebP to `<repo>/img/states/<slug>.webp`. Records capture dates in
screenshots_meta.json so build.py can caption them honestly.

Date is parsed from the FILENAME (mtimes are a bulk-sync date, unreliable).
Handles "State MM-DD-YYYY.png", "State-MM-DD-YYYY.png", "State-MM-DD-YYYY(1).png",
and "State Month DD YYYY.png".
"""
import os, re, json, datetime
from PIL import Image

STATES_ROOT = os.environ.get("STATES_ROOT", r"G:/My Drive/RHT/States")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get("REPO_ROOT", os.path.abspath(os.path.join(HERE, "..", "..")))
OUT_IMG = os.path.join(REPO_ROOT, "img", "states")
META = os.path.join(HERE, "screenshots_meta.json")

TARGET_W = 1000            # output width (px)
BAND_RATIO = 0.52          # crop top band = width * ratio (≈1.9:1 hero)
WEBP_QUALITY = 80

STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
"Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas",
"Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota",
"Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
"New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas",
"Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

MON = {m: i for i, m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], 1)}

def slug(n): return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")

def parse_date(fn):
    s = fn.lower()
    m = re.search(r"(\d{1,2})[-_ ](\d{1,2})[-_ ](20\d{2})", s)   # MM-DD-YYYY
    if m:
        mm, dd, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try: return datetime.date(yy, mm, dd)
        except ValueError: pass
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})[,\s]+(20\d{2})", s)
    if m:
        try: return datetime.date(int(m.group(3)), MON[m.group(1)], int(m.group(2)))
        except (ValueError, KeyError): pass
    return None

def most_recent(folder):
    best = None
    for fn in os.listdir(folder):
        if not fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue
        d = parse_date(fn)
        if d is None:
            try: d = datetime.date.fromtimestamp(os.path.getmtime(os.path.join(folder, fn)))
            except OSError: continue
        if best is None or d > best[0] or (d == best[0] and fn < best[1]):
            best = (d, fn)
    return best  # (date, filename) or None

def main():
    os.makedirs(OUT_IMG, exist_ok=True)
    meta, made, total = {}, 0, 0
    for st in STATES:
        folder = os.path.join(STATES_ROOT, f"{st}-RHT")
        if not os.path.isdir(folder):
            continue
        pick = most_recent(folder)
        if not pick:
            continue
        d, fn = pick
        try:
            im = Image.open(os.path.join(folder, fn)).convert("RGB")
        except Exception as e:
            print("skip", st, e); continue
        w, h = im.size
        band = min(h, int(w * BAND_RATIO))
        im = im.crop((0, 0, w, band))
        if w > TARGET_W:
            im = im.resize((TARGET_W, int(band * TARGET_W / w)), Image.LANCZOS)
        out = os.path.join(OUT_IMG, f"{slug(st)}.webp")
        im.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
        kb = os.path.getsize(out) // 1024
        total += kb; made += 1
        meta[st] = {"date": d.isoformat(), "src": fn}
    json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Built {made} hero thumbnails -> {OUT_IMG}  ({total} KB total, avg {total//max(made,1)} KB)")
    print(f"Meta -> {META}")
    oldest = min(meta.values(), key=lambda v: v["date"])["date"] if meta else "-"
    newest = max(meta.values(), key=lambda v: v["date"])["date"] if meta else "-"
    print(f"capture dates span {oldest} .. {newest}")

if __name__ == "__main__":
    main()
