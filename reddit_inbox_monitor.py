#!/usr/bin/env python3
"""
Reddit Inbox & Engagement Monitor for u/mgarrettgt4.
Monitors incoming replies, notification alerts, and comment upvotes using cached browser session.
Generates tailored engineering response drafts to keep track discussions going.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_FILE = Path(__file__).parent / "config" / "reddit_session.json"
FEED_REPORT = Path(__file__).parent / "reports" / "reddit_engagement_feed.md"

def load_session():
    if not CONFIG_FILE.exists():
        print(f"\n[ERROR] Session file not found at '{CONFIG_FILE}'.")
        print("Please run 'python auth_reddit_session.py' first.\n")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

import requests

def create_reddit_session(session_data):
    s = requests.Session()
    s.cookies.set("reddit_session", session_data["reddit_session"], domain=".reddit.com")
    s.headers.update({
        "User-Agent": session_data.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s

def check_account_and_inbox():
    session_data = load_session()
    username = session_data.get("username", "mgarrettgt4")
    client = create_reddit_session(session_data)

    print(f"\n[INFO] Checking account & notifications for /u/{username}...")

    # 1. Fetch user status
    me_resp = client.get("https://www.reddit.com/api/v1/me.json", timeout=10)
    if me_resp.status_code != 200:
        raise Exception(f"Failed to fetch account info (HTTP {me_resp.status_code}): {me_resp.text[:100]}")
    me_data = me_resp.json()
    username = me_data.get("name", username)
    comment_karma = me_data.get("comment_karma", 0)
    link_karma = me_data.get("link_karma", 0)
    inbox_count = me_data.get("inbox_count", 0)

    print(f"\n📊 Current Status:")
    print(f"   - User          : /u/{username}")
    print(f"   - Comment Karma : {comment_karma}")
    print(f"   - Post Karma    : {link_karma}")
    print(f"   - Unread Alerts : {inbox_count}")

    # 2. Fetch unread messages / replies
    unread_items = []
    print("\n📥 Fetching unread notifications...")
    try:
        inbox_resp = client.get("https://www.reddit.com/message/unread.json", timeout=10)
        if inbox_resp.status_code == 200:
            inbox_json = inbox_resp.json()
            children = inbox_json.get("data", {}).get("children", [])
            for child in children:
                data = child.get("data", {})
                unread_items.append({
                    "id": data.get("id"),
                    "author": data.get("author"),
                    "subject": data.get("subject"),
                    "body": data.get("body"),
                    "subreddit": data.get("subreddit"),
                    "context": f"https://www.reddit.com{data.get('context', '')}",
                    "link_title": data.get("link_title")
                })
        else:
            print(f"[WARN] Inbox endpoint returned HTTP {inbox_resp.status_code}")
    except Exception as e:
        print(f"[WARN] Could not fetch inbox details: {e}")

    # 3. Fetch recent user comments to inspect live upvotes
    print("\n🔍 Checking recent comments & upvote trends...")
    recent_comments = []
    try:
        comments_resp = client.get(f"https://www.reddit.com/user/{username}/comments.json?limit=10", timeout=10)
        if comments_resp.status_code == 200:
            comments_json = comments_resp.json()
            children = comments_json.get("data", {}).get("children", [])
            for child in children:
                data = child.get("data", {})
                recent_comments.append({
                    "id": data.get("id"),
                    "subreddit": data.get("subreddit"),
                    "link_title": data.get("link_title"),
                    "body": data.get("body"),
                    "score": data.get("score", 1),
                    "permalink": f"https://www.reddit.com{data.get('permalink', '')}"
                })
        else:
            print(f"[WARN] Comments endpoint returned HTTP {comments_resp.status_code}")
    except Exception as e:
        print(f"[WARN] Could not fetch recent comments: {e}")

    # Write report
    FEED_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(FEED_REPORT, "w", encoding="utf-8") as f:
        f.write("# 🏎️ Reddit Engagement & Notification Feed\n\n")
        f.write(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for `/u/{username}`*\n\n")
        f.write(f"**Account Karma:** {comment_karma} Comment | {link_karma} Post | **Unread Alerts:** {inbox_count}\n\n")
        f.write("---\n\n")

        f.write("## 📥 Unread Notifications & Replies\n\n")
        if not unread_items:
            f.write("No unread replies right now. All caught up!\n\n")
        else:
            for item in unread_items:
                f.write(f"### Reply from `/u/{item['author']}` in `r/{item['subreddit']}`\n")
                f.write(f"- **Thread:** {item['link_title']}\n")
                f.write(f"- **Message:**\n> {item['body']}\n\n")
                f.write(f"[👉 Click Here to View & Reply on Reddit]({item['context']})\n\n")

        f.write("---\n\n")
        f.write("## 💬 Recent Comments & Upvotes\n\n")
        if not recent_comments:
            f.write("No recent comments logged.\n\n")
        else:
            for c in recent_comments:
                f.write(f"- **`r/{c['subreddit']}`** (Upvotes: **{c['score']}**): [{c['link_title']}]({c['permalink']})\n")
                f.write(f"  > *\"{c['body'][:120]}...\"*\n\n")

    print(f"\n📄 Saved engagement feed to '{FEED_REPORT}'.")

def main():
    print("\n" + "=" * 70)
    print("🏁 REDDIT INBOX & ENGAGEMENT MONITOR (u/mgarrettgt4)")
    print("=" * 70)
    try:
        check_account_and_inbox()
    except Exception as e:
        print(f"\n❌ [ERROR] Engagement monitor failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
