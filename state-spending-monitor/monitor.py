#!/usr/bin/env python3
"""
State Spending News Monitor for Rural Health Transformation Program
Monitors CA, NY, FL, and TX for news about RHT program spending
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install requests beautifulsoup4 lxml")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StateSpendingMonitor:
    """Monitor for state spending news related to CMS Rural Health Transformation Program"""

    # Target states
    STATES = {
        'CA': 'California',
        'NY': 'New York',
        'FL': 'Florida',
        'TX': 'Texas'
    }

    # Keywords to search for
    KEYWORDS = [
        'rural health transformation',
        'RHT program',
        'rural health funding',
        'CMS rural health',
        'rural health awards',
        'rural healthcare spending',
        'rural hospital funding',
        'rural health initiative'
    ]

    # Additional context keywords
    CONTEXT_KEYWORDS = [
        'CMS', 'Centers for Medicare', 'Medicaid',
        'billion', 'million', 'funding', 'award',
        'rural', 'hospital', 'clinic', 'healthcare'
    ]

    def __init__(self):
        """Initialize the monitor"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.findings = []

        # Configuration from environment variables
        self.send_email = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.notification_email = os.getenv('NOTIFICATION_EMAIL', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Days to look back for news
        self.lookback_days = int(os.getenv('LOOKBACK_DAYS', '7'))

    def parse_rss_feed(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse RSS feed XML and return list of entries"""
        entries = []
        try:
            soup = BeautifulSoup(xml_content, 'xml')
            items = soup.find_all('item')

            for item in items:
                entry = {}

                # Extract title
                title_tag = item.find('title')
                entry['title'] = title_tag.get_text(strip=True) if title_tag else ''

                # Extract description/summary
                desc_tag = item.find('description') or item.find('summary')
                entry['description'] = desc_tag.get_text(strip=True) if desc_tag else ''

                # Extract link
                link_tag = item.find('link')
                entry['link'] = link_tag.get_text(strip=True) if link_tag else ''

                # Extract published date
                pub_tag = item.find('pubDate') or item.find('published')
                if pub_tag:
                    try:
                        from email.utils import parsedate_to_datetime
                        entry['published'] = parsedate_to_datetime(pub_tag.get_text(strip=True))
                    except:
                        entry['published'] = datetime.now()
                else:
                    entry['published'] = datetime.now()

                entries.append(entry)
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")

        return entries

    def is_relevant(
        self,
        title: str,
        description: str,
        state_code: str,
        *,
        require_state: bool = True,
        min_context_matches: int = 3,
        require_rural_context: bool = False,
    ) -> bool:
        """Check if a news item is relevant to our monitoring criteria"""
        text = f"{title} {description}".lower()
        state_name = self.STATES[state_code].lower()

        # Must mention the state
        if require_state and state_code.lower() not in text and state_name not in text:
            return False

        # Must contain at least one primary keyword
        has_keyword = any(keyword.lower() in text for keyword in self.KEYWORDS)

        # Or have multiple context keywords
        context_count = sum(1 for keyword in self.CONTEXT_KEYWORDS if keyword.lower() in text)

        if has_keyword:
            return True

        if require_rural_context and 'rural' not in text:
            return False

        return context_count >= min_context_matches

    def check_cms_newsroom(self) -> List[Dict[str, Any]]:
        """Check CMS newsroom for relevant announcements"""
        logger.info("Checking CMS newsroom...")
        findings = []

        try:
            # CMS has an RSS feed for press releases
            url = "https://www.cms.gov/newsroom/press-releases.rss"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                entries = self.parse_rss_feed(response.text)
                cutoff_date = datetime.now() - timedelta(days=self.lookback_days)

                for entry in entries[:20]:  # Check last 20 entries
                    published = entry.get('published', datetime.now())

                    if published < cutoff_date:
                        continue

                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    link = entry.get('link', '')

                    # Check each state
                    for state_code in self.STATES.keys():
                        if self.is_relevant(title, description, state_code):
                            findings.append({
                                'source': 'CMS Newsroom',
                                'state': state_code,
                                'title': title,
                                'description': description[:300],
                                'url': link,
                                'published': published.isoformat(),
                                'found_at': datetime.now().isoformat()
                            })
                            logger.info(f"Found relevant CMS news for {state_code}: {title}")

            time.sleep(2)  # Rate limiting

        except Exception as e:
            logger.error(f"Error checking CMS newsroom: {e}")

        return findings

    def check_google_news_rss(self, state_code: str) -> List[Dict[str, Any]]:
        """Check Google News RSS for state-specific news"""
        logger.info(f"Checking Google News for {state_code}...")
        findings = []

        try:
            state_name = self.STATES[state_code]
            # Search for rural health news in the state
            query = f"{state_name} rural health funding CMS"
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                entries = self.parse_rss_feed(response.text)
                cutoff_date = datetime.now() - timedelta(days=self.lookback_days)

                for entry in entries[:15]:  # Check last 15 entries
                    published = entry.get('published', datetime.now())

                    if published < cutoff_date:
                        continue

                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    link = entry.get('link', '')

                    if self.is_relevant(title, description, state_code):
                        findings.append({
                            'source': 'Google News',
                            'state': state_code,
                            'title': title,
                            'description': description[:300],
                            'url': link,
                            'published': published.isoformat(),
                            'found_at': datetime.now().isoformat()
                        })
                        logger.info(f"Found relevant Google News for {state_code}: {title}")

            time.sleep(3)  # Rate limiting

        except Exception as e:
            logger.error(f"Error checking Google News for {state_code}: {e}")

        return findings

    def check_state_health_dept(self, state_code: str) -> List[Dict[str, Any]]:
        """Check state health department news/press releases"""
        logger.info(f"Checking {state_code} health department...")
        findings = []

        # State health department news pages
        state_urls = {
            'CA': 'https://www.cdph.ca.gov/Programs/OPA/Pages/New-Release-2026.aspx',
            'NY': 'https://health.ny.gov/press/releases/',
            'FL': 'https://www.floridahealth.gov/newsroom/all-articles.html',
            'TX': 'https://www.dshs.texas.gov/news-alerts'
        }

        if state_code not in state_urls:
            return findings

        try:
            url = state_urls[state_code]
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for links that might be press releases
                links = soup.find_all('a', href=True)

                for link in links[:30]:  # Check first 30 links
                    title = link.get_text(strip=True)
                    href = link['href']

                    # Make absolute URL
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)

                    if self.is_relevant(
                        title,
                        '',
                        state_code,
                        require_state=False,
                        min_context_matches=2,
                        require_rural_context=True,
                    ):
                        findings.append({
                            'source': f'{state_code} Health Department',
                            'state': state_code,
                            'title': title,
                            'description': 'State health department announcement',
                            'url': href,
                            'published': datetime.now().isoformat(),
                            'found_at': datetime.now().isoformat()
                        })
                        logger.info(f"Found relevant state news for {state_code}: {title}")

            time.sleep(3)  # Rate limiting

        except Exception as e:
            logger.error(f"Error checking {state_code} health department: {e}")

        return findings

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Run all monitoring checks"""
        logger.info("Starting state spending news monitoring...")
        logger.info(f"Monitoring states: {', '.join(self.STATES.values())}")
        logger.info(f"Looking back {self.lookback_days} days")

        all_findings = []

        # Check CMS newsroom (covers all states)
        cms_findings = self.check_cms_newsroom()
        all_findings.extend(cms_findings)

        # Check Google News and state sites for each state
        for state_code in self.STATES.keys():
            google_findings = self.check_google_news_rss(state_code)
            all_findings.extend(google_findings)

            state_findings = self.check_state_health_dept(state_code)
            all_findings.extend(state_findings)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_findings = []
        for finding in all_findings:
            if finding['url'] not in seen_urls:
                seen_urls.add(finding['url'])
                unique_findings.append(finding)

        self.findings = unique_findings
        logger.info(f"Found {len(unique_findings)} relevant news items")

        return unique_findings

    def save_findings(self, filename: str = 'findings.json'):
        """Save findings to JSON file"""
        try:
            # Load existing findings if any
            existing = []
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    existing = json.load(f)

            # Add new findings (avoid duplicates)
            existing_urls = {f['url'] for f in existing}
            new_findings = [f for f in self.findings if f['url'] not in existing_urls]

            if new_findings:
                existing.extend(new_findings)
                with open(filename, 'w') as f:
                    json.dump(existing, f, indent=2)
                logger.info(f"Saved {len(new_findings)} new findings to {filename}")
            else:
                logger.info("No new findings to save")

        except Exception as e:
            logger.error(f"Error saving findings: {e}")

    def send_notification(self):
        """Send email notification with findings"""
        if not self.send_email or not self.findings:
            return

        if not all([self.smtp_user, self.smtp_password, self.notification_email]):
            logger.warning("Email configuration incomplete, skipping notification")
            return

        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"State Spending News Alert: {len(self.findings)} items found"
            msg['From'] = self.smtp_user
            msg['To'] = self.notification_email

            # Create text body
            text_parts = [
                f"Found {len(self.findings)} relevant news items about Rural Health Transformation Program spending:\n"
            ]

            # Group by state
            by_state = {}
            for finding in self.findings:
                state = finding['state']
                if state not in by_state:
                    by_state[state] = []
                by_state[state].append(finding)

            for state_code in sorted(by_state.keys()):
                state_name = self.STATES[state_code]
                findings = by_state[state_code]
                text_parts.append(f"\n{state_name} ({len(findings)} items):")
                text_parts.append("-" * 50)

                for finding in findings:
                    text_parts.append(f"\nTitle: {finding['title']}")
                    text_parts.append(f"Source: {finding['source']}")
                    text_parts.append(f"URL: {finding['url']}")
                    text_parts.append(f"Published: {finding['published']}")
                    if finding.get('description'):
                        text_parts.append(f"Description: {finding['description']}")
                    text_parts.append("")

            text_body = "\n".join(text_parts)

            # Attach text body
            msg.attach(MIMEText(text_body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Sent email notification to {self.notification_email}")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    def create_summary(self) -> str:
        """Create a summary of findings for GitHub Actions"""
        if not self.findings:
            return "No relevant news found."

        summary_parts = [
            f"# State Spending News Monitor Results\n",
            f"**Found {len(self.findings)} relevant items**\n",
            f"**Monitoring Period:** Last {self.lookback_days} days\n",
            f"**States:** {', '.join(self.STATES.values())}\n"
        ]

        # Group by state
        by_state = {}
        for finding in self.findings:
            state = finding['state']
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(finding)

        for state_code in sorted(by_state.keys()):
            state_name = self.STATES[state_code]
            findings = by_state[state_code]
            summary_parts.append(f"\n## {state_name} ({len(findings)} items)\n")

            for i, finding in enumerate(findings, 1):
                summary_parts.append(f"{i}. **{finding['title']}**")
                summary_parts.append(f"   - Source: {finding['source']}")
                summary_parts.append(f"   - URL: {finding['url']}")
                summary_parts.append(f"   - Published: {finding['published']}\n")

        return "\n".join(summary_parts)


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("State Spending News Monitor - Starting")
    logger.info("=" * 60)

    monitor = StateSpendingMonitor()

    # Run all checks
    findings = monitor.run_all_checks()

    # Save findings
    monitor.save_findings()

    # Send notification if enabled
    if findings:
        monitor.send_notification()

    # Create summary
    summary = monitor.create_summary()
    print("\n" + summary)

    # Save summary for GitHub Actions
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(summary)

    logger.info("=" * 60)
    logger.info(f"Monitoring complete: {len(findings)} items found")
    logger.info("=" * 60)

    return len(findings)


if __name__ == '__main__':
    exit(0 if main() >= 0 else 1)
