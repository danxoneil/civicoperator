#!/usr/bin/env python3
"""
Google Drive uploader for RHTP page screenshots.

Uploads screenshot PNGs to a shared Google Drive folder and returns
public-viewable links that can be embedded in GitHub issues.

Requires a Google service account with Drive API enabled.
The target folder must be shared with the service account email.

Required env vars:
  GOOGLE_SERVICE_ACCOUNT_JSON — service account key JSON (as string)
  GOOGLE_DRIVE_FOLDER_ID      — ID of the target Drive folder
"""

import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def upload_screenshots_to_drive(
    screenshots: Dict[str, str],
    folder_id: str,
    credentials_json: str,
) -> Dict[str, str]:
    """Upload screenshot files to Google Drive.

    Args:
        screenshots: Dict mapping state name to local file path.
        folder_id: Google Drive folder ID to upload into.
        credentials_json: Service account JSON key as a string.

    Returns:
        Dict mapping state name to public Drive view URL.
    """
    if not screenshots:
        return {}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        logger.warning(
            "Google API libraries not installed — skipping Drive upload. "
            "Install with: pip install google-auth google-api-python-client"
        )
        return {}

    # Authenticate
    try:
        creds_dict = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive.file'],
        )
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Drive: {e}")
        return {}

    drive_links = {}

    for name, filepath in screenshots.items():
        if not os.path.exists(filepath):
            logger.warning(f"  Screenshot file not found: {filepath}")
            continue

        logger.info(f"  Uploading to Drive: {name}")

        try:
            file_metadata = {
                'name': os.path.basename(filepath),
                'parents': [folder_id],
            }
            media = MediaFileUpload(filepath, mimetype='image/png')

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink',
            ).execute()

            # Make the file viewable by anyone with the link
            service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'},
            ).execute()

            drive_links[name] = file.get('webViewLink', '')
            logger.info(f"  Uploaded: {drive_links[name]}")

        except Exception as e:
            logger.warning(f"  Failed to upload {name}: {e}")

    logger.info(f"Uploaded {len(drive_links)}/{len(screenshots)} screenshots to Drive")
    return drive_links
