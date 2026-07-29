#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helpers for the weekly re-author routine (grounded on official .gov sources).

  python reauthor_diff.py rotate [--n 12]
      Print the states to re-check this week (one per line). Deterministic weekly
      rotation by ISO week number, so all states cycle over a few weeks and then
      repeat to catch updates. Only states with a hub or advisory URL in
      states_data.json are eligible (there must be a .gov page to fetch).

  python reauthor_diff.py summary
      Compare the working content.json against the committed (HEAD) version and
      print a Markdown per-state summary of what changed. Use as the PR body.
"""
import json, os, sys, subprocess, datetime, argparse, math

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "state-spending-monitor/state_pages/content.json"

def load(p): return json.load(open(p, encoding="utf-8"))

def eligible_states():
    d = load(os.path.join(HERE, "states_data.json"))
    out = []
    for name, v in d.items():
        if name == "CMS":
            continue
        if v.get("hub_url") or v.get("advisory"):
            out.append(name)
    return sorted(out)

def rotate(n):
    states = eligible_states()
    if not states:
        return
    slices = max(1, math.ceil(len(states) / n))
    wk = datetime.date.today().isocalendar()[1]      # 1..53
    idx = wk % slices
    chunk = states[idx * n:(idx + 1) * n]
    for s in chunk:
        print(s)

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
        qn = [f"Q{i}" for i, (ca, oa) in enumerate(zip(c.get("answers", []), o.get("answers", [])), 1)
              if ca.get("text") != oa.get("text") or ca.get("html") != oa.get("html")]
        if qn: deltas.append("answers: " + ", ".join(qn))
        if deltas:
            lines.append(f"- **{st}** — " + "; ".join(deltas)); changed += 1
    lines.insert(1, f"_{changed} state(s) changed._" if changed else "_No content changes this run._")
    print("\n".join(lines))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rotate"); r.add_argument("--n", type=int, default=12)
    sub.add_parser("summary")
    a = ap.parse_args()
    if a.cmd == "rotate": rotate(a.n)
    else: summary()
