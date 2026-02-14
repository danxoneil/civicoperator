#!/usr/bin/env python3
"""
URL Validator — checks all URLs from a monday.com board, finds replacements
for broken ones, and updates the board.

Usage:
  python validate_urls.py                  # check only (dry run)
  python validate_urls.py --fix            # check + update broken URLs on monday.com
  python validate_urls.py --report-only    # just print the report, no changes

Required env vars: MONDAY_API_TOKEN, MONDAY_BOARD_ID
Optional: MONDAY_URL_COLUMN_ID (column title or ID, default: auto-detect)
"""

import argparse
import json
import logging
import os
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4 lxml")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validate-urls.log'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class URLValidator:

    # Known search patterns for state RHT pages
    SEARCH_QUERIES = [
        '{state} rural health transformation program site:.gov',
        '{state} rural health transformation program',
        '{state} RHTP state plan site:.gov',
        '{state} CMS rural health transformation 2026',
    ]

    def __init__(self):
        self.monday_token = os.getenv('MONDAY_API_TOKEN', '')
        self.monday_board_id = os.getenv('MONDAY_BOARD_ID', '')
        self.monday_url_column = os.getenv('MONDAY_URL_COLUMN_ID', '')

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        })
        self.session.trust_env = False
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        self.session.mount('http://', HTTPAdapter(max_retries=retry))

    # ------------------------------------------------------------------
    # monday.com API
    # ------------------------------------------------------------------

    def _monday_query(self, query: str, variables: dict = None) -> dict:
        resp = requests.post(
            'https://api.monday.com/v2',
            json={'query': query, 'variables': variables or {}},
            headers={
                'Authorization': self.monday_token,
                'Content-Type': 'application/json',
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if 'errors' in data:
            raise RuntimeError(f"monday.com API errors: {data['errors']}")
        return data

    def fetch_board_items(self) -> Tuple[List[dict], str]:
        """Fetch items from the board. Returns (items, target_column_id)."""
        query = """
        query ($boardId: [ID!]!) {
          boards(ids: $boardId) {
            columns { id title type }
            items_page(limit: 500) {
              items {
                id
                name
                column_values { id type text value }
              }
            }
          }
        }
        """
        data = self._monday_query(query, {"boardId": [self.monday_board_id]})
        board = data['data']['boards'][0]
        columns = board['columns']

        # Resolve target column
        col_id_to_title = {c['id']: c['title'] for c in columns}
        col_title_to_id = {c['title']: c['id'] for c in columns}

        target_col_id = None
        if self.monday_url_column:
            if self.monday_url_column in col_id_to_title:
                target_col_id = self.monday_url_column
            elif self.monday_url_column in col_title_to_id:
                target_col_id = col_title_to_id[self.monday_url_column]
            else:
                raise RuntimeError(
                    f"Column '{self.monday_url_column}' not found. "
                    f"Available: {[c['title'] for c in columns]}"
                )
        else:
            # Auto-detect first link column
            for c in columns:
                if c['type'] in ('link', 'url'):
                    target_col_id = c['id']
                    break

        if not target_col_id:
            raise RuntimeError("No URL column found")

        logger.info(f"Using column: {target_col_id} ({col_id_to_title.get(target_col_id, '?')})")

        items = board['items_page']['items']
        result = []
        for item in items:
            url = None
            for col in item['column_values']:
                if col['id'] == target_col_id:
                    url = self._extract_url(col)
                    break
            result.append({
                'item_id': item['id'],
                'name': item['name'],
                'url': url,
            })

        return result, target_col_id

    @staticmethod
    def _extract_url(col: dict) -> Optional[str]:
        raw = col.get('value')
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict) and 'url' in parsed:
                    return parsed['url'].strip()
            except (json.JSONDecodeError, TypeError):
                pass
        text = col.get('text', '')
        if text and text.startswith('http'):
            return text.strip()
        return None

    def update_item_url(self, item_id: str, column_id: str, new_url: str, link_text: str = ''):
        """Update a link column on a monday.com item."""
        value = json.dumps({"url": new_url, "text": link_text or new_url})
        query = """
        mutation ($boardId: ID!, $itemId: ID!, $columnId: String!, $value: JSON!) {
          change_column_value(
            board_id: $boardId,
            item_id: $itemId,
            column_id: $columnId,
            value: $value
          ) {
            id
          }
        }
        """
        self._monday_query(query, {
            "boardId": self.monday_board_id,
            "itemId": item_id,
            "columnId": column_id,
            "value": value,
        })
        logger.info(f"Updated item {item_id} with URL: {new_url}")

    # ------------------------------------------------------------------
    # URL checking
    # ------------------------------------------------------------------

    def check_url(self, url: str) -> dict:
        """Check if a URL is reachable and has RHT-related content."""
        result = {'url': url, 'status': None, 'ok': False, 'has_rht_content': False, 'error': None}

        try:
            resp = self.session.get(url, timeout=20, allow_redirects=True)
            result['status'] = resp.status_code
            result['final_url'] = resp.url

            if resp.status_code != 200:
                result['error'] = f'HTTP {resp.status_code}'
                return result

            result['ok'] = True

            # Check for RHT-related content
            text = resp.text.lower()
            rht_terms = ['rural health transformation', 'rhtp', 'rht program', 'rural health funding']
            result['has_rht_content'] = any(term in text for term in rht_terms)

        except requests.exceptions.RequestException as e:
            result['error'] = type(e).__name__

        return result

    def find_replacement_url(self, state_name: str) -> Optional[str]:
        """Search Google for a state's RHT program page and return the best URL."""
        for query_template in self.SEARCH_QUERIES:
            query = query_template.format(state=state_name)
            try:
                # Use Google search via a simple scrape
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=5"
                resp = self.session.get(search_url, timeout=15)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')

                # Extract URLs from search results
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    # Google wraps URLs in /url?q=...
                    if '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        parsed = urlparse(actual_url)
                        # Prefer .gov domains
                        if parsed.netloc.endswith('.gov') and 'rural' in actual_url.lower():
                            # Verify it works
                            check = self.check_url(actual_url)
                            if check['ok']:
                                logger.info(f"Found replacement for {state_name}: {actual_url}")
                                return actual_url

                # If no .gov found, try any relevant result
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        if 'rural' in actual_url.lower() and 'health' in actual_url.lower():
                            check = self.check_url(actual_url)
                            if check['ok'] and check['has_rht_content']:
                                logger.info(f"Found replacement for {state_name}: {actual_url}")
                                return actual_url

            except Exception as e:
                logger.warning(f"Search failed for '{query}': {e}")

            time.sleep(2)  # Rate limit between searches

        logger.warning(f"No replacement found for {state_name}")
        return None

    # ------------------------------------------------------------------
    # Main
    # ------------------------------------------------------------------

    def run(self, fix: bool = False) -> dict:
        """Validate all URLs and optionally fix broken ones."""
        logger.info("=" * 60)
        logger.info(f"URL Validator — {'FIX mode' if fix else 'CHECK mode'}")
        logger.info("=" * 60)

        items, col_id = self.fetch_board_items()
        logger.info(f"Found {len(items)} items on board")

        results = {
            'total': len(items),
            'valid': [],
            'broken': [],
            'fixed': [],
            'no_url': [],
            'no_replacement': [],
        }

        for item in items:
            name = item['name']
            url = item['url']
            item_id = item['item_id']

            if not url:
                logger.warning(f"  {name}: no URL set")
                results['no_url'].append({'name': name, 'item_id': item_id})
                continue

            logger.info(f"Checking: {name} — {url}")
            check = self.check_url(url)

            if check['ok']:
                rht_note = " (has RHT content)" if check['has_rht_content'] else " (no RHT keywords found)"
                logger.info(f"  VALID{rht_note}")
                results['valid'].append({
                    'name': name,
                    'url': url,
                    'has_rht_content': check['has_rht_content'],
                })
            else:
                logger.warning(f"  BROKEN: {check['error']}")
                results['broken'].append({
                    'name': name,
                    'url': url,
                    'error': check['error'],
                    'item_id': item_id,
                })

                if fix:
                    logger.info(f"  Searching for replacement...")
                    new_url = self.find_replacement_url(name)
                    if new_url:
                        self.update_item_url(item_id, col_id, new_url, name)
                        results['fixed'].append({
                            'name': name,
                            'old_url': url,
                            'new_url': new_url,
                        })
                        # Remove from broken since it's been fixed
                        results['broken'].pop()
                    else:
                        results['no_replacement'].append({'name': name, 'url': url})

            time.sleep(1)

        # Print summary
        logger.info("=" * 60)
        logger.info(f"Results: {len(results['valid'])} valid, "
                     f"{len(results['broken'])} broken, "
                     f"{len(results['fixed'])} fixed, "
                     f"{len(results['no_url'])} no URL, "
                     f"{len(results['no_replacement'])} no replacement found")
        logger.info("=" * 60)

        return results

    def format_report(self, results: dict) -> str:
        """Format a markdown report."""
        parts = [
            "# URL Validation Report\n",
            f"**Total items:** {results['total']}",
            f"**Valid:** {len(results['valid'])} | "
            f"**Broken:** {len(results['broken'])} | "
            f"**Fixed:** {len(results['fixed'])} | "
            f"**No URL:** {len(results['no_url'])} | "
            f"**No replacement:** {len(results['no_replacement'])}\n",
        ]

        if results['fixed']:
            parts.append("## Fixed (updated on monday.com)\n")
            for item in results['fixed']:
                parts.append(f"- **{item['name']}**")
                parts.append(f"  - Old: {item['old_url']}")
                parts.append(f"  - New: {item['new_url']}\n")

        if results['broken']:
            parts.append("## Still Broken\n")
            for item in results['broken']:
                parts.append(f"- **{item['name']}** — {item['url']} ({item['error']})")

        if results['no_replacement']:
            parts.append("\n## No Replacement Found\n")
            for item in results['no_replacement']:
                parts.append(f"- **{item['name']}** — {item['url']}")

        if results['no_url']:
            parts.append("\n## No URL Set\n")
            for item in results['no_url']:
                parts.append(f"- **{item['name']}**")

        if results['valid']:
            parts.append("\n## Valid URLs\n")
            parts.append("| State | URL | RHT Content |")
            parts.append("|-------|-----|-------------|")
            for item in results['valid']:
                rht = "Yes" if item['has_rht_content'] else "No"
                parts.append(f"| {item['name']} | {item['url']} | {rht} |")

        return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description='Validate and fix URLs on monday.com board')
    parser.add_argument('--fix', action='store_true', help='Replace broken URLs with found replacements')
    parser.add_argument('--report-only', action='store_true', help='Just print report, no changes')
    args = parser.parse_args()

    validator = URLValidator()
    results = validator.run(fix=args.fix)

    # Save results
    with open('validation-results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    report = validator.format_report(results)
    print("\n" + report)

    # GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(report)


if __name__ == '__main__':
    main()
