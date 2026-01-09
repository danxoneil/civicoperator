#!/usr/bin/env python3
"""
Enhanced Emilio Pucci Dress Availability Monitor
with improved scraping logic and API integrations
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
import re

# Configuration
TARGET_BRAND = "Emilio Pucci"
TARGET_ITEM = "graphic-print maxi dress"
TARGET_SIZE = "IT 40"
ALTERNATIVE_SIZES = ["EU 40", "40", "Italian 40"]

# Notification settings
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
SEND_EMAIL = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedDressMonitor:
    """Enhanced monitoring with better scraping capabilities"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.results = []
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def is_match(self, title: str, description: str = "") -> bool:
        """Check if item matches our criteria"""
        text = (title + " " + description).lower()

        # Must contain brand
        if "pucci" not in text and "emilio pucci" not in text:
            return False

        # Must be a dress
        if "dress" not in text:
            return False

        # Should be maxi or long
        if "maxi" not in text and "long" not in text:
            return False

        # Should mention print/pattern/graphic
        has_print = any(word in text for word in ["print", "graphic", "pattern", "printed"])

        return has_print

    def check_size_available(self, sizes: List[str]) -> bool:
        """Check if target size is in available sizes"""
        sizes_normalized = [s.upper().replace("SIZE", "").strip() for s in sizes]

        for target in [TARGET_SIZE] + ALTERNATIVE_SIZES:
            target_normalized = target.upper().replace("SIZE", "").strip()
            if any(target_normalized in size for size in sizes_normalized):
                return True

        return False

    def check_farfetch_api(self) -> List[Dict]:
        """Check Farfetch using their API/search"""
        logger.info("Checking Farfetch via API...")
        findings = []

        try:
            # Farfetch search endpoint (example - may need adjustment)
            search_url = "https://www.farfetch.com/shopping/women/emilio-pucci-dresses-1/items.aspx"

            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for product cards (adjust selectors based on actual HTML)
                products = soup.find_all('div', class_=re.compile('productCard|product-card', re.I))

                for product in products[:20]:  # Check first 20 results
                    try:
                        title_elem = product.find(['h2', 'h3', 'a'], class_=re.compile('title|name', re.I))
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)

                        if self.is_match(title):
                            link_elem = product.find('a', href=True)
                            product_url = link_elem['href'] if link_elem else None

                            if product_url and not product_url.startswith('http'):
                                product_url = f"https://www.farfetch.com{product_url}"

                            # Check product detail page for size
                            if product_url:
                                size_available = self.check_farfetch_product_page(product_url)

                                if size_available:
                                    price_elem = product.find(class_=re.compile('price', re.I))
                                    price = price_elem.get_text(strip=True) if price_elem else "N/A"

                                    findings.append({
                                        'retailer': 'Farfetch',
                                        'title': title,
                                        'url': product_url,
                                        'price': price,
                                        'condition': 'New',
                                        'size': TARGET_SIZE,
                                        'notes': 'Available now'
                                    })

                    except Exception as e:
                        logger.debug(f"Error parsing product: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error checking Farfetch: {str(e)}")

        return findings

    def check_farfetch_product_page(self, url: str) -> bool:
        """Check specific Farfetch product page for size availability"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for size selector
                size_elements = soup.find_all(['button', 'option', 'span'], class_=re.compile('size', re.I))

                sizes = [elem.get_text(strip=True) for elem in size_elements]
                return self.check_size_available(sizes)

        except Exception as e:
            logger.debug(f"Error checking product page: {e}")

        return False

    def check_vestiaire_collective(self) -> List[Dict]:
        """Enhanced Vestiaire Collective check"""
        logger.info("Checking Vestiaire Collective...")
        findings = []

        try:
            # Search URL
            search_url = "https://www.vestiairecollective.com/search/"
            params = {
                'q': 'Emilio Pucci maxi dress',
                'size': '10728'  # IT 40 size code (may need verification)
            }

            response = self.session.get(search_url, params=params, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for product listings
                products = soup.find_all(['div', 'article'], class_=re.compile('product|item', re.I))

                for product in products[:15]:
                    try:
                        title_elem = product.find(['h2', 'h3', 'p'], class_=re.compile('title|name', re.I))
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)

                        if self.is_match(title):
                            link_elem = product.find('a', href=True)
                            product_url = link_elem['href'] if link_elem else None

                            if product_url and not product_url.startswith('http'):
                                product_url = f"https://www.vestiairecollective.com{product_url}"

                            # Extract size info
                            size_elem = product.find(class_=re.compile('size', re.I))
                            size_text = size_elem.get_text(strip=True) if size_elem else ""

                            if any(s in size_text.upper() for s in ["IT 40", "40"]):
                                price_elem = product.find(class_=re.compile('price', re.I))
                                price = price_elem.get_text(strip=True) if price_elem else "N/A"

                                condition_elem = product.find(class_=re.compile('condition', re.I))
                                condition = condition_elem.get_text(strip=True) if condition_elem else "Pre-owned"

                                findings.append({
                                    'retailer': 'Vestiaire Collective',
                                    'title': title,
                                    'url': product_url,
                                    'price': price,
                                    'condition': condition,
                                    'size': TARGET_SIZE,
                                    'notes': 'Resale item - verify authenticity'
                                })

                    except Exception as e:
                        logger.debug(f"Error parsing product: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error checking Vestiaire Collective: {str(e)}")

        return findings

    def check_lyst(self) -> List[Dict]:
        """Check Lyst aggregator"""
        logger.info("Checking Lyst...")
        findings = []

        try:
            search_url = "https://www.lyst.com/shop/womens-dresses/"
            params = {
                'q': 'Emilio Pucci graphic print maxi dress',
                'size': '40'
            }

            response = self.session.get(search_url, params=params, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Lyst shows products from multiple retailers
                products = soup.find_all(['div', 'article'], attrs={'data-product-id': True})

                for product in products[:15]:
                    try:
                        title_elem = product.find(['h2', 'h3'])
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)

                        if self.is_match(title):
                            link_elem = product.find('a', href=True)
                            product_url = link_elem['href'] if link_elem else None

                            if product_url and not product_url.startswith('http'):
                                product_url = f"https://www.lyst.com{product_url}"

                            # Get retailer info
                            retailer_elem = product.find(class_=re.compile('merchant|retailer', re.I))
                            retailer = retailer_elem.get_text(strip=True) if retailer_elem else "Various retailers"

                            price_elem = product.find(class_=re.compile('price', re.I))
                            price = price_elem.get_text(strip=True) if price_elem else "N/A"

                            findings.append({
                                'retailer': f'Lyst ({retailer})',
                                'title': title,
                                'url': product_url,
                                'price': price,
                                'condition': 'New',
                                'size': TARGET_SIZE,
                                'notes': 'Available via Lyst - verify on retailer site'
                            })

                    except Exception as e:
                        logger.debug(f"Error parsing product: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error checking Lyst: {str(e)}")

        return findings

    def send_notification(self, finding: Dict):
        """Send notification when dress is found"""
        message = f"""
