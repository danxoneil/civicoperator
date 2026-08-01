# -*- coding: utf-8 -*-
"""RHT State Pages generator.
Merges  states_data.json (Monday) + dispatch_index.json (Substack export parse)
+ content.json (authored Q&A)  ->  work/rht/states/<slug>/index.html  for all 50
states, plus a states index. Authored states render full prose; the rest render
honest structured-derived answers that upgrade automatically once authored."""
import json, os, re, html, urllib.parse, datetime

LAST_REVIEWED = datetime.date.today().isoformat()
SITE = "https://www.civicoperator.com"
TRACKER = "https://www.ruralhealthtransformation.life"

# Canonical Organization entity for Civic Operator LLC. Stable @id so any page
# (here, About, homepage) that references {SITE}/#organization consolidates to one entity.
ORG = {
    "@type": "Organization",
    "@id": f"{SITE}/#organization",
    "name": "Civic Operator LLC",
    "legalName": "Civic Operator LLC",
    "url": SITE,
    "logo": {"@type": "ImageObject", "url": f"{SITE}/img/Civic-Operator-Logo-Transparent.png"},
    "description": ("Civic Operator LLC is an independent research and consulting firm. It maintains a "
                    "neutral, structured reference to the CMS Rural Health Transformation Program and "
                    "publishes the Rural Health Transformation Grant Tracker newsletter."),
    "founder": {"@type": "Person", "name": "Daniel X. O’Neil"},
    "knowsAbout": ["Rural Health Transformation Program", "CMS rural health policy",
                   "State health procurement", "Rural health care"],
    "sameAs": [TRACKER],
}

# GA4 tag (public Measurement ID; ships in page HTML by design). Emitted into
# every page <head> when set; empty string = no tag.
GA_ID = "G-H2EB005NB5"
def ga_tag(page_type, state=None):
    """gtag.js snippet with GA4 custom-dimension params (event-scoped). Register
    'page_type' and 'state_name' as custom dimensions in the GA4 UI to segment."""
    if not GA_ID:
        return ""
    params = {"page_type": page_type}
    if state:
        params["state_name"] = state
    cfg = json.dumps(params)
    return (f'<!-- Google tag (gtag.js) -->\n'
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
            f'<script>\n'
            f'window.dataLayer = window.dataLayer || [];\n'
            f'function gtag(){{dataLayer.push(arguments);}}\n'
            f"gtag('js', new Date());\n"
            f"gtag('config', '{GA_ID}', {cfg});\n"
            f'</script>')

HERE = os.path.dirname(os.path.abspath(__file__))
# Default repo root = two levels up from state-spending-monitor/state_pages/.
# Override with env REPO_ROOT when running from elsewhere (e.g. scratchpad).
REPO_ROOT = os.environ.get("REPO_ROOT", os.path.abspath(os.path.join(HERE, "..", "..")))
OUT_ROOT = os.path.join(REPO_ROOT, "work", "rht", "states")
ACT = os.path.join(REPO_ROOT, "work", "rht", "activity", "index.html")

states_data = json.load(open(os.path.join(HERE, "states_data.json"), encoding="utf-8"))
dispatches  = json.load(open(os.path.join(HERE, "dispatch_index.json"), encoding="utf-8"))
content     = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
PROC_PATH   = os.path.join(HERE, "procurements.json")
procurements = json.load(open(PROC_PATH, encoding="utf-8")) if os.path.exists(PROC_PATH) else {}
SHOTS_PATH  = os.path.join(HERE, "screenshots_meta.json")
screenshots = json.load(open(SHOTS_PATH, encoding="utf-8")) if os.path.exists(SHOTS_PATH) else {}
KPI_PATH    = os.path.join(HERE, "kpis.json")
kpis_raw    = json.load(open(KPI_PATH, encoding="utf-8")) if os.path.exists(KPI_PATH) else {"states": []}
# self-declared metrics/objectives extracted from each state's CMS project narrative,
# keyed by state display name. Only `tracked` (the topic list) is surfaced publicly;
# the detailed baseline->target rows stay for the paywalled tracker.
KPIS        = {s["state"]: s for s in kpis_raw.get("states", []) if s.get("tracked")}
# per-state factual add-ons: rural-geography classification + exact CMS/USAspending
# obligated award. NB: the maturity "Stage" analysis is intentionally NOT here —
# it lives in the paid Field Guide, not this public repo.
FACTS_PATH  = os.path.join(HERE, "state_facts.json")
state_facts = json.load(open(FACTS_PATH, encoding="utf-8")) if os.path.exists(FACTS_PATH) else {}
QUESTIONS   = content["questions"]
AUTHORED    = content["authored"]

