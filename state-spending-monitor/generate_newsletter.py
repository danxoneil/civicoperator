#!/usr/bin/env python3
"""
Weekly Newsletter Generator — collects URL monitor changes from the past week,
pulls topic context from monday.com, uses Claude API to write an analyst-quality
newsletter focused on RHT spending movement, and emails it to Substack.

Required environment variables:
  ANTHROPIC_API_KEY       — Claude API key
  SUBSTACK_EMAIL          — Substack email-to-publish address
  SMTP_USER / SMTP_PASSWORD / SMTP_SERVER / SMTP_PORT — email config

Optional:
  MONDAY_API_TOKEN        — for fetching Topics board context
  MONDAY_TOPICS_BOARD_ID  — monday.com Topics board ID
  GITHUB_TOKEN            — for fetching issues (auto-set in GitHub Actions)
  GITHUB_REPOSITORY       — owner/repo (auto-set in GitHub Actions)
  LOOKBACK_DAYS           — how many days back to look (default: 7)
"""

import json
import logging
import os
import re
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

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


# ── GitHub Issues ─────────────────────────────────────────────────────

def fetch_weekly_changes(github_token: str, repo: str, lookback_days: int = 7) -> List[Dict]:
    """Fetch URL monitor issues with page-changed label from the last N days."""
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()

    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    url = f'https://api.github.com/repos/{repo}/issues'
    params = {
        'labels': 'url-monitor,page-changed',
        'state': 'open',
        'since': since,
        'per_page': 50,
        'sort': 'created',
        'direction': 'desc',
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        issues = resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch GitHub issues: {e}")
        return []

    # Filter to only issues created within our lookback window
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    changes = []
    for issue in issues:
        created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
        if created < cutoff:
            continue
        changes.append({
            'title': issue['title'],
            'body': issue['body'],
            'date': created.strftime('%Y-%m-%d'),
            'url': issue['html_url'],
        })

    logger.info(f"Found {len(changes)} change issues from the last {lookback_days} days")
    return changes


# ── monday.com Topics Board ──────────────────────────────────────────

def fetch_topics(monday_token: str, board_id: str) -> List[Dict]:
    """Fetch items from the monday.com Topics board for newsletter context."""
    if not monday_token or not board_id:
        logger.info("No Topics board configured, skipping")
        return []

    query = """
    query ($boardId: [ID!]!) {
      boards(ids: $boardId) {
        columns { id title type }
        items_page(limit: 500) {
          items {
            name
            group { title }
            column_values { id text value }
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
                'Authorization': monday_token,
                'Content-Type': 'application/json',
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if 'errors' in data:
            logger.error(f"monday.com API errors: {data['errors']}")
            return []

        board = data['data']['boards'][0]
        columns = board.get('columns', [])
        items = board.get('items_page', {}).get('items', [])

        topics = []
        for item in items:
            topic = {
                'name': item['name'],
                'group': item.get('group', {}).get('title', ''),
                'columns': {},
            }
            for col in item.get('column_values', []):
                col_title = next(
                    (c['title'] for c in columns if c['id'] == col['id']), col['id']
                )
                text = col.get('text', '')
                if text:
                    topic['columns'][col_title] = text
            topics.append(topic)

        logger.info(f"Fetched {len(topics)} topics from monday.com board {board_id}")
        return topics

    except Exception as e:
        logger.error(f"Failed to fetch topics: {e}")
        return []


# ── Claude API ────────────────────────────────────────────────────────

def generate_newsletter_content(
    api_key: str,
    changes: List[Dict],
    topics: List[Dict],
    week_date: str,
) -> Optional[str]:
    """Use Claude API to generate newsletter HTML from change data."""

    # Build the change summaries
    change_text = ""
    for issue in changes:
        change_text += f"\n--- Issue: {issue['title']} ({issue['date']}) ---\n"
        change_text += issue['body'] + "\n"

    # Build topics context
    topics_text = ""
    if topics:
        topics_text = "\n\nREFERENCE — Active RHT Topics from tracking board:\n"
        for t in topics:
            group = f" [{t['group']}]" if t['group'] else ""
            topics_text += f"- {t['name']}{group}"
            for col_name, col_val in t['columns'].items():
                topics_text += f" | {col_name}: {col_val}"
            topics_text += "\n"

    prompt = f"""You are writing a weekly analyst newsletter about the Rural Health Transformation (RHT) Program —
a $50B federal program where CMS awards funds to all 50 US states for rural healthcare infrastructure.

Your audience is healthcare technology executives, policy analysts, and investors who pay for this newsletter.
They care about:
- NEW RFPs and procurement opportunities (especially technology-related)
- Award announcements and funding allocations
- State program milestones and implementation progress
- Technology infrastructure investments (EHR, telehealth, data systems, broadband)
- Shifts in state strategy or priorities

Below are the raw page changes detected on state RHTP websites this week, plus reference topics from our tracking board.

CHANGES DETECTED THIS WEEK:
{change_text}

{topics_text}

Write the newsletter as clean HTML suitable for Substack. Requirements:
- Lead with a 2-3 sentence executive summary of the most significant developments
- Organize by theme (e.g. "New RFPs", "Awards & Funding", "Program Updates", "Technology") rather than by state
- For each item, name the state, what changed, and why it matters for the audience
- If a change is just minor formatting/cosmetic, skip it or briefly note it under "Minor Updates"
- Keep the tone professional but accessible — like a Bloomberg or Axios briefing
- Use <h2> for section headers, <p> for paragraphs, <strong> for emphasis
- Do NOT include <html>, <head>, or <body> tags — just the inner content
- If there are no substantive spending/technology changes this week, say so directly
- End with a brief "What to Watch" section with 2-3 things to monitor next week
- Keep it concise — aim for 500-800 words total"""

    try:
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-sonnet-4-5-20250929',
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data['content'][0]['text']
        logger.info(f"Claude API generated {len(content)} chars of newsletter content")
        return content

    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        return None


# ── Email to Substack ─────────────────────────────────────────────────

def send_to_substack(
    html_content: str,
    subject: str,
    substack_email: str,
    smtp_user: str,
    smtp_password: str,
    smtp_server: str = 'smtp.gmail.com',
    smtp_port: int = 587,
):
    """Send the newsletter HTML to Substack's email-to-publish address."""
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_user
    msg['To'] = substack_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info(f"Newsletter sent to {substack_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


# ── Main ──────────────────────────────────────────────────────────────

def main():
    # Config
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    substack_email = os.getenv('SUBSTACK_EMAIL', '')
    github_token = os.getenv('GITHUB_TOKEN', '')
    repo = os.getenv('GITHUB_REPOSITORY', 'danxoneil/civicoperator')
    monday_token = os.getenv('MONDAY_API_TOKEN', '')
    topics_board_id = os.getenv('MONDAY_TOPICS_BOARD_ID', '')
    lookback_days = int(os.getenv('LOOKBACK_DAYS', '7'))

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')

    if not anthropic_key:
        logger.error("ANTHROPIC_API_KEY is required")
        sys.exit(1)

    # 1. Collect changes from GitHub issues
    logger.info(f"Fetching changes from last {lookback_days} days...")
    changes = fetch_weekly_changes(github_token, repo, lookback_days)

    if not changes:
        logger.info("No page changes detected this week — skipping newsletter")
        # Write step summary
        summary_file = os.getenv('GITHUB_STEP_SUMMARY')
        if summary_file:
            with open(summary_file, 'a') as f:
                f.write("# Weekly Newsletter\n\nNo page changes detected this week. Newsletter skipped.\n")
        return

    # 2. Fetch topics context from monday.com
    topics = fetch_topics(monday_token, topics_board_id)

    # 3. Generate newsletter via Claude API
    week_date = datetime.now().strftime('%B %d, %Y')
    logger.info("Generating newsletter via Claude API...")
    html_content = generate_newsletter_content(anthropic_key, changes, topics, week_date)

    if not html_content:
        logger.error("Failed to generate newsletter content")
        sys.exit(1)

    # 4. Save draft locally
    with open('newsletter-draft.html', 'w') as f:
        f.write(html_content)
    logger.info("Saved newsletter draft to newsletter-draft.html")

    # 5. Send to Substack
    subject = f"RHT Monitor: Week of {week_date}"

    if substack_email and smtp_user and smtp_password:
        send_to_substack(
            html_content, subject, substack_email,
            smtp_user, smtp_password, smtp_server, smtp_port,
        )
    else:
        logger.warning("Substack email or SMTP not configured — draft saved but not sent")

    # 6. GitHub Actions summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(f"# Weekly Newsletter — {week_date}\n\n")
            f.write(f"**Changes analyzed:** {len(changes)} issues\n")
            f.write(f"**Topics context:** {len(topics)} items\n")
            sent = "Yes" if (substack_email and smtp_user) else "No (draft only)"
            f.write(f"**Sent to Substack:** {sent}\n\n")
            f.write("## Newsletter Preview\n\n")
            f.write(html_content)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
