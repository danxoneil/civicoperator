"""Maintenance script: rebuild rural_maps.json (committed) from the Geographies
CSV + the curated source/provenance below, and convert the authentic state-
published rural-map PNGs to web-sized webp under img/states/rural-maps/.

Run locally where the Geographies folder is available (Google Drive). CI never
runs this; it only consumes the committed outputs (rural_maps.json + the webp).
To add a state: drop its authentic map PNG in the Geographies folder, add a row
to MAPS below with the source URL, and re-run. Self-generated FALLBACK maps are
deliberately excluded — only verifiable state-published maps belong here.

  GEO_DIR=/path/to/Geographies python gen_rural_maps.py   # override the default
"""
import csv, json, os, re, glob
from PIL import Image

# This file lives in state-spending-monitor/state_pages/; repo root is two up.
STATE_PAGES = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(STATE_PAGES, os.pardir, os.pardir))
GEO = os.environ.get("GEO_DIR", "G:/My Drive/RHT/Geographies")
IMG_OUT = os.path.join(REPO, "img", "states", "rural-maps")
MAX_W = 1000  # cap width; keep aspect ratio

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

# --- curated: authoritative definition-source URL per state (from RHTP-Rural-Definition-Maps-by-State.md)
SOURCE = {
 "Alabama":"https://adeca.alabama.gov/wp-content/uploads/ARHTP-Rural-Counties.pdf",
 "Arizona":"https://crh.arizona.edu/sites/default/files/2025-08/250819RHTP-Defining-Rural.pdf",
 "California":"https://hcai.ca.gov/wp-content/uploads/2020/10/MSSADefinitionMap.pdf",
 "Colorado":"https://hcpf.colorado.gov/sites/hcpf/files/52%20Rural%20%26%20Frontier%20Counties%20%28for%20publication%29.pdf",
 "Connecticut":"https://ruralhealthct.org/about-us/map",
 "Florida":"https://ahca.myflorida.com/content/download/28497/file/AHCA-Rural_Definition_March_2026_1.pdf",
 "Georgia":"https://greathealth.georgia.gov/about-program/eligible-counties-list",
 "Idaho":"https://healthandwelfare.idaho.gov/providers/rural-health-transformation-program-grant/funding-opportunities-rural-health",
 "Indiana":"https://www.in.gov/grow-rural-health/regional-grants",
 "Maryland":"https://health.maryland.gov/pophealth/Pages/Rural-health.aspx",
 "Massachusetts":"https://www.mass.gov/info-details/state-office-of-rural-health-rural-definition",
 "Missouri":"https://mydss.mo.gov/media/pdf/rural-health-transformation-program-rhtp-hub-county-groupings-map",
 "Nebraska":"https://dhhs.ne.gov/Pages/RHTP-Health-Care-Advisory-Regions.aspx",
 "New Hampshire":"https://www.dhhs.nh.gov/document/rural-status-map-new-hampshire",
 "New Mexico":"https://www.hca.nm.gov/wp-content/uploads/RHT-Program_Regional-Map.png",
 "Ohio":"https://odh.ohio.gov/know-our-programs/rural-health-transformation-program/solicitation-reference-documents/odh-rht-rural-health-transformation-counties-of-focus-map",
 "Oregon":"https://www.ohsu.edu/media/881",
 "Utah":"https://ruralhealth.health.utah.gov/utah-state-profile/county-classifications-map/",
 "Wisconsin":"https://worh.org/resources/data-maps/maps/",
 "Kentucky":"https://ruralhealthplan.ky.gov/Documents/KY%20RHTP%20Other%20Supporting%20Documentation_CMS-RHT-26-001.pdf",
 "Montana":"https://dphhs.mt.gov/RuralHealthTransformationProgram/",
 "New Jersey":"https://www.nj.gov/health/fhs/primarycare/rural-health/DesignatedRuralAreasinNewJersey.pdf",
 "New York":"https://health.ny.gov/facilities/transforming_rural_healthcare/docs/project_narrative.pdf",
 "North Carolina":"https://www.ncdhhs.gov/divisions/office-rural-health/rural-health-transformation-program/nc-rural-health-transformation-program-frequently-asked-questions",
 "Oklahoma":"https://oklahoma.gov/content/dam/ok/en/health/health2/aem-documents/health-promotion/rhtp/Project%20Narrative.pdf",
 "Pennsylvania":"https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/rural-health/2026-02-06-pennsylvania-rural-health-transformation-plan-february-2026.pdf",
 "Rhode Island":"https://health.ri.gov/sites/g/files/xkgbur1006/files/publications/definitions/2022Rural-definition.pdf",
 "Texas":"https://pfd.hhs.texas.gov/sites/default/files/documents/rural-hlth-prgm/bdgt-prd-1-rvsd-prjt-narr.pdf",
 "Virginia":"https://dmas.virginia.gov/media/visgijnd/rhc-transformation-project-narrative.pdf",
 "Illinois":"https://hfs.illinois.gov/content/dam/soi/en/web/hfs/info/fedresctr/rhtsprogramnarrative.pdf",
 "Maine":"https://www.maine.gov/dhhs/mecdc/healthy-living/rural-health/rural-health-systems",
}

