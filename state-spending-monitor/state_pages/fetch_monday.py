#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pull the States - RHT board (18398815878) from monday.com -> states_data.json.

Uses the monday.com GraphQL API. Requires env MONDAY_API_TOKEN (same secret the
existing fix-board-urls workflow uses). Writes states_data.json next to this
script, in the schema build.py expects.
"""
import json, os, sys, urllib.request

BOARD_ID = os.environ.get("STATES_BOARD_ID", "18398815878")
TOKEN = os.environ.get("MONDAY_API_TOKEN")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "states_data.json")

# Monday column id -> our key
COLS = {
    "text_mm0nyz7b": "program", "email_mm09kw4a": "email", "text_mm091x53": "hub_url",
    "link_mm2216hv": "signup", "link_mm275gys": "advisory", "numeric_mm09w234": "award_m",
    "dropdown_mm09e6p3": "key_projects", "file_mm0nrbq2": "narrative_pdf",
    "file_mm1jsg1b": "budget_pdf", "link_mm1fg5nj": "rfp_link", "text_mm3hxx8f": "gov_news",
}

QUERY = """
query ($board: [ID!], $cols: [String!]) {
  boards(ids: $board) {
    items_page(limit: 200) {
      items {
        name
        column_values(ids: $cols) {
          id
          ... on LinkValue { url text }
          text
        }
      }
    }
  }
}"""

def main():
    if not TOKEN:
        print("MONDAY_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    payload = json.dumps({"query": QUERY,
                          "variables": {"board": [BOARD_ID], "cols": list(COLS)}}).encode()
    req = urllib.request.Request(
        "https://api.monday.com/v2", data=payload,
        headers={"Authorization": TOKEN, "Content-Type": "application/json",
                 "API-Version": "2024-10"})
    resp = json.load(urllib.request.urlopen(req, timeout=60))
    if "errors" in resp:
        print("Monday API errors:", resp["errors"], file=sys.stderr)
        sys.exit(1)
    items = resp["data"]["boards"][0]["items_page"]["items"]
    out = {}
    for it in items:
        row = {"name": it["name"]}
        for cv in it["column_values"]:
            key = COLS.get(cv["id"])
            if not key:
                continue
            # LinkValue exposes url; everything else uses text
            row[key] = cv.get("url") or cv.get("text") or None
        for key in COLS.values():
            row.setdefault(key, None)
        out[it["name"]] = row
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Fetched {len(out)} items -> {OUT}")

if __name__ == "__main__":
    main()
