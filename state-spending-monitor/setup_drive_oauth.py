#!/usr/bin/env python3
"""
One-time setup: generate a Google Drive OAuth refresh token.

This creates the credentials needed for the RHTP screenshot uploader
to write to your personal Google Drive (instead of a service account,
which has zero storage quota on regular Drive).

Prerequisites:
  1. Go to https://console.cloud.google.com/apis/credentials
  2. Create an OAuth 2.0 Client ID (type: Desktop app)
  3. Download the JSON — you'll need the client_id and client_secret

Usage:
  pip install google-auth-oauthlib
  python setup_drive_oauth.py --client-id YOUR_ID --client-secret YOUR_SECRET

After running, add these three GitHub Actions secrets:
  GOOGLE_CLIENT_ID          — the client ID you provided
  GOOGLE_CLIENT_SECRET      — the client secret you provided
  GOOGLE_OAUTH_REFRESH_TOKEN — the refresh token printed by this script
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Generate Google Drive OAuth refresh token',
    )
    parser.add_argument('--client-id', required=True, help='OAuth client ID')
    parser.add_argument('--client-secret', required=True, help='OAuth client secret')
    args = parser.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Install required package: pip install google-auth-oauthlib")
        sys.exit(1)

    # Build client config from command-line args
    client_config = {
        'installed': {
            'client_id': args.client_id,
            'client_secret': args.client_secret,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'redirect_uris': ['http://localhost'],
        },
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
    )

    # Opens browser for user to sign in and authorize
    creds = flow.run_local_server(port=0)

    print()
    print('=' * 60)
    print('SUCCESS — Add these GitHub Actions secrets:')
    print('=' * 60)
    print()
    print(f'GOOGLE_CLIENT_ID={args.client_id}')
    print(f'GOOGLE_CLIENT_SECRET={args.client_secret}')
    print(f'GOOGLE_OAUTH_REFRESH_TOKEN={creds.refresh_token}')
    print()
    print('The refresh token does not expire unless you revoke it.')
    print('You can keep your existing GOOGLE_DRIVE_FOLDER_ID secret.')
    print()


if __name__ == '__main__':
    main()
