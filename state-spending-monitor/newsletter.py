#!/usr/bin/env python3
"""
Weekly RHT Newsletter Generator

Collects URL change data from the past week's GitHub issues,
pulls topic context from monday.com, and uses Claude API to
generate a polished newsletter draft focused on spending movement,
RFPs, awards, and technology.

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

import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Missing dependency: requests")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Missing dependency: anthropic")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# ── GitHub: collect changes from url-monitor issues ───────────────────

def fetch_weekly_changes(token: str, repo: str, lookback_days: int = 7) -> List[Dict]:
    """Fetch url-monitor issues with page-changed label from the past week."""
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    # Fetch issues with url-monitor label, sorted by creation date
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
    for issue in issues:
        created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
        if created < datetime.now(timezone.utc) - timedelta(days=lookback_days):
            continue

        body = issue.get('body', '')
        title = issue.get('title', '')
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', title)
        issue_date = date_match.group(0) if date_match else created.strftime('%Y-%m-%d')

        # Parse the issue body for changed pages
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

    # Split on "####" headers (each changed state)
    sections = re.split(r'####\s+', body)

    for section in sections[1:]:  # skip preamble
        lines = section.strip().split('\n')
        if not lines:
            continue

        state_name = lines[0].strip()

        # Extract URL
        url = ''
        for line in lines:
            if line.startswith('URL:'):
                url = line.replace('URL:', '').strip()
                break

        # Extract diff block
        diff = ''
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

SYSTEM_PROMPT = """You are an expert analyst writing a weekly newsletter about the Rural Health Transformation Program (RHTP) — a $50 billion CMS initiative funding all 50 US states to transform rural healthcare.

Your audience is paid subscribers who are healthcare executives, state officials, consultants, and technology vendors interested in rural health spending.

Your newsletter should:
- Lead with the most significant developments (new awards, large RFPs, program launches)
- Focus on SPENDING MOVEMENT: new RFPs released, awards announced, funding allocated, contracts signed
- Highlight TECHNOLOGY aspects: what tech is being deployed, digital health, telehealth, EHR, broadband, data platforms
- Organize by theme (not just state-by-state) when possible — group related developments
- Be concise but substantive — each item should tell the reader WHY it matters
- Use a professional, authoritative tone
- Include specific dollar amounts, dates, and state names
- End with a brief "What to Watch" section for upcoming developments

Format the output as clean HTML suitable for Substack, using:
- <h1> for the newsletter title
- <h2> for section headers
- <h3> for subsections
- <p> for paragraphs
- <ul>/<li> for lists
- <strong> and <em> for emphasis
- <a href="..."> for links to state pages
- <hr> for section breaks

Do NOT include <html>, <head>, or <body> tags — just the content HTML.
If there are no meaningful changes to report, still produce a brief newsletter noting that no significant movement was detected and point to upcoming items to watch."""

def generate_newsletter(changes: List[Dict], topics: List[Dict],
                        api_key: str) -> str:
    """Use Claude API to generate the newsletter from changes and topics."""

    # Build the prompt with this week's data
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
                user_content += f"URL: {c['url']}\n"
                user_content += f"Date detected: {c['date']}\n"
                user_content += f"Changes:\n{c['diff']}\n\n"
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

    user_content += "Please write the newsletter now. Focus on spending movement and technology."

    client = anthropic.Anthropic(api_key=api_key)

    logger.info("Calling Claude API to generate newsletter...")
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

    # 2. Fetch topics from monday.com for context
    topics = fetch_topics(monday_token, topics_board_id)

    # 3. Generate newsletter via Claude API
    newsletter_html = generate_newsletter(changes, topics, anthropic_key)

    # 4. Save HTML draft
    output_path = 'newsletter-draft.html'
    with open(output_path, 'w') as f:
        f.write(newsletter_html)
    logger.info(f"Saved newsletter draft to {output_path}")

    # 5. Print for logs
    print("\n" + "=" * 60)
    print("NEWSLETTER DRAFT")
    print("=" * 60)
    print(newsletter_html)

    # 6. GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write("# Weekly RHT Newsletter Draft\n\n")
            f.write(newsletter_html)

    # 7. Save metadata
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
