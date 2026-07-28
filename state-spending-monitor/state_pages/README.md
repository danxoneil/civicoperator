# RHT State Pages generator

Generates the permanent, LLM-structured Q&A profile pages for all 50 states'
CMS Rural Health Transformation Program, published under
`work/rht/states/<slug>/` on civicoperator.com.

Each page has four layers:

1. **Header + facts block** — deterministic, from the Monday *States – RHT* board.
2. **8-question FAQ** — the canonical question set (`content.json → questions`),
   answered per state. Authored states render full prose; the rest render honest
   structured-derived answers that upgrade automatically once authored.
3. **`FAQPage` JSON-LD** — machine-readable schema.org markup for answer engines.
4. **Dispatch list** — every newsletter story that led with the state's name,
   deep-linked with the Substack `§`-anchor into the exact section of the
   (paywalled) brief. This is the auto-refreshing layer.

## Files

| file | what it is | refreshed by |
|------|-----------|--------------|
| `build.py` | the generator (merges the three inputs → HTML) | — |
| `content.json` | canonical questions + **authored** Q&A per state | edited by hand |
| `states_data.json` | Monday board snapshot | `fetch_monday.py` |
| `dispatch_index.json` | per-state Substack dispatch links | `parse_dispatches.py` |
| `fetch_monday.py` | pulls board 18398815878 via the Monday API | — |
| `parse_dispatches.py` | parses the latest Substack export | — |

## Run locally

```bash
cd state-spending-monitor/state_pages

# 1. refresh the Substack dispatch links (needs the Google Drive export)
EXPORT_ROOT="G:/My Drive/RHT/Substack Exports" python parse_dispatches.py

# 2. refresh Monday data (needs the API token)
MONDAY_API_TOKEN=xxxxx python fetch_monday.py

# 3. build all 50 pages + the index
python build.py
```

`build.py` writes to `<repo-root>/work/rht/states/`. Override the repo root with
`REPO_ROOT=/path/to/repo python build.py`.

## Authoring a state

Add an entry under `content.json → authored → "<State>"` with `lede`, optional
`award_exact`, optional `facts` (list of `[label, html]`), and `answers` (a list
of 8 `{ "html": ..., "text": ... }` objects, one per canonical question). Re-run
`build.py`. Arizona is the worked example.

## Automation & the Google Drive boundary

`build-state-pages.yml` runs nightly: it re-pulls Monday, rebuilds, and commits
any diff. The GitHub runner **cannot reach Google Drive**, so
`dispatch_index.json` is kept in the repo and refreshed by running
`parse_dispatches.py` wherever the Drive export is synced (e.g. the same machine
/ automation that produces the nightly Substack export). A push of an updated
`dispatch_index.json` re-triggers the build.