STYLE = re.search(r"<style>.*?</style>", open(ACT, encoding="utf-8").read(), re.S).group(0)
EXTRA_CSS = """
<style>
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:2px 22px;background:#fff;border:1px solid #eadbcd;border-radius:10px;padding:16px 20px;margin:16px 0 8px;}
.facts div{padding:7px 0;border-bottom:1px solid #f1e6d9;}
.facts .k{font-family:'Poppins',sans-serif;font-weight:600;font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;color:#8a7f72;}
.facts .v{font-size:.98rem;color:#333a40;word-break:break-word;}
.faq details{background:#fff;border:1px solid #eadbcd;border-radius:10px;margin:10px 0;padding:2px 18px;}
.faq summary{font-family:'Poppins',sans-serif;font-weight:600;font-size:1.06rem;color:#005f75;cursor:pointer;padding:14px 0;list-style:none;}
.faq summary::-webkit-details-marker{display:none;}
.faq summary::before{content:'+';float:right;color:#c9a37e;font-weight:700;}
.faq details[open] summary::before{content:'\u2013';}
.faq .a{padding:0 0 14px;color:#3d4348;font-size:1rem;}
.faq .a ul{margin:6px 0 0;padding-left:20px;} .faq .a li{margin:4px 0;} .faq .a p{margin:0 0 10px;}
.prov{color:#8a7f72;font-size:.8rem;margin:6px 0 0;}
.pending{display:inline-block;font-family:'Poppins',sans-serif;font-weight:600;font-size:.62rem;letter-spacing:.05em;text-transform:uppercase;color:#a06a2c;background:#f6e6d0;border-radius:5px;padding:2px 7px;margin-left:8px;vertical-align:middle;}
.btn{display:inline-block;margin:4px 18px 0 0;color:#005f75;font-weight:600;font-family:'Poppins',sans-serif;text-decoration:none;font-size:.92rem;}
.btn:hover{text-decoration:underline;}
/* index */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin-top:18px;}
.card{display:block;background:#fff;border:1px solid #eadbcd;border-radius:10px;padding:14px 16px;text-decoration:none;color:#333a40;}
.card:hover{border-color:#007a99;box-shadow:0 2px 10px rgba(0,122,153,.08);}
.card .nm{font-family:'Poppins',sans-serif;font-weight:700;font-size:1.12rem;color:#005f75;}
.card .meta{font-size:.85rem;color:#6c757d;margin-top:4px;}
.card .badge{font-family:'Poppins',sans-serif;font-size:.6rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:#0a7a3f;background:#e4f5ea;border-radius:5px;padding:2px 6px;}
/* wave 1: hub intro, stats, how-it-works, sources, governance, methodology */
.intro{color:#3d4348;font-size:1.02rem;max-width:70ch;}
.intro p{margin:0 0 12px;}
.stats{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0 6px;}
.stat{background:#fff;border:1px solid #eadbcd;border-radius:10px;padding:12px 18px;min-width:120px;}
.stat .num{font-family:'Poppins',sans-serif;font-weight:700;font-size:1.5rem;color:#005f75;line-height:1.1;}
.stat .lbl{font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;color:#8a7f72;margin-top:2px;}
.how{background:#fff;border:1px solid #eadbcd;border-radius:10px;padding:16px 20px;margin:16px 0;}
.how h2{border:0;font-size:1.15rem;margin:0 0 8px;padding:0;}
.how .layer{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #f1e6d9;}
.how .layer:last-child{border-bottom:0;}
.how .tag{font-family:'Poppins',sans-serif;font-weight:700;font-size:.66rem;letter-spacing:.05em;text-transform:uppercase;color:#005f75;flex:none;width:120px;}
.how .desc{font-size:.95rem;color:#3d4348;}
.st h3{font-family:'Poppins',sans-serif;font-weight:600;font-size:1rem;color:#333a40;margin:16px 0 4px;}
.srcs{list-style:none;padding:0;margin:6px 0;}
.srcs li{padding:6px 0;border-bottom:1px solid #eadbcd;font-size:.96rem;}
.srcs .lbl{font-family:'Poppins',sans-serif;font-weight:600;font-size:.68rem;letter-spacing:.05em;text-transform:uppercase;color:#8a7f72;display:block;}
.gov{margin-top:8px;color:#8a7f72;font-size:.82rem;line-height:1.5;}
.gov a{color:#007a99;text-decoration:none;} .gov a:hover{text-decoration:underline;}
.doc{color:#3d4348;font-size:1rem;} .doc h2{margin-top:28px;}
/* wave 2: procurement table */
.ptab-wrap{overflow-x:auto;border:1px solid #eadbcd;border-radius:10px;background:#fff;margin:12px 0;max-height:640px;overflow-y:auto;}
.ptab{width:100%;border-collapse:collapse;font-size:.88rem;}
.ptab th{position:sticky;top:0;background:#fff;text-align:left;font-family:'Poppins',sans-serif;font-weight:600;font-size:.64rem;letter-spacing:.05em;text-transform:uppercase;color:#8a7f72;padding:10px 12px;border-bottom:2px solid #eadbcd;white-space:nowrap;}
.ptab td{padding:9px 12px;border-bottom:1px solid #f1e6d9;vertical-align:top;color:#333a40;}
.ptab tr:last-child td{border-bottom:0;}
.ptab td a{color:#005f75;text-decoration:none;} .ptab td a:hover{text-decoration:underline;}
.ptab .dt{font-family:'Poppins',sans-serif;font-weight:600;font-size:.62rem;letter-spacing:.03em;text-transform:uppercase;color:#005f75;background:#eef4f6;border-radius:5px;padding:2px 7px;white-space:nowrap;}
.ptab td:nth-child(3),.ptab td:nth-child(4){font-family:ui-monospace,monospace;font-size:.78rem;color:#6c757d;white-space:nowrap;}
/* state page hero (official .gov page capture) */
.hero{margin:16px 0 4px;}
.hero img{display:block;width:100%;height:auto;border:1px solid #eadbcd;border-radius:10px;}
.hero figcaption{color:#8a7f72;font-size:.82rem;margin-top:6px;line-height:1.45;}
.hero figcaption a{color:#007a99;text-decoration:none;} .hero figcaption a:hover{text-decoration:underline;}
/* self-declared metrics: Topics-style chips from the state's project narrative */
.kpi{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px;}
.kpi .kchip{font-family:'Poppins',sans-serif;font-size:.82rem;color:#00596c;background:#eef4f6;border:1px solid #d5e5ea;border-radius:20px;padding:5px 13px;white-space:nowrap;}
/* breadcrumbs (visible, mirrors the BreadcrumbList JSON-LD) */
.crumbs{font-size:.78rem;color:#8a7f72;margin:0 0 10px;letter-spacing:.01em;}
.crumbs a{color:#007a99;text-decoration:none;} .crumbs a:hover{text-decoration:underline;}
.crumbs span{color:#8a7f72;}
.crumbs .sep{color:#c9a37e;margin:0 6px;}
/* related-links strip */
.related{margin:14px 0 0;font-size:.92rem;}
.related a{color:#005f75;font-weight:600;font-family:'Poppins',sans-serif;text-decoration:none;margin-right:18px;}
.related a:hover{text-decoration:underline;}
.rowlink{color:#005f75;text-decoration:none;} .rowlink:hover{text-decoration:underline;}
</style>"""

# Global header: identical link set to the hand-authored pages (Work / About / Book a call).
NAV = """<header class="sitebar">
  <a class="brand" href="/"><img src="/img/Civic-Operator-Logo-Transparent.png" alt="Civic Operator"></a>
  <nav>
    <a href="/work">Work</a>
    <a href="/about">About</a>
    <a class="book" href="https://calendar.app.google/XruT8HoUjnKLCkwD8">Book a call</a>
  </nav>
</header>"""

# RHT section sub-nav: one bar spanning both halves of RHT, shown on every generated
# reference page. These are all States-section pages, so "States" is the active item.
SUBNAV = """<div class="rht-subnav">
  <a href="/work/rht">Overview</a>
  <a class="active" href="/work/rht/states">States</a>
  <a href="https://www.ruralhealthtransformation.life/" target="_blank" rel="noopener">Newsletter</a>
  <a href="/work/rht/brief">State Fit Brief</a>
  <span class="arch-sep">&middot;</span>
  <a class="arch" href="/work/rht/activity">Activity Index</a>
  <a class="arch" href="/work/rht/dashboard">Quarterly Report</a>
</div>"""