# --- curated: the 15 authentic rendered maps. png filename in GEO + one-line provenance.
MAPS = {
 "California":("map-california.png","HCAI Medical Service Study Area (MSSA) Definition Map — frontier/rural/urban."),
 "Colorado":("map-colorado.png","HCPF Rural & Frontier Counties map — 52 of 64 counties."),
 "Florida":("map-florida.png","AHCA RHTP Regional Map — the program's rural regions."),
 "Idaho":("map-idaho.png","DHW RHTP eligibility map (replacement issued 8/27/2026, superseding the withdrawn Appendix A) — eligible rural tracts plus 225 named eligible cities, 29 of them under 25,000 residents inside urban areas."),
 "Indiana":("map-indiana.png","GROW Rural Health eight-region map."),
 "Maryland":("map-maryland.png","State-designated rural counties — 18 of 24 jurisdictions."),
 "Michigan":("map-michigan.png","MDHHS county map — Fully Rural, Partially Rural, Metropolitan (from the state narrative)."),
 "Mississippi":("map-mississippi.png","Mississippi RHT \u201cDefining Rural\u201d ArcGIS map."),
 "Missouri":("map-missouri.png","ToRCH Hub County Groupings map — ~104 counties in hubs."),
 "New Jersey":("map-new-jersey.png","Designated Rural Areas in New Jersey."),
 "Ohio":("map-ohio.png","ODH RHTP Counties of Focus map."),
 "Oklahoma":("map-oklahoma.png","Eligible-communities map (Project Narrative, Attachment A) — pop. <55,000, 75 counties."),
 "Pennsylvania":("map-pennsylvania.png","PREP Regions (Figure 2, p7) — regional collaboratives with HRSA rural tracts shaded."),
 "Virginia":("map-virginia-png.png","Map of Virginia's rural regions (Figure 2, p3) — the six-region rural horseshoe."),
 "Wisconsin":("map-wisconsin.png","WORH FORHP rural-areas map."),
}

def netloc(url):
    m = re.match(r"https?://([^/]+)", url or "")
    return m.group(1).replace("www.", "") if m else ""

# --- parse the CSV
rows = {}
with open(os.path.join(GEO, "RHTP-State-Map-Index.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows[r["State"].strip()] = r

TIER_LABEL = {"T1":"Publishes a rural map","T2":"Publishes a list/definition","T3":"Federal (HRSA) default"}

out = {}
for state, r in rows.items():
    tier = (r.get("SurveyTier") or "").strip()
    grain = (r.get("Grain") or "").strip()
    try:
        rural = int(r.get("FallbackRural") or 0); total = int(r.get("FallbackTotal") or 0)
    except ValueError:
        rural, total = 0, 0
    pct = round(rural / total * 100) if total else None
    src = SOURCE.get(state)
    entry = {
        "tier": tier,
        "tier_label": TIER_LABEL.get(tier, ""),
        "grain": grain,
        "forhp_rural": rural,
        "forhp_total": total,
        "forhp_pct": pct,
        "source_url": src,
        "source_label": netloc(src),
    }
    if state in MAPS:
        png, note = MAPS[state]
        entry["map"] = {"file": f"/img/states/rural-maps/{slug(state)}.webp",
                        "source_url": src, "source_label": netloc(src), "note": note}
    out[state] = entry

os.makedirs(STATE_PAGES, exist_ok=True)
with open(os.path.join(STATE_PAGES, "rural_maps.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
print("wrote rural_maps.json with", len(out), "states,", sum(1 for v in out.values() if "map" in v), "authentic maps")

# --- convert the 15 PNGs to webp
os.makedirs(IMG_OUT, exist_ok=True)
for state, (png, _note) in MAPS.items():
    src = os.path.join(GEO, png)
    im = Image.open(src).convert("RGB")
    if im.width > MAX_W:
        h = round(im.height * MAX_W / im.width)
        im = im.resize((MAX_W, h), Image.LANCZOS)
    dst = os.path.join(IMG_OUT, f"{slug(state)}.webp")
    im.save(dst, "WEBP", quality=82, method=6)
    print(f"  {slug(state)}.webp  {im.width}x{im.height}  {os.path.getsize(dst)//1024}KB")
print("done")
