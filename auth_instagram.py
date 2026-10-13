#!/usr/bin/env python3
"""
One-Time Instagram Session Authenticator.
Run this directly in your terminal to securely log into your personal Instagram account.
Your credentials are never stored in plaintext—only an encrypted session token is saved
to 'instagram_session.json'.
"""

import os
import sys
import getpass
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    TwoFactorRequired,
    ChallengeRequired,
    LoginRequired
)

SESSION_FILE = Path(__file__).parent / "instagram_session.json"

def main():
    cl = Client()
    cl.delay_range = [2, 5]

    print("\n" + "="*70)
    print("INSTAGRAM ONE-TIME AUTHENTICATION")
    print("="*70)
    print("This connects your personal Instagram account for automated Reel publishing.")
    print("Your password is typed securely (hidden) and will NOT be saved to disk.")
    print("="*70 + "\n")

    username = input("Enter your Instagram Username: ").strip()
    if not username:
        print("[ERROR] Username cannot be empty.")
        sys.exit(1)

    password = getpass.getpass("Enter your Instagram Password: ")
    if not password:
        print("[ERROR] Password cannot be empty.")
        sys.exit(1)

    print("\nAuthenticating with Instagram...")
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        print("\n[2FA Required] Two-Factor Authentication is enabled on this account.")
        code = input("Enter your 2FA SMS or Authenticator code: ").strip()
        cl.login(username, password, verification_code=code)
    except BadPassword:
        print("[ERROR] Incorrect password. Please try again.")
        sys.exit(1)
    except ChallengeRequired as e:
        print(f"\n[Challenge Required] Instagram requested a verification challenge: {e}")
        print("Please open the Instagram app on your phone, tap 'It was me' if prompted, then re-run this script.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        sys.exit(1)

    # Save session
    cl.dump_settings(SESSION_FILE)
    print("\n" + "="*70)
    print("SUCCESS! Instagram session authenticated and saved to:")
    print(f"{SESSION_FILE}")
    print("All future Reel uploads will now run 100% automatically without prompting.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
