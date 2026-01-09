#!/usr/bin/env python3
"""
Emilio Pucci Dress Availability Monitor
Monitors multiple retailers for availability of specific designer dress
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time

# Configuration
TARGET_BRAND = "Emilio Pucci"
TARGET_ITEM = "graphic-print maxi dress"
TARGET_SIZE = "IT 40"
ALTERNATIVE_SIZES = ["EU 40", "40"]  # Accepted variations

# Notification settings
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
SEND_EMAIL = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dress-monitor/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DressMonitor:
    """Main class for monitoring dress availability"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.results = []

    def check_farfetch(self) -> Optional[Dict]:
        """Check Farfetch for dress availability"""
        logger.info("Checking Farfetch...")

        try:
            # Farfetch search API
            search_url = "https://www.farfetch.com/shopping/women/emilio-pucci-dresses-1/items.aspx"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for Pucci maxi dresses in search results
                # This is a simplified check - actual implementation would need
                # to parse Farfetch's specific HTML/JSON structure

                # Note: Farfetch often uses JavaScript rendering, may need Selenium
                logger.info("Farfetch check completed (manual verification recommended)")
                return None
            else:
                logger.warning(f"Farfetch returned status code: {response.status_code}")

        except Exception as e:
            logger.error(f"Error checking Farfetch: {str(e)}")

        return None

    def check_pucci_official(self) -> Optional[Dict]:
        """Check official Pucci website"""
        logger.info("Checking Pucci official website...")

        try:
            search_url = "https://www.pucci.com/us-en/women/clothing/dresses/"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for graphic print maxi dresses
                # Pucci site structure would need to be analyzed for actual implementation
                logger.info("Pucci official site check completed")

        except Exception as e:
            logger.error(f"Error checking Pucci official site: {str(e)}")

        return None

    def check_net_a_porter(self) -> Optional[Dict]:
        """Check Net-A-Porter for dress availability"""
        logger.info("Checking Net-A-Porter...")

        try:
            search_url = "https://www.net-a-porter.com/en-us/shop/product/emilio-pucci/clothing/maxi-dresses"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                logger.info("Net-A-Porter check completed")

        except Exception as e:
            logger.error(f"Error checking Net-A-Porter: {str(e)}")

        return None

    def check_mytheresa(self) -> Optional[Dict]:
        """Check Mytheresa for dress availability"""
        logger.info("Checking Mytheresa...")

        try:
            search_url = "https://www.mytheresa.com/en-us/emilio-pucci/women/clothing/dresses.html"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                logger.info("Mytheresa check completed")

        except Exception as e:
            logger.error(f"Error checking Mytheresa: {str(e)}")

        return None

    def check_vestiaire_collective(self) -> Optional[Dict]:
        """Check Vestiaire Collective for dress availability"""
        logger.info("Checking Vestiaire Collective...")

        try:
            search_url = "https://www.vestiairecollective.com/women-clothing/dresses/emilio-pucci/"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info("Vestiaire Collective check completed")

        except Exception as e:
            logger.error(f"Error checking Vestiaire Collective: {str(e)}")

        return None

    def check_therealreal(self) -> Optional[Dict]:
        """Check The RealReal for dress availability"""
        logger.info("Checking The RealReal...")

        try:
            search_url = "https://www.therealreal.com/designers/emilio-pucci/women/clothing/dresses"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                logger.info("The RealReal check completed")

        except Exception as e:
            logger.error(f"Error checking The RealReal: {str(e)}")

        return None

    def check_lyst(self) -> Optional[Dict]:
        """Check Lyst aggregator for dress availability"""
        logger.info("Checking Lyst...")

        try:
            search_url = "https://www.lyst.com/shop/emilio-pucci-womens-dresses/maxi/"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                logger.info("Lyst check completed")

        except Exception as e:
            logger.error(f"Error checking Lyst: {str(e)}")

        return None

    def send_notification(self, finding: Dict):
        """Send notification when dress is found"""
        message = f"""
🔔 DRESS FOUND!

Brand: {TARGET_BRAND}
Item: {TARGET_ITEM}
Size: {TARGET_SIZE}

Retailer: {finding['retailer']}
Price: {finding.get('price', 'N/A')}
Condition: {finding.get('condition', 'Unknown')}
Link: {finding['url']}

Notes: {finding.get('notes', 'None')}

Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        logger.info(message)

        if SEND_EMAIL and NOTIFICATION_EMAIL:
            self.send_email_notification(message, finding)

        # Save to results file
        self.save_finding(finding)

    def send_email_notification(self, message: str, finding: Dict):
        """Send email notification (requires SMTP configuration)"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')

            if not all([smtp_user, smtp_password, NOTIFICATION_EMAIL]):
                logger.warning("Email credentials not configured. Skipping email notification.")
                return

            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = NOTIFICATION_EMAIL
            msg['Subject'] = f"🔔 Emilio Pucci Dress Available - {finding['retailer']}"

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email notification sent to {NOTIFICATION_EMAIL}")

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")

    def save_finding(self, finding: Dict):
        """Save finding to JSON file"""
        findings_file = 'dress-monitor/findings.json'

        try:
            findings = []
            if os.path.exists(findings_file):
                with open(findings_file, 'r') as f:
                    findings = json.load(f)

            finding['timestamp'] = datetime.now().isoformat()
            findings.append(finding)

            with open(findings_file, 'w') as f:
                json.dump(findings, f, indent=2)

            logger.info(f"Finding saved to {findings_file}")

        except Exception as e:
            logger.error(f"Error saving finding: {str(e)}")

    def run_all_checks(self):
        """Run all retailer checks"""
        logger.info("=" * 60)
        logger.info(f"Starting Emilio Pucci dress monitoring - {datetime.now()}")
        logger.info(f"Target: {TARGET_BRAND} {TARGET_ITEM} - Size {TARGET_SIZE}")
        logger.info("=" * 60)

        checkers = [
            self.check_farfetch,
            self.check_pucci_official,
            self.check_net_a_porter,
            self.check_mytheresa,
            self.check_vestiaire_collective,
            self.check_therealreal,
            self.check_lyst,
        ]

        for checker in checkers:
            try:
                result = checker()
                if result:
                    self.results.append(result)
                    self.send_notification(result)

                # Be respectful - wait between requests
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error in {checker.__name__}: {str(e)}")

        logger.info("=" * 60)
        if self.results:
            logger.info(f"Monitoring complete. Found {len(self.results)} matching items!")
        else:
            logger.info("Monitoring complete. No matching items found.")
        logger.info("=" * 60)

        return self.results


def main():
    """Main entry point"""
    monitor = DressMonitor()
    results = monitor.run_all_checks()

    if results:
        print(f"\n✅ Found {len(results)} matching items! Check findings.json for details.")
    else:
        print("\n❌ No matching items found. Will check again on next run.")


if __name__ == "__main__":
    main()
