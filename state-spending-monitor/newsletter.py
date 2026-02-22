#!/usr/bin/env python3
"""
Weekly RHT Briefing Report

Collects URL change data from the past week's GitHub issues,
enriches it by re-fetching changed pages and following key links,
pulls topic context from monday.com, and outputs a structured
briefing report ready to paste into Claude.ai for newsletter drafting.

Output: Markdown briefing saved to newsletter-draft.html and posted
as a GitHub issue for easy copy-paste.

Required env vars:
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


def is_binary_garbage(text: str) -> bool:
    """Detect if text looks like binary/Brotli gibberish rather than real content."""
    if not text or len(text) < 50:
        return False
    sample = text[:2000]
    non_printable = sum(
        1 for c in sample
        if not c.isprintable() and c not in '\n\r\t'
    )
    return (non_printable / len(sample)) > 0.1


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

        # Skip diffs that are binary garbage (from pre-Brotli-fix runs)
        if is_binary_garbage(diff):
            logger.warning(f"  Skipping {state_name}: diff is binary garbage")
            continue

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


# ── Format briefing report ────────────────────────────────────────────

def format_briefing_report(changes: List[Dict], topics: List[Dict]) -> str:
    """Build a structured markdown briefing from collected changes and topics.

    Output is designed to be copy-pasted into Claude.ai for newsletter drafting
    or read directly as a raw briefing.
    """
    today = datetime.now().strftime('%B %d, %Y')
    week_start = (datetime.now() - timedelta(days=7)).strftime('%B %d')

    lines = []
    lines.append(f"# RHTP Weekly Briefing: {week_start} – {today}")
    lines.append("")

    if not changes:
        lines.append("## No page changes detected this week.")
        lines.append("")
        lines.append("The URL monitor checked all 51 RHTP pages daily but found no content updates.")
        lines.append("")
    else:
        # Group by state
        by_state = {}
        for c in changes:
            state = c['state']
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(c)

        lines.append(f"## {len(changes)} changes across {len(by_state)} states")
        lines.append("")

        for state, state_changes in sorted(by_state.items()):
            lines.append(f"### {state}")
            lines.append("")

            for c in state_changes:
                lines.append(f"**URL:** {c['url']}")
                lines.append(f"**Date detected:** {c['date']}")
                lines.append("")

                # Diff
                lines.append("**Changes (diff):**")
                lines.append("```diff")
                lines.append(c['diff'])
                lines.append("```")
                lines.append("")

                # Enriched page content
                if c.get('page_content'):
                    lines.append("**Current page content (excerpt):**")
                    lines.append("")
                    lines.append(c['page_content'])
                    lines.append("")

                # Linked content from followed links
                if c.get('linked_content'):
                    lines.append("**Content from key links on this page:**")
                    lines.append("")
                    for link in c['linked_content']:
                        lines.append(f"#### {link['label']}")
                        lines.append(f"URL: {link['url']}")
                        lines.append("")
                        lines.append(link['content'])
                        lines.append("")

                # All discovered key links
                if c.get('key_links'):
                    lines.append("**All key links discovered:**")
                    for link in c['key_links']:
                        pdf_tag = " [PDF]" if link.get('is_pdf') else ""
                        lines.append(f"- {link['label']}{pdf_tag}: {link['url']}")
                    lines.append("")

            lines.append("---")
            lines.append("")

    # Topics from monday.com
    if topics:
        lines.append("## Active Topics (monday.com)")
        lines.append("")
        for t in topics:
            entry = f"- **{t['name']}**"
            if t['group']:
                entry += f" ({t['group']})"
            cols = t.get('columns', {})
            if cols:
                details = ', '.join(f"{k}: {v}" for k, v in cols.items())
                entry += f" — {details}"
            lines.append(entry)
        lines.append("")

    return '\n'.join(lines)


# ── Main ──────────────────────────────────────────────────────────────

def main():
    github_token = os.getenv('GITHUB_TOKEN', '')
    repo = os.getenv('GITHUB_REPOSITORY', '')
    monday_token = os.getenv('MONDAY_API_TOKEN', '')
    topics_board_id = os.getenv('MONDAY_TOPICS_BOARD_ID', '')
    lookback_days = int(os.getenv('LOOKBACK_DAYS', '7'))

    if not github_token or not repo:
        logger.error("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
        sys.exit(1)

    # 1. Collect this week's changes from GitHub issues
    changes = fetch_weekly_changes(github_token, repo, lookback_days)

    # 2. Enrich: re-fetch changed pages and follow key links
    if changes:
        logger.info("Enriching changes with linked content...")
        changes = enrich_changes(changes)

    # 3. Fetch topics from monday.com for context
    topics = fetch_topics(monday_token, topics_board_id)

    # 4. Format the briefing report
    report = format_briefing_report(changes, topics)

    # 5. Save report
    output_path = 'newsletter-draft.html'
    with open(output_path, 'w') as f:
        f.write(report)
    logger.info(f"Saved briefing report to {output_path}")

    # 6. Print for logs
    print("\n" + "=" * 60)
    print("RHTP WEEKLY BRIEFING REPORT")
    print("=" * 60)
    print(report)

    # 7. GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(report)

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