def slug(name): return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
def strip_tags(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()

def award_str(m):
    if not m: return None
    try: v = float(m)
    except: return None
    return f"${v:,.2f}M".replace(".00M", "M")

def award_usd(auth, d):
    """Best whole-dollar award figure: exact authored value if present, else Monday millions."""
    if auth and auth.get("award_exact"):
        digits = re.sub(r"[^0-9]", "", auth["award_exact"].split(".")[0])
        if digits: return int(digits)
    try: return int(round(float(d.get("award_m")) * 1_000_000))
    except: return None

def linkline(url, label):
    if not url: return ""
    u = url.split(" - ")[-1].strip() if " - " in url else url
    u = u.strip()
    if not u.startswith("http"): u = "https://" + u
    return f'<a class="btn" href="{html.escape(u)}" target="_blank" rel="noopener">{label} &rarr;</a>'

def clean_url(url):
    if not url: return None
    u = url.split(" - ")[-1].strip() if " - " in url else url.strip()
    return ("https://" + u) if not u.startswith("http") else u

# ---------- firm award (exact CMS/USAspending obligation) ----------
def _obligated(name):
    return (state_facts.get(name) or {}).get("obligated")

def award_firm_full(name):
    ob = _obligated(name)
    return f"${ob:,.0f}" if ob else None      # e.g. $203,404,327 — no tilde

def award_firm_compact(name):
    ob = _obligated(name)
    return f"${ob/1e6:,.1f}M" if ob else None  # e.g. $203.4M — no tilde

# ---------- facts ----------
def build_facts(name, d):
    firm = award_firm_full(name)
    aw = award_str(d.get("award_m"))
    rows = []
    if firm:
        rows.append(("FY26 award (Year 1)",
                     f'{firm} <span style="color:#8a7f72;font-size:.82rem;">&middot; CMS obligated</span>'))
    elif aw:
        rows.append(("FY26 award (Year 1)", f"~{aw}"))
    if d.get("program"): rows.append(("Program name", html.escape(d["program"])))
    if d.get("hub_url"): rows.append(("Official RHTP hub", f'<a href="{html.escape(clean_url(d["hub_url"]))}">{html.escape(name)} program page</a>'))
    if d.get("email"): rows.append(("Program contact", f'<a href="mailto:{html.escape(d["email"])}">{html.escape(d["email"])}</a>'))
    if d.get("rfp_link"): rows.append(("Funding / RFP portal", f'<a href="{html.escape(clean_url(d["rfp_link"]))}">Funding opportunities</a>'))
    if d.get("advisory"): rows.append(("Advisory committee", f'<a href="{html.escape(clean_url(d["advisory"]))}" target="_blank" rel="noopener">Members &amp; meetings</a>'))
    if d.get("gov_news"): rows.append(("Governor's newsroom", f'<a href="{html.escape(clean_url(d["gov_news"]))}">Press releases</a>'))
    if d.get("key_projects"): rows.append(("Key project focus", html.escape(d["key_projects"])))
    return rows

# ---------- derived answers (non-authored states) ----------
def derived_answers(name, d):
    aw = award_str(d.get("award_m"))
    hub = clean_url(d.get("hub_url")); rfp = clean_url(d.get("rfp_link"))
    kp = d.get("key_projects"); email = d.get("email"); prog = d.get("program")
    A = []
    # Q1 allocation
    a1 = (f"<p>{name} received approximately <strong>{aw}</strong> in Year 1 Rural Health Transformation "
          f"Program funding from CMS &mdash; its share of the federal $50&nbsp;billion program. The exact award "
          f"and five-year structure are set out in the state's CMS-approved project and budget narratives.</p>"
          if aw else
          f"<p>{name}'s Year 1 Rural Health Transformation Program allocation from CMS is detailed in the "
          f"state's approved project and budget narratives.</p>")
    A.append((a1, None))
    # Q2 agency
    prog_bit = f" &mdash; <strong>{html.escape(prog)}</strong>" if prog else ""
    a2 = f"<p>{name}'s Rural Health Transformation Program is administered by the state's designated lead agency{prog_bit}."
    if email: a2 += f' Program contact: <a href="mailto:{html.escape(email)}">{html.escape(email)}</a>.'
    a2 += "</p>" + (linkline(hub, f"{name} RHTP hub") if hub else "")
    A.append((a2, None))
    # Q3 thesis (honest pending)
    a3 = (f'<p>We\u2019re finalizing {name}\u2019s plan summary from its CMS-approved project narrative '
          f'<span class="pending">narrative pending</span>. In the meantime, read the state\u2019s official '
          f'Rural Health Transformation plan and priorities on its program hub.</p>' + (linkline(hub, "Official plan & priorities") if hub else ""))
    A.append((a3, None))
    # Q4 money split
    a4 = (f"<p>{name}'s publicly flagged project focus areas include <strong>{html.escape(kp)}</strong>. "
          f'A full initiative-by-initiative budget breakdown is being summarized from the state\u2019s approved '
          f'budget narrative <span class="pending">breakdown pending</span>.</p>'
          if kp else
          f'<p>{name}\u2019s initiative and budget breakdown is being summarized from its approved budget narrative '
          f'<span class="pending">breakdown pending</span>.</p>')
    A.append((a4, None))
    # Q5 procured / open
    a5 = (f"<p>Live procurements and awards for {name} appear in the dispatch list below as we publish them. "
          f"The state's official funding-opportunities page is the authoritative source for open solicitations.</p>"
          + (linkline(rfp, "Open funding opportunities") if rfp else (linkline(hub, "Program hub") if hub else "")))
    A.append((a5, None))
    # Q6 dates
    a6 = (f"<p>Upcoming deadlines, technical-assistance calls and webinars surface first in the dated dispatches "
          f"below, and on the state's funding-opportunities page.</p>" + (linkline(rfp, "Deadlines & funding page") if rfp else ""))
    A.append((a6, None))
    # Q7 legislation
    a7 = (f"<p>The Rural Health Transformation Program was created by <strong>Section 71401 of the One Big "
          f"Beautiful Bill Act (2025)</strong> and is administered federally by CMS. {name} administers its award "
          f"through its state-designated agency under CMS-approved project and budget narratives.</p>")
    A.append((a7, None))
    # Q8 engage
    a8 = ("<p>Eligibility runs on two tracks. <strong>Direct-to-state contracts</strong> go out as competitive "
          "RFPs where firms bid as <strong>prime contractors</strong>; <strong>subgrants and subawards</strong> "
          "flow to rural providers &mdash; hospitals, Rural Health Clinics, FQHCs, Tribal health organizations, "
          "EMS agencies, counties and fire districts &mdash; where technology vendors and consultants most often "
          "engage as <strong>subcontractors or implementation partners</strong> rather than direct grantees.</p>")
    engage_links = "".join(x for x in [
        (linkline(hub, f"{name} RHTP hub") if hub else ""),
        (linkline(rfp, "Funding opportunities") if rfp else ""),
        (linkline(clean_url(d.get("advisory")), "Advisory council") if d.get("advisory") else ""),
        (linkline(clean_url(d.get("signup")), "Join the update list") if d.get("signup") else ""),
    ] if x)
    a8 += engage_links
    A.append((a8, None))
    return A

# ---------- dispatch list ----------
def dispatch_html(name):
    items = dispatches.get(name, [])
    out = ""
    for it in items:
        base, _, frag = it["url"].partition("#")
        url = base + "#" + urllib.parse.quote(frag) if frag else base
        out += (f'<div class="item"><span class="d">{it["date"]}</span>'
                f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(it["headline"])}</a></div>')
    return out, len(items)

# ---------- federal award link ----------
# Direct USAspending award pages for each state's RHTP cooperative agreement
# (CFDA 93.798, awarding agency HHS/CMS, sub-tier code _075). Keyed by state
# display name -> award FAIN. The prior free-text ?query= search matched nothing
# on USAspending's site; these land straight on the state's $-figure award page.
# Source: USAspending spending_by_award API, program_numbers=["93.798"].
RHTP_AWARD_FAIN = {
    "Alabama": "RHTCMS332060", "Alaska": "RHTCMS332062", "Arizona": "RHTCMS332059",
    "Arkansas": "RHTCMS332061", "California": "RHTCMS332078", "Colorado": "RHTCMS332081",
    "Connecticut": "RHTCMS332073", "Delaware": "RHTCMS332053", "Florida": "RHTCMS332067",
    "Georgia": "RHTCMS332046", "Hawaii": "RHTCMS332064", "Idaho": "RHTCMS332084",
    "Illinois": "RHTCMS332055", "Indiana": "RHTCMS332070", "Iowa": "RHTCMS332065",
    "Kansas": "RHTCMS332072", "Kentucky": "RHTCMS332079", "Louisiana": "RHTCMS332085",
    "Maine": "RHTCMS332075", "Maryland": "RHTCMS332066", "Massachusetts": "RHTCMS332069",
    "Michigan": "RHTCMS332041", "Minnesota": "RHTCMS332077", "Mississippi": "RHTCMS332063",
    "Missouri": "RHTCMS332090", "Montana": "RHTCMS332058", "Nebraska": "RHTCMS332086",
    "Nevada": "RHTCMS332074", "New Hampshire": "RHTCMS332050", "New Jersey": "RHTCMS332089",
    "New Mexico": "RHTCMS332083", "New York": "RHTCMS332049", "North Carolina": "RHTCMS332042",
    "North Dakota": "RHTCMS332043", "Ohio": "RHTCMS332087", "Oklahoma": "RHTCMS332048",
    "Oregon": "RHTCMS332071", "Pennsylvania": "RHTCMS332052", "Rhode Island": "RHTCMS332045",
    "South Carolina": "RHTCMS332056", "South Dakota": "RHTCMS332080", "Tennessee": "RHTCMS332057",
    "Texas": "RHTCMS332068", "Utah": "RHTCMS332051", "Vermont": "RHTCMS332047",
    "Virginia": "RHTCMS332088", "Washington": "RHTCMS332044", "West Virginia": "RHTCMS332054",
    "Wisconsin": "RHTCMS332076", "Wyoming": "RHTCMS332082",
}

def usaspending_url(name):
    """Direct award page when we have the state's RHTP FAIN; else fall back to
    a keyword search (broader match than the old full-phrase query)."""
    fain = RHTP_AWARD_FAIN.get(name)
    if fain:
        return f"https://www.usaspending.gov/award/ASST_NON_{fain}_075/"
    q = urllib.parse.quote("Rural Health Transformation")
    return f"https://www.usaspending.gov/search/?query={q}"

def procurement_block(name):
    items = procurements.get(name, [])
    if not items:
        return (f'<div class="st"><h2>Procurements &amp; official documents</h2>'
                f'<p class="note-q">No RFPs, RFAs, NOFOs or awards are on record for {name} yet. '
                f'Solicitations will appear here, each linked to its primary source, as the state publishes them.</p></div>')
    rows = ""
    for r in items:
        title = html.escape(r["title"])
        if r.get("source"):
            title = f'<a href="{html.escape(r["source"])}" target="_blank" rel="noopener">{title}</a>'
        dt = html.escape(r.get("doctype") or "&mdash;") if r.get("doctype") else "&mdash;"
        dt_cell = f'<span class="dt">{dt}</span>' if r.get("doctype") else "&mdash;"
        rows += (f'<tr><td>{title}</td><td>{dt_cell}</td>'
                 f'<td>{r.get("published") or "&mdash;"}</td><td>{r.get("deadline") or "&mdash;"}</td></tr>')
    return (f'<div class="st"><h2>Procurements &amp; official documents <span class="n">&middot; {len(items)}</span></h2>'
            f'<p class="note-q">RFPs, RFAs, NOFOs and awards on record for {name}, each row linked to its primary source '
            f'document. Compiled from state .gov portals and the program’s reporting; newest first.</p>'
            f'<div class="ptab-wrap"><table class="ptab"><thead><tr><th>Document</th><th>Type</th>'
            f'<th>Published</th><th>Deadline</th></tr></thead><tbody>{rows}</tbody></table></div></div>')

# ---------- self-declared metrics (Topics-style) ----------
def kpi_block(name):
    """Public 'what the state committed to measure' list, drawn from the state's
    CMS project narrative's metrics/evaluation section. Surfaces only the topic
    chips; detailed baselines/targets stay in the paywalled tracker."""
    k = KPIS.get(name)
    if not k or not k.get("tracked"):
        return ""
    chips = "".join(f'<span class="kchip">{html.escape(t)}</span>' for t in k["tracked"])
    url = (k.get("source") or {}).get("url")
    if url:
        srcline = (f'Source: <a href="{html.escape(clean_url(url))}" target="_blank" rel="noopener">'
                   f'{name}’s RHTP project narrative</a>.')
    else:
        srcline = f'Source: {name}’s CMS-approved RHTP project narrative.'
    return (f'<div class="st"><h2>What {name} committed to measure</h2>'
            f'<p class="note-q">The subjects {name}’s funded application pledges to track and report to CMS '
            f'— the yardsticks its progress will be measured against. Extracted from the state’s own '
            f'project narrative; the detailed baselines and targets behind each are tracked in the '
            f'<a href="{TRACKER}/" target="_blank" rel="noopener" style="color:#007a99;">newsletter</a>.</p>'
            f'<div class="kpi">{chips}</div>'
            f'<p class="prov">{srcline} These are the state’s self-declared objectives; '
            f'CMS weighs each state’s progress against its own commitments.</p></div>')

# ---------- render one state ----------
def hero_block(name):
    """Cropped top-of-page capture of the state's official RHTP .gov page."""
    meta = screenshots.get(name)
    if not meta:
        return ""
    sl = slug(name)
    hub = clean_url(states_data.get(name, {}).get("hub_url"))
    domain = urllib.parse.urlparse(hub).netloc.replace("www.", "") if hub else ""
    alt = (f"Screenshot of the top of {name}'s official Rural Health Transformation Program page"
           + (f" at {domain}" if domain else "") + ", the state's primary RHTP source.")
    o = f'<a href="{html.escape(hub)}" target="_blank" rel="noopener">' if hub else ""
    c = "</a>" if hub else ""
    cap_src = f'{o}{html.escape(domain)}{c}' if domain else "the official state page"
    return (f'<figure class="hero">{o}'
            f'<img src="/img/states/{sl}.webp" width="1000" height="519" loading="lazy" '
            f'alt="{html.escape(alt)}">{c}'
            f'<figcaption>{name}’s official Rural Health Transformation Program page &mdash; '
            f'{cap_src}, captured {meta.get("date","")}.</figcaption></figure>')

def render_state(name, d):
    sl = slug(name)
    auth = AUTHORED.get(name)
    # questions filled with state name
    qs = [q.replace("{STATE}", name) for q in QUESTIONS]
    if auth:
        answers = [(a["html"], a["text"]) for a in auth["answers"]]
        facts = auth.get("facts")
        if not facts:
            facts = build_facts(name, d)
            if auth.get("award_exact") and not award_firm_full(name):  # firm USAspending figure wins
                facts = [(("FY26 award (Year 1)", auth["award_exact"]) if k.startswith("FY26 award") else (k, v))
                         for k, v in facts]
        lede = auth["lede"].replace("{STATE}", name)
        status = "authored"
    else:
        answers = derived_answers(name, d)
        facts = build_facts(name, d)
        firm_c = award_firm_compact(name); aw = award_str(d.get("award_m"))
        award_bit = (f"<strong>{firm_c}</strong> " if firm_c else (f"<strong>~{aw}</strong> " if aw else ""))
        lede = (f"Everything we track on {name}'s "
                + award_bit
                + "Rural Health Transformation Program award &mdash; the plan, the administering agency, "
                  "live procurements, and every dispatch we've published, in a question-and-answer format.")
        status = "derived"

    disp, ndisp = dispatch_html(name)
    nproc = len(procurements.get(name, []))
    hub = clean_url(d.get("hub_url"))
    usa = usaspending_url(name)
    usa_label = "View federal award" if name in RHTP_AWARD_FAIN else "Search USAspending"
    # append procurement count, federal-data link, and dispatch count to the at-a-glance grid
    # Procurements list intentionally NOT surfaced here — the live procurement/RFP
    # feed is the paywalled newsletter's core product and the RHTP Alerts input;
    # this public reference layer links to sources but does not enumerate it.
    ag = (state_facts.get(name) or {}).get("agency_name")
    ag_val = f'<a class="rowlink" href="/work/rht/states/agencies/">{html.escape(ag)}</a>' if ag else None
    ag_rows = [("Administering agency", ag_val)] if ag and not any(k == "Administering agency" for k, _ in facts) else []
    rg = (state_facts.get(name) or {}).get("rural_geography")
    rg_val = f'<a class="rowlink" href="/work/rht/states/rural-definitions/">{html.escape(rg)}</a>' if rg else None
    rg_rows = [("Rural geography", rg_val)] if rg and not any(k == "Rural geography" for k, _ in facts) else []
    facts = list(facts) + ag_rows + rg_rows + [
        ("Federal award data", f'<a href="{usa}" target="_blank" rel="noopener">{usa_label}</a>'),
        ("Tracker dispatches", f'{ndisp} dated {"brief" if ndisp==1 else "briefs"}'),
    ]
    fact_rows = "".join(f'<div><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in facts)

    faq = ""
    ld_faq = []
    for (q, (ah, at)) in zip(qs, answers):
        faq += f'<details><summary>{html.escape(q)}</summary><div class="a">{ah}</div></details>'
        ld_faq.append({"@type": "Question", "name": q,
                       "acceptedAnswer": {"@type": "Answer", "text": at or strip_tags(ah)}})

    # ---- JSON-LD @graph: WebPage + GovernmentService + Dataset + FAQPage + BreadcrumbList ----
    page_url = f"{SITE}/work/rht/states/{sl}/"
    usd = award_usd(auth, d)
    admin_name = d.get("program") or f"{name} state administering agency"
    gov_service = {
        "@type": "GovernmentService",
        "@id": page_url + "#service",
        "name": f"{name} Rural Health Transformation Program",
        "serviceType": "Rural health transformation funding",
        "areaServed": {"@type": "State", "name": name},
        "provider": {"@type": "GovernmentOrganization", "name":
                     "Centers for Medicare & Medicaid Services", "url": "https://www.cms.gov/"},
        "administrator": {"@type": "GovernmentOrganization", "name": admin_name,
                          **({"url": hub} if hub else {})},
    }
    _ob = _obligated(name)
    _kpi = KPIS.get(name)
    _rg = (state_facts.get(name) or {}).get("rural_geography")
    dataset = {
        "@type": "Dataset", "@id": page_url + "#dataset",
        "name": f"{name} Rural Health Transformation Program \u2014 award, metrics & activity",
        "description": f"Structured profile of {name}'s CMS Rural Health Transformation Program: "
                       f"exact federal award, administering agency, how the state defines rural, "
                       f"the performance measures it committed to CMS, official sources and dated activity.",
        "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "Civic Operator LLC"},
        "dateModified": LAST_REVIEWED,
        "variableMeasured": [
            *([{"@type": "PropertyValue", "name": "CMS Year-1 federal award (obligated)",
                "unitText": "USD", "value": int(round(_ob)) if _ob else usd}] if (_ob or usd) else []),
            *([{"@type": "PropertyValue", "name": "Rural definition (RHTP)", "value": _rg}] if _rg else []),
            *([{"@type": "PropertyValue", "name": "Committed RHTP performance measure", "value": t}
               for t in _kpi["tracked"]] if _kpi else []),
            {"@type": "PropertyValue", "name": "Tracker dispatches", "value": ndisp},
        ],
    }
    webpage = {
        "@type": "WebPage", "@id": page_url, "url": page_url,
        "name": f"{name} Rural Health Transformation Program State Profile",
        "isPartOf": {"@type": "CollectionPage", "@id": f"{SITE}/work/rht/states/"},
        "about": {"@id": page_url + "#service"},
        "dateModified": LAST_REVIEWED,
        "publisher": {"@type": "Organization", "name": "Civic Operator LLC", "url": SITE},
        **({"primaryImageOfPage": {"@type": "ImageObject",
            "url": f"{SITE}/img/states/{sl}.webp",
            "caption": f"{name}'s official Rural Health Transformation Program page"}}
           if name in screenshots else {}),
    }
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
        for i, (n, u) in enumerate([("Home", "/"), ("Work", "/work"), ("RHT", "/work/rht"),
                                    ("States", "/work/rht/states/"), (name, f"/work/rht/states/{sl}/")])]}
    faqpage = {"@type": "FAQPage", "@id": page_url + "#faq", "mainEntity": ld_faq}
    ld = json.dumps({"@context": "https://schema.org",
                     "@graph": [webpage, gov_service, dataset, faqpage, breadcrumb]},
                    ensure_ascii=False, indent=1)

    hub_line = (f'<a class="hub" href="{html.escape(hub)}" target="_blank" rel="noopener">'
                f'{name}\u2019s official RHTP hub &rarr;</a>') if hub else ""
    disp_block = (f'<div class="st"><h2>Activity log <span class="n">&middot; {ndisp} dated '
                  f'{"brief" if ndisp==1 else "briefs"}</span></h2>'
                  f'<p class="note-q">Chronology of official activity compiled from automated monitoring '
                  f'of state sources, with personal review and verification. Links to primary documents and '
                  f'related <a href="{TRACKER}/" target="_blank" rel="noopener" style="color:#007a99;">Tracker '
                  f'analysis</a>.</p>{disp}</div>') if ndisp else ""

    analytics = ga_tag("state_profile", name)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} Rural Health Transformation Program &mdash; CMS award, lead agency, committed metrics &amp; activity &middot; Civic Operator</title>
