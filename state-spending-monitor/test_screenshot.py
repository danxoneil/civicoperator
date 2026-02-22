#!/usr/bin/env python3
"""
Test and baseline screenshot utility.

Modes:
  --url <url>     Test mode: screenshot one URL, upload to Drive
  --baseline      Baseline mode: screenshot all 51 RHTP state URLs from
                  monday.com and upload to Drive in a dated subfolder

Reuses screenshots.py and drive_upload.py.
"""

import argparse
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def test_single_url(url: str):
    """Screenshot a single URL and upload to Drive."""
    from screenshots import capture_screenshots
    from drive_upload import upload_screenshots_to_drive

    items = [{'name': 'Test', 'url': url}]
    screenshots = capture_screenshots(items)

    if not screenshots:
        logger.error("Screenshot capture failed")
        sys.exit(1)

    logger.info(f"Screenshot saved: {list(screenshots.values())[0]}")

    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')
    if folder_id and creds:
        links = upload_screenshots_to_drive(screenshots, folder_id, creds)
        for name, link in links.items():
            print(f"\nDrive link: {link}")
    else:
        logger.info("Drive credentials not set — screenshot saved locally only")


def baseline_all():
    """Screenshot all 51 RHTP URLs from monday.com."""
    from url_monitor import URLMonitor
    from screenshots import capture_screenshots
    from drive_upload import upload_screenshots_to_drive

    monitor = URLMonitor()
    urls = monitor.fetch_urls_from_monday()
    if not urls:
        logger.error("No URLs found on monday.com board")
        sys.exit(1)

    logger.info(f"Taking baseline screenshots of {len(urls)} URLs...")

    # Use dated output dir
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = f'screenshots/baseline-{date_str}'
    screenshots = capture_screenshots(urls, output_dir=output_dir, timeout=45000)

    logger.info(f"Captured {len(screenshots)}/{len(urls)} screenshots")

    # Upload to Drive in a dated subfolder
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')
    if folder_id and creds:
        subfolder = f"Baseline {date_str}"
        links = upload_screenshots_to_drive(
            screenshots, folder_id, creds, subfolder_name=subfolder,
        )
        print(f"\n{'='*60}")
        print(f"BASELINE SCREENSHOTS — {date_str}")
        print(f"{'='*60}")
        print(f"Uploaded {len(links)}/{len(urls)} to Drive subfolder: {subfolder}")
        for name, link in sorted(links.items()):
            print(f"  {name}: {link}")
    else:
        logger.info("Drive credentials not set — screenshots saved locally only")

    # Write summary for GitHub Actions
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(f"# Baseline Screenshots — {date_str}\n\n")
            f.write(f"Captured **{len(screenshots)}** of **{len(urls)}** state pages\n\n")
            if folder_id and creds:
                f.write("| State | Drive Link |\n|-------|------------|\n")
                for name, link in sorted(links.items()):
                    f.write(f"| {name} | [View]({link}) |\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test/baseline screenshot utility')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='Screenshot a single test URL')
    group.add_argument('--baseline', action='store_true', help='Screenshot all 51 state URLs')
    args = parser.parse_args()

    if args.url:
        test_single_url(args.url)
    elif args.baseline:
        baseline_all()
