#!/usr/bin/env python3
"""
Google Drive uploader for RHTP page screenshots.

Uploads screenshot PNGs to a Google Drive folder and returns
public-viewable links that can be embedded in GitHub issues.

Supports two authentication methods:
  1. OAuth refresh token (works with personal Google accounts)
  2. Service account (works with Shared Drives only — service accounts
     have zero storage quota on regular Drive)

OAuth env vars (preferred):
  GOOGLE_OAUTH_REFRESH_TOKEN — refresh token from setup_drive_oauth.py
  GOOGLE_CLIENT_ID           — OAuth client ID
  GOOGLE_CLIENT_SECRET       — OAuth client secret
  GOOGLE_DRIVE_FOLDER_ID     — ID of the target Drive folder

Service account env vars (Shared Drives only):
  GOOGLE_SERVICE_ACCOUNT_JSON — service account key JSON (as string)
  GOOGLE_DRIVE_FOLDER_ID      — ID of the target Drive folder
"""

import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _get_drive_service(
    credentials_json: str = '',
    refresh_token: str = '',
    client_id: str = '',
    client_secret: str = '',
):
    """Authenticate and return a Drive API service object.

    Tries OAuth refresh token first (works with personal Drive),
    falls back to service account (Shared Drives only).
    """
    from googleapiclient.discovery import build

    if refresh_token and client_id and client_secret:
        from google.oauth2.credentials import Credentials

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri='https://oauth2.googleapis.com/token',
        )
        logger.info("Authenticated with OAuth refresh token")
        return build('drive', 'v3', credentials=creds), 'oauth'

    if credentials_json:
        from google.oauth2 import service_account

        creds_dict = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive'],
        )
        logger.info("Authenticated with service account (Shared Drives only)")
        return build('drive', 'v3', credentials=creds), 'service_account'

    raise ValueError("No Drive credentials provided")


def create_or_get_subfolder(
    service, parent_id: str, folder_name: str, use_shared: bool = False,
) -> str:
    """Create a subfolder in Drive (or return existing one's ID)."""
    safe_name = folder_name.replace("\\", "\\\\").replace("'", "\\'")
    query = (
        f"'{parent_id}' in parents and name = '{safe_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = (
        service.files()
        .list(q=query, fields='files(id)', supportsAllDrives=True,
              includeItemsFromAllDrives=True)
        .execute()
    )
    files = results.get('files', [])
    if files:
        return files[0]['id']

    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id],
    }
    folder = (
        service.files()
        .create(body=metadata, fields='id', supportsAllDrives=True)
        .execute()
    )

    # Make viewable by anyone with the link
    try:
        service.permissions().create(
            fileId=folder['id'],
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True,
        ).execute()
    except Exception as e:
        logger.warning(f"Could not set public permissions on subfolder: {e}")

    logger.info(f"Created Drive subfolder: {folder_name}")
    return folder['id']


def upload_screenshots_to_drive(
    screenshots: Dict[str, str],
    folder_id: str,
    credentials_json: str = '',
    subfolder_name: Optional[str] = None,
    refresh_token: str = '',
    client_id: str = '',
    client_secret: str = '',
) -> Dict[str, str]:
    """Upload screenshot files to Google Drive.

    Args:
        screenshots: Dict mapping state name to local file path.
        folder_id: Google Drive folder ID to upload into.
        credentials_json: Service account JSON key as a string.
        subfolder_name: If set, create/use a subfolder with this name.
        refresh_token: OAuth refresh token (preferred over service account).
        client_id: OAuth client ID.
        client_secret: OAuth client secret.

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
        service, auth_type = _get_drive_service(
            credentials_json=credentials_json,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Drive: {e}")
        return {}

    use_shared = auth_type == 'service_account'

    # Use subfolder if requested
    target_folder = folder_id
    if subfolder_name:
        try:
            target_folder = create_or_get_subfolder(
                service, folder_id, subfolder_name, use_shared=use_shared,
            )
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

            file = (
                service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, webViewLink',
                    supportsAllDrives=True,
                )
                .execute()
            )

            # Make the file viewable by anyone with the link
            try:
                service.permissions().create(
                    fileId=file['id'],
                    body={'type': 'anyone', 'role': 'reader'},
                    supportsAllDrives=True,
                ).execute()
            except Exception as e:
                logger.warning(f"  Could not set public permission for {name}: {e}")

            drive_links[name] = file.get('webViewLink', '')
            logger.info(f"  Uploaded: {drive_links[name]}")

        except Exception as e:
            error_str = str(e)
            if 'storageQuotaExceeded' in error_str:
                logger.error(
                    f"  Storage quota exceeded uploading {name}. "
                    "Service accounts have zero storage on regular Drive. "
                    "Fix: use OAuth credentials (run setup_drive_oauth.py) "
                    "or move the folder to a Shared Drive."
                )
                break  # No point retrying — all uploads will fail
            logger.warning(f"  Failed to upload {name}: {e}")

    logger.info(f"Uploaded {len(drive_links)}/{len(screenshots)} screenshots to Drive")
    return drive_links
