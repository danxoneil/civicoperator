#!/usr/bin/env python3
"""
Mass Texting System via monday.com and Twilio
==============================================

This script fetches contact lists from monday.com boards and sends
mass text messages via Twilio SMS API.

Features:
- Fetch contacts from monday.com boards
- Send personalized SMS messages via Twilio
- Support for message templating with placeholders
- Rate limiting to respect Twilio limits
- Dry-run mode for testing
- Detailed logging and error handling
- Status tracking in monday.com
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mass_texter.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MondayClient:
    """Client for interacting with monday.com API."""

    def __init__(self, api_key: str, api_version: str = "2024-01"):
        self.api_key = api_key
        self.api_version = api_version
        self.api_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": api_key,
            "API-Version": api_version,
            "Content-Type": "application/json"
        }

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query against monday.com API."""
        data = {"query": query}
        if variables:
            data["variables"] = variables

        try:
            response = requests.post(
                self.api_url,
                json=data,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if "errors" in result:
                logger.error(f"monday.com API errors: {result['errors']}")
                raise Exception(f"monday.com API error: {result['errors']}")

            return result.get("data", {})
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query monday.com API: {e}")
            raise

    def get_board_items(self, board_id: str, limit: int = 500) -> List[Dict]:
        """Fetch all items from a monday.com board."""
        query = """
        query ($boardId: [ID!], $limit: Int) {
            boards(ids: $boardId) {
                items_page(limit: $limit) {
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                            type
                        }
                    }
                }
            }
        }
        """
        variables = {"boardId": [board_id], "limit": limit}

        data = self.execute_query(query, variables)
        boards = data.get("boards", [])

        if not boards:
            logger.warning(f"No board found with ID: {board_id}")
            return []

        items = boards[0].get("items_page", {}).get("items", [])
        logger.info(f"Fetched {len(items)} items from board {board_id}")
        return items

    def update_item_column(self, board_id: str, item_id: str, column_id: str, value: str):
        """Update a column value for a specific item."""
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
        variables = {
            "boardId": board_id,
            "itemId": item_id,
            "columnId": column_id,
            "value": json.dumps(value)
        }

        try:
            self.execute_query(query, variables)
            logger.info(f"Updated item {item_id} column {column_id}")
        except Exception as e:
            logger.error(f"Failed to update item {item_id}: {e}")


class TwilioClient:
    """Client for sending SMS messages via Twilio."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    def send_sms(self, to_number: str, message: str) -> Dict:
        """Send an SMS message via Twilio."""
        data = {
            "From": self.from_number,
            "To": to_number,
            "Body": message
        }

        try:
            response = requests.post(
                self.api_url,
                data=data,
                auth=(self.account_sid, self.auth_token),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"SMS sent to {to_number} - SID: {result.get('sid')}")
            return {
                "success": True,
                "sid": result.get("sid"),
                "status": result.get("status"),
                "error": None
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get("message", error_message)
                except:
                    pass

            return {
                "success": False,
                "sid": None,
                "status": "failed",
                "error": error_message
            }


class MassTexter:
    """Main class for mass texting operations."""

    def __init__(self):
        # monday.com configuration
        self.monday_api_key = os.getenv("MONDAY_API_KEY")
        self.monday_board_id = os.getenv("MONDAY_BOARD_ID")

        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")

        # Column configuration
        self.phone_column_id = os.getenv("MONDAY_PHONE_COLUMN_ID", "phone")
        self.status_column_id = os.getenv("MONDAY_STATUS_COLUMN_ID", "status")
        self.opt_in_column_id = os.getenv("MONDAY_OPT_IN_COLUMN_ID", "opt_in")

        # Message configuration
        self.message_template = os.getenv("MESSAGE_TEMPLATE", "")

        # Operation configuration
        self.dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        self.rate_limit_delay = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
        self.update_monday_status = os.getenv("UPDATE_MONDAY_STATUS", "true").lower() == "true"

        # Validate configuration
        self._validate_config()

        # Initialize clients
        self.monday_client = MondayClient(self.monday_api_key)
        self.twilio_client = TwilioClient(
            self.twilio_account_sid,
            self.twilio_auth_token,
            self.twilio_from_number
        )

        # Statistics
        self.stats = {
            "total_contacts": 0,
            "opted_in": 0,
            "messages_sent": 0,
            "messages_failed": 0,
            "skipped": 0
        }

    def _validate_config(self):
        """Validate required configuration variables."""
        required_vars = [
            "MONDAY_API_KEY",
            "MONDAY_BOARD_ID",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_FROM_NUMBER",
            "MESSAGE_TEMPLATE"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not self.message_template:
            logger.error("MESSAGE_TEMPLATE cannot be empty")
            raise ValueError("MESSAGE_TEMPLATE cannot be empty")

        logger.info("Configuration validated successfully")

    def _get_column_value(self, item: Dict, column_id: str) -> Optional[str]:
        """Extract column value from a monday.com item."""
        for col in item.get("column_values", []):
            if col["id"] == column_id:
                return col.get("text", "").strip()
        return None

    def _format_phone_number(self, phone: str) -> Optional[str]:
        """Format and validate phone number."""
        if not phone:
            return None

        # Remove common formatting characters
        phone = phone.replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace(".", "")

        # Add +1 for US numbers if not present
        if not phone.startswith("+"):
            if len(phone) == 10:
                phone = f"+1{phone}"
            elif len(phone) == 11 and phone.startswith("1"):
                phone = f"+{phone}"
            else:
                phone = f"+{phone}"

        # Basic validation
        if len(phone) < 10:
            return None

        return phone

    def _personalize_message(self, template: str, item: Dict) -> str:
        """Replace placeholders in message template with item data."""
        message = template

        # Replace {name} with item name
        message = message.replace("{name}", item.get("name", ""))

        # Replace other column placeholders like {column_id}
        for col in item.get("column_values", []):
            placeholder = f"{{{col['id']}}}"
            value = col.get("text", "")
            message = message.replace(placeholder, value)

        return message

    def _check_opt_in(self, item: Dict) -> bool:
        """Check if contact has opted in to receive messages."""
        opt_in_value = self._get_column_value(item, self.opt_in_column_id)

        # If no opt-in column is configured, assume opted in
        if not opt_in_value:
            return True

        # Check for various "yes" values
        opt_in_value = opt_in_value.lower()
        return opt_in_value in ["yes", "true", "1", "opted in", "subscribed", "✓", "checked"]

    def send_mass_texts(self):
        """Main method to send mass texts."""
        logger.info("=" * 60)
        logger.info("Starting Mass Texting Campaign")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        logger.info(f"Board ID: {self.monday_board_id}")
        logger.info("=" * 60)

        # Fetch contacts from monday.com
        logger.info("Fetching contacts from monday.com...")
        items = self.monday_client.get_board_items(self.monday_board_id)
        self.stats["total_contacts"] = len(items)

        if not items:
            logger.warning("No contacts found in board")
            return

        # Process each contact
        results = []
        for idx, item in enumerate(items, 1):
            item_id = item["id"]
            item_name = item["name"]

            logger.info(f"\n[{idx}/{len(items)}] Processing: {item_name} (ID: {item_id})")

            # Check opt-in status
            if not self._check_opt_in(item):
                logger.info(f"  ⊘ Skipped - Not opted in")
                self.stats["skipped"] += 1
                results.append({
                    "item_id": item_id,
                    "name": item_name,
                    "status": "skipped",
                    "reason": "not_opted_in"
                })
                continue

            self.stats["opted_in"] += 1

            # Get phone number
            phone = self._get_column_value(item, self.phone_column_id)
            if not phone:
                logger.warning(f"  ⊘ Skipped - No phone number")
                self.stats["skipped"] += 1
                results.append({
                    "item_id": item_id,
                    "name": item_name,
                    "status": "skipped",
                    "reason": "no_phone"
                })
                continue

            # Format phone number
            formatted_phone = self._format_phone_number(phone)
            if not formatted_phone:
                logger.warning(f"  ⊘ Skipped - Invalid phone: {phone}")
                self.stats["skipped"] += 1
                results.append({
                    "item_id": item_id,
                    "name": item_name,
                    "status": "skipped",
                    "reason": "invalid_phone",
                    "phone": phone
                })
                continue

            # Personalize message
            message = self._personalize_message(self.message_template, item)
            logger.info(f"  → To: {formatted_phone}")
            logger.info(f"  → Message: {message[:50]}..." if len(message) > 50 else f"  → Message: {message}")

            # Send SMS (or simulate if dry run)
            if self.dry_run:
                logger.info(f"  ✓ [DRY RUN] Would send SMS")
                result = {
                    "success": True,
                    "sid": "DRY_RUN_SID",
                    "status": "dry_run",
                    "error": None
                }
            else:
                result = self.twilio_client.send_sms(formatted_phone, message)

            # Update statistics
            if result["success"]:
                self.stats["messages_sent"] += 1
                logger.info(f"  ✓ Sent successfully - SID: {result['sid']}")
            else:
                self.stats["messages_failed"] += 1
                logger.error(f"  ✗ Failed - {result['error']}")

            # Update monday.com status
            if self.update_monday_status and not self.dry_run:
                status_text = "Sent" if result["success"] else "Failed"
                try:
                    self.monday_client.update_item_column(
                        self.monday_board_id,
                        item_id,
                        self.status_column_id,
                        status_text
                    )
                except Exception as e:
                    logger.error(f"  ⚠ Failed to update status in monday.com: {e}")

            # Store result
            results.append({
                "item_id": item_id,
                "name": item_name,
                "phone": formatted_phone,
                "status": "sent" if result["success"] else "failed",
                "sid": result.get("sid"),
                "error": result.get("error")
            })

            # Rate limiting
            if not self.dry_run:
                time.sleep(self.rate_limit_delay)

        # Save results
        self._save_results(results)

        # Print summary
        self._print_summary()

    def _save_results(self, results: List[Dict]):
        """Save campaign results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"campaign_results_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "board_id": self.monday_board_id,
            "dry_run": self.dry_run,
            "statistics": self.stats,
            "results": results
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"\n✓ Results saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    def _print_summary(self):
        """Print campaign summary statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("CAMPAIGN SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Contacts:     {self.stats['total_contacts']}")
        logger.info(f"Opted In:           {self.stats['opted_in']}")
        logger.info(f"Messages Sent:      {self.stats['messages_sent']}")
        logger.info(f"Messages Failed:    {self.stats['messages_failed']}")
        logger.info(f"Skipped:            {self.stats['skipped']}")

        if self.stats['opted_in'] > 0:
            success_rate = (self.stats['messages_sent'] / self.stats['opted_in']) * 100
            logger.info(f"Success Rate:       {success_rate:.1f}%")

        logger.info("=" * 60)


def main():
    """Main entry point."""
    try:
        texter = MassTexter()
        texter.send_mass_texts()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
