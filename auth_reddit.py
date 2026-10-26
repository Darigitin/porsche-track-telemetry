#!/usr/bin/env python3
"""
Interactive Reddit Authentication & Credential Manager.
Verifies your dedicated Reddit credentials and caches them in config/reddit_credentials.json.
"""

import os
import sys
import json
import getpass
import argparse
from pathlib import Path
import praw

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_FILE = Path(__file__).parent / "config" / "reddit_credentials.json"

def authenticate_and_save(client_id, client_secret, username, password, user_agent=None):
    if not user_agent:
        user_agent = f"python:porsche-track-telemetry:v1.0 (by /u/{username})"
    
    print(f"\n[INFO] Validating credentials with Reddit OAuth API for /u/{username}...")
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
        
        # Test authentication
        user = reddit.user.me()
        if user is None:
            print("[ERROR] Authentication failed: user object returned None.")
            return False
            
        print(f"\n✅ Successfully authenticated as: /u/{user.name}")
        print(f"   - Comment Karma : {user.comment_karma}")
        print(f"   - Link Karma    : {user.link_karma}")
        print(f"   - Total Karma   : {user.total_karma}")
        print(f"   - Account ID    : {user.id}")
        
        # Save credentials
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        creds_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
            "user_agent": user_agent
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(creds_data, f, indent=2)
            
        print(f"\n📁 Credentials safely stored in '{CONFIG_FILE}'.")
        return True

    except Exception as e:
        print(f"\n❌ [ERROR] Authentication failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Authenticate dedicated Reddit account for track debriefs.")
    parser.add_argument("--client-id", help="Reddit Script App Client ID")
    parser.add_argument("--client-secret", help="Reddit Script App Client Secret")
    parser.add_argument("--username", help="Reddit username (e.g. mgarrettgt4)")
    parser.add_argument("--password", help="Reddit password")
    parser.add_argument("--check-status", action="store_true", help="Check current authenticated account status")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🏎️  REDDIT DEDICATED ACCOUNT AUTHENTICATOR (u/mgarrettgt4)")
    print("=" * 70)

    if args.check_status:
        if not CONFIG_FILE.exists():
            print(f"[ERROR] No credentials found at '{CONFIG_FILE}'. Run without --check-status first.")
            sys.exit(1)
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            creds = json.load(f)
        try:
            reddit = praw.Reddit(**creds)
            user = reddit.user.me()
            print(f"✅ Current Active User: /u/{user.name}")
            print(f"   - Comment Karma : {user.comment_karma}")
            print(f"   - Link Karma    : {user.link_karma}")
            print(f"   - Total Karma   : {user.total_karma}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Failed to verify credentials: {e}")
            sys.exit(1)

    client_id = args.client_id
    client_secret = args.client_secret
    username = args.username
    password = args.password

    if not client_id:
        print("\n1. Go to: https://www.reddit.com/prefs/apps")
        print("2. Click 'are you a developer? create an app...' at the bottom")
        print("3. Select 'script', name it 'GT4 Telemetry Bot', set redirect URI to 'http://localhost:8080'")
        print("4. Copy the Client ID (string under the app name) and Client Secret.\n")
        client_id = input("Enter Reddit Client ID: ").strip()

    if not client_secret:
        client_secret = input("Enter Reddit Client Secret: ").strip()

    if not username:
        username = input("Enter Reddit Username (default: mgarrettgt4): ").strip() or "mgarrettgt4"

    if not password:
        password = getpass.getpass("Enter Reddit Password: ")

    success = authenticate_and_save(client_id, client_secret, username, password)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
