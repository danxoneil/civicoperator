# -*- coding: utf-8 -*-
"""RHT State Pages generator.
Merges  states_data.json (Monday) + dispatch_index.json (Substack export parse)
+ content.json (authored Q&A)  ->  work/rht/states/<slug>/index.html  for all 50
states, plus a states index. Authored states render full prose; the rest render
honest structured-derived answers that upgrade automatically once authored."""
import json, os, re, html, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
# Default repo root = two levels up from state-spending-monitor/state_pages/.
# Override with env REPO_ROOT when running from elsewhere (e.g. scratchpad).
REPO_ROOT = os.environ.get("REPO_ROOT", os.path.abspath(os.path.join(HERE, "..", "..")))
OUT_ROOT = os.path.join(REPO_ROOT, "work", "rht", "states")
ACT = os.path.join(REPO_ROOT, "work", "rht", "activity", "index.html")

states_data = json.load(open(os.path.join(HERE, "states_data.json"), encoding="utf-8"))
dispatches  = json.load(open(os.path.join(HERE, "dispatch_index.json"), encoding="utf-8"))
content     = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
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
</style>"""

NAV = """<header class="sitebar">
  <a class="brand" href="/"><img src="/img/Civic-Operator-Logo-Transparent.png" alt="Civic Operator"></a>
  <nav>
    <a href="/work">Work</a>
    <a href="/work/rht">RHT Consulting</a>
    <a href="/work/rht/states">States</a>
    <a href="/about">About</a>
    <a href="https://www.ruralhealthtransformation.life/" target="_blank" rel="noopener">The Tracker</a>
  </nav>
</header>"""

def slug(name): return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
def strip_tags(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()

def award_str(m):
    if not m: return None
    try: v = float(m)
    except: return None
    return f"${v:,.2f}M".replace(".00M", "M")

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

# ---------- facts ----------
def build_facts(name, d):
    aw = award_str(d.get("award_m"))
    rows = []
    if aw: rows.append(("FY26 award (Year 1)", f"~{aw}"))
    if d.get("program"): rows.append(("Program name", html.escape(d["program"])))
    if d.get("hub_url"): rows.append(("Official RHTP hub", f'<a href="{html.escape(clean_url(d["hub_url"]))}">{html.escape(name)} program page</a>'))
    if d.get("email"): rows.append(("Program contact", f'<a href="mailto:{html.escape(d["email"])}">{html.escape(d["email"])}</a>'))
    if d.get("rfp_link"): rows.append(("Funding / RFP portal", f'<a href="{html.escape(clean_url(d["rfp_link"]))}">Funding opportunities</a>'))
    if d.get("advisory"): rows.append(("Advisory council", f'<a href="{html.escape(clean_url(d["advisory"]))}">Advisory council</a>'))
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

# ---------- render one state ----------
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
            if auth.get("award_exact"):   # show precise award instead of ~rounded
                facts = [(("FY26 award (Year 1)", auth["award_exact"]) if k.startswith("FY26 award") else (k, v))
                         for k, v in facts]
        lede = auth["lede"].replace("{STATE}", name)
        status = "authored"
    else:
        answers = derived_answers(name, d)
        facts = build_facts(name, d)
        aw = award_str(d.get("award_m"))
        lede = (f"Everything we track on {name}'s "
                + (f"<strong>~{aw}</strong> " if aw else "")
                + "Rural Health Transformation Program award &mdash; the plan, the administering agency, "
                  "live procurements, and every dispatch we've published, in a question-and-answer format.")
        status = "derived"

    fact_rows = "".join(f'<div><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in facts)
    faq = ""
    ld_items = []
    for (q, (ah, at)) in zip(qs, answers):
        faq += f'<details><summary>{html.escape(q)}</summary><div class="a">{ah}</div></details>'
        ld_items.append({"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": at or strip_tags(ah)}})
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld_items},
                    ensure_ascii=False, indent=1)
    disp, ndisp = dispatch_html(name)
    hub = clean_url(d.get("hub_url"))
    hub_line = (f'<a class="hub" href="{html.escape(hub)}" target="_blank" rel="noopener">'
                f'{name}\u2019s official RHTP hub &rarr;</a>') if hub else ""
    disp_block = (f'<div class="st"><h2>{name} dispatches <span class="n">&middot; {ndisp} from the Tracker</span></h2>'
                  f'<p class="note-q">Auto-updated from newsletter exports &mdash; each headline deep-links to that '
                  f'story inside the dated brief (subscriber content).</p>{disp}</div>') if ndisp else ""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} Rural Health Transformation Program &mdash; Plan, Budget &amp; Procurements &middot; Civic Operator</title>
<meta name="description" content="{name}'s CMS Rural Health Transformation Program: who runs it, where the money goes, what's been procured, and every newsletter dispatch &mdash; in a Q&amp;A format.">
<link rel="icon" href="/favicon.ico">
<meta property="og:title" content="{name} Rural Health Transformation Program &mdash; Q&amp;A">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.civicoperator.com/work/rht/states/{sl}">
<link rel="canonical" href="https://www.civicoperator.com/work/rht/states/{sl}/">
{STYLE}
{EXTRA_CSS}
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{NAV}
<div class="ai">
<p class="eyebrow">Rural Health Transformation Program &middot; State Profile</p>
<h1>{name}</h1>
<p class="lede">{lede}</p>
{hub_line}
<div class="rule"></div>
<div class="facts">{fact_rows}</div>
<p class="prov">Quick facts sourced from the Civic Operator RHT tracker (Monday board: States &ndash; RHT). Last reviewed 2026-07-28.</p>
<div class="st"><h2>Questions &amp; answers</h2><div class="faq">{faq}</div></div>
{disp_block}
<footer>Rural Health Transformation Grant Tracker &middot; State profile: {name} &middot; <a href="https://www.ruralhealthtransformation.life/" style="color:#007a99;">ruralhealthtransformation.life</a> &middot; <a href="/work/rht/states" style="color:#007a99;">All states</a></footer>
</div>
</body>
</html>"""
    d_out = os.path.join(OUT_ROOT, sl)
    os.makedirs(d_out, exist_ok=True)
    open(os.path.join(d_out, "index.html"), "w", encoding="utf-8").write(page)
    return {"name": name, "slug": sl, "award": award_str(d.get("award_m")), "ndisp": ndisp, "status": status}

