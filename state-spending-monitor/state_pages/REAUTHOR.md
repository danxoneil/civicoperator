# Weekly RHT state re-authoring routine

**You are the Sunday re-author agent.** Keep the 50 state Q&A profiles in sync
with each state's **official government sources**, and surface any improvements
as a **pull request** for DXO to review before they reach production.
**Never push to `main`.** Work only on a branch and open a PR — that PR *is* the
reviewable diff.

This routine grounds on **primary .gov sources**, not the newsletter. The
newsletter is the analysis layer and its content is deliberately kept out of
this public repo — do not reintroduce it.

## Inputs (in `state-spending-monitor/state_pages/`)
- `content.json` — the authored Q&A per state (what you edit). `content.json.questions` holds the 8 canonical questions in order.
- `states_data.json` — public Monday metadata per state: `hub_url` (official RHTP page), `advisory` (advisory-committee page), `email`, `rfp_link`, `gov_news`, `award_m`, `key_projects`. **This is your list of .gov URLs to fetch.**
- `build.py` — regenerates the HTML.

There is intentionally **no** `dispatch_sources.json` or `procurements.json`
here (product data). Do not look for them or recreate them.

## Procedure
1. From the repo root: `git checkout main && git pull origin main`.
2. `cd state-spending-monitor/state_pages`.
3. **Pick this week's states:** `python reauthor_diff.py rotate --n 12` prints a
   rotating slice (all states cycle over a few weeks, then repeat to catch
   updates).
4. **For each state:** read its `states_data.json` entry, then **WebFetch its
   `hub_url` and its `advisory` page** (skip a URL that won't load; note it).
   Compare the authoritative content on those pages against the state's current
   `content.json` answers. **Update an answer only where the .gov source gives a
   better, newer, or more accurate fact** than what's there — especially:
   - Q2 (administering agency / who leads it),
   - Q3 (what the plan is trying to accomplish),
   - Q6 (upcoming dates & deadlines shown on the hub),
   - Q7 (enabling legislation / state action),
   - Q8 (how to engage / advisory participation).
   Preserve accurate existing prose. Follow the authoring rules below.
5. `python build.py`.
6. If `git status` shows changes:
   - `git checkout -b reauthor/$(date +%F)`
   - `git add content.json work/rht/states`
   - `git commit -m "RHT weekly re-author $(date +%F)"`
   - `git push -u origin HEAD`
   - `gh pr create --title "Weekly RHT re-author $(date +%F)" --body "$(python reauthor_diff.py summary)"`
   Report the PR URL. **Do not merge it.**
7. If there are no changes, do nothing further (no empty PR).

## Authoring rules
- **Ground every claim in the fetched .gov page(s) or `states_data.json`.** Never
  invent awards, agencies, dates, or program names. If the .gov page doesn't
  support a change, leave the answer as-is.
- **Cite the source.** When a fact comes from a .gov page, link that page in the
  answer (`<a href=… target="_blank" rel="noopener">`).
- **Neutral reference voice — no first person** (no "we/our/us"). Third-person,
  factual. Do not edit the methodology page.
- **Q8 keeps the two-track eligibility framing**: direct-to-state contracts
  (firms bid as prime contractors) vs subgrants/subawards to rural providers
  (vendors/consultants as subcontractors/implementation partners).
- **Do not add a procurements table or enumerate RFPs/awards.** The public
  reference layer links to sources but never lists the procurement feed — that
  stays exclusive to the newsletter and RHTP Alerts.
- **Schema:** each answer is `{ "html": ..., "text": ... }`; `text` is a
  tag-free version for JSON-LD. Keep answers concise (Arizona is the model).
  Use `&mdash;` for em dashes in `html`.

## The 8 questions (answer order)
1. Allocation & how the funding is structured.
2. Which agency administers it & who leads it.
3. What the state's plan is trying to accomplish.
4. Where the money is going — initiatives & shares.
5. What's been procured so far & what's open (prose only — no table).
6. Key upcoming dates & deadlines.
7. What legislation/state action enables it (always: Section 71401 of the One Big Beautiful Bill Act (2025), administered by CMS; add state-specific action only if the .gov page names it).
8. How vendors/providers/consultants engage.

## Guardrails
- Never push to `main`; only branch + PR.
- If a .gov page won't fetch, skip that state's affected answers and note it in
  the PR body — don't guess.
- If `git push` or `gh` auth fails, save `python reauthor_diff.py summary` to
  `reauthor-summary.md` and stop with a clear message.
