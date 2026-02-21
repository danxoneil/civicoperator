#!/usr/bin/env python3
"""
Weekly RHT Newsletter Generator

Collects URL change data from the past week's GitHub issues,
enriches it by re-fetching changed pages and following key links,
pulls topic context from monday.com, and uses Claude API to
generate a newsletter draft.

Output: HTML draft saved to newsletter-draft.html and printed as
markdown for the GitHub Actions step summary / issue.

Required env vars:
  ANTHROPIC_API_KEY       — Claude API key
  GITHUB_TOKEN            — GitHub token (auto-provided in Actions)
  GITHUB_REPOSITORY       — owner/repo (auto-provided in Actions)

Optional env vars:
  MONDAY_API_TOKEN        — monday.com API token (for topics board)
  MONDAY_TOPICS_BOARD_ID  — monday.com topics board ID
  LOOKBACK_DAYS           — days to look back for changes (default: 7)
"""

import io
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Missing dependency: anthropic")
    sys.exit(1)

# Optional PDF support
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# ── HTTP session ─────────────────────────────────────────────────────

def make_session() -> requests.Session:
    """Create an HTTP session with browser-like headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/131.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    })
    session.trust_env = False
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retry))
    session.mount('http://', HTTPAdapter(max_retries=retry))
    return session


SESSION = make_session()


# ── GitHub: collect changes from url-monitor issues ───────────────────

def fetch_weekly_changes(token: str, repo: str, lookback_days: int = 7) -> List[Dict]:
    """Fetch url-monitor issues with page-changed label from the past week."""
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    url = f'https://api.github.com/repos/{repo}/issues'
    params = {
        'labels': 'url-monitor,page-changed',
        'since': since,
        'state': 'open',
        'sort': 'created',
        'direction': 'desc',
        'per_page': 50,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    issues = resp.json()

    logger.info(f"Found {len(issues)} page-changed issues in the past {lookback_days} days")

    changes = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    for issue in issues:
        created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
        if created < cutoff:
            continue

        body = issue.get('body', '')
        title = issue.get('title', '')
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', title)
        issue_date = date_match.group(0) if date_match else created.strftime('%Y-%m-%d')

        parsed = parse_issue_changes(body)
        for change in parsed:
            change['date'] = issue_date
            change['issue_number'] = issue['number']

        changes.extend(parsed)

    logger.info(f"Extracted {len(changes)} state changes total")
    return changes


def parse_issue_changes(body: str) -> List[Dict]:
    """Parse a url-monitor issue body to extract changed pages and their diffs."""
    changes = []

    sections = re.split(r'####\s+', body)

    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines:
            continue

        state_name = lines[0].strip()

        url = ''
        for line in lines:
            if line.startswith('URL:'):
                url = line.replace('URL:', '').strip()
                break

        in_diff = False
        diff_lines = []
        for line in lines:
            if line.strip().startswith('```diff'):
                in_diff = True
                continue
            if in_diff and line.strip() == '```':
                in_diff = False
                continue
            if in_diff:
                diff_lines.append(line)

        diff = '\n'.join(diff_lines)

        if state_name and diff:
            changes.append({
                'state': state_name,
                'url': url,
                'diff': diff,
            })

    return changes


# ── Link enrichment: follow key links on changed pages ────────────────

def enrich_changes(changes: List[Dict]) -> List[Dict]:
    """For each changed state, re-fetch the page and follow key links.

    Adds 'page_content', 'key_links', and 'linked_content' to each change dict.
    """
    # Deduplicate by URL (a state may appear in multiple daily issues)
    seen_urls = set()
    unique_changes = []
    for c in changes:
        if c['url'] not in seen_urls:
            seen_urls.add(c['url'])
            unique_changes.append(c)

    for change in unique_changes:
        url = change['url']
        if not url:
            continue

        logger.info(f"Enriching: {change['state']} — {url}")

        # Fetch the main page
        page_text, soup = fetch_page_with_soup(url)
        if not page_text:
            logger.warning(f"  Could not fetch page for enrichment")
            continue

        change['page_content'] = page_text[:5000]  # Cap at 5k chars

        # Extract key links from the page
        key_links = extract_key_links(soup, url)
        change['key_links'] = key_links
        logger.info(f"  Found {len(key_links)} key links")

        # Follow key links and extract content
        linked_content = []
        for link in key_links[:10]:  # Cap at 10 links per state
            link_url = link['url']
            link_label = link['label']
            logger.info(f"  Following: {link_label} — {link_url}")

            content = fetch_link_content(link_url)
            if content:
                linked_content.append({
                    'url': link_url,
                    'label': link_label,
                    'content': content[:3000],  # Cap each link
                })

            time.sleep(0.5)

        change['linked_content'] = linked_content
        time.sleep(1)

    return changes


def fetch_page_with_soup(url: str):
    """Fetch a URL, return (text, soup) or (None, None)."""
    try:
        resp = SESSION.get(url, timeout=20, allow_redirects=True)
        if resp.status_code == 403:
            return None, None
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return None, None

    soup = BeautifulSoup(resp.content, 'html.parser')

    for tag in soup.find_all(['script', 'style', 'nav', 'noscript', 'iframe']):
        tag.decompose()

    main = soup.find('main') or soup.find('article') or soup.find(role='main')
    if main:
        text = main.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines), soup


def extract_key_links(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """Extract links that are likely important: PDFs, subpages, forms, media."""
    if not soup:
        return []

    base_domain = urlparse(base_url).netloc
    key_links = []
    seen = set()

    # Look in main content area first, fall back to whole page
    content = soup.find('main') or soup.find('article') or soup.find(role='main') or soup

    for a in content.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        if full_url in seen:
            continue
        seen.add(full_url)

        label = a.get_text(strip=True)[:100] or href.split('/')[-1]
        path_lower = parsed.path.lower()

        # Score relevance
        is_pdf = path_lower.endswith('.pdf')
        is_same_domain = parsed.netloc == base_domain or parsed.netloc.endswith('.gov')
        is_form = 'survey' in full_url.lower() or 'form' in full_url.lower() or 'redcap' in full_url.lower()
        is_media = '/media/' in full_url or '/document' in full_url or '/content/dam/' in full_url

        label_lower = label.lower()
        has_keyword = any(kw in label_lower for kw in [
            'narrative', 'rfp', 'award', 'grant', 'funding', 'application',
            'involved', 'partner', 'initiative', 'plan', 'program',
            'notice', 'intent', 'opportunity', 'hub', 'telehealth',
        ])

        if is_pdf or is_form or is_media or (is_same_domain and has_keyword):
            key_links.append({
                'url': full_url,
                'label': label,
                'is_pdf': is_pdf,
            })

    return key_links


def fetch_link_content(url: str) -> Optional[str]:
    """Fetch content from a link — handles HTML pages and PDFs."""
    parsed = urlparse(url)

    if parsed.path.lower().endswith('.pdf'):
        return fetch_pdf_text(url)

    try:
        resp = SESSION.get(url, timeout=15, allow_redirects=True)
        if resp.status_code != 200:
            return None
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(resp.content, 'html.parser')
    for tag in soup.find_all(['script', 'style', 'nav', 'noscript']):
        tag.decompose()

    main = soup.find('main') or soup.find('article') or soup
    text = main.get_text(separator='\n', strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines)


def fetch_pdf_text(url: str) -> Optional[str]:
    """Download a PDF and extract text."""
    if not HAS_PYPDF:
        return f"[PDF at {url} — pypdf not installed for text extraction]"

    try:
        resp = SESSION.get(url, timeout=30)
        if resp.status_code != 200:
            return None

        reader = PdfReader(io.BytesIO(resp.content))
        pages_text = []
        for i, page in enumerate(reader.pages[:20]):  # Cap at 20 pages
            text = page.extract_text()
            if text:
                pages_text.append(text)

        return '\n'.join(pages_text) if pages_text else None

    except Exception as e:
        logger.warning(f"  PDF extraction failed for {url}: {e}")
        return None


# ── monday.com: fetch topics for context ──────────────────────────────

def fetch_topics(token: str, board_id: str) -> List[Dict]:
    """Fetch items from the monday.com topics board for newsletter context."""
    if not token or not board_id:
        logger.info("No topics board configured, skipping")
        return []

    query = """
    query ($boardId: [ID!]!) {
      boards(ids: $boardId) {
        items_page(limit: 500) {
          items {
            name
            group { title }
            column_values { title text }
          }
        }
      }
    }
    """

    try:
        resp = requests.post(
            'https://api.monday.com/v2',
            json={'query': query, 'variables': {'boardId': [board_id]}},
            headers={
                'Authorization': token,
                'Content-Type': 'application/json',
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if 'errors' in data:
            logger.warning(f"monday.com topics errors: {data['errors']}")
            return []

        boards = data.get('data', {}).get('boards', [])
        if not boards:
            return []

        items = boards[0].get('items_page', {}).get('items', [])
        topics = []
        for item in items:
            topic = {
                'name': item['name'],
                'group': item.get('group', {}).get('title', ''),
                'columns': {
                    cv['title']: cv['text']
                    for cv in item.get('column_values', [])
                    if cv.get('text')
                },
            }
            topics.append(topic)

        logger.info(f"Fetched {len(topics)} topics from monday.com")
        return topics

    except Exception as e:
        logger.warning(f"Error fetching topics: {e}")
        return []


# ── Claude API: generate newsletter ──────────────────────────────────

SYSTEM_PROMPT = """You are writing a weekly factual briefing about the Rural Health Transformation Program (RHTP) — a $50 billion CMS initiative funding all 50 US states to transform rural healthcare.