<meta name="description" content="{name}'s CMS Rural Health Transformation Program at a glance: the exact Year-1 federal award, administering agency and contacts, how the state defines rural, the metrics it committed to CMS, official .gov sources, and a dated activity log. Independent reference by Civic Operator.">
<link rel="icon" href="/favicon.ico">
<meta property="og:title" content="{name} Rural Health Transformation Program State Profile">
<meta property="og:description" content="Exact CMS award, administering agency, committed metrics, rural definition, official sources and a dated activity log for {name}'s Rural Health Transformation Program.">
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<link rel="canonical" href="{page_url}">
{analytics}
{STYLE}
{EXTRA_CSS}
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{NAV}
{SUBNAV}
<div class="ai">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep">&rsaquo;</span><a href="/work/rht">RHT</a><span class="sep">&rsaquo;</span><a href="/work/rht/states/">States</a><span class="sep">&rsaquo;</span><span>{name}</span></nav>
<h1>{name} Rural Health Transformation Program State Profile</h1>
<p class="lede">{lede}</p>
{hub_line}
{hero_block(name)}
<div class="rule"></div>
<div class="st"><h2>At a glance</h2>
<div class="facts">{fact_rows}</div></div>
{kpi_block(name)}
<div class="st"><h2>Questions &amp; answers</h2><div class="faq">{faq}</div></div>
{disp_block}
<div class="st"><h2>Related</h2><p class="related">
<a href="/work/rht/states/">&larr; All 50 state profiles</a>
<a href="/work/rht/states/rural-definitions/">How states define &ldquo;rural&rdquo; &rarr;</a>
<a href="/work/rht/states/agencies/">Administering agencies by state &rarr;</a>
<a href="/work/rht/states/methodology">Methodology &amp; sources &rarr;</a>
<a href="{TRACKER}/" target="_blank" rel="noopener">Newsletter analysis &rarr;</a>
</p></div>
<p class="gov">Independent reference profile compiled and maintained by <strong>Civic Operator LLC</strong> from primary sources (CMS, {name} .gov program and procurement pages, the Governor's newsroom) and the Rural Health Transformation Grant Tracker. Official-source data and dispatch links refresh nightly; profiles are regenerated weekly from the latest reporting and changes reviewed before publication. Last reviewed {LAST_REVIEWED}. &middot; <a href="/work/rht/states/methodology">Methodology &amp; sources</a> &middot; <a href="/work/rht/states">All states</a></p>
<footer>Rural Health Transformation Grant Tracker &middot; {name} &middot; <a href="{TRACKER}/" style="color:#007a99;">ruralhealthtransformation.life</a></footer>
</div>
</body>
</html>"""
    d_out = os.path.join(OUT_ROOT, sl)
    os.makedirs(d_out, exist_ok=True)
    open(os.path.join(d_out, "index.html"), "w", encoding="utf-8").write(page)
    return {"name": name, "slug": sl, "award": award_str(d.get("award_m")),
            "award_firm": award_firm_compact(name),
            "rural_geography": (state_facts.get(name) or {}).get("rural_geography"),
            "usd": usd, "ndisp": ndisp, "status": status}

# ---------- index page (hub root) ----------
def render_index(cards):
    cards_sorted = sorted(cards, key=lambda c: c["name"])
    grid = ""
    for c in cards_sorted:
        aw = c.get("award_firm") or (f'~{c["award"]}' if c["award"] else "&mdash;")
        rg = c.get("rural_geography")
        rg_bit = f' &middot; {html.escape(rg)}' if rg else ""
        grid += (f'<a class="card" href="/work/rht/states/{c["slug"]}/">'
                 f'<div class="nm">{c["name"]}</div>'
                 f'<div class="meta">{aw} &middot; {c["ndisp"]} dispatch{"es" if c["ndisp"]!=1 else ""}{rg_bit}</div></a>')
    total_disp = sum(c["ndisp"] for c in cards)
    total_usd = sum(c.get("usd") or 0 for c in cards)
    total_b = f"${total_usd/1_000_000_000:.1f}B"
    total_proc = sum(len(procurements.get(c["name"], [])) for c in cards)
    stats = (f'<div class="stats">'
             f'<div class="stat"><div class="num">{len(cards)}</div><div class="lbl">States tracked</div></div>'
             f'<div class="stat"><div class="num">{total_b}</div><div class="lbl">Year-1 CMS awards</div></div>'
             f'<div class="stat"><div class="num">{total_disp}</div><div class="lbl">Dated dispatches</div></div>'
             f'</div>')
    how = ('<div class="how"><h2>How this works</h2>'
           '<div class="layer"><div class="tag">Primary source</div><div class="desc">Federal and state government pages &mdash; CMS, each state’s .gov RHTP program and procurement portals, and Governor newsrooms. Every profile links out to these. Also relies on <a href="https://kffhealthnews.org/rural-health/tracking-state-rural-health-transformation-plans/" target="_blank" rel="noopener">KFF Health News</a> for many approved plans.</div></div>'
           '<div class="layer"><div class="tag">Reference layer</div><div class="desc">This site. A neutral, structured, independently maintained profile of each state’s program &mdash; award, administering agency, official sources, and a dated activity log.</div></div>'
           '<div class="layer"><div class="tag">Analysis layer</div><div class="desc">The <a href="' + TRACKER + '/" target="_blank" rel="noopener">Rural Health Transformation Grant Tracker</a> newsletter &mdash; commentary, interpretation and reporting. Profiles link into its dated briefs; the analysis lives there, not here.</div></div>'
           '</div>')
    coll = json.dumps({"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "CollectionPage", "@id": f"{SITE}/work/rht/states/",
         "url": f"{SITE}/work/rht/states/", "name": "Rural Health Transformation Program — State Profiles",
         "description": "Independent, state-by-state reference profiles of the CMS Rural Health Transformation Program.",
         "dateModified": LAST_REVIEWED,
         "isPartOf": {"@type": "WebSite", "name": "Civic Operator", "url": SITE},
         "publisher": {"@id": f"{SITE}/#organization"},
         "hasPart": [{"@type": "WebPage", "name": c["name"],
                      "url": f'{SITE}/work/rht/states/{c["slug"]}/'} for c in cards_sorted]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": n, "item": SITE+u} for i, (n, u) in
            enumerate([("Home", "/"), ("Work", "/work"), ("RHT", "/work/rht"), ("States", "/work/rht/states/")])]}
    ]}, ensure_ascii=False, indent=1)
    analytics = ga_tag("reference_hub")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rural Health Transformation Program &mdash; State-by-State Reference &middot; Civic Operator</title>
<meta name="description" content="An independent, state-by-state reference for the $50B CMS Rural Health Transformation Program: exact Year-1 federal awards, administering agencies, how each state defines rural, the metrics states committed to CMS, official .gov sources, and a dated activity log for all 50 states.">
<meta property="og:title" content="Rural Health Transformation Program — State-by-State Reference Guide">
<meta property="og:description" content="Exact CMS awards, administering agencies, rural definitions, committed metrics and official sources for all 50 states' Rural Health Transformation Programs.">
<link rel="icon" href="/favicon.ico">
<link rel="canonical" href="{SITE}/work/rht/states/">
{analytics}
{STYLE}
{EXTRA_CSS}
<script type="application/ld+json">
{coll}
</script>
</head>
<body>
{NAV}
{SUBNAV}
<div class="ai">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep">&rsaquo;</span><a href="/work/rht">RHT</a><span class="sep">&rsaquo;</span><span>States</span></nav>
<h1>Rural Health Transformation Program State-by-State Reference Guide</h1>
<div class="intro">
<p>The <strong>Rural Health Transformation Program (RHTP)</strong> is a $50 billion, five-year CMS program &mdash; created by Section 71401 of the One Big Beautiful Bill Act (2025) &mdash; that awarded every U.S. state a share to transform rural health care. Each state administers its own award through a designated agency, on its own timeline, with its own procurements.</p>
<p>This is an <strong>independent reference</strong> to that program, state by state. Each profile collects the facts that are otherwise scattered across dozens of web sites: the state’s CMS award, its administering agency and contacts, its official program and procurement pages, and a dated log of activity &mdash; each entry deep-linked to the source. It is maintained by Civic Operator LLC as a neutral archive; commentary and analysis live separately on the newsletter.</p>
</div>
{how}
<div class="st"><h2>Compare across states</h2>
<p class="note-q">Single-dimension reference tables that cut across all 50 states, each linking back to the full profiles.</p>
<p class="related">
<a href="/work/rht/states/rural-definitions/">How states define &ldquo;rural&rdquo; &rarr;</a>
<a href="/work/rht/states/agencies/">Administering agencies by state &rarr;</a>
<a href="/work/rht/states/methodology">Methodology &amp; sources &rarr;</a>
</p></div>
<div class="st"><h2>Browse all {len(cards)} states</h2>
<p class="note-q">Each card: state &middot; exact CMS Year-1 award &middot; dated dispatches &middot; how it defines rural. Open a state for its full profile.</p>
<div class="grid">{grid}</div></div>
<p class="gov">Maintained by <strong>Civic Operator LLC</strong>. Official-source data and dispatch links refresh nightly; profiles are regenerated weekly and reviewed before publication. Last reviewed {LAST_REVIEWED}. &middot; <a href="/work/rht/states/methodology">Methodology &amp; sources</a> &middot; <a href="/work/rht/activity">Quarterly activity index</a></p>
<footer>Rural Health Transformation Program &middot; State-by-state reference &middot; Civic Operator LLC &middot; <a href="{TRACKER}/" style="color:#007a99;">Newsletter &amp; analysis</a></footer>
</div>
</body>
</html>"""
    open(os.path.join(OUT_ROOT, "index.html"), "w", encoding="utf-8").write(page)

# ---------- methodology / sources / about ----------
def render_methodology(cards):
    total_usd = sum(c.get("usd") or 0 for c in cards)
    total_b = f"${total_usd/1_000_000_000:.1f}B"
    body = f"""<div class="doc">
<p class="lede">How the Civic Operator Rural Health Transformation Program reference is compiled, sourced, and maintained.</p>

<h2>What this is (and isn’t)</h2>
<p>This is an independent, structured <strong>reference</strong> to the CMS Rural Health Transformation Program (RHTP) &mdash; a $50 billion, five-year program covering all 50 states ({total_b} in Year-1 awards tracked here). It exists to collect, in one predictable place per state, facts that are otherwise scattered across federal and state government sites. It is <strong>not</strong> a government site, and it is not the program’s commentary layer &mdash; interpretation, opinion and reporting live on the separate <a href="{TRACKER}/" target="_blank" rel="noopener">Rural Health Transformation Grant Tracker</a> newsletter.</p>

<h2>Sources we monitor</h2>
<ul>
<li><strong>CMS</strong> &mdash; the federal program, Notices of Award, and guidance (cms.gov/RHTProgram).</li>
<li><strong>USAspending.gov</strong> &mdash; the federal record of award obligations; each profile links to a state-scoped search.</li>
<li><strong>State .gov program pages</strong> &mdash; each state’s official RHTP hub.</li>
<li><strong>State procurement portals</strong> &mdash; RFPs, NOFOs, RFAs and award postings.</li>
<li><strong>Governor newsrooms</strong> &mdash; press releases, monitored for rural-health announcements.</li>
<li><strong>Primary documents</strong> &mdash; CMS-approved project and budget narratives.</li>
<li><strong>The Tracker’s dated dispatches</strong> &mdash; used as a chronological record of what happened and when, each deep-linked to its source brief.</li>
</ul>

<h2>How facts are derived</h2>
<p>Award amounts, administering agencies, procurement details and dates are drawn from the primary sources above and from the program’s own dated reporting. Where a precise figure appears in a primary source, we use it; otherwise we label a figure as approximate. We do not invent figures, agencies, or dates.</p>
<p>The <strong>Year-1 award</strong> shown on each profile is the state’s exact obligated amount from <a href="https://www.usaspending.gov/" target="_blank" rel="noopener">USAspending.gov</a> (CFDA 93.798), not a rounded estimate.</p>
<p>The <strong>“Rural geography”</strong> fact records how each state itself defines “rural” for its RHTP — a state-published rural definition or map, a fixed county list, or the default federal (HRSA/FORHP) designation. It is a factual classification of the state’s own methodology, drawn from its program materials; it is not a ranking, score, or judgment of the program.</p>

<h2>Update cadence</h2>
<ul>
<li><strong>Nightly</strong> &mdash; official-source links and the dated activity log refresh automatically.</li>
<li><strong>Weekly (Sundays)</strong> &mdash; state profiles are regenerated from the latest reporting; material changes are reviewed before publication.</li>
<li>Every page carries a <strong>&ldquo;last reviewed&rdquo;</strong> date.</li>
</ul>

<h2>Inclusion &amp; corrections</h2>
<p>A state is profiled once it has a CMS RHTP award. An activity-log entry is included when the program’s reporting covers that state by name. Spotted an error or omission? Corrections are welcome &mdash; the fastest path is the newsletter contact channel; verified corrections are applied at the next regeneration.</p>

<h2>Reference vs. analysis</h2>
<p>We keep a strict line between <strong>facts</strong> (award amounts, agencies, official documents, procurements, dates &mdash; here) and <strong>analysis</strong> (interpretation, trends, implications &mdash; on the newsletter). Profiles link into the newsletter’s dated briefs for context, but the reference layer stays neutral.</p>

<h2>Editorial ownership</h2>
<p>Compiled and maintained by <strong>Civic Operator LLC</strong>. Last reviewed {LAST_REVIEWED}.</p>
</div>"""
    coll = json.dumps({"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "WebPage", "@id": f"{SITE}/work/rht/states/methodology/",
         "url": f"{SITE}/work/rht/states/methodology/",
         "name": "Methodology & Sources — RHTP State Reference",
         "dateModified": LAST_REVIEWED,
         "publisher": {"@id": f"{SITE}/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": n, "item": SITE+u} for i, (n, u) in
            enumerate([("Home", "/"), ("Work", "/work"), ("RHT", "/work/rht"),
                       ("States", "/work/rht/states/"), ("Methodology", "/work/rht/states/methodology/")])]}
    ]}, ensure_ascii=False, indent=1)
    analytics = ga_tag("methodology")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Methodology &amp; Sources &mdash; RHTP State Reference &middot; Civic Operator</title>
