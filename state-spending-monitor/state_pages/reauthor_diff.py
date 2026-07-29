#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helpers for the weekly re-author routine.

  python reauthor_diff.py fresh [--days 8]
      Print states (one per line) whose most-recent dispatch in
      dispatch_sources.json is within N days of today — i.e. states with fresh
      coverage worth re-authoring this week.

  python reauthor_diff.py summary
      Compare the working content.json against the committed (HEAD) version and
      print a Markdown per-state summary of which answers/ledes/awards changed.
      Use this as the PR body.
"""
import json, os, sys, subprocess, datetime, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "state-spending-monitor/state_pages/content.json"

def load(p): return json.load(open(p, encoding="utf-8"))

def fresh(days):
    src = load(os.path.join(HERE, "dispatch_sources.json"))
    today = datetime.date.today()
    out = []
    for st, rows in src.items():
        dates = [r["date"] for r in rows if r.get("date")]
        if not dates: continue
        newest = max(dates)
        try: d = datetime.date.fromisoformat(newest)
        except ValueError: continue
        if (today - d).days <= days:
            out.append((newest, st))
    for _, st in sorted(out, reverse=True):
        print(st)

def head_content():
    try:
        raw = subprocess.check_output(["git", "show", f"HEAD:{REL}"], cwd=HERE)  # bytes
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        print(f"(warning: could not read HEAD content.json: {e})", file=sys.stderr)
        return {"authored": {}}

def summary():
    cur = load(os.path.join(HERE, "content.json")).get("authored", {})
    old = head_content().get("authored", {})
    lines = ["## Weekly RHT re-author — proposed changes", ""]
    changed = 0
    for st in sorted(cur):
        c, o = cur[st], old.get(st)
        if not o:
            lines.append(f"- **{st}** — new profile"); changed += 1; continue
        deltas = []
        if c.get("award_exact") != o.get("award_exact"):
            deltas.append(f"award {o.get('award_exact')!r}→{c.get('award_exact')!r}")
        if c.get("lede") != o.get("lede"):
            deltas.append("lede")
        qn = []
        for i, (ca, oa) in enumerate(zip(c.get("answers", []), o.get("answers", [])), 1):
            if ca.get("text") != oa.get("text") or ca.get("html") != oa.get("html"):
                qn.append(f"Q{i}")
        if qn: deltas.append("answers: " + ", ".join(qn))
        if deltas:
            lines.append(f"- **{st}** — " + "; ".join(deltas)); changed += 1
    if not changed:
        lines.append("_No content changes this run._")
    else:
        lines.insert(1, f"_{changed} state(s) changed._")
    print("\n".join(lines))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fresh"); f.add_argument("--days", type=int, default=8)
    sub.add_parser("summary")
    a = ap.parse_args()
    if a.cmd == "fresh": fresh(a.days)
    else: summary()
