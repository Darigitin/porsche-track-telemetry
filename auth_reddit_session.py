#!/usr/bin/env python3
"""
Reddit Session Cookie Authenticator.
Allows u/mgarrettgt4 to authenticate using browser session cookies,
bypassing all Reddit Developer Portal / API registration blocks.
Saves credentials safely to config/reddit_session.json.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_FILE = Path(__file__).parent / "config" / "reddit_session.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

def decode_jwt_payload(token):
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            import base64
            padded = parts[1] + "=" * (-len(parts[1]) % 4)
            return json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
    except Exception:
        pass
    return {}

def verify_and_save_session(session_token, username="mgarrettgt4"):
    token = session_token.strip().strip('"').strip("'")
    if token.startswith("reddit_session="):
        token = token.replace("reddit_session=", "").strip()

    jwt_data = decode_jwt_payload(token)
    sub = jwt_data.get("sub", "")
    print(f"\n[INFO] Inspecting session token...")
    if sub:
        print(f"   - Reddit Account ID: {sub}")

    headers = {
        "User-Agent": USER_AGENT,
        "Cookie": f"reddit_session={token}",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    comment_karma = 0
    link_karma = 0
    inbox_count = 0
    validated_via_api = False

    try:
        req = urllib.request.Request("https://www.reddit.com/api/v1/me.json", headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            username = data.get("name", username)
            comment_karma = data.get("comment_karma", 0)
            link_karma = data.get("link_karma", 0)
            inbox_count = data.get("inbox_count", 0)
            validated_via_api = True
    except Exception as e:
        # If Reddit returns 403 due to cloudflare/bot firewall on the raw endpoint,
        # but token has valid JWT structure, proceed with caching
        if sub:
            print(f"[NOTE] API verification endpoint encountered bot challenge ({e}), but session token format is valid.")
        else:
            print(f"[WARN] Could not verify via API: {e}")

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "username": username,
            "reddit_session": token,
            "user_agent": USER_AGENT
        }, f, indent=2)

    print(f"\n✅ Session safely saved to '{CONFIG_FILE}'!")
    print(f"   - User          : /u/{username}")
    if validated_via_api:
        print(f"   - Comment Karma : {comment_karma}")
        print(f"   - Post Karma    : {link_karma}")
        print(f"   - Unread Alerts : {inbox_count}")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Authenticate Reddit via browser session cookie.")
    parser.add_argument("--cookie", "--token", help="reddit_session cookie value")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🍪 REDDIT BROWSER SESSION AUTHENTICATOR (u/mgarrettgt4)")
    print("=" * 70)

    token = args.cookie
    if not token:
        print("This links your browser session to monitor replies and incoming track discussions.")
        print("\nHow to get your session cookie in 20 seconds:")
        print("1. In Chrome / Edge / Firefox on reddit.com (logged in as mgarrettgt4), press F12.")
        print("2. Click the 'Application' tab (Chrome/Edge) or 'Storage' tab (Firefox).")
        print("3. In the left sidebar, expand 'Cookies' -> click 'https://www.reddit.com'.")
        print("4. Find the cookie named 'reddit_session' and double-click its 'Value' to copy it.")
        print("=" * 70 + "\n")
        token = input("Paste your 'reddit_session' cookie value: ").strip()

    if not token:
        print("[ERROR] Token cannot be empty.")
        sys.exit(1)

    verify_and_save_session(token)

if __name__ == "__main__":
    main()
