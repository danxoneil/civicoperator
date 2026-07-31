# RHTP State Pages — SEO / structured-data implementation

Context brief for reviewers (human or LLM). **Everything here is invisible in
rendered page text or is withheld by design** — a critique based on a copy/paste
of a sample page will miss it or wrongly flag it. Read this alongside the pages.

**Site:** `civicoperator.com/work/rht/states/` — independent reference to the CMS
Rural Health Transformation Program (RHTP). Static, GitHub Pages, custom domain,
rebuilt nightly by `build.py`. ~54 generator-produced pages + 21 other tracked pages.

## 1. `<head>` metadata (per page, unique)
- **`<title>` is intentionally distinct from the `<h1>`.** Title is descriptive/
  longer for SERP scent (e.g. *"Florida Rural Health Transformation Program — CMS
  award, lead agency, committed metrics & activity · Civic Operator"*); the H1 is
  the clean human form (*"Florida Rural Health Transformation Program State Profile"*).
- Per-page **meta description**, **`og:title`**, **`og:description`**, **`og:type`**,
  **`og:url`**, and **`rel=canonical`**. Descriptions were rewritten to reflect
  current content (award, agency, rural definition, committed metrics, activity);
  they no longer foreground procurements.

## 2. JSON-LD structured data (`schema.org`, `@graph` per page type)
- **State profile** → `WebPage` + `GovernmentService` + `Dataset` + `FAQPage` +
  `BreadcrumbList`. `GovernmentService` models CMS as `provider` and the state
  agency as `administrator`; `WebPage` carries `primaryImageOfPage` when a
  screenshot hero exists.
- **Index (hub)** → `Organization` + `CollectionPage` (`hasPart` links all 50
  profiles) + `BreadcrumbList`.
- **Methodology** → `Organization` + `WebPage` + `BreadcrumbList`.
- **Cluster pages** → `CollectionPage`+`Dataset` (combined) + `BreadcrumbList`.
- Visible breadcrumbs are backed by matching `BreadcrumbList` on every page.

## 3. Canonical entity consolidation (knowledge graph)
- A single **`Organization`** node with a **stable `@id` (`…/#organization`)** —
  name, legalName, logo `ImageObject`, description, `founder` (Person),
  `knowsAbout[]`, `sameAs` (newsletter). Other pages reference it **by `@id`** as
  `publisher`, so search/AI systems consolidate one entity instead of 50 loose
  "Civic Operator LLC" strings.

## 4. Machine-readable data exposure — `Dataset.variableMeasured`
Each state's `Dataset` exposes structured `PropertyValue`s so a bot can read the
facts without parsing prose:
- **Exact CMS Year-1 federal award** (USD, obligated),
- **Rural definition** (own / county-list / HRSA default),
- **each committed RHTP performance measure** (states with an extracted narrative
  carry N of these — e.g. Indiana = 7; states without a published narrative carry
  the 3 base variables),
- **tracker dispatch count**.

So "what did Indiana commit to measure" is answerable from the structured data,
not just the visible chips.

## 5. Internal-link architecture (hub-and-spoke) + machine-scrapable cluster pages
- **Two cross-state cluster pages** a single leaf page doesn't reveal:
  `…/rural-definitions/` and `…/agencies/` — real HTML `<table>` markup, all 50
  states, each row linking back to a profile. Built so an LLM answering "which
  states use their own rural definition?" scrapes a clean table and cites the site.
- Dense internal mesh: per-page **Related** strip, index **Compare across states**
  strip, and the **rural-geography** and **administering-agency** facts on each
  profile **link to the cluster tables**. Visible breadcrumbs link up
  (Home › RHT › States › {State}).

## 6. Deliberate free/paid data boundary (do NOT mistake for "shallow")
The pages **withhold data on purpose**; a reviewer pasting one page can't tell
what's intentionally absent:
- The KPI section shows only **topic chips**; the underlying **baseline→target
  numbers exist but are held back** for a paid tracker — **not in the public HTML
  or repo at all.**
- A per-state **maturity "Stage" analysis exists** but is **deliberately excluded**
  from the public site/repo (paid Field Guide only). Only the *factual* Tier (rural
  geography) is public.
- Live procurement/RFP lists are **intentionally not enumerated** (paywalled
  product), though primary sources are linked.

## 7. Provenance (structured, not scraped)
- Awards: **exact obligated $ from the USAspending API** (CFDA 93.798), not
  rounded estimates.
- Agency names: **Monday.com "Agency Name" mirror** (federal recipient of record),
  title-cased.
- Committed metrics: extracted from each state's **CMS project narrative** (the
  federally-mandated metrics/evaluation section).
- Activity log: automated monitoring + human verification; each entry deep-linked
  to a primary source.

## 8. Analytics
- **GA4 `G-H2EB005NB5`** on the **entire domain** (all RHTP pages via the generator
  + 21 other tracked pages). Referrer / AI-source measurement starts now (GA4 is
  not retroactive).
