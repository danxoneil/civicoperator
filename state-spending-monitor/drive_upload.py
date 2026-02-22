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


def _get_drive_service(credentials_json: str):
    """Authenticate and return a Drive API service object."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds_dict = json.loads(credentials_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/drive.file'],
    )
    return build('drive', 'v3', credentials=creds)


def create_or_get_subfolder(service, parent_id: str, folder_name: str) -> str:
    """Create a subfolder in Drive (or return existing one's ID)."""
    # Check if folder already exists
    query = (
        f"'{parent_id}' in parents and name = '{folder_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = service.files().list(q=query, fields='files(id)').execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']

    # Create it
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id],
    }
    folder = service.files().create(body=metadata, fields='id').execute()

    # Make viewable
    service.permissions().create(
        fileId=folder['id'],
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()

    logger.info(f"Created Drive subfolder: {folder_name}")
    return folder['id']


def upload_screenshots_to_drive(
    screenshots: Dict[str, str],
    folder_id: str,
    credentials_json: str,
    subfolder_name: Optional[str] = None,
) -> Dict[str, str]:
    """Upload screenshot files to Google Drive.

    Args:
        screenshots: Dict mapping state name to local file path.
        folder_id: Google Drive folder ID to upload into.
        credentials_json: Service account JSON key as a string.
        subfolder_name: If set, create/use a subfolder with this name.

    Returns:
        Dict mapping state name to public Drive view URL.
    """
    if not screenshots:
        return {}

    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        logger.warning(
            "Google API libraries not installed — skipping Drive upload. "
            "Install with: pip install google-auth google-api-python-client"
        )
        return {}

    try:
        service = _get_drive_service(credentials_json)
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Drive: {e}")
        return {}

    # Use subfolder if requested
    target_folder = folder_id
    if subfolder_name:
        try:
            target_folder = create_or_get_subfolder(service, folder_id, subfolder_name)
        except Exception as e:
            logger.warning(f"Could not create subfolder '{subfolder_name}': {e}")

    drive_links = {}

    for name, filepath in screenshots.items():
        if not os.path.exists(filepath):
            logger.warning(f"  Screenshot file not found: {filepath}")
            continue

        logger.info(f"  Uploading to Drive: {name}")

        try:
            file_metadata = {
                'name': os.path.basename(filepath),
                'parents': [target_folder],
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
