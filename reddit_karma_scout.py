#!/usr/bin/env python3
"""
Reddit Karma Scout & Opportunity Finder for /u/mgarrettgt4.
Scans r/CarTrackDays, r/Porsche, and r/Porsche_Cayman for active discussions
where Matthew Garrett's real-world 718 Cayman GT4 telemetry and track setup
can provide high-value, authentic technical replies to build organic karma safely.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import praw

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_FILE = Path(__file__).parent / "config" / "reddit_credentials.json"
REPORT_FILE = Path(__file__).parent / "reports" / "reddit_karma_opportunities.md"

TARGET_SUBREDDITS = ["CarTrackDays", "Porsche", "Porsche_Cayman"]

TOPIC_PROFILES = [
    {
        "id": "tires_and_pressures",
        "category": "Tire Pressures & 200TW Compounds",
        "keywords": [
            "tire", "tyre", "tires", "tyres", "200tw", "vitour", "cup 2", "cup2", 
            "a052", "re-71rs", "re71r", "pressure", "cold psi", "hot psi", "psi", 
            "temperatures", "greasy", "scrub", "pyrometer"
        ],
        "draft_template": (
            "I run a 2023 718 Cayman GT4 on 19\" Apex VS-5RE forged wheels with Vitour Tempesta P1s "
            "(265/35R19 front, 295/30R19 rear). For 200TW tires like these, I start cold at 23.5–24.0 PSI "
            "to hit an exact hot target of 30.5 PSI Front / 31.0 PSI Rear. In my telemetry, crossing over "
            "32.5 PSI hot immediately causes mid-corner greasy slip and costs tenths on corner exit. "
            "Dials in sustained 1.35G and 1.54G peak cornering without rolling over onto the sidewalls."
        )
    },
    {
        "id": "brakes_and_fluid",
        "category": "Brakes, Pads & Caliper Pucks",
        "keywords": [
            "brake", "brakes", "pad", "pads", "rotor", "rotors", "fade", "srf", "fluid", 
            "pagid", "rsl29", "ferodo", "girodisc", "caliper", "calipers", "puck", "pucks", 
            "piston", "spiegler", "soft pedal", "spongy"
        ],
        "draft_template": (
            "On my 718 GT4, I run GiroDisc 380mm floating rotors with Pagid RSL29 endurance pads and "
            "Castrol React SRF fluid, coupled with Spiegler stainless lines and Tarett caliper studs. "
            "If you track a 718/981 Cayman or 991, keep a close eye on the factory Brembo ceramic caliper pucks—"
            "they crack under severe track heat. Instead of spending $2k+ on boutique titanium pistons, "
            "Girodisc 1mm titanium pad heat shields (TS-1741) or Demon Speed / AutoQuest replacement pucks "
            "drastically lower thermal transfer to the pistons and protect your dust boots and fluid."
        )
    },
    {
        "id": "suspension_and_understeer",
        "category": "Suspension, Alignment & 718 Understeer",
        "keywords": [
            "camber", "caster", "toe", "sway bar", "monoball", "tarett", "push", "understeer", 
            "handling", "alignment", "bump steer", "gt4", "drop links", "corner balance"
        ],
        "draft_template": (
            "The factory 718 Cayman GT4 understeer can be completely resolved with proper front geometry. "
            "I did a full monoball conversion with Tarett front camber plates, GT3 lower control arm shims, "
            "and caster-adjustable thrust arm bushings (essential to keep the 265 front tire from rubbing the "
            "fender liner under lock). On the rear, Tarett toe control arms with the bump steer locking plates "
            "cured the nervous dynamic rear toe-out under threshold braking. The car now rotates predictably on trail-brake."
        )
    },
    {
        "id": "track_hpr",
        "category": "High Plains Raceway / Colorado Track Days",
        "keywords": [
            "hpr", "high plains", "high plains raceway", "colorado", "pueblo", "rmr", 
            "rocky mountain", "denver"
        ],
        "draft_template": (
            "High Plains Raceway is my home track (running a 1:59.67 PB in my 718 GT4). At Colorado's 5,000+ ft "
            "elevation, ambient heat and thinner air demand serious fluid management—Castrol SRF has been rock solid. "
            "Key time on the full course is in Turn 4 (deep trail braking curing understeer down to the apex) "
            "and maximizing exit speed out of Turn 3 onto the 2,838 ft back straight."
        )
    }
]

SESSION_FILE = Path(__file__).parent / "config" / "reddit_session.json"

def score_and_match(title, text):
    content = (title + " " + text).lower()
    matches = []
    for profile in TOPIC_PROFILES:
        matched_kw = [kw for kw in profile["keywords"] if kw in content]
        if matched_kw:
            score = len(matched_kw)
            matches.append({
                "profile": profile,
                "score": score,
                "matched_keywords": matched_kw
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def scout_subreddits(limit=25):
    opportunities = []
    seen_ids = set()
    now = datetime.now(timezone.utc)

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            creds = json.load(f)
        reddit = praw.Reddit(**creds)
        user = reddit.user.me()
        print(f"\n[INFO] Authenticated via OAuth as /u/{user.name} (Comment Karma: {user.comment_karma}, Post Karma: {user.link_karma})")
        print(f"[INFO] Scanning target subreddits: {', '.join(TARGET_SUBREDDITS)}...")

        for sub_name in TARGET_SUBREDDITS:
            sub = reddit.subreddit(sub_name)
            posts = list(sub.hot(limit=limit)) + list(sub.new(limit=limit))
            for post in posts:
                if post.id in seen_ids:
                    continue
                seen_ids.add(post.id)
                post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                age_days = (now - post_time).total_seconds() / 86400.0
                if age_days > 7.0:
                    continue
                matches = score_and_match(post.title, post.selftext)
                if matches:
                    best_match = matches[0]
                    opportunities.append({
                        "subreddit": sub_name,
                        "title": post.title,
                        "author": str(post.author),
                        "url": f"https://www.reddit.com{post.permalink}",
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "age_hours": round((now - post_time).total_seconds() / 3600.0, 1),
                        "category": best_match["profile"]["category"],
                        "keywords": best_match["matched_keywords"],
                        "draft": best_match["profile"]["draft_template"]
                    })
    elif SESSION_FILE.exists():
        import requests
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        username = session_data.get("username", "mgarrettgt4")
        print(f"\n[INFO] Authenticated via Browser Session as /u/{username}")
        print(f"[INFO] Scanning target subreddits: {', '.join(TARGET_SUBREDDITS)}...")

        s = requests.Session()
        s.cookies.set("reddit_session", session_data["reddit_session"], domain=".reddit.com")
        s.headers.update({
            "User-Agent": session_data.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })

        for sub_name in TARGET_SUBREDDITS:
            for feed in ["hot", "new"]:
                url = f"https://www.reddit.com/r/{sub_name}/{feed}.json?limit={limit}"
                try:
                    resp = s.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        children = data.get("data", {}).get("children", [])
                        for child in children:
                            post = child.get("data", {})
                            pid = post.get("id")
                            if pid in seen_ids:
                                continue
                            seen_ids.add(pid)
                            created_utc = post.get("created_utc", 0)
                            post_time = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                            age_days = (now - post_time).total_seconds() / 86400.0
                            if age_days > 7.0:
                                continue
                            title = post.get("title", "")
                            selftext = post.get("selftext", "")
                            matches = score_and_match(title, selftext)
                            if matches:
                                best_match = matches[0]
                                opportunities.append({
                                    "subreddit": sub_name,
                                    "title": title,
                                    "author": post.get("author", "unknown"),
                                    "url": f"https://www.reddit.com{post.get('permalink', '')}",
                                    "score": post.get("score", 1),
                                    "num_comments": post.get("num_comments", 0),
                                    "age_hours": round((now - post_time).total_seconds() / 3600.0, 1),
                                    "category": best_match["profile"]["category"],
                                    "keywords": best_match["matched_keywords"],
                                    "draft": best_match["profile"]["draft_template"]
                                })
                except Exception as e:
                    print(f"[WARN] Could not fetch r/{sub_name}/{feed}: {e}")
    else:
        print(f"\n[ERROR] Neither OAuth credentials nor browser session found.")
        print("Run 'python auth_reddit_session.py' to paste your browser cookie.\n")
        sys.exit(1)

    # Sort opportunities by highest relevance and recent engagement
    opportunities.sort(key=lambda x: (len(x["keywords"]), -x["age_hours"]), reverse=True)
    return opportunities

def write_report(opportunities):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🎯 Reddit Organic Karma Opportunities\n\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for `/u/mgarrettgt4`*\n\n")
        f.write("Posting 2–3 authentic, data-backed replies below will build 50–100+ comment karma quickly ")
        f.write("and establish driver authority in track communities without any spam risk.\n\n")
        f.write("---\n\n")

        if not opportunities:
            f.write("No matching high-relevance threads found right now. Try re-running tomorrow!\n")
            return

        for i, opp in enumerate(opportunities[:10], 1):
            f.write(f"### {i}. [{opp['title']}]({opp['url']})\n")
            f.write(f"- **Subreddit:** `r/{opp['subreddit']}` | **Author:** `/u/{opp['author']}` | **Age:** {opp['age_hours']}h ago\n")
            f.write(f"- **Engagement:** {opp['score']} upvotes, {opp['num_comments']} comments\n")
            f.write(f"- **Matched Topic:** **{opp['category']}** *(Keywords: `{', '.join(opp['keywords'])}`)*\n\n")
            f.write("**Suggested Authentic Reply Draft:**\n")
            f.write(f"> {opp['draft']}\n\n")
            f.write(f"[👉 Click Here to Open Reddit Thread]({opp['url']})\n\n")
            f.write("---\n\n")

    print(f"\n📄 Saved full opportunity report to '{REPORT_FILE}'.")

def main():
    parser = argparse.ArgumentParser(description="Find high-karma Reddit opportunities for track telemetry expertise.")
    parser.add_argument("--limit", type=int, default=30, help="Posts to scan per subreddit (default: 30)")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🏁 REDDIT ORGANIC KARMA SCOUT (r/CarTrackDays, r/Porsche)")
    print("=" * 70)

    try:
        opps = scout_subreddits(limit=args.limit)
        print(f"\nFound {len(opps)} relevant discussion threads across target subreddits!\n")

        # Display top 3 directly in CLI
        for i, opp in enumerate(opps[:3], 1):
            print(f"[{i}] r/{opp['subreddit']}: {opp['title'][:65]}...")
            print(f"    Topic: {opp['category']} (Matched: {', '.join(opp['keywords'][:4])})")
            print(f"    Link:  {opp['url']}")
            print(f"    Draft preview: {opp['draft'][:100]}...\n")

        write_report(opps)
        print("=" * 70)
        print("💡 TIP: Pick 2-3 links in reports/reddit_karma_opportunities.md, tweak and submit.")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ [ERROR] Failed to scout Reddit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