<meta name="description" content="How the Civic Operator Rural Health Transformation Program state reference is sourced, derived, updated, and maintained &mdash; and how it separates neutral reference from newsletter analysis.">
<link rel="icon" href="/favicon.ico">
<link rel="canonical" href="{SITE}/work/rht/states/methodology/">
{analytics}
{STYLE}
{EXTRA_CSS}
<script type="application/ld+json">
{coll}
</script>
</head>
<body>
{NAV}
{SUBNAV}
<div class="ai">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep">&rsaquo;</span><a href="/work/rht">RHT</a><span class="sep">&rsaquo;</span><a href="/work/rht/states/">States</a><span class="sep">&rsaquo;</span><span>Methodology</span></nav>
<p class="eyebrow">Rural Health Transformation Program &middot; Reference</p>
<h1>Methodology &amp; Sources</h1>
{body}
<footer>Rural Health Transformation Program &middot; Methodology &middot; Civic Operator LLC &middot; <a href="/work/rht/states" style="color:#007a99;">All states</a></footer>
</div>
</body>
</html>"""
    d_out = os.path.join(OUT_ROOT, "methodology")
    os.makedirs(d_out, exist_ok=True)
    open(os.path.join(d_out, "index.html"), "w", encoding="utf-8").write(page)

# ---------- cross-state cluster pages ----------
def render_cluster(slug_, h1, title, description, intro, headers, rows, note=None):
    """Generic single-dimension reference table across all 50 states. Each row
    links back to a full profile — hub-and-spoke internal linking."""
    page_url = f"{SITE}/work/rht/states/{slug_}/"
    thead = "".join(f"<th>{h}</th>" for h in headers)
    tbody = ""
    for r in rows:
        tds = "".join(f"<td>{c}</td>" for c in r)
        tbody += f"<tr>{tds}</tr>"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": ["CollectionPage", "Dataset"], "@id": page_url, "url": page_url,
         "name": title, "description": strip_tags(intro), "isAccessibleForFree": True,
         "dateModified": LAST_REVIEWED,
         "isPartOf": {"@type": "CollectionPage", "@id": f"{SITE}/work/rht/states/"},
         "creator": {"@type": "Organization", "name": "Civic Operator LLC", "url": SITE},
         "publisher": {"@type": "Organization", "name": "Civic Operator LLC", "url": SITE}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": n, "item": SITE+u} for i, (n, u) in
            enumerate([("Home", "/"), ("Work", "/work"), ("RHT", "/work/rht"),
                       ("States", "/work/rht/states/"), (h1, f"/work/rht/states/{slug_}/")])]}
    ]}, ensure_ascii=False, indent=1)
    note_html = f'<p class="note-q">{note}</p>' if note else ""
    analytics = ga_tag("cluster")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} &middot; Civic Operator</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{h1} — RHTP">
<meta property="og:description" content="{description}">
<link rel="icon" href="/favicon.ico">
<link rel="canonical" href="{page_url}">
{analytics}
{STYLE}
{EXTRA_CSS}
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{NAV}
{SUBNAV}
<div class="ai">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep">&rsaquo;</span><a href="/work/rht">RHT</a><span class="sep">&rsaquo;</span><a href="/work/rht/states/">States</a><span class="sep">&rsaquo;</span><span>{h1}</span></nav>
<h1>{h1}</h1>
<div class="intro">{intro}</div>
<div class="st">{note_html}
<div class="ptab-wrap"><table class="ptab"><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div></div>
<div class="st"><h2>Related</h2><p class="related">
<a href="/work/rht/states/">&larr; All 50 state profiles</a>
<a href="/work/rht/states/rural-definitions/">How states define &ldquo;rural&rdquo; &rarr;</a>
<a href="/work/rht/states/agencies/">Administering agencies by state &rarr;</a>
<a href="/work/rht/states/methodology">Methodology &amp; sources &rarr;</a>
</p></div>
<p class="gov">Independent reference compiled and maintained by <strong>Civic Operator LLC</strong> from primary sources. Last reviewed {LAST_REVIEWED}. &middot; <a href="/work/rht/states/methodology">Methodology &amp; sources</a> &middot; <a href="/work/rht/states">All states</a></p>
<footer>Rural Health Transformation Program &middot; {h1} &middot; Civic Operator LLC &middot; <a href="{TRACKER}/" style="color:#007a99;">Newsletter &amp; analysis</a></footer>
</div>
</body>
</html>"""
    d_out = os.path.join(OUT_ROOT, slug_)
    os.makedirs(d_out, exist_ok=True)
    open(os.path.join(d_out, "index.html"), "w", encoding="utf-8").write(page)