🔔 EMILIO PUCCI DRESS FOUND!

Item: {finding['title']}
Size: {finding['size']}

Retailer: {finding['retailer']}
Price: {finding['price']}
Condition: {finding['condition']}
Link: {finding['url']}

Notes: {finding.get('notes', 'None')}

Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        logger.info(message)
        print(message)

        if SEND_EMAIL and NOTIFICATION_EMAIL:
            self.send_email_notification(message, finding)

        self.save_finding(finding)

    def send_email_notification(self, message: str, finding: Dict):
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')

            if not all([smtp_user, smtp_password, NOTIFICATION_EMAIL]):
                logger.warning("Email credentials not configured.")
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

            logger.info(f"Email sent to {NOTIFICATION_EMAIL}")

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")

    def save_finding(self, finding: Dict):
        """Save finding to JSON file"""
        findings_file = 'findings.json'

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
        logger.info(f"Starting ENHANCED monitoring - {datetime.now()}")
        logger.info(f"Target: {TARGET_BRAND} {TARGET_ITEM} - Size {TARGET_SIZE}")
        logger.info("=" * 60)

        all_findings = []

        # Run checks
        checks = [
            ('Farfetch', self.check_farfetch_api),
            ('Vestiaire Collective', self.check_vestiaire_collective),
            ('Lyst', self.check_lyst),
        ]

        for name, checker in checks:
            try:
                logger.info(f"\nChecking {name}...")
                findings = checker()

                if findings:
                    all_findings.extend(findings)
                    logger.info(f"✅ Found {len(findings)} matching items on {name}")

                # Be respectful - wait between requests
                time.sleep(3)

            except Exception as e:
                logger.error(f"Error checking {name}: {str(e)}")

        # Send notifications for all findings
        for finding in all_findings:
            self.send_notification(finding)

        logger.info("=" * 60)
        if all_findings:
            logger.info(f"✅ Monitoring complete. Found {len(all_findings)} matching items!")
        else:
            logger.info("❌ Monitoring complete. No matching items found.")
        logger.info("=" * 60)

        return all_findings


def main():
    """Main entry point"""
    monitor = EnhancedDressMonitor()
    results = monitor.run_all_checks()

    if results:
        print(f"\n✅ Found {len(results)} matching items! Check findings.json for details.")
    else:
        print("\n❌ No matching items found. Will check again on next run.")


if __name__ == "__main__":
    main()
