#!/usr/bin/env python3
"""
Reddit Post & Debrief Uploader for /u/mgarrettgt4.
Publishes telemetry debriefs, track videos, or build sheets to target subreddits
(e.g., r/CarTrackDays, r/Porsche) and automatically drops the value-first
telemetry and YouTube master link in the first comment.
"""

import os
import sys
import json
import time
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

DEFAULT_FIRST_COMMENT_TEMPLATE = """**Vehicle & Setup Summary (2023 Porsche 718 Cayman GT4):**
* **Chassis / Geometry:** Tarett Monoball Camber Plates & Control Arm Ends, Tarett Caster Bushings, Tarett Rear Toe Links w/ Bump Steer Kit
* **Brakes:** GiroDisc 380mm 2-Piece Floating Rotors, Pagid RSL29 endurance pads, Spiegler SS braided lines, Castrol React SRF fluid, Tarett caliper studs
* **Wheels & Tires:** Apex VS-5RE Forged (19x9F / 19x11R) with Vitour Tempesta P1 (265/35R19 front, 295/30R19 rear)
* **Hot Pressures:** 30.5 PSI Front / 31.0 PSI Rear (1.35G sustained, 1.54G peak)
* **Home Track:** High Plains Raceway (Full Course) — PB: 1:59.67

🎥 **Full 1440p Lap with Complete CAN-bus Telemetry HUD** (throttle, brake pressure, lateral Gs, delta timer):
{youtube_url}
"""

def get_authenticated_reddit():
    if not CONFIG_FILE.exists():
        print(f"\n[ERROR] Reddit credentials not found at '{CONFIG_FILE}'.")
        print("Please run 'python auth_reddit.py' first.\n")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)

    reddit = praw.Reddit(**creds)
    user = reddit.user.me()
    if user is None:
        print("[ERROR] Failed to authenticate user from cached credentials.")
        sys.exit(1)
    return reddit, user

def main():
    parser = argparse.ArgumentParser(description="Upload track telemetry debriefs and videos to Reddit.")
    parser.add_argument("--subreddit", default="CarTrackDays", help="Target subreddit (default: CarTrackDays)")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--body-file", help="Path to markdown body text file (for self-post)")
    parser.add_argument("--body", help="Inline markdown body text")
    parser.add_argument("--url", help="External URL (e.g., direct YouTube video link)")
    parser.add_argument("--youtube-url", default="https://youtu.be/PRz7gJhED00", help="YouTube telemetry video URL for first comment")
    parser.add_argument("--skip-comment", action="store_true", help="Do not post the automatic technical spec comment")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without posting")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print(f"🏎️  REDDIT UPLOADER -> r/{args.subreddit}")
    print("=" * 70)

    reddit, user = get_authenticated_reddit()
    print(f"[AUTH] Logged in as: /u/{user.name}")
    print(f"       Karma: {user.comment_karma} comment / {user.link_karma} post")

    # Prepare body text if applicable
    body_content = ""
    if args.body_file:
        body_path = Path(args.body_file)
        if not body_path.exists():
            print(f"[ERROR] Body file not found: {args.body_file}")
            sys.exit(1)
        with open(body_path, "r", encoding="utf-8") as f:
            body_content = f.read()
    elif args.body:
        body_content = args.body

    # Format first comment
    first_comment_text = DEFAULT_FIRST_COMMENT_TEMPLATE.format(youtube_url=args.youtube_url)

    if args.dry_run:
        print("\n[DRY RUN MODE] Simulating post:")
        print(f"Target Subreddit : r/{args.subreddit}")
        print(f"Title            : {args.title}")
        if args.url:
            print(f"Post Type        : Link Post ({args.url})")
        else:
            print(f"Post Type        : Text Post ({len(body_content)} characters)")
            print(f"Body Preview     :\n{body_content[:200]}...\n")
        if not args.skip_comment:
            print("Auto First Comment Preview:")
            print(first_comment_text)
        print("\n✅ Dry run successful. Run without --dry-run to post live.\n")
        return

    sub = reddit.subreddit(args.subreddit)

    print(f"\nSubmitting to r/{args.subreddit}...")
    submission = None
    try:
        if args.url:
            submission = sub.submit(title=args.title, url=args.url)
        else:
            submission = sub.submit(title=args.title, selftext=body_content)

        post_url = f"https://www.reddit.com{submission.permalink}"
        print(f"✅ Post published successfully!")
        print(f"   URL: {post_url}")

        if not args.skip_comment:
            print("\nDropping automated value-first first comment...")
            time.sleep(2)
            comment = submission.reply(first_comment_text)
            print(f"✅ First comment posted! (ID: {comment.id})")

        print("\n" + "=" * 70)
        print("🎉 REDDIT PUBLISHING COMPLETE")
        print(f"View live at: {post_url}")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ [ERROR] Failed to submit post: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
