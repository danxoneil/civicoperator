#!/usr/bin/env python3
"""
USASpending Award Monitor — tracks RHTP federal award data for all 50 states.

Queries the USASpending.gov API for award amounts, outlays, and modifications,
compares with the previous snapshot to detect changes, and updates the
monday.com board with latest values.  Sends an email summary every run.

Every run logs all board columns (with IDs and types) for easy configuration.

Required env vars:
  MONDAY_API_TOKEN
  MONDAY_SPENDING_BOARD_ID         — board ID for the spending board
                                     (separate from URL monitor board)

Email (uses same SMTP secrets as URL monitor):
  NOTIFICATION_EMAIL / SMTP_SERVER / SMTP_PORT / SMTP_USER / SMTP_PASSWORD

Optional column mapping (column title or ID — defaults shown):
  SPENDING_AWARD_ID_COLUMN         — "Award ID"
  SPENDING_OBLIGATION_COLUMN       — "Total Obligation"
  SPENDING_OUTLAYS_COLUMN          — "Total Outlays"
  SPENDING_LAST_MODIFIED_COLUMN    — "USASpending Last Modified"

Snapshots file:
  SPENDING_SNAPSHOTS_FILE          — "spending_snapshots.json"
"""

import json
import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Tuple

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spending-monitor.log'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── RHTP Award ID → State mapping ────────────────────────────────────

AWARD_MAP = {
    "RHTCMS332041": "Michigan",
    "RHTCMS332042": "North Carolina",
    "RHTCMS332043": "North Dakota",
    "RHTCMS332044": "Washington",
    "RHTCMS332045": "Rhode Island",
    "RHTCMS332046": "Georgia",
    "RHTCMS332047": "Vermont",
    "RHTCMS332048": "Oklahoma",
    "RHTCMS332049": "New York",
    "RHTCMS332050": "New Hampshire",
    "RHTCMS332051": "Utah",
    "RHTCMS332052": "Pennsylvania",
    "RHTCMS332053": "Delaware",
    "RHTCMS332054": "West Virginia",
    "RHTCMS332055": "Illinois",
    "RHTCMS332056": "South Carolina",
    "RHTCMS332057": "Tennessee",
    "RHTCMS332058": "Montana",
    "RHTCMS332059": "Arizona",
    "RHTCMS332060": "Alabama",
    "RHTCMS332061": "Arkansas",
    "RHTCMS332062": "Alaska",
    "RHTCMS332063": "Mississippi",
    "RHTCMS332064": "Hawaii",
    "RHTCMS332065": "Iowa",
    "RHTCMS332066": "Maryland",
    "RHTCMS332067": "Florida",
    "RHTCMS332068": "Texas",
    "RHTCMS332069": "Massachusetts",
    "RHTCMS332070": "Indiana",
    "RHTCMS332071": "Oregon",
    "RHTCMS332072": "Kansas",
    "RHTCMS332073": "Connecticut",
    "RHTCMS332074": "Nevada",
    "RHTCMS332075": "Maine",
    "RHTCMS332076": "Wisconsin",
    "RHTCMS332077": "Minnesota",
    "RHTCMS332078": "California",
    "RHTCMS332079": "Kentucky",
    "RHTCMS332080": "South Dakota",
    "RHTCMS332081": "Colorado",
    "RHTCMS332082": "Wyoming",
    "RHTCMS332083": "New Mexico",
    "RHTCMS332084": "Idaho",
    "RHTCMS332085": "Louisiana",
    "RHTCMS332086": "Nebraska",
    "RHTCMS332087": "Ohio",
    "RHTCMS332088": "Virginia",
    "RHTCMS332089": "New Jersey",
    "RHTCMS332090": "Missouri",
}

STATE_TO_FAIN = {v: k for k, v in AWARD_MAP.items()}

# Fields we request from the spending_by_award search
USASPENDING_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Start Date",
    "End Date",
    "Award Amount",
    "Total Outlays",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Award Type",
    "Description",
    "Last Modified Date",
    "CFDA Number",
]

USASPENDING_API = "https://api.usaspending.gov/api/v2"