Your audience is paid subscribers: healthcare executives, state officials, consultants, and technology vendors.

EDITORIAL RULES — follow these strictly:
- NO hype, NO superlatives, NO breathless language. Never say "landmark", "groundbreaking", "game-changing", etc.
- Dry, factual, wire-service tone. Think Reuters or CQ Roll Call, not TechCrunch.
- ALWAYS attribute claims. Write "Iowa states it is the first state to award RHTP funding" — NOT "Iowa becomes the first state to award RHTP funding." You are reporting what states say, not endorsing it.
- When information comes from a state website, say "according to [state]'s RHTP page" or "[state]'s website now shows..."
- Report only what the data shows. Do not speculate about motives, implications, or future events unless directly supported by the source material.
- Do NOT invent dollar amounts, dates, or details not present in the provided data.
- If a change is just minor formatting/cosmetic (e.g., CAPTCHA rotation), skip it entirely.
- The "What to Watch" section should only reference concrete items visible in the data, not speculation.

STRUCTURE AND FORMAT:
- <h1>: Descriptive headline summarizing the key developments (e.g., "Iowa awards, Illinois narrative, and Kentucky program details")
- <h2> directly after h1: "Rural Health Transformation Program Brief: [date range]" as a dateline subhead
- <h2>: Thematic section headers (e.g., "Funding and Awards", "Application Materials", "Program Updates")
- <h3>: State name as header — say the state name ONCE here, then go straight to bullet points
- NO <hr> line separators between sections
- Use <ul>/<li> bullet format for all state content. Start each bullet with a verb clause: "Posted a news item...", "Published its project narrative...", "Added a Get Involved page..."
- Use DIRECT QUOTES from source material in quotation marks when available
- Show full URLs inline as display text for deep links: https://hhs.iowa.gov/media/18093/ — this shows geekiness and transparency
- For every state, include a linked reference to their main RHTP page
- When enriched content from linked pages is provided (subpages, PDFs, forms), PULL KEY DETAILS directly into the newsletter — quote program descriptions, list initiative names, note specific RFP numbers and dates
- For PDFs and subpages, include the full URL so readers can access them directly
- 500-1000 words. Do not pad. If a week is quiet, keep it short.