def render_rural_definitions(names):
    rows = []
    for name in sorted(names):
        sl = slug(name)
        rg = (state_facts.get(name) or {}).get("rural_geography") or "&mdash;"
        prof = f'<a class="rowlink" href="/work/rht/states/{sl}/">{name}</a>'
        rows.append((prof, html.escape(rg) if rg != "&mdash;" else rg))
    render_cluster(
        "rural-definitions", "How states define &ldquo;rural&rdquo;",
        "How every state defines rural for its Rural Health Transformation Program",
        "How each U.S. state defines &ldquo;rural&rdquo; for its CMS Rural Health Transformation Program &mdash; its own published definition, a fixed county list, or the federal HRSA default. Factual classification for all 50 states, by Civic Operator.",
        "<p>Each state decides which communities count as &ldquo;rural&rdquo; for its Rural Health Transformation Program. Some publish their own rural definition or map; some adopt a fixed county list; others default to the federal (HRSA/FORHP) designation. This table records that choice for every state &mdash; a factual classification of the state&rsquo;s own methodology, not a ranking or judgment. See <a href=\"/work/rht/states/methodology\">Methodology</a> for how this is derived.</p>",
        ["State", "Rural definition (RHTP)"], rows,
        note="How each state defines rural for RHTP &mdash; own definition, county list, or federal HRSA default. Click a state for its full profile.")

