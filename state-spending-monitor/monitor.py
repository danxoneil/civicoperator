#!/usr/bin/env python3
"""
State Spending News Monitor for Rural Health Transformation Program
Monitors all 50 US states for news about RHT program spending.

Data sources:
  - CMS Newsroom (multiple feed URLs attempted)
  - CMS RHT Program page (direct scrape)
  - Google News RSS (per-state searches)
  - State health department websites (all 50 states)
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
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

    # Target states - all 50 US states
    STATES = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    # Primary keywords (direct match = relevant)
    KEYWORDS = [
        'rural health transformation',
        'RHT program',
        'RHTP',
        'rural health funding',
        'CMS rural health',
        'rural health awards',
        'rural healthcare spending',
        'rural hospital funding',
        'rural health initiative',
        'rural healthcare transformation',
        'transform rural health',
        'rural health grant',
    ]

    # CMS RSS feed URLs to try (multiple patterns since CMS has changed URLs)
    CMS_FEED_URLS = [
        'https://www.cms.gov/newsroom/press-releases/rss.xml',
        'https://www.cms.gov/newsroom/press-releases.rss',
        'https://www.cms.gov/feeds/newsroom/press-releases.rss',
        'https://www.cms.gov/about-cms/web-policies-important-links/rss-feeds',
    ]

    # CMS pages to scrape directly for RHT content
    CMS_DIRECT_URLS = [
        'https://www.cms.gov/priorities/rural-health-transformation-rht-program/overview',
        'https://www.cms.gov/about-cms/contact/newsroom',
        'https://www.hhs.gov/about/news/index.html',
    ]

    # State health department news pages
    STATE_URLS = {
        'AL': 'https://www.alabamapublichealth.gov/blog/news-releases.html',
        'AK': 'https://health.alaska.gov/en/news/',
        'AZ': 'https://directorsblog.health.azdhs.gov/',
        'AR': 'https://healthy.arkansas.gov/news/press-releases/',
        'CA': 'https://www.cdph.ca.gov/Programs/OPA/Pages/New-Release-2026.aspx',
        'CO': 'https://hcpf.colorado.gov/rural-health-transformation-program',
        'CT': 'https://portal.ct.gov/dph/newsroom',
        'DE': 'https://dhss.delaware.gov/dhss/newsroom.html',
        'FL': 'https://www.floridahealth.gov/newsroom/all-articles.html',
        'GA': 'https://dph.georgia.gov/press-releases',
        'HI': 'https://health.hawaii.gov/news/category/newsroom/',
        'ID': 'https://healthandwelfare.idaho.gov/news',
        'IL': 'https://dph.illinois.gov/recent-news.html',
        'IN': 'https://www.in.gov/health/office-of-public-affairs/',
        'IA': 'https://hhs.iowa.gov/newsroom',
        'KS': 'https://www.kdhe.ks.gov/CivicAlerts.aspx',
        'KY': 'https://www.chfs.ky.gov/News/Pages/default.aspx',
        'LA': 'https://ldh.la.gov/page/newsroom',
        'ME': 'https://www.maine.gov/dhhs/news',
        'MD': 'https://health.maryland.gov/newsroom/Pages/Index.aspx',
        'MA': 'https://www.mass.gov/orgs/department-of-public-health/news',
        'MI': 'https://www.michigan.gov/mdhhs/inside-mdhhs/newsroom/releases',
        'MN': 'https://www.health.state.mn.us/news/index.html',
        'MS': 'https://msdh.ms.gov/page/23,0,341.html',
        'MO': 'https://health.mo.gov/news',
        'MT': 'https://dphhs.mt.gov/News/index',
        'NE': 'https://dhhs.ne.gov/Pages/News-Releases.aspx',
        'NV': 'https://www.dhhs.nv.gov/News/',
        'NH': 'https://www.dhhs.nh.gov/news-events/news-releases',
        'NJ': 'https://www.nj.gov/health/news/',
        'NM': 'https://www.nmhealth.org/news/',
        'NY': 'https://health.ny.gov/press/releases/',
        'NC': 'https://www.ncdhhs.gov/news',
        'ND': 'https://www.health.nd.gov/news',
        'OH': 'https://odh.ohio.gov/media-center/news-releases',
        'OK': 'https://oklahoma.gov/health/about-us/news-and-updates.html',
        'OR': 'https://www.oregon.gov/oha/PH/Pages/newsrel.aspx',
        'PA': 'https://www.media.pa.gov/pages/health-details.aspx',
        'RI': 'https://health.ri.gov/news/',
        'SC': 'https://scdhec.gov/news-releases',
        'SD': 'https://doh.sd.gov/news/',
        'TN': 'https://www.tn.gov/health/news.html',
        'TX': 'https://www.dshs.texas.gov/news-alerts',
        'UT': 'https://dhhs.utah.gov/news/',
        'VT': 'https://www.healthvermont.gov/news',
        'VA': 'https://www.vdh.virginia.gov/news/',
        'WA': 'https://doh.wa.gov/newsroom',
        'WV': 'https://dhhr.wv.gov/News/Pages/default.aspx',
        'WI': 'https://www.dhs.wisconsin.gov/news/index.htm',
        'WY': 'https://health.wyo.gov/news/',
    }

    def __init__(self):
        """Initialize the monitor with retry-capable HTTP session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        # Disable proxy env vars (fixes GitHub Actions proxy errors)
        self.session.trust_env = False

        # Mount retry adapter for automatic retries on transient errors
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,  # 2s, 4s, 8s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.findings = []

        # Source health tracking
        self.source_stats = {
            'cms_feeds': {'attempted': 0, 'succeeded': 0, 'errors': []},
            'cms_direct': {'attempted': 0, 'succeeded': 0, 'errors': []},
            'google_news': {'attempted': 0, 'succeeded': 0, 'errors': []},
            'state_depts': {'attempted': 0, 'succeeded': 0, 'errors': []},
        }

        # Configuration from environment variables
        self.send_email = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.notification_email = os.getenv('NOTIFICATION_EMAIL', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.lookback_days = int(os.getenv('LOOKBACK_DAYS', '7'))

    def _get(self, url: str, timeout: int = 15) -> Optional[requests.Response]:
        """Make a GET request with error handling. Retries are handled by the session adapter."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # Shorten the error message for logging
            err_type = type(e).__name__
            logger.warning(f"Request failed for {url}: {err_type}")
            return None

    def parse_rss_feed(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse RSS feed XML and return list of entries"""
        entries = []
        try:
            soup = BeautifulSoup(xml_content, 'xml')
            items = soup.find_all('item')

            for item in items:
                entry = {}
                title_tag = item.find('title')
                entry['title'] = title_tag.get_text(strip=True) if title_tag else ''

                desc_tag = item.find('description') or item.find('summary')
                entry['description'] = desc_tag.get_text(strip=True) if desc_tag else ''

                link_tag = item.find('link')
                entry['link'] = link_tag.get_text(strip=True) if link_tag else ''

                pub_tag = item.find('pubDate') or item.find('published')
                if pub_tag:
                    try:
                        from email.utils import parsedate_to_datetime
                        entry['published'] = parsedate_to_datetime(pub_tag.get_text(strip=True))
                    except Exception:
                        entry['published'] = datetime.now()
                else:
                    entry['published'] = datetime.now()

                entries.append(entry)
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")

        return entries

    def is_relevant(self, title: str, description: str, state_code: str,
                    *, require_state: bool = True) -> bool:
        """Check if a news item is relevant to our monitoring criteria"""
        text = f"{title} {description}".lower()
        state_name = self.STATES[state_code].lower()

        # Must mention the state unless explicitly waived
        if require_state and state_code.lower() not in text and state_name not in text:
            return False

        # Direct keyword match = relevant
        if any(kw.lower() in text for kw in self.KEYWORDS):
            logger.info(f"Match via keyword for {state_code}: {title[:80]}")
            return True

        # "rural" + health/funding term = relevant
        if 'rural' in text and any(t in text for t in [
            'health', 'healthcare', 'hospital', 'clinic',
            'million', 'billion', 'funding', 'award', 'grant',
        ]):
            logger.info(f"Match via rural+context for {state_code}: {title[:80]}")
            return True

        return False

    def check_cms_feeds(self) -> List[Dict[str, Any]]:
        """Check CMS newsroom RSS feeds, trying multiple known URLs"""
        logger.info("Checking CMS newsroom RSS feeds...")
        findings = []
        feed_worked = False

        for feed_url in self.CMS_FEED_URLS:
            self.source_stats['cms_feeds']['attempted'] += 1
            logger.info(f"  Trying feed: {feed_url}")
            response = self._get(feed_url)

            if response is None:
                self.source_stats['cms_feeds']['errors'].append(feed_url)
                continue

            # Check if we actually got XML/RSS content
            content_type = response.headers.get('content-type', '')
            if 'xml' in content_type or 'rss' in content_type or response.text.strip().startswith('<?xml'):
                entries = self.parse_rss_feed(response.text)
                if entries:
                    feed_worked = True
                    self.source_stats['cms_feeds']['succeeded'] += 1
                    cutoff = datetime.now() - timedelta(days=self.lookback_days)
                    logger.info(f"  CMS RSS: got {len(entries)} entries from {feed_url}")

                    for entry in entries[:30]:
                        published = entry.get('published', datetime.now())
                        if hasattr(published, 'tzinfo') and published.tzinfo is not None:
                            published = published.replace(tzinfo=None)
                        if published < cutoff:
                            continue

                        title = entry.get('title', '')
                        description = entry.get('description', '')
                        link = entry.get('link', '')

                        for state_code in self.STATES:
                            if self.is_relevant(title, description, state_code):
                                findings.append({
                                    'source': 'CMS Newsroom',
                                    'state': state_code,
                                    'title': title,
                                    'description': description[:500],
                                    'url': link,
                                    'published': published.isoformat(),
                                    'found_at': datetime.now().isoformat(),
                                })
                    break  # Got a working feed, stop trying others
            else:
                logger.info(f"  Got non-RSS response from {feed_url} (content-type: {content_type})")
                self.source_stats['cms_feeds']['errors'].append(feed_url)

            time.sleep(2)

        if not feed_worked:
            logger.warning("No CMS RSS feeds returned valid data")

        return findings

    def check_cms_direct(self) -> List[Dict[str, Any]]:
        """Scrape CMS pages directly for RHT program news"""
        logger.info("Checking CMS direct pages for RHT content...")
        findings = []

        for url in self.CMS_DIRECT_URLS:
            self.source_stats['cms_direct']['attempted'] += 1
            logger.info(f"  Checking: {url}")
            response = self._get(url)

            if response is None:
                self.source_stats['cms_direct']['errors'].append(url)
                continue

            self.source_stats['cms_direct']['succeeded'] += 1
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links[:50]:
                title = link.get_text(strip=True)
                href = link['href']
                if not title or len(title) < 10:
                    continue

                if href.startswith('/'):
                    href = urljoin(url, href)

                for state_code in self.STATES:
                    if self.is_relevant(title, '', state_code, require_state=True):
                        findings.append({
                            'source': 'CMS Direct',
                            'state': state_code,
                            'title': title,
                            'description': 'Found on CMS website',
                            'url': href,
                            'published': datetime.now().isoformat(),
                            'found_at': datetime.now().isoformat(),
                        })

            time.sleep(2)

        return findings

    def check_google_news_rss(self, state_code: str) -> List[Dict[str, Any]]:
        """Check Google News RSS for state-specific RHT news"""
        findings = []
        state_name = self.STATES[state_code]

        # Use two search queries per state for better coverage
        queries = [
            f'{state_name} rural health transformation program',
            f'{state_name} CMS rural health funding 2026',
        ]

        for query in queries:
            self.source_stats['google_news']['attempted'] += 1
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"

            response = self._get(url)
            if response is None:
                self.source_stats['google_news']['errors'].append(f"{state_code}: {query[:40]}")
                continue

            self.source_stats['google_news']['succeeded'] += 1
            entries = self.parse_rss_feed(response.text)
            cutoff = datetime.now() - timedelta(days=self.lookback_days)
            logger.info(f"  Google News {state_code} ({query[:30]}...): {len(entries)} entries")

            for entry in entries[:15]:
                published = entry.get('published', datetime.now())
                if hasattr(published, 'tzinfo') and published.tzinfo is not None:
                    published = published.replace(tzinfo=None)
                if published < cutoff:
                    continue

                title = entry.get('title', '')
                description = entry.get('description', '')
                link = entry.get('link', '')

                if self.is_relevant(title, description, state_code):
                    findings.append({
                        'source': 'Google News',
                        'state': state_code,
                        'title': title,
                        'description': description[:500],
                        'url': link,
                        'published': published.isoformat(),
                        'found_at': datetime.now().isoformat(),
                    })

            time.sleep(2)

        return findings

    def check_state_health_dept(self, state_code: str) -> List[Dict[str, Any]]:
        """Check a state health department website for relevant press releases"""
        findings = []

        if state_code not in self.STATE_URLS:
            return findings

        url = self.STATE_URLS[state_code]
        self.source_stats['state_depts']['attempted'] += 1

        response = self._get(url)
        if response is None:
            self.source_stats['state_depts']['errors'].append(state_code)
            return findings

        self.source_stats['state_depts']['succeeded'] += 1
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links[:30]:
            title = link.get_text(strip=True)
            href = link['href']
            if not title or len(title) < 10:
                continue

            if href.startswith('/'):
                href = urljoin(url, href)

            if self.is_relevant(title, '', state_code, require_state=False):
                findings.append({
                    'source': f'{state_code} Health Department',
                    'state': state_code,
                    'title': title,
                    'description': f'Found on {self.STATES[state_code]} health department website',
                    'url': href,
                    'published': datetime.now().isoformat(),
                    'found_at': datetime.now().isoformat(),
                })

        time.sleep(2)
        return findings

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Run all monitoring checks and return deduplicated findings"""
        logger.info("=" * 60)
        logger.info("Starting state spending news monitoring")
        logger.info(f"Monitoring {len(self.STATES)} states, lookback {self.lookback_days} days")
        logger.info("=" * 60)

        all_findings = []

        # 1. CMS RSS feeds (covers all states)
        all_findings.extend(self.check_cms_feeds())

        # 2. CMS direct page scrapes (covers all states)
        all_findings.extend(self.check_cms_direct())

        # 3. Per-state: Google News + state health dept
        for state_code in self.STATES:
            logger.info(f"Checking {state_code} ({self.STATES[state_code]})...")
            all_findings.extend(self.check_google_news_rss(state_code))
            all_findings.extend(self.check_state_health_dept(state_code))

        # Deduplicate by URL
        seen_urls = set()
        unique = []
        for f in all_findings:
            if f['url'] not in seen_urls:
                seen_urls.add(f['url'])
                unique.append(f)

        self.findings = unique
        logger.info(f"Total unique findings: {len(unique)}")
        return unique

    def save_findings(self, filename: str = 'findings.json'):
        """Save findings to JSON, merging with any existing data"""
        try:
            existing = []
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    existing = json.load(f)

            existing_urls = {item['url'] for item in existing}
            new_findings = [f for f in self.findings if f['url'] not in existing_urls]

            if new_findings:
                existing.extend(new_findings)
                with open(filename, 'w') as f:
                    json.dump(existing, f, indent=2)
                logger.info(f"Saved {len(new_findings)} new findings ({len(existing)} total)")
            else:
                # Always write the file so the workflow can upload it
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        json.dump([], f, indent=2)
                logger.info("No new findings to save")

            return len(new_findings)
        except Exception as e:
            logger.error(f"Error saving findings: {e}")
            return 0

    def send_notification(self, *, always_notify: bool = True):
        """Send email notification with findings or run status

        Args:
            always_notify: If True, send a status email even when there are 0 findings.
        """
        if not self.send_email:
            logger.info("Email notifications disabled")
            return

        if not all([self.smtp_user, self.smtp_password, self.notification_email]):
            logger.warning("Email configuration incomplete, skipping notification")
            return

        has_findings = bool(self.findings)
        if not has_findings and not always_notify:
            return

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = self.notification_email

            if has_findings:
                msg['Subject'] = f"State Spending Alert: {len(self.findings)} items found"
                text_body = self._format_findings_email()
            else:
                msg['Subject'] = "State Spending Monitor: Run completed (0 findings)"
                text_body = self._format_status_email()

            msg.attach(MIMEText(text_body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Sent email notification to {self.notification_email}")

        except Exception as e:
            logger.error(f"Error sending email: {e}")

    def _format_findings_email(self) -> str:
        """Format findings into email body text"""
        parts = [
            f"Found {len(self.findings)} relevant news items about "
            f"Rural Health Transformation Program spending:\n",
        ]

        by_state = {}
        for f in self.findings:
            by_state.setdefault(f['state'], []).append(f)

        for sc in sorted(by_state):
            items = by_state[sc]
            parts.append(f"\n{self.STATES[sc]} ({len(items)} items)")
            parts.append("-" * 50)
            for item in items:
                parts.append(f"\n  Title: {item['title']}")
                parts.append(f"  Source: {item['source']}")
                parts.append(f"  URL: {item['url']}")
                parts.append(f"  Published: {item['published']}")
                if item.get('description'):
                    parts.append(f"  Description: {item['description'][:200]}")
                parts.append("")

        parts.append("\n" + self._format_source_health())
        return "\n".join(parts)

    def _format_status_email(self) -> str:
        """Format a status-only email (no findings)"""
        parts = [
            "State Spending News Monitor completed a run with 0 findings.\n",
            "This email confirms the monitor is running. If you consistently see",
            "0 findings, the data sources may need updating.\n",
            self._format_source_health(),
        ]
        return "\n".join(parts)

    def _format_source_health(self) -> str:
        """Format source health stats as plain text"""
        lines = ["--- Source Health Report ---"]
        for source, stats in self.source_stats.items():
            attempted = stats['attempted']
            succeeded = stats['succeeded']
            failed = attempted - succeeded
            if attempted == 0:
                status = "not checked"
            elif failed == 0:
                status = f"OK ({succeeded}/{attempted})"
            else:
                status = f"{succeeded}/{attempted} succeeded, {failed} failed"
            lines.append(f"  {source}: {status}")
            if stats['errors']:
                for err in stats['errors'][:5]:
                    lines.append(f"    - failed: {err}")
                if len(stats['errors']) > 5:
                    lines.append(f"    ... and {len(stats['errors']) - 5} more")
        return "\n".join(lines)

    def create_summary(self) -> str:
        """Create a markdown summary for GitHub Actions step summary"""
        parts = [
            "# State Spending News Monitor Results\n",
            f"**Run date:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Lookback:** {self.lookback_days} days",
            f"**Findings:** {len(self.findings)}\n",
        ]

        # Source health table
        parts.append("## Source Health\n")
        parts.append("| Source | Attempted | Succeeded | Failed |")
        parts.append("|--------|-----------|-----------|--------|")
        for source, stats in self.source_stats.items():
            a = stats['attempted']
            s = stats['succeeded']
            f = a - s
            emoji = "✅" if f == 0 and a > 0 else ("⚠️" if s > 0 else "❌")
            parts.append(f"| {emoji} {source} | {a} | {s} | {f} |")
        parts.append("")

        if self.findings:
            by_state = {}
            for finding in self.findings:
                by_state.setdefault(finding['state'], []).append(finding)

            parts.append("## Findings by State\n")
            for sc in sorted(by_state):
                items = by_state[sc]
                parts.append(f"### {self.STATES[sc]} ({len(items)} items)\n")
                for i, item in enumerate(items, 1):
                    parts.append(f"{i}. **{item['title']}**")
                    parts.append(f"   - Source: {item['source']}")
                    parts.append(f"   - URL: {item['url']}")
                    parts.append(f"   - Published: {item['published']}\n")
        else:
            parts.append("## No findings this run\n")
            parts.append("No relevant news items matched the monitoring criteria.")
            parts.append("This may be normal — the monitor will keep checking daily.\n")

        # Failed sources detail
        all_errors = []
        for source, stats in self.source_stats.items():
            for err in stats['errors']:
                all_errors.append(f"- **{source}**: {err}")
        if all_errors:
            parts.append("## Failed Sources (first 20)\n")
            for err in all_errors[:20]:
                parts.append(err)
            if len(all_errors) > 20:
                parts.append(f"\n*... and {len(all_errors) - 20} more*")

        return "\n".join(parts)

    def create_status_json(self) -> Dict[str, Any]:
        """Create a machine-readable status report"""
        return {
            'run_date': datetime.now().isoformat(),
            'lookback_days': self.lookback_days,
            'findings_count': len(self.findings),
            'source_health': {
                source: {
                    'attempted': stats['attempted'],
                    'succeeded': stats['succeeded'],
                    'failed': stats['attempted'] - stats['succeeded'],
                    'error_count': len(stats['errors']),
                }
                for source, stats in self.source_stats.items()
            },
        }


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("State Spending News Monitor - Starting")
    logger.info("=" * 60)

    monitor = StateSpendingMonitor()

    # Run all checks
    findings = monitor.run_all_checks()

    # Save findings
    new_count = monitor.save_findings()

    # Save status report
    status = monitor.create_status_json()
    with open('status.json', 'w') as f:
        json.dump(status, f, indent=2)
    logger.info(f"Saved status report to status.json")

    # Send notification (always, so user knows it ran)
    monitor.send_notification(always_notify=True)

    # Create summary
    summary = monitor.create_summary()
    print("\n" + summary)

    # Write GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(summary)

    logger.info("=" * 60)
    logger.info(f"Monitoring complete: {len(findings)} findings, {new_count} new")
    logger.info("=" * 60)

    return len(findings)


if __name__ == '__main__':
    exit(0 if main() >= 0 else 1)
