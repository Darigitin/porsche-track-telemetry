#!/usr/bin/env python3
"""
One-Time YouTube OAuth Authenticator.
Starts an available local callback listener, displays the exact auth URL,
and saves credentials to 'youtube_token.json'.
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secrets.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "youtube_token.json")

def main():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"[ERROR] '{CLIENT_SECRETS_FILE}' not found.")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES
    )

    print("\nStarting local OAuth server...")
    sys.stdout.flush()

    creds = flow.run_local_server(
        host="localhost",
        port=0,
        authorization_prompt_message="\nPLEASE OPEN THIS LINK IN YOUR BROWSER:\n{url}\n",
        success_message="Authentication successful! You can close this tab and return to the terminal.",
        open_browser=False
    )

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print("\n" + "="*80)
    print(f"SUCCESS! Permanent token saved to: {TOKEN_FILE}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
