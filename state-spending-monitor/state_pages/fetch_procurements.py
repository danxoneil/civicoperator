#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pull the RFPs - RHT board (18406309904) -> procurements.json, keyed by state.

Every published RFP / RFA / NOFO / award, each with its primary-source link.
Requires env MONDAY_API_TOKEN. Writes procurements.json next to this script,
in the schema build.py expects: { "<State>": [ {title, doctype, deadline,
published, source}, ... ] }.
"""
import json, os, sys, urllib.request

BOARD_ID = os.environ.get("RFP_BOARD_ID", "18406309904")
TOKEN = os.environ.get("MONDAY_API_TOKEN")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "procurements.json")

COLS = ["color_mm1y9n4k", "color_mm1zbx2s", "date_mm20g17d", "date_mm3v4aes",
        "link_mm1y4rmy", "board_relation_mm1zxtt4"]
QUERY = """
query ($board: [ID!], $cols: [String!], $cursor: String) {
  boards(ids: $board) {
    items_page(limit: 250, cursor: $cursor) {
      cursor
      items {
        name
        column_values(ids: $cols) {
          id text
          ... on BoardRelationValue { display_value }
          ... on LinkValue { url }
        }
      }
    }
  }
}"""

def api(cursor):
    payload = json.dumps({"query": QUERY, "variables":
                          {"board": [BOARD_ID], "cols": COLS, "cursor": cursor}}).encode()
    req = urllib.request.Request("https://api.monday.com/v2", data=payload,
        headers={"Authorization": TOKEN, "Content-Type": "application/json", "API-Version": "2024-10"})
    r = json.load(urllib.request.urlopen(req, timeout=90))
    if "errors" in r:
        print("Monday API errors:", r["errors"], file=sys.stderr); sys.exit(1)
    return r["data"]["boards"][0]["items_page"]

def clean_url(u):
    if not u: return None
    u = u.split(" - ")[-1].strip() if " - " in u else u.strip()
    return u if u.startswith("http") else None

def main():
    if not TOKEN:
        print("MONDAY_API_TOKEN not set", file=sys.stderr); sys.exit(1)
    items, cursor = [], None
    while True:
        page = api(cursor)
        items += page["items"]
        cursor = page["cursor"]
        if not cursor: break
    by = {}
    for it in items:
        c = {cv["id"]: cv for cv in it["column_values"]}
        state = (c.get("board_relation_mm1zxtt4") or {}).get("display_value")
        if not state: continue
        by.setdefault(state, []).append({
            "title": it["name"],
            "doctype": (c.get("color_mm1y9n4k") or {}).get("text") or "",
            "deadline": (c.get("date_mm20g17d") or {}).get("text") or "",
            "published": (c.get("date_mm3v4aes") or {}).get("text") or "",
            "source": clean_url((c.get("link_mm1y4rmy") or {}).get("url")
                                or (c.get("link_mm1y4rmy") or {}).get("text")),
        })
    for s in by:
        by[s].sort(key=lambda r: (r["published"] or r["deadline"] or "", r["deadline"] or ""), reverse=True)
    json.dump(by, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Fetched {sum(len(v) for v in by.values())} procurements across {len(by)} states -> {OUT}")

if __name__ == "__main__":
    main()
