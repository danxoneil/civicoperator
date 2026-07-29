# Weekly RHT state re-authoring routine

> **⏸ PAUSED (2026-07-29).** The scheduled routine is disabled. Its grounding
> files — `dispatch_sources.json` (paywalled newsletter content) and
> `procurements.json` (RHTP Alerts feed) — were removed from this **public**
> repo to protect those products, so the inputs below are no longer present
> here. Before re-enabling, re-point grounding to a **private source** (the
> `danxoneil/RHT` repo produced by the RHT automation, or runtime regeneration
> via the routine's Monday/Drive MCP connectors), and update the input paths
> below. Tracked for the next working session.

**You are the Sunday re-author agent.** Keep the 50 state Q&A profiles current
with the week's newsletter reporting, and surface any changes as a **pull
request** for DXO to review before it reaches production. **Never push to
`main`.** Work only on a branch and open a PR — that PR *is* the reviewable diff.

## Inputs (all in `state-spending-monitor/state_pages/`)
- `content.json` — the authored Q&A per state (what you edit). `content.json.questions` holds the 8 canonical questions in order.
- `dispatch_sources.json` — per-state dispatch text (date, headline, body): your primary grounding.
- `states_data.json` — Monday facts (award, agency, hub, contact, links).
- `procurements.json` — per-state RFPs/RFAs/NOFOs/awards.
- `build.py` — regenerates the HTML from the above.

## Procedure
1. From the repo root: `git checkout main && git pull origin main`.
2. `cd state-spending-monitor/state_pages`.
3. **Pick states to re-author:** `python reauthor_diff.py fresh --days 8` prints
   states with dispatch coverage in the last 8 days. Re-author those (cap at 15;
   if more, take the most recent 15 and note the rest in the PR body).
4. **Re-author each picked state.** Read that state's `dispatch_sources.json`
   entry + its current `content.json → authored[State]` + `states_data.json` +
   `procurements.json`. Update the 8 answers, the `lede`, and `award_exact`
   **only where the newer reporting changes a fact** (a confirmed exact award, a
   new procurement or deadline, a named agency/official, a status change).
   Preserve accurate existing prose. Follow the authoring rules below exactly.
5. `python build.py` (regenerates all pages).
6. If `git status` shows changes:
   - `git checkout -b reauthor/$(date +%F)`
   - `git add content.json work/rht/states`
   - `git commit -m "RHT weekly re-author $(date +%F)"`
   - `git push -u origin HEAD`
   - `gh pr create --title "Weekly RHT re-author $(date +%F)" --body "$(python reauthor_diff.py summary)"`
   Report the PR URL. **Do not merge it.**
7. If there are no changes, do nothing further (no empty PR).

## Authoring rules (identical to the original build)
- **Ground every claim** in the four input files. Never invent awards, agencies,
  dates, or program names. If a fact isn't supported, keep the honest existing
  answer + hub link.
- **Neutral reference voice — no first person.** No "we/our/us." Third-person,
  factual. (The methodology page is the only place first person is allowed; you
  don't edit it.) Verbatim dispatch headlines are generated from
  `dispatch_index.json`, not here — don't touch them.
- **Exact awards:** if a dispatch states a precise CMS award figure, set
  `award_exact` (e.g. `"$200,105,604.17"`) and use it in Q1.
- **Q8 must keep the two-track eligibility framing**: direct-to-state contracts
  (firms bid as prime contractors) vs subgrants/subawards to rural providers
  (vendors/consultants as subcontractors/implementation partners), tailored with
  any state-specific eligibility, then engagement links.
- **Schema:** each answer is `{ "html": ..., "text": ... }`. `html` uses
  `<p>/<ul>/<strong>/<a href target=_blank rel=noopener>`; `text` is a faithful
  tag-free version for the JSON-LD. Keep answers concise (Arizona is the model).
- Use `&mdash;` for em dashes in `html`.

## The 8 questions (answer order)
1. Allocation & how the funding is structured.
2. Which agency administers it & who leads it.
3. What the state's plan is trying to accomplish.
4. Where the money is going — initiatives & shares.
5. What's been procured so far & what's open.
6. Key upcoming dates & deadlines.
7. What legislation/state action enables it (always: Section 71401 of the One Big Beautiful Bill Act (2025), administered by CMS; add state-specific action only if sourced).
8. How vendors/providers/consultants engage.

## Guardrails
- Never push to `main`; only branch + PR.
- If `git push` or `gh` auth fails, save `python reauthor_diff.py summary` output
  to `reauthor-summary.md` and stop with a clear message.
- `dispatch_sources.json`, `states_data.json`, `procurements.json` are refreshed
  upstream (Drive-side automation + the nightly Action). If they're stale, note
  it in the PR body but proceed with what's present.