def render_agencies(cards_by_name):
    rows = []
    for name in sorted(cards_by_name):
        d = cards_by_name[name]
        sl = slug(name)
        prof = f'<a class="rowlink" href="/work/rht/states/{sl}/">{name}</a>'
        ag = (state_facts.get(name) or {}).get("agency_name") or d.get("program")
        agency = html.escape(ag) if ag else "&mdash;"
        hub = clean_url(d.get("hub_url"))
        hub_cell = f'<a href="{html.escape(hub)}" target="_blank" rel="noopener">Official hub</a>' if hub else "&mdash;"
        rows.append((prof, agency, hub_cell))
    render_cluster(
        "agencies", "Administering agencies by state",
        "RHTP administering agency for every state",
        "The state agency administering each state's CMS Rural Health Transformation Program, with a link to its official .gov hub. All 50 states, by Civic Operator.",
        "<p>Every state runs its Rural Health Transformation Program through a designated lead agency. This table lists that administering body for all 50 states &mdash; the federal award recipient of record &mdash; each linked to the state&rsquo;s official program hub and full profile. See <a href=\"/work/rht/states/methodology\">Methodology</a> for sourcing.</p>",
        ["State", "Administering agency", "Official hub"], rows,
        note="The designated lead agency running RHTP in each state (federal award recipient of record). Click a state for its full profile.")

# ---------- run ----------
os.makedirs(OUT_ROOT, exist_ok=True)
cards = []
for name, d in states_data.items():
    if name == "CMS":
        continue
    cards.append(render_state(name, d))
render_index(cards)
render_methodology(cards)
_state_names = [n for n in states_data if n != "CMS"]
render_rural_definitions(_state_names)
render_agencies({n: states_data[n] for n in _state_names})
auth = sum(1 for c in cards if c["status"] == "authored")
print(f"Generated {len(cards)} state pages + index + methodology + 2 cluster pages  |  authored: {auth}  |  derived: {len(cards)-auth}")
print(f"Total dispatches linked: {sum(c['ndisp'] for c in cards)}  |  Year-1 awards: ${sum(c.get('usd') or 0 for c in cards)/1e9:.1f}B")
print("Output:", OUT_ROOT)