# ---------- index page ----------
def render_index(cards):
    cards_sorted = sorted(cards, key=lambda c: c["name"])
    grid = ""
    for c in cards_sorted:
        badge = '<span class="badge">Full profile</span>' if c["status"] == "authored" else ""
        aw = f'~{c["award"]}' if c["award"] else "&mdash;"
        grid += (f'<a class="card" href="/work/rht/states/{c["slug"]}/">'
                 f'<div class="nm">{c["name"]} {badge}</div>'
                 f'<div class="meta">{aw} &middot; {c["ndisp"]} dispatch{"es" if c["ndisp"]!=1 else ""}</div></a>')
    total_disp = sum(c["ndisp"] for c in cards)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rural Health Transformation Program &mdash; State Profiles &middot; Civic Operator</title>
<meta name="description" content="Q&amp;A profiles of all 50 states' CMS Rural Health Transformation Program plans, budgets, procurements and dispatches.">
<link rel="icon" href="/favicon.ico">
<link rel="canonical" href="https://www.civicoperator.com/work/rht/states/">
{STYLE}
{EXTRA_CSS}
</head>
<body>
{NAV}
<div class="ai">
<p class="eyebrow">Rural Health Transformation Program</p>
<h1>State Profiles</h1>
<p class="lede">A permanent, question-and-answer profile of every state's CMS Rural Health Transformation Program &mdash; the plan, the money, the agencies, live procurements, and every dispatch from the Tracker. {len(cards)} states &middot; {total_disp} dispatches.</p>
<a class="hub" href="/work/rht/activity">See the quarterly activity index &rarr;</a>
<div class="rule"></div>
<div class="grid">{grid}</div>
<footer>Rural Health Transformation Grant Tracker &middot; State profiles &middot; <a href="https://www.ruralhealthtransformation.life/" style="color:#007a99;">ruralhealthtransformation.life</a></footer>
</div>
</body>
</html>"""
    open(os.path.join(OUT_ROOT, "index.html"), "w", encoding="utf-8").write(page)

# ---------- run ----------
os.makedirs(OUT_ROOT, exist_ok=True)
cards = []
for name, d in states_data.items():
    if name == "CMS":
        continue
    cards.append(render_state(name, d))
render_index(cards)
auth = sum(1 for c in cards if c["status"] == "authored")
print(f"Generated {len(cards)} state pages + index  |  authored: {auth}  |  derived: {len(cards)-auth}")
print(f"Total dispatches linked: {sum(c['ndisp'] for c in cards)}")
print("Output:", OUT_ROOT)