class SpendingMonitor:
    def __init__(self):
        self.monday_token = os.getenv('MONDAY_API_TOKEN', '')
        self.monday_board_id = os.getenv('MONDAY_SPENDING_BOARD_ID', '')
        self.snapshots_file = os.getenv(
            'SPENDING_SNAPSHOTS_FILE', 'spending_snapshots.json',
        )

        # Drive upload config
        self.drive_folder_id = os.getenv('GOOGLE_DRIVE_SPENDING_FOLDER_ID', '')
        self.drive_creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')
        self.drive_oauth_token = os.getenv('GOOGLE_OAUTH_REFRESH_TOKEN', '')
        self.drive_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        self.drive_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')

        # Email config (reuses same SMTP secrets as URL monitor)
        self.notification_email = os.getenv('NOTIFICATION_EMAIL', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Column mapping: env var → default column title
        self.col_map = {
            'award_id': os.getenv('SPENDING_AWARD_ID_COLUMN', 'Award ID'),
            'obligation': os.getenv('SPENDING_OBLIGATION_COLUMN', 'Total Obligation'),
            'outlays': os.getenv('SPENDING_OUTLAYS_COLUMN', 'Total Outlays'),
            'last_modified': os.getenv(
                'SPENDING_LAST_MODIFIED_COLUMN', 'USASpending Last Modified',
            ),
        }

        # Resolved at runtime: column title/id → monday column id
        self._resolved_cols: Dict[str, Optional[str]] = {}
        # monday.com item name → item id
        self._item_ids: Dict[str, str] = {}
        # Column type lookup
        self._col_types: Dict[str, str] = {}

    # ── USASpending API ──────────────────────────────────────────────

    def fetch_awards_from_usaspending(self) -> Dict[str, Dict]:
        """Fetch all 50 RHTP awards from USASpending.gov.

        Returns dict keyed by FAIN with award data as values.
        """
        all_fains = list(AWARD_MAP.keys())
        awards = {}

        # Query in batches of 50 (one batch should cover all)
        logger.info(f"Querying USASpending for {len(all_fains)} RHTP awards...")

        payload = {
            "subawards": False,
            "limit": 100,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc",
            "filters": {
                "award_type_codes": ["02", "03", "04", "05"],
                "award_ids": all_fains,
            },
            "fields": USASPENDING_FIELDS,
        }

        try:
            resp = requests.post(
                f"{USASPENDING_API}/search/spending_by_award/",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

            results = data.get('results', [])
            logger.info(f"  Got {len(results)} results from spending_by_award")

            for r in results:
                fain = r.get('Award ID', '')
                if fain in AWARD_MAP:
                    awards[fain] = r
                    logger.info(
                        f"  {AWARD_MAP[fain]}: "
                        f"${r.get('Award Amount', 0):,.2f} obligated, "
                        f"${r.get('Total Outlays', 0):,.2f} outlayed"
                    )

            # Check for pagination
            total = data.get('page_metadata', {}).get('total', 0)
            if total > len(results):
                logger.info(f"  {total} total results, fetching remaining pages...")
                page = 2
                while len(awards) < total and page <= 10:
                    payload['page'] = page
                    resp = requests.post(
                        f"{USASPENDING_API}/search/spending_by_award/",
                        json=payload,
                        timeout=60,
                    )
                    resp.raise_for_status()
                    more = resp.json().get('results', [])
                    if not more:
                        break
                    for r in more:
                        fain = r.get('Award ID', '')
                        if fain in AWARD_MAP:
                            awards[fain] = r
                    page += 1
                    time.sleep(0.5)

        except requests.RequestException as e:
            logger.error(f"USASpending API error: {e}")

        # If award_ids search returned nothing, try by CFDA program number
        if not awards:
            logger.info("  No results by award_ids, trying CFDA 93.798...")
            awards = self._fetch_by_cfda()

        # Report missing awards
        found = set(awards.keys())
        missing = set(all_fains) - found
        if missing:
            logger.warning(
                f"  {len(missing)} awards not found on USASpending: "
                f"{', '.join(AWARD_MAP[f] for f in sorted(missing))}"
            )

        logger.info(f"Fetched {len(awards)}/50 awards from USASpending")
        return awards

    def _fetch_by_cfda(self) -> Dict[str, Dict]:
        """Fallback: search by CFDA program number 93.798."""
        awards = {}
        payload = {
            "subawards": False,
            "limit": 100,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc",
            "filters": {
                "award_type_codes": ["02", "03", "04", "05"],
                "program_numbers": ["93.798"],
            },
            "fields": USASPENDING_FIELDS,
        }

        try:
            resp = requests.post(
                f"{USASPENDING_API}/search/spending_by_award/",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            results = resp.json().get('results', [])
            logger.info(f"  CFDA search returned {len(results)} results")

            for r in results:
                fain = r.get('Award ID', '')
                if fain in AWARD_MAP:
                    awards[fain] = r

        except requests.RequestException as e:
            logger.error(f"  CFDA search failed: {e}")

        return awards

    # ── monday.com board ─────────────────────────────────────────────

    def fetch_board_data(self) -> Tuple[List[Dict], Dict[str, Dict]]:
        """Fetch all items and columns from monday.com board.

        Returns (items, columns_metadata).
        Logs every column for discovery/configuration.
        """
        if not self.monday_token or not self.monday_board_id:
            logger.error("MONDAY_API_TOKEN and MONDAY_BOARD_ID are required")
            return [], {}

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
                id
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
                logger.error(f"monday.com errors: {data['errors']}")
                return [], {}

            board = data['data']['boards'][0]
            columns = board.get('columns', [])
            items = board['items_page']['items']

            # Log all columns for discovery
            logger.info("=" * 60)
            logger.info("MONDAY.COM BOARD COLUMNS (for column mapping):")
            logger.info("=" * 60)
            for c in columns:
                logger.info(f"  {c['title']:40s} id={c['id']:25s} type={c['type']}")
            logger.info("=" * 60)

            # Build lookups
            col_id_to_title = {c['id']: c['title'] for c in columns}
            col_title_to_id = {c['title']: c['id'] for c in columns}
            self._col_types = {c['id']: c['type'] for c in columns}

            # Resolve configured columns
            for key, name_or_id in self.col_map.items():
                if name_or_id in col_id_to_title:
                    self._resolved_cols[key] = name_or_id
                    logger.info(f"  Column '{key}' → id={name_or_id} ({col_id_to_title[name_or_id]})")
                elif name_or_id in col_title_to_id:
                    self._resolved_cols[key] = col_title_to_id[name_or_id]
                    logger.info(f"  Column '{key}' → '{name_or_id}' (id={col_title_to_id[name_or_id]})")
                else:
                    self._resolved_cols[key] = None
                    logger.warning(
                        f"  Column '{key}' = '{name_or_id}' NOT FOUND on board. "
                        f"Set SPENDING_{key.upper()}_COLUMN env var to a valid column title or ID."
                    )

            # Build item name → item id mapping
            for item in items:
                self._item_ids[item['name']] = item['id']

            logger.info(f"Found {len(items)} items on board")
            return items, {c['id']: c for c in columns}

        except Exception as e:
            logger.error(f"Failed to fetch monday.com board: {e}")
            return [], {}

    def update_monday_item(self, state: str, updates: Dict[str, Any]) -> bool:
        """Update column values for a state's row on monday.com.

        Args:
            state: State name (must match item name on board).
            updates: Dict of {resolved_col_key: value} to set.
        """
        item_id = self._item_ids.get(state)
        if not item_id:
            logger.warning(f"  No board item found for '{state}'")
            return False

        # Build column_values JSON for monday.com
        column_values = {}
        for key, value in updates.items():
            col_id = self._resolved_cols.get(key)
            if not col_id:
                continue

            col_type = self._col_types.get(col_id, '')

            if col_type == 'numeric':
                # Numbers columns expect string of the number
                column_values[col_id] = str(value) if value is not None else ''
            elif col_type == 'date':
                # Date columns expect {"date": "YYYY-MM-DD"}
                if value:
                    column_values[col_id] = json.dumps({"date": str(value)[:10]})
                else:
                    column_values[col_id] = ''
            else:
                # Text and other columns: plain string
                column_values[col_id] = str(value) if value is not None else ''

        if not column_values:
            return False

        mutation = """
        mutation ($boardId: ID!, $itemId: ID!, $columnValues: JSON!) {
          change_multiple_column_values(
            board_id: $boardId,
            item_id: $itemId,
            column_values: $columnValues
          ) {
            id
          }
        }
        """
        variables = {
            'boardId': self.monday_board_id,
            'itemId': item_id,
            'columnValues': json.dumps(column_values),
        }

        try:
            resp = requests.post(
                'https://api.monday.com/v2',
                json={'query': mutation, 'variables': variables},
                headers={
                    'Authorization': self.monday_token,
                    'Content-Type': 'application/json',
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if 'errors' in data:
                logger.warning(f"  monday.com update error for {state}: {data['errors']}")
                return False

            return True

        except Exception as e:
            logger.warning(f"  Failed to update {state}: {e}")
            return False

    # ── Snapshots ────────────────────────────────────────────────────

    def load_snapshots(self) -> Dict:
        """Load previous spending snapshots."""
        if os.path.exists(self.snapshots_file):
            with open(self.snapshots_file) as f:
                return json.load(f)
        return {}

    def save_snapshots(self, snapshots: Dict):
        """Save current spending snapshots."""
        with open(self.snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2, default=str)

    def detect_changes(
        self, previous: Dict, current: Dict,
    ) -> Dict[str, List[Dict]]:
        """Compare previous and current snapshots to find changes.

        Returns dict with 'changed', 'new', 'unchanged' lists.
        """
        changes = {'changed': [], 'new': [], 'unchanged': []}

        for fain, new_data in current.items():
            state = AWARD_MAP.get(fain, fain)
            old_data = previous.get(fain)

            if not old_data:
                changes['new'].append({
                    'state': state,
                    'fain': fain,
                    'data': new_data,
                })
                continue

            # Compare key financial fields
            diffs = []
            for field in ['Award Amount', 'Total Outlays', 'Recipient Name',
                          'Start Date', 'End Date', 'Description']:
                old_val = old_data.get(field)
                new_val = new_data.get(field)
                if old_val != new_val:
                    diffs.append({
                        'field': field,
                        'old': old_val,
                        'new': new_val,
                    })

            if diffs:
                changes['changed'].append({
                    'state': state,
                    'fain': fain,
                    'diffs': diffs,
                    'data': new_data,
                })
            else:
                changes['unchanged'].append({
                    'state': state,
                    'fain': fain,
                })

        return changes

    # ── Main ─────────────────────────────────────────────────────────

    def run(self):
        """Main execution: fetch data, detect changes, update board."""
        run_date = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Spending Monitor run — {run_date}")
        logger.info(f"Tracking {len(AWARD_MAP)} RHTP awards")

        # 1. Fetch board data (also logs columns for discovery)
        items, columns = self.fetch_board_data()

        # 2. Fetch awards from USASpending
        api_data = self.fetch_awards_from_usaspending()

        if not api_data:
            logger.warning("No award data returned from USASpending API")
            self._write_results({
                'run_date': run_date,
                'awards_found': 0,
                'changed': [],
                'new': [],
                'unchanged': [],
                'errors': ['No data returned from USASpending API'],
            })
            return

        # 3. Load previous snapshots and detect changes
        previous = self.load_snapshots()
        changes = self.detect_changes(previous, api_data)

        logger.info(
            f"Changes: {len(changes['changed'])} changed, "
            f"{len(changes['new'])} new, "
            f"{len(changes['unchanged'])} unchanged"
        )

        # 4. Log all changes in detail
        for item in changes['changed']:
            logger.info(f"  CHANGED: {item['state']} ({item['fain']})")
            for d in item['diffs']:
                logger.info(f"    {d['field']}: {d['old']} → {d['new']}")

        for item in changes['new']:
            logger.info(
                f"  NEW: {item['state']} ({item['fain']}) — "
                f"${item['data'].get('Award Amount', 0):,.2f}"
            )

        # 5. Update monday.com board
        updated_count = 0
        if items:
            update_items = changes['changed'] + changes['new']
            for item in update_items:
                state = item['state']
                data = item['data']
                updates = {
                    'award_id': item['fain'],
                    'obligation': data.get('Award Amount'),
                    'outlays': data.get('Total Outlays'),
                    'last_modified': data.get('Last Modified Date'),
                }
                if self.update_monday_item(state, updates):
                    updated_count += 1
                    logger.info(f"  Updated board: {state}")
                time.sleep(0.3)  # Rate limit

        logger.info(f"Updated {updated_count} items on monday.com")

        # 6. Save new snapshots
        self.save_snapshots(api_data)
        logger.info(f"Saved snapshots to {self.snapshots_file}")

        # 7. Write results JSON
        results = {
            'run_date': run_date,
            'awards_found': len(api_data),
            'changed': [
                {
                    'state': c['state'],
                    'fain': c['fain'],
                    'diffs': c['diffs'],
                    'award_amount': c['data'].get('Award Amount'),
                    'total_outlays': c['data'].get('Total Outlays'),
                }
                for c in changes['changed']
            ],
            'new': [
                {
                    'state': c['state'],
                    'fain': c['fain'],
                    'award_amount': c['data'].get('Award Amount'),
                    'total_outlays': c['data'].get('Total Outlays'),
                    'recipient': c['data'].get('Recipient Name'),
                }
                for c in changes['new']
            ],
            'unchanged': [c['state'] for c in changes['unchanged']],
        }
        self._write_results(results)

        # 8. Upload results to Google Drive
        if self.drive_folder_id and (self.drive_creds or self.drive_oauth_token):
            try:
                from drive_upload import upload_screenshots_to_drive, create_or_get_subfolder, _get_drive_service
                service, auth_type = _get_drive_service(
                    credentials_json=self.drive_creds,
                    refresh_token=self.drive_oauth_token,
                    client_id=self.drive_client_id,
                    client_secret=self.drive_client_secret,
                )
                subfolder = f"Run {run_date}"
                subfolder_id = create_or_get_subfolder(
                    service, self.drive_folder_id, subfolder,
                )
                # Upload results JSON and snapshots
                from googleapiclient.http import MediaFileUpload
                for filepath in ['spending-monitor-results.json', self.snapshots_file]:
                    if os.path.exists(filepath):
                        meta = {'name': os.path.basename(filepath), 'parents': [subfolder_id]}
                        media = MediaFileUpload(filepath, mimetype='application/json')
                        service.files().create(
                            body=meta, media_body=media, supportsAllDrives=True,
                        ).execute()
                        logger.info(f"  Uploaded to Drive: {filepath}")
            except Exception as e:
                logger.warning(f"Drive upload failed: {e}")

        # 9. Print summary
        print(f"\n{'='*60}")
        print(f"RHTP SPENDING MONITOR — {run_date}")
        print(f"{'='*60}")
        print(f"Awards found on USASpending: {len(api_data)}/50")
        print(f"Changed: {len(changes['changed'])}")
        print(f"New: {len(changes['new'])}")
        print(f"Unchanged: {len(changes['unchanged'])}")
        print(f"Board items updated: {updated_count}")

        if changes['changed']:
            print(f"\nChanges detected:")
            for c in changes['changed']:
                print(f"  {c['state']}:")
                for d in c['diffs']:
                    old = f"${d['old']:,.2f}" if isinstance(d['old'], (int, float)) else d['old']
                    new = f"${d['new']:,.2f}" if isinstance(d['new'], (int, float)) else d['new']
                    print(f"    {d['field']}: {old} → {new}")

        print(f"{'='*60}\n")

        # 9. Send email notification
        self.send_email(changes, api_data, run_date)

    # ── Email ──────────────────────────────────────────────────────

    def send_email(self, changes: Dict[str, List], api_data: Dict, run_date: str):
        """Send email summary of spending monitor run."""
        if not all([self.smtp_user, self.smtp_password, self.notification_email]):
            logger.info("Email config incomplete — skipping notification")
            return

        n_changed = len(changes['changed'])
        n_new = len(changes['new'])
        n_unchanged = len(changes['unchanged'])

        if n_changed or n_new:
            subject = f"RHTP Outlay Monitor: {n_changed} changed, {n_new} new ({run_date})"
        else:
            subject = f"RHTP Outlay Monitor: no changes ({run_date})"

        body = self._format_email(changes, api_data, run_date)

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

            logger.info(f"Sent email to {self.notification_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def _format_email(
        self, changes: Dict[str, List], api_data: Dict, run_date: str,
    ) -> str:
        """Format plain-text email body."""
        parts = [
            f"RHTP Outlay Monitor — {run_date}",
            f"Awards found on USASpending: {len(api_data)}/50",
            f"Changed: {len(changes['changed'])}  |  "
            f"New: {len(changes['new'])}  |  "
            f"Unchanged: {len(changes['unchanged'])}",
            "",
        ]

        if changes['changed']:
            parts.append("=" * 60)
            parts.append(f"OUTLAY CHANGES ({len(changes['changed'])} awards)")
            parts.append("=" * 60)
            for item in changes['changed']:
                parts.append(f"\n  {item['state']} ({item['fain']})")
                for d in item['diffs']:
                    old = f"${d['old']:,.2f}" if isinstance(d['old'], (int, float)) else d['old']
                    new = f"${d['new']:,.2f}" if isinstance(d['new'], (int, float)) else d['new']
                    parts.append(f"    {d['field']}: {old} → {new}")
            parts.append("")

        if changes['new']:
            parts.append("=" * 60)
            parts.append(f"NEW OUTLAYS ({len(changes['new'])} states)")
            parts.append("=" * 60)
            for item in changes['new']:
                amt = item['data'].get('Award Amount', 0)
                outlays = item['data'].get('Total Outlays', 0)
                recipient = item['data'].get('Recipient Name', 'Unknown')
                parts.append(
                    f"  {item['state']} ({item['fain']}): "
                    f"${outlays:,.2f} outlayed (${amt:,.2f} obligated)"
                )
                parts.append(f"    Recipient: {recipient}")
            parts.append("")

        if not changes['changed'] and not changes['new']:
            parts.append("No changes detected. All tracked awards are unchanged.")
            parts.append("")

        parts.append("Review your monday.com board for full details.")
        return "\n".join(parts)

    def _write_results(self, results: Dict):
        """Write results JSON for GitHub Actions."""
        with open('spending-monitor-results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)


def main():
    monitor = SpendingMonitor()
    monitor.run()


if __name__ == '__main__':
    main()