HTML TAGS:
- <h1>, <h2>, <h3>, <p>, <ul>/<li>, <a href="...">, <strong>, <em>, <blockquote>
- Do NOT include <html>, <head>, <body>, or <hr> tags"""


def generate_newsletter(changes: List[Dict], topics: List[Dict],
                        api_key: str) -> str:
    """Use Claude API to generate the newsletter from changes and topics."""

    today = datetime.now().strftime('%B %d, %Y')
    week_start = (datetime.now() - timedelta(days=7)).strftime('%B %d')

    user_content = f"Generate the weekly RHT newsletter for the week of {week_start} – {today}.\n\n"

    if changes:
        user_content += "## Page Changes Detected This Week\n\n"
        # Group by state
        by_state = {}
        for c in changes:
            state = c['state']
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(c)

        for state, state_changes in sorted(by_state.items()):
            user_content += f"### {state}\n"
            for c in state_changes:
                user_content += f"State RHTP URL: {c['url']}\n"
                user_content += f"Date detected: {c['date']}\n"
                user_content += f"Diff:\n{c['diff']}\n\n"

                # Include enriched page content
                if c.get('page_content'):
                    user_content += f"Current page content (excerpt):\n{c['page_content']}\n\n"

                # Include linked content
                if c.get('linked_content'):
                    user_content += "Key links found on this page:\n"
                    for link in c['linked_content']:
                        user_content += f"\n--- Link: {link['label']} ({link['url']}) ---\n"
                        user_content += f"{link['content']}\n"
                    user_content += "\n"

                if c.get('key_links'):
                    user_content += "All key links discovered:\n"
                    for link in c['key_links']:
                        pdf_tag = " [PDF]" if link.get('is_pdf') else ""
                        user_content += f"- {link['label']}{pdf_tag}: {link['url']}\n"
                    user_content += "\n"
    else:
        user_content += "## No page changes were detected this week.\n\n"
        user_content += "The URL monitor checked all 51 RHTP pages daily but found no content updates.\n\n"

    if topics:
        user_content += "## Active Topics Being Tracked (from monday.com board)\n\n"
        for t in topics:
            user_content += f"- **{t['name']}**"
            if t['group']:
                user_content += f" ({t['group']})"
            cols = t.get('columns', {})
            if cols:
                details = ', '.join(f"{k}: {v}" for k, v in cols.items())
                user_content += f" — {details}"
            user_content += "\n"
        user_content += "\n"

    user_content += "Write the newsletter now. Bullet format, full URLs, direct quotes, no hype."

    client = anthropic.Anthropic(api_key=api_key)

    logger.info(f"Calling Claude API ({len(user_content)} chars of context)...")
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    newsletter_html = message.content[0].text
    logger.info(f"Newsletter generated: {len(newsletter_html)} chars, "
                f"input tokens: {message.usage.input_tokens}, "
                f"output tokens: {message.usage.output_tokens}")

    return newsletter_html


# ── Main ──────────────────────────────────────────────────────────────

def main():
    github_token = os.getenv('GITHUB_TOKEN', '')
    repo = os.getenv('GITHUB_REPOSITORY', '')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    monday_token = os.getenv('MONDAY_API_TOKEN', '')
    topics_board_id = os.getenv('MONDAY_TOPICS_BOARD_ID', '')
    lookback_days = int(os.getenv('LOOKBACK_DAYS', '7'))

    if not github_token or not repo:
        logger.error("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
        sys.exit(1)
    if not anthropic_key:
        logger.error("ANTHROPIC_API_KEY is required")
        sys.exit(1)

    # 1. Collect this week's changes from GitHub issues
    changes = fetch_weekly_changes(github_token, repo, lookback_days)

    # 2. Enrich: re-fetch changed pages and follow key links
    if changes:
        logger.info("Enriching changes with linked content...")
        changes = enrich_changes(changes)

    # 3. Fetch topics from monday.com for context
    topics = fetch_topics(monday_token, topics_board_id)

    # 4. Generate newsletter via Claude API
    newsletter_html = generate_newsletter(changes, topics, anthropic_key)

    # 5. Save HTML draft
    output_path = 'newsletter-draft.html'
    with open(output_path, 'w') as f:
        f.write(newsletter_html)
    logger.info(f"Saved newsletter draft to {output_path}")

    # 6. Print for logs
    print("\n" + "=" * 60)
    print("NEWSLETTER DRAFT")
    print("=" * 60)
    print(newsletter_html)

    # 7. GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write("# Weekly RHT Newsletter Draft\n\n")
            f.write(newsletter_html)

    # 8. Save metadata
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'changes_count': len(changes),
        'topics_count': len(topics),
        'states_with_changes': list(set(c['state'] for c in changes)),
        'lookback_days': lookback_days,
    }
    with open('newsletter-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info("Done!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
