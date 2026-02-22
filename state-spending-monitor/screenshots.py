#!/usr/bin/env python3
"""
Screenshot capture for changed RHTP pages.

Uses Playwright (headless Chromium) to take full-page screenshots of
URLs that the URL monitor detected as changed.

Saves screenshots to a configurable output directory as PNG files
named by state (e.g., "Delaware.png").

Required: pip install playwright && playwright install chromium
"""

import logging
import os
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Convert a state name to a safe filename."""
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')


def capture_screenshots(
    changed: List[Dict],
    output_dir: str = 'screenshots',
    timeout: int = 30000,
) -> Dict[str, str]:
    """Take full-page screenshots of changed URLs.

    Args:
        changed: List of dicts with 'name' and 'url' keys (from url_monitor results).
        output_dir: Directory to save screenshots.
        timeout: Page load timeout in milliseconds.

    Returns:
        Dict mapping state name to screenshot file path.
    """
    if not changed:
        logger.info("No changed pages to screenshot")
        return {}

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed — skipping screenshots")
        return {}

    os.makedirs(output_dir, exist_ok=True)
    screenshots = {}

    logger.info(f"Capturing {len(changed)} screenshots...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
        )

        for item in changed:
            name = item['name']
            url = item['url']
            filename = f"{sanitize_filename(name)}.png"
            filepath = os.path.join(output_dir, filename)

            logger.info(f"  Screenshotting: {name} ({url})")

            try:
                page = context.new_page()
                page.goto(url, wait_until='networkidle', timeout=timeout)
                page.screenshot(path=filepath, full_page=True)
                page.close()

                screenshots[name] = filepath
                logger.info(f"  Saved: {filepath}")

            except Exception as e:
                logger.warning(f"  Failed to screenshot {name}: {e}")
                try:
                    page.close()
                except Exception:
                    pass

        browser.close()

    logger.info(f"Captured {len(screenshots)}/{len(changed)} screenshots")
    return screenshots
