#!/usr/bin/env python3
"""
One-time script to populate missing RHTP URLs on the monday.com board
and fix known URL issues.

Run via GitHub Actions workflow or locally with:
  MONDAY_API_TOKEN=xxx MONDAY_BOARD_ID=yyy python fix_board_urls.py

Set DRY_RUN=true to preview changes without writing to monday.com.
"""

import json
import logging
import os
import sys

try:
    import requests
except ImportError:
    print("Missing dependency: requests")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# ── URLs to set for states that are missing them ──────────────────────
MISSING_URLS = {
    'Alaska': 'https://health.alaska.gov/en/education/rural-health-transformation-program/',
    'Arkansas': 'https://governor.arkansas.gov/arkansas-rural-health-transformation-program-application/',
    'Florida': 'https://ahca.myflorida.com/rural-health-transformation-program',
    'Kansas': 'https://www.kdhe.ks.gov/2361/Rural-Health-Transformation-Program',
}

# ── URLs to replace (state -> new URL) ────────────────────────────────
REPLACE_URLS = {
    'Massachusetts': 'https://www.mass.gov/rural-health-transformation-program',
}


def monday_query(token: str, query: str, variables: dict = None) -> dict:
    resp = requests.post(
        'https://api.monday.com/v2',
        json={'query': query, 'variables': variables or {}},
        headers={
            'Authorization': token,
            'Content-Type': 'application/json',
        },
        timeout=30,
    )
    logger.info(f"monday.com API response status: {resp.status_code}")
    resp.raise_for_status()
    data = resp.json()
    if 'errors' in data:
        logger.error(f"monday.com API errors: {data['errors']}")
        raise RuntimeError(f"monday.com API errors: {data['errors']}")
    return data


def main():
    token = os.getenv('MONDAY_API_TOKEN', '')
    board_id = os.getenv('MONDAY_BOARD_ID', '')
    url_column_title = os.getenv('MONDAY_URL_COLUMN_ID', 'RHTP Specific URL')
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

    if not token or not board_id:
        logger.error("MONDAY_API_TOKEN and MONDAY_BOARD_ID are required")
        sys.exit(1)

    # Fetch board
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
    data = monday_query(token, query, {"boardId": [board_id]})
    board = data['data']['boards'][0]
    columns = board['columns']

    # Resolve URL column
    col_title_to_id = {c['title']: c['id'] for c in columns}
    col_id_to_title = {c['id']: c['title'] for c in columns}

    # Also build case-insensitive lookup
    col_title_lower_to_id = {c['title'].lower(): c['id'] for c in columns}

    logger.info(f"Looking for column: '{url_column_title}'")
    logger.info(f"Available columns: {[(c['id'], c['title'], c['type']) for c in columns]}")

    url_col_id = None
    if url_column_title in col_id_to_title:
        url_col_id = url_column_title
    elif url_column_title in col_title_to_id:
        url_col_id = col_title_to_id[url_column_title]
    elif url_column_title.lower() in col_title_lower_to_id:
        url_col_id = col_title_lower_to_id[url_column_title.lower()]
        logger.info(f"Matched column by case-insensitive title")
    else:
        logger.error(f"Column '{url_column_title}' not found. Available: {list(col_title_to_id.keys())}")
        sys.exit(1)

    logger.info(f"URL column: {url_col_id} ({col_id_to_title.get(url_col_id, '?')})")

    items = board['items_page']['items']
    logger.info(f"Found {len(items)} items on board")
    logger.info(f"Item names: {[item['name'] for item in items]}")

    # Build item lookup by name
    changes = []
    for item in items:
        name = item['name'].strip()
        item_id = item['id']

        # Get current URL
        current_url = None
        for col in item['column_values']:
            if col['id'] == url_col_id:
                raw = col.get('value')
                if raw:
                    try:
                        parsed = json.loads(raw)
                        if isinstance(parsed, dict) and 'url' in parsed:
                            current_url = parsed['url'].strip()
                    except (json.JSONDecodeError, TypeError):
                        pass
                if not current_url:
                    text = col.get('text', '')
                    if text and text.startswith('http'):
                        current_url = text.strip()
                break

        # Check if this state needs a URL set
        if name in MISSING_URLS and not current_url:
            changes.append({
                'item_id': item_id,
                'name': name,
                'action': 'add',
                'old_url': None,
                'new_url': MISSING_URLS[name],
            })
        elif name in REPLACE_URLS:
            new_url = REPLACE_URLS[name]
            if current_url != new_url:
                changes.append({
                    'item_id': item_id,
                    'name': name,
                    'action': 'replace',
                    'old_url': current_url,
                    'new_url': new_url,
                })

    if not changes:
        logger.info("No changes needed — all URLs are already set correctly")
        return

    # Apply changes
    logger.info(f"\n{'DRY RUN — ' if dry_run else ''}Applying {len(changes)} changes:\n")

    for change in changes:
        action = change['action'].upper()
        logger.info(f"  [{action}] {change['name']}")
        if change['old_url']:
            logger.info(f"    Old: {change['old_url']}")
        logger.info(f"    New: {change['new_url']}")

        if not dry_run:
            value = json.dumps({"url": change['new_url'], "text": change['name']})
            mutation = """
            mutation ($boardId: ID!, $itemId: ID!, $columnId: String!, $value: JSON!) {
              change_column_value(
                board_id: $boardId, item_id: $itemId,
                column_id: $columnId, value: $value
              ) { id }
            }
            """
            monday_query(token, mutation, {
                'boardId': board_id,
                'itemId': change['item_id'],
                'columnId': url_col_id,
                'value': value,
            })
            logger.info(f"    ✓ Updated on monday.com")

    # Summary
    summary = f"\n{'DRY RUN — ' if dry_run else ''}Done: {len(changes)} URLs updated"
    logger.info(summary)

    # GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        lines = ["# Board URL Fix Report\n"]
        for change in changes:
            action = "Added" if change['action'] == 'add' else "Replaced"
            lines.append(f"- **{change['name']}**: {action} → {change['new_url']}")
        with open(summary_file, 'a') as f:
            f.write('\n'.join(lines))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
