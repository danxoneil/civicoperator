#!/usr/bin/env python3
"""
Topic Extractor — parses URLs and PDFs for RHT funding topics.

Extracts the exact noun phrases each state uses to describe what they're
funding under the Rural Health Transformation Program. Phrases are preserved
in their original language (not normalized).

Usage:
  python extract_topics.py --url https://example.gov/rht-plan
  python extract_topics.py --url https://example.gov/report.pdf
  python extract_topics.py --url URL1 --url URL2
  python extract_topics.py --url URL --create-items   # also create monday.com items

Required: spacy, en_core_web_sm model
Optional: MONDAY_API_TOKEN, MONDAY_TOPICS_BOARD_ID (for --create-items)
"""

import argparse
import io
import json
import logging
import os
import re
from typing import Dict, List, Optional, Set, Tuple

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import spacy
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4 lxml spacy")
    print("Then run: python -m spacy download en_core_web_sm")
    exit(1)

try:
    import pypdf
except ImportError:
    pypdf = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extract-topics.log'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# US states for detection
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
    'WI': 'Wisconsin', 'WY': 'Wyoming',
}
STATE_NAME_TO_CODE = {v.lower(): k for k, v in STATES.items()}


class TopicExtractor:
    """Extracts RHT funding topic phrases from web pages and PDFs."""

    # Verbs/contexts that signal a funding topic follows
    FUNDING_CONTEXTS = [
        'fund', 'invest', 'support', 'expand', 'improve', 'develop',
        'establish', 'create', 'launch', 'implement', 'enhance', 'build',
        'strengthen', 'provide', 'deliver', 'increase', 'advance',
        'promote', 'address', 'transform', 'modernize', 'deploy',
        'allocate', 'dedicate', 'prioritize', 'focus on', 'target',
    ]

    # Sentence-level keywords that indicate the sentence is about RHT activities
    ACTIVITY_KEYWORDS = [
        'rural health', 'transformation', 'rht', 'rhtp', 'grant', 'funding',
        'award', 'program', 'initiative', 'investment', 'priority', 'strategy',
        'plan', 'proposal', 'allocation', 'spending', 'budget',
        'cms', 'medicaid', 'medicare', 'federal',
    ]

    # Phrases to exclude (too generic or structural)
    EXCLUDE_PATTERNS = [
        r'^the\s', r'^this\s', r'^that\s', r'^these\s', r'^those\s',
        r'^a\s', r'^an\s', r'^our\s', r'^their\s', r'^its\s',
        r'^more\s+information', r'^click\s+here', r'^read\s+more',
        r'^page\s', r'^section\s', r'^table\s', r'^figure\s',
        r'^https?://', r'^\d+$', r'^©',
    ]

    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            logger.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            raise

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        })
        self.session.trust_env = False
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        self.session.mount('http://', HTTPAdapter(max_retries=retry))

        # monday.com config
        self.monday_token = os.getenv('MONDAY_API_TOKEN', '')
        self.monday_topics_board = os.getenv('MONDAY_TOPICS_BOARD_ID', '')

    # ------------------------------------------------------------------
    # Content fetching
    # ------------------------------------------------------------------

    def fetch_content(self, url: str) -> Tuple[str, str]:
        """Fetch content from a URL. Returns (text, content_type).

        Handles both HTML pages and PDF files (by URL).
        """
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()

        content_type = resp.headers.get('content-type', '').lower()

        if 'pdf' in content_type or url.lower().endswith('.pdf'):
            text = self._extract_pdf_text(resp.content)
            return text, 'pdf'
        else:
            text = self._extract_html_text(resp.content)
            return text, 'html'

    @staticmethod
    def _extract_html_text(content: bytes) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
            tag.decompose()
        main = soup.find('main') or soup.find('article') or soup.find(role='main')
        if main:
            text = main.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        return text

    @staticmethod
    def _extract_pdf_text(content: bytes) -> str:
        if pypdf is None:
            raise ImportError("pypdf is required for PDF support. Install with: pip install pypdf")
        reader = pypdf.PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return '\n'.join(pages)

    # ------------------------------------------------------------------
    # State detection
    # ------------------------------------------------------------------

    def detect_state(self, text: str) -> Optional[str]:
        """Detect which state the content is about. Returns state code or None."""
        text_lower = text[:5000].lower()  # Check beginning of doc

        # Count state mentions
        counts = {}
        for name, code in STATE_NAME_TO_CODE.items():
            count = text_lower.count(name)
            if count > 0:
                counts[code] = count

        if not counts:
            return None

        # Return the most-mentioned state
        return max(counts, key=counts.get)

    # ------------------------------------------------------------------
    # Topic extraction
    # ------------------------------------------------------------------

    def extract_topics(self, text: str) -> List[str]:
        """Extract funding topic phrases from text using spaCy NLP.

        Returns a list of unique noun phrases in their original language.
        """
        # Split into sentences, keep only those relevant to funding/RHT
        doc = self.nlp(text)
        relevant_sents = []
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            has_activity_kw = any(kw in sent_lower for kw in self.ACTIVITY_KEYWORDS)
            has_funding_ctx = any(ctx in sent_lower for ctx in self.FUNDING_CONTEXTS)
            if has_activity_kw or has_funding_ctx:
                relevant_sents.append(sent)

        logger.info(f"Found {len(relevant_sents)} relevant sentences out of {len(list(doc.sents))}")

        # Extract noun chunks from relevant sentences
        raw_topics: Set[str] = set()
        for sent in relevant_sents:
            sent_lower = sent.text.lower()
            has_funding_verb = any(ctx in sent_lower for ctx in self.FUNDING_CONTEXTS)

            for chunk in sent.noun_chunks:
                phrase = chunk.text.strip()

                # Skip very short or very long phrases
                if len(phrase) < 5 or len(phrase) > 120:
                    continue

                # Skip single-word chunks
                if ' ' not in phrase:
                    continue

                # Skip excluded patterns
                if any(re.match(pat, phrase, re.IGNORECASE) for pat in self.EXCLUDE_PATTERNS):
                    continue

                # Skip if it's just a state name or generic government term
                phrase_lower = phrase.lower()
                if phrase_lower in STATE_NAME_TO_CODE:
                    continue
                if phrase_lower in ('the state', 'the program', 'the grant', 'the federal government'):
                    continue

                # Prefer phrases from sentences with funding verbs
                # but also accept phrases from activity-keyword sentences
                # if they look like program/initiative descriptions
                if has_funding_verb:
                    raw_topics.add(phrase)
                elif self._looks_like_initiative(phrase_lower):
                    raw_topics.add(phrase)

        # Deduplicate: if one phrase is a substring of another, keep the longer one
        topics = self._deduplicate_phrases(sorted(raw_topics))

        logger.info(f"Extracted {len(topics)} unique topic phrases")
        return topics

    @staticmethod
    def _looks_like_initiative(phrase: str) -> bool:
        """Check if a phrase looks like it describes a program or initiative."""
        initiative_words = [
            'program', 'initiative', 'project', 'service', 'system',
            'network', 'center', 'clinic', 'facility', 'training',
            'workforce', 'telehealth', 'telemedicine', 'broadband',
            'behavioral health', 'mental health', 'substance',
            'maternal', 'prenatal', 'pediatric', 'emergency',
            'ambulance', 'ems', 'pharmacy', 'dental',
            'community health', 'health worker', 'expansion',
            'improvement', 'modernization', 'transformation',
            'access', 'equity', 'pipeline', 'recruitment', 'retention',
        ]
        return any(word in phrase for word in initiative_words)

    @staticmethod
    def _deduplicate_phrases(phrases: List[str]) -> List[str]:
        """Remove phrases that are substrings of longer phrases."""
        result = []
        phrases_lower = [p.lower() for p in phrases]
        for i, phrase in enumerate(phrases):
            is_substring = False
            for j, other in enumerate(phrases_lower):
                if i != j and phrases_lower[i] in other and len(phrases_lower[i]) < len(other):
                    is_substring = True
                    break
            if not is_substring:
                result.append(phrase)
        return result

    # ------------------------------------------------------------------
    # monday.com integration
    # ------------------------------------------------------------------

    def create_topic_item(self, topic: str, state_code: str, source_url: str) -> Optional[str]:
        """Create a topic item on the monday.com topics board. Returns item ID."""
        if not self.monday_token or not self.monday_topics_board:
            logger.warning("monday.com not configured, skipping item creation")
            return None

        # Create item with topic as the name
        query = """
        mutation ($boardId: ID!, $itemName: String!) {
          create_item(
            board_id: $boardId,
            item_name: $itemName
          ) {
            id
          }
        }
        """
        try:
            resp = requests.post(
                'https://api.monday.com/v2',
                json={
                    'query': query,
                    'variables': {
                        'boardId': self.monday_topics_board,
                        'itemName': topic,
                    },
                },
                headers={
                    'Authorization': self.monday_token,
                    'Content-Type': 'application/json',
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            if 'errors' in data:
                logger.error(f"monday.com error creating topic: {data['errors']}")
                return None

            item_id = data['data']['create_item']['id']
            logger.info(f"Created topic item {item_id}: {topic}")
            return item_id

        except Exception as e:
            logger.error(f"Error creating monday.com item: {e}")
            return None

    # ------------------------------------------------------------------
    # Main
    # ------------------------------------------------------------------

    def process_url(self, url: str) -> Dict:
        """Process a single URL and extract topics."""
        logger.info(f"Processing: {url}")

        try:
            text, content_type = self.fetch_content(url)
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return {'url': url, 'error': str(e), 'topics': [], 'state': None}

        logger.info(f"Fetched {len(text)} chars ({content_type})")

        state = self.detect_state(text)
        if state:
            logger.info(f"Detected state: {STATES[state]} ({state})")
        else:
            logger.warning("Could not detect state from content")

        topics = self.extract_topics(text)

        return {
            'url': url,
            'content_type': content_type,
            'state': state,
            'state_name': STATES.get(state, 'Unknown'),
            'topics': topics,
            'topic_count': len(topics),
        }

    def run(self, urls: List[str], create_items: bool = False) -> Dict:
        """Process multiple URLs and optionally create monday.com items."""
        logger.info("=" * 60)
        logger.info(f"Topic Extractor — {len(urls)} URLs")
        logger.info("=" * 60)

        all_results = []
        all_topics_created = []

        for url in urls:
            result = self.process_url(url)
            all_results.append(result)

            if create_items and result['topics'] and result['state']:
                for topic in result['topics']:
                    item_id = self.create_topic_item(topic, result['state'], url)
                    if item_id:
                        all_topics_created.append({
                            'topic': topic,
                            'state': result['state'],
                            'state_name': result['state_name'],
                            'item_id': item_id,
                            'source_url': url,
                        })

        return {
            'results': all_results,
            'created_items': all_topics_created,
            'total_topics': sum(r['topic_count'] for r in all_results),
            'total_created': len(all_topics_created),
        }

    def format_report(self, output: Dict) -> str:
        """Format a markdown report."""
        parts = [
            "# Topic Extraction Report\n",
            f"**Total topics extracted:** {output['total_topics']}",
            f"**Items created on monday.com:** {output['total_created']}\n",
        ]

        for result in output['results']:
            state_label = f"{result['state_name']} ({result['state']})" if result['state'] else "Unknown state"
            parts.append(f"## {state_label}\n")
            parts.append(f"**Source:** {result['url']}")
            parts.append(f"**Content type:** {result.get('content_type', '?')}")
            parts.append(f"**Topics found:** {result['topic_count']}\n")

            if result.get('error'):
                parts.append(f"**Error:** {result['error']}\n")
            elif result['topics']:
                for i, topic in enumerate(result['topics'], 1):
                    parts.append(f"{i}. {topic}")
                parts.append("")
            else:
                parts.append("No funding topics found in this document.\n")

        if output['created_items']:
            parts.append("## Created on monday.com\n")
            for item in output['created_items']:
                parts.append(f"- **{item['topic']}** ({item['state_name']}) — item #{item['item_id']}")

        return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description='Extract RHT funding topics from URLs and PDFs')
    parser.add_argument('--url', action='append', required=True, help='URL to process (can be repeated)')
    parser.add_argument('--create-items', action='store_true', help='Create items on monday.com topics board')
    args = parser.parse_args()

    extractor = TopicExtractor()
    output = extractor.run(args.url, create_items=args.create_items)

    # Save results
    with open('topics-results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    # Print report
    report = extractor.format_report(output)
    print("\n" + report)

    # GitHub Actions step summary
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(report)


if __name__ == '__main__':
    main()
