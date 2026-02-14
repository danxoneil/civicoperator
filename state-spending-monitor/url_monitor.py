#!/usr/bin/env python3
"""
URL Change Monitor — tracks a list of URLs from a monday.com board
and sends a daily email noting which pages changed and how.

State persistence: reads/writes snapshots.json (cached between runs
via GitHub Actions cache).

Required environment variables:
  MONDAY_API_TOKEN    — monday.com API token
  MONDAY_BOARD_ID     — board ID containing the URL list

Optional environment variables:
  MONDAY_URL_COLUMN_ID — column ID for URLs (default: auto-detect link/url column)
  MONDAY_NAME_AS_URL   — if 'true', use the item name as the URL (default: false)
  SNAPSHOTS_FILE       — path to snapshots file (default: snapshots.json)
  SEND_EMAIL_NOTIFICATIONS / NOTIFICATION_EMAIL / SMTP_* — email config
"""

import os
import json
import hashlib
import logging
import difflib
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        logging.FileHandler('url-monitor.log'),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


class URLMonitor:
    """Monitors URLs from a monday.com board for content changes."""

    def __init__(self):
        # monday.com config
        self.monday_token = os.getenv('MONDAY_API_TOKEN', '')
        self.monday_board_id = os.getenv('MONDAY_BOARD_ID', '')
        self.monday_url_column = os.getenv('MONDAY_URL_COLUMN_ID', '')
        self.monday_name_as_url = os.getenv('MONDAY_NAME_AS_URL', 'false').lower() == 'true'

        # State file
        self.snapshots_file = os.getenv('SNAPSHOTS_FILE', 'snapshots.json')

        # Email config
        self.send_email = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.notification_email = os.getenv('NOTIFICATION_EMAIL', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # HTTP session with retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        })
        self.session.trust_env = False
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        self.session.mount('http://', HTTPAdapter(max_retries=retry))

    # ------------------------------------------------------------------
    # monday.com integration
    # ------------------------------------------------------------------

    def fetch_urls_from_monday(self) -> List[Dict[str, str]]:
        """Fetch URL list from a monday.com board.

        Returns list of dicts with 'name' and 'url' keys.

        MONDAY_URL_COLUMN_ID can be a column ID (e.g. 'link__1') or a column
        title (e.g. 'RHTP Specific URL') — both are matched.
        """
        if not self.monday_token or not self.monday_board_id:
            logger.error("MONDAY_API_TOKEN and MONDAY_BOARD_ID are required")
            return []

        # Fetch columns metadata + items in one query
        query = """
        query ($boardId: [ID!]!) {
          boards(ids: $boardId) {
            columns {
              id
              title
              type
            }
            items_page(limit: 500) {
              items {
                name
                column_values {
                  id
                  type
                  text
                  value
                }
              }
            }
          }
        }
        """
        variables = {"boardId": [self.monday_board_id]}

        try:
            resp = requests.post(
                'https://api.monday.com/v2',
                json={'query': query, 'variables': variables},
                headers={
                    'Authorization': self.monday_token,
                    'Content-Type': 'application/json',
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if 'errors' in data:
                logger.error(f"monday.com API errors: {data['errors']}")
                return []

            boards = data.get('data', {}).get('boards', [])
            if not boards:
                logger.error("No boards found")
                return []

            board = boards[0]

            # Build column lookup: id -> title, title -> id
            columns = board.get('columns', [])
            col_id_to_title = {c['id']: c['title'] for c in columns}
            col_title_to_id = {c['title']: c['id'] for c in columns}

            # Log all columns for debugging
            logger.info("Board columns:")
            for c in columns:
                logger.info(f"  id={c['id']}  type={c['type']}  title={c['title']}")

            # Resolve the target column: match by ID or by title
            target_col_id = None
            if self.monday_url_column:
                if self.monday_url_column in col_id_to_title:
                    target_col_id = self.monday_url_column
                    logger.info(f"Matched column by ID: {target_col_id} ({col_id_to_title[target_col_id]})")
                elif self.monday_url_column in col_title_to_id:
                    target_col_id = col_title_to_id[self.monday_url_column]
                    logger.info(f"Matched column by title: '{self.monday_url_column}' -> id={target_col_id}")
                else:
                    logger.error(
                        f"MONDAY_URL_COLUMN_ID '{self.monday_url_column}' not found. "
                        f"Available columns: {[c['title'] + ' (' + c['id'] + ')' for c in columns]}"
                    )
                    return []

            items = board.get('items_page', {}).get('items', [])
            logger.info(f"monday.com: found {len(items)} items on board {self.monday_board_id}")

            urls = []
            for item in items:
                name = item.get('name', '').strip()
                url = None

                if self.monday_name_as_url and name.startswith('http'):
                    url = name
                else:
                    for col in item.get('column_values', []):
                        col_id = col.get('id', '')
                        col_type = col.get('type', '')

                        # Match the resolved target column
                        if target_col_id and col_id == target_col_id:
                            url = self._extract_url_from_column(col)
                            break

                        # Auto-detect if no column specified
                        if not target_col_id and col_type in ('link', 'url'):
                            url = self._extract_url_from_column(col)
                            if url:
                                break

                    # Fallback: any column with a URL in text
                    if not url and not target_col_id:
                        for col in item.get('column_values', []):
                            text = col.get('text', '') or ''
                            if text.startswith('http'):
                                url = text.strip()
                                break

                if url:
                    urls.append({'name': name, 'url': url})
                else:
                    logger.warning(f"No URL found for item: {name}")

            logger.info(f"Extracted {len(urls)} URLs from monday.com")
            return urls

        except Exception as e:
            logger.error(f"Error fetching from monday.com: {e}")
            return []

    @staticmethod
    def _extract_url_from_column(col: Dict) -> Optional[str]:
        """Extract a URL from a monday.com column value."""
        # Link columns store URL in the JSON value field
        raw_value = col.get('value')
        if raw_value:
            try:
                parsed = json.loads(raw_value)
                if isinstance(parsed, dict) and 'url' in parsed:
                    return parsed['url'].strip()
            except (json.JSONDecodeError, TypeError):
                pass

        # Text/url columns may have the URL in the text field
        text = col.get('text', '')
        if text and text.startswith('http'):
            return text.strip()

        return None

    # ------------------------------------------------------------------
    # Page fetching and text extraction
    # ------------------------------------------------------------------

    def fetch_page_text(self, url: str) -> Optional[str]:
        """Fetch a URL and extract meaningful text content (no nav/script/style)."""
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {type(e).__name__}")
            return None

        soup = BeautifulSoup(resp.content, 'html.parser')

        # Remove noise elements
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'noscript', 'iframe']):
            tag.decompose()

        # Try to find main content area
        main = soup.find('main') or soup.find('article') or soup.find(role='main')
        if main:
            text = main.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)

        # Normalize whitespace: collapse blank lines, strip trailing spaces
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # Change detection
    # ------------------------------------------------------------------

    @staticmethod
    def compute_hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_diff_summary(old_text: str, new_text: str, max_lines: int = 30) -> str:
        """Generate a human-readable summary of what changed."""
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm='', n=1))

        if not diff:
            return "(no visible text changes)"

        added = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]
        removed = [line[1:] for line in diff if line.startswith('-') and not line.startswith('---')]

        parts = []
        if added:
            parts.append(f"ADDED ({len(added)} lines):")
            for line in added[:max_lines]:
                parts.append(f"  + {line[:200]}")
            if len(added) > max_lines:
                parts.append(f"  ... and {len(added) - max_lines} more lines")

        if removed:
            parts.append(f"REMOVED ({len(removed)} lines):")
            for line in removed[:max_lines]:
                parts.append(f"  - {line[:200]}")
            if len(removed) > max_lines:
                parts.append(f"  ... and {len(removed) - max_lines} more lines")

        return '\n'.join(parts)

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def load_snapshots(self) -> Dict[str, Any]:
        """Load previous snapshots from file."""
        if os.path.exists(self.snapshots_file):
            try:
                with open(self.snapshots_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading snapshots: {e}")
        return {}

    def save_snapshots(self, snapshots: Dict[str, Any]):
        """Save snapshots to file."""
        with open(self.snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)
        logger.info(f"Saved {len(snapshots)} snapshots to {self.snapshots_file}")

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        """Run the monitor. Returns a results dict."""
        logger.info("=" * 60)
        logger.info("URL Change Monitor - Starting")
        logger.info("=" * 60)

        urls = self.fetch_urls_from_monday()
        if not urls:
            logger.error("No URLs to monitor — check monday.com config")
            return {'changed': [], 'unchanged': [], 'new': [], 'errors': [], 'url_count': 0}

        previous = self.load_snapshots()
        new_snapshots = {}
        results = {
            'changed': [],
            'unchanged': [],
            'new': [],
            'errors': [],
            'url_count': len(urls),
            'run_date': datetime.now().isoformat(),
        }

        for item in urls:
            name = item['name']
            url = item['url']
            logger.info(f"Checking: {name} ({url})")

            text = self.fetch_page_text(url)
            if text is None:
                results['errors'].append({'name': name, 'url': url, 'error': 'fetch failed'})
                # Preserve previous snapshot on fetch failure
                if url in previous:
                    new_snapshots[url] = previous[url]
                continue

            current_hash = self.compute_hash(text)
            new_snapshots[url] = {
                'name': name,
                'hash': current_hash,
                'content': text,
                'last_checked': datetime.now().isoformat(),
            }

            if url not in previous:
                results['new'].append({'name': name, 'url': url})
                logger.info(f"  NEW — first time seeing this URL")
            elif previous[url]['hash'] != current_hash:
                diff = self.generate_diff_summary(previous[url].get('content', ''), text)
                results['changed'].append({
                    'name': name,
                    'url': url,
                    'diff': diff,
                    'previous_check': previous[url].get('last_checked', 'unknown'),
                })
                logger.info(f"  CHANGED")
            else:
                results['unchanged'].append({'name': name, 'url': url})
                logger.info(f"  unchanged")

            time.sleep(1)  # Rate limiting

        self.save_snapshots(new_snapshots)

        logger.info("=" * 60)
        logger.info(
            f"Done: {len(results['changed'])} changed, "
            f"{len(results['unchanged'])} unchanged, "
            f"{len(results['new'])} new, "
            f"{len(results['errors'])} errors"
        )
        logger.info("=" * 60)

        return results

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def send_notification(self, results: Dict[str, Any]):
        """Send email notification with change report."""
        if not self.send_email:
            logger.info("Email notifications disabled")
            return

        if not all([self.smtp_user, self.smtp_password, self.notification_email]):
            logger.warning("Email config incomplete, skipping")
            return

        changed = results['changed']
        new = results['new']
        errors = results['errors']
        unchanged = results['unchanged']

        has_changes = bool(changed or new)

        if has_changes:
            subject = f"URL Monitor: {len(changed)} changed, {len(new)} new"
        else:
            subject = f"URL Monitor: no changes detected ({len(unchanged)} URLs checked)"

        body = self._format_email(results)

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = self.notification_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Sent notification to {self.notification_email}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")

    def _format_email(self, results: Dict[str, Any]) -> str:
        """Format email body."""
        parts = [
            f"URL Change Monitor Report — {datetime.now().strftime('%Y-%m-%d')}",
            f"Checked {results['url_count']} URLs\n",
        ]

        changed = results['changed']
        new = results['new']
        errors = results['errors']
        unchanged = results['unchanged']

        # Changed URLs (the important part)
        if changed:
            parts.append(f"{'='*60}")
            parts.append(f"CHANGED ({len(changed)} URLs)")
            parts.append(f"{'='*60}\n")
            for item in changed:
                parts.append(f">> {item['name']}")
                parts.append(f"   {item['url']}")
                parts.append(f"   Last checked: {item.get('previous_check', 'unknown')}")
                parts.append(f"   Changes:")
                for line in item['diff'].splitlines():
                    parts.append(f"   {line}")
                parts.append("")
        else:
            parts.append("No pages changed since last check.\n")

        # New URLs (first time seen)
        if new:
            parts.append(f"{'-'*60}")
            parts.append(f"NEW ({len(new)} URLs — first check, baseline saved)")
            parts.append(f"{'-'*60}")
            for item in new:
                parts.append(f"  {item['name']} — {item['url']}")
            parts.append("")

        # Errors
        if errors:
            parts.append(f"{'-'*60}")
            parts.append(f"ERRORS ({len(errors)} URLs — could not fetch)")
            parts.append(f"{'-'*60}")
            for item in errors:
                parts.append(f"  {item['name']} — {item['url']} ({item['error']})")
            parts.append("")

        # Unchanged (brief)
        if unchanged:
            parts.append(f"{'-'*60}")
            parts.append(f"UNCHANGED ({len(unchanged)} URLs)")
            parts.append(f"{'-'*60}")
            for item in unchanged:
                parts.append(f"  {item['name']} — {item['url']}")

        return '\n'.join(parts)

    def create_summary(self, results: Dict[str, Any]) -> str:
        """Create markdown summary for GitHub Actions."""
        changed = results['changed']
        new = results['new']
        errors = results['errors']
        unchanged = results['unchanged']

        parts = [
            "# URL Change Monitor\n",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
            f"**URLs checked:** {results['url_count']}",
            f"**Changed:** {len(changed)} | **New:** {len(new)} "
            f"| **Unchanged:** {len(unchanged)} | **Errors:** {len(errors)}\n",
        ]

        if changed:
            parts.append("## Changed\n")
            for item in changed:
                parts.append(f"### {item['name']}")
                parts.append(f"URL: {item['url']}\n")
                parts.append("```diff")
                parts.append(item['diff'])
                parts.append("```\n")

        if new:
            parts.append("## New (baseline saved)\n")
            for item in new:
                parts.append(f"- **{item['name']}** — {item['url']}")
            parts.append("")

        if errors:
            parts.append("## Errors\n")
            for item in errors:
                parts.append(f"- **{item['name']}** — {item['url']} ({item['error']})")
            parts.append("")

        if unchanged:
            parts.append("## Unchanged\n")
            for item in unchanged:
                parts.append(f"- {item['name']} — {item['url']}")

        return '\n'.join(parts)


def main():
    monitor = URLMonitor()
    results = monitor.run()

    # Save results JSON
    with open('url-monitor-results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # Send email
    monitor.send_notification(results)

    # Print summary
    summary = monitor.create_summary(results)
    print("\n" + summary)

    # GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(summary)

    # Exit with count of changes (0 = no changes, >0 = changes found)
    return len(results['changed'])


if __name__ == '__main__':
    main()
