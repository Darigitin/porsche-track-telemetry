#!/usr/bin/env python3
"""
Daily Community Pulse & Engagement Orchestrator for Matthew Garrett (/u/mgarrettgt4).
Unified 1-click scanner that:
1. Checks Reddit inbox, notifications, and live comment upvotes.
2. Scrapes the live Rennlist PB debrief thread for new member replies.
3. Scouts fresh high-value track discussion threads on r/CarTrackDays & r/Porsche.
4. Generates a consolidated daily action brief in reports/community_pulse_feed.md.
"""

import os
import sys
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import requests

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_DIR = Path(__file__).parent / "config"
REPORTS_DIR = Path(__file__).parent / "reports"
SESSION_FILE = CONFIG_DIR / "reddit_session.json"
PULSE_REPORT = REPORTS_DIR / "community_pulse_feed.md"

RENNLIST_THREAD_URL = (
    "https://rennlist.com/forums/718-gts-4-0-gt4-gt4rs-spyder-25th-anniversary/"
    "1527713-718-cayman-gt4-telemetry-debrief-1-56-55-pb-at-high-plains-raceway.html"
)

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
        "id": "suspension_and_geometry",
        "category": "Suspension, Alignment & Understeer",
        "keywords": [
            "camber", "caster", "toe", "sway bar", "monoball", "tarett", "push", "understeer", 
            "handling", "alignment", "bump steer", "gt4", "drop links", "corner balance"
        ],
        "draft_template": (
            "The factory 718 Cayman GT4 understeer can be completely resolved with proper front geometry. "
            "I did a full monoball conversion with Tarett front camber plates, GT3 lower control arm shims, "
            "and caster-adjustable thrust arm bushings (essential to keep the 265 front tire from rubbing the "
            "fender liner under lock). On the rear, Tarett toe control arms with bump steer locking plates "
            "cured the nervous dynamic rear toe-out under threshold braking. The car now rotates predictably on trail-brake."
        )
    },
    {
        "id": "telemetry_and_data",
        "category": "Data Analysis & VBO / CSV Logging",
        "keywords": [
            "telemetry", "vbo", "aim", "solow", "trackaddict", "circuit tools", "delta", 
            "speed trace", "friction circle", "throttle", "coasting"
        ],
        "draft_template": (
            "I log all my sessions on my 718 GT4 via CAN telemetry and analyze them in Circuit Tools / Python. "
            "When analyzing lap delta traces, look specifically for coasting dead-zones where throttle and brake are both 0%, "
            "and compare minimum apex speeds versus brake release rate. Carrying just 10-15% trail brake down to the apex "
            "often keeps the front axle loaded and cures corner-entry push."
        )
    }
]

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

def check_rennlist_thread():
    print("[1/3] Checking live Rennlist PB debrief thread...")
    result = {
        "url": RENNLIST_THREAD_URL,
        "total_posts": 0,
        "last_post_id": None,
        "last_author": None,
        "last_snippet": "",
        "needs_reply": False
    }
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        req = urllib.request.Request(RENNLIST_THREAD_URL, headers=headers)
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        
        posts = re.findall(r'<div id="post_message_(\d+)">(.*?)<!-- / message -->', html, re.DOTALL)
        result["total_posts"] = len(posts)
        if posts:
            last_pid, last_body = posts[-1]
            idx = html.find(f'id="post_message_{last_pid}"')
            pre_chunk = html[max(0, idx-1500):idx]
            author_match = re.search(r'class="bigusername"[^>]*>(.*?)</a>', pre_chunk)
            last_author = author_match.group(1).strip() if author_match else "Unknown"
            
            clean = re.sub(r'<[^>]+>', ' ', last_body)
            clean = ' '.join(clean.split())
            
            result["last_post_id"] = last_pid
            result["last_author"] = last_author
            result["last_snippet"] = clean[:180]
            result["needs_reply"] = (last_author.lower() != "mgarrettgt4")
    except Exception as e:
        print(f"  [WARN] Rennlist check error: {e}")
    return result

def check_reddit_status():
    print("[2/3] Checking Reddit account, inbox & recent posts...")
    status = {
        "authenticated": False,
        "username": "mgarrettgt4",
        "comment_karma": 0,
        "post_karma": 0,
        "unread_alerts": 0,
        "unread_messages": [],
        "recent_comments": [],
        "session_client": None
    }
    
    if not SESSION_FILE.exists():
        print("  [WARN] Reddit session file not found. Run 'python auth_reddit_session.py'.")
        return status
        
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            
        s = requests.Session()
        s.cookies.set("reddit_session", session_data["reddit_session"], domain=".reddit.com")
        s.headers.update({
            "User-Agent": session_data.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        me_resp = s.get("https://www.reddit.com/api/v1/me.json", timeout=10)
        if me_resp.status_code == 200:
            me_data = me_resp.json()
            status["authenticated"] = True
            status["username"] = me_data.get("name", "mgarrettgt4")
            status["comment_karma"] = me_data.get("comment_karma", 0)
            status["post_karma"] = me_data.get("link_karma", 0)
            status["unread_alerts"] = me_data.get("inbox_count", 0)
            status["session_client"] = s
        else:
            print(f"  [WARN] Reddit /api/v1/me.json returned HTTP {me_resp.status_code}")
            return status

        # Unread messages
        inbox_resp = s.get("https://www.reddit.com/message/unread.json", timeout=10)
        if inbox_resp.status_code == 200:
            for child in inbox_resp.json().get("data", {}).get("children", []):
                data = child.get("data", {})
                status["unread_messages"].append({
                    "id": data.get("id"),
                    "author": data.get("author"),
                    "subject": data.get("subject"),
                    "body": data.get("body"),
                    "subreddit": data.get("subreddit"),
                    "context": f"https://www.reddit.com{data.get('context', '')}",
                    "link_title": data.get("link_title")
                })

        # Recent comments
        comm_resp = s.get(f"https://www.reddit.com/user/{status['username']}/comments.json?limit=6", timeout=10)
        if comm_resp.status_code == 200:
            for child in comm_resp.json().get("data", {}).get("children", []):
                data = child.get("data", {})
                status["recent_comments"].append({
                    "subreddit": data.get("subreddit"),
                    "link_title": data.get("link_title"),
                    "score": data.get("score", 1),
                    "permalink": f"https://www.reddit.com{data.get('permalink', '')}",
                    "body": data.get("body", "")[:120]
                })

    except Exception as e:
        print(f"  [WARN] Reddit check error: {e}")
        
    return status

def scout_reddit_threads(session_client, limit=20):
    print("[3/3] Scouting active track discussion threads on Reddit...")
    opportunities = []
    seen_ids = set()
    now = datetime.now(timezone.utc)

    if session_client:
        for sub_name in TARGET_SUBREDDITS:
            for feed in ["hot", "new"]:
                url = f"https://www.reddit.com/r/{sub_name}/{feed}.json?limit={limit}"
                try:
                    resp = session_client.get(url, timeout=10)
                    if resp.status_code != 200:
                        continue
                    children = resp.json().get("data", {}).get("children", [])
                    for child in children:
                        post = child.get("data", {})
                        pid = post.get("id")
                        if pid in seen_ids or post.get("author") == "mgarrettgt4":
                            continue
                        seen_ids.add(pid)

                        created_utc = post.get("created_utc", 0)
                        post_time = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                        age_hours = (now - post_time).total_seconds() / 3600.0
                        if age_hours > 72.0:
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
                                "age_hours": round(age_hours, 1),
                                "category": best_match["profile"]["category"],
                                "keywords": best_match["matched_keywords"],
                                "draft": best_match["profile"]["draft_template"]
                            })
                except Exception:
                    pass

    # Fallback to combined multi-subreddit RSS feed if unauthenticated or no opportunities returned via JSON
    if not opportunities:
        import time
        import xml.etree.ElementTree as ET
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0'}
        combined_subs = "+".join(TARGET_SUBREDDITS)
        rss_url = f"https://www.reddit.com/r/{combined_subs}/new/.rss?limit=50"
        try:
            r = requests.get(rss_url, headers=headers, timeout=10)
            if r.status_code == 429:
                wait_s = int(float(r.headers.get("x-ratelimit-reset", 15))) + 1
                print(f"  [INFO] Waiting {wait_s}s for Reddit RSS rate-limit reset...")
                time.sleep(wait_s)
                r = requests.get(rss_url, headers=headers, timeout=10)
            if r.status_code == 200:
                root = ET.fromstring(r.text)
                for entry in root.findall('atom:entry', ns):
                    pid_elem = entry.find('atom:id', ns)
                    pid = pid_elem.text if pid_elem is not None else ""
                    if pid in seen_ids:
                        continue
                    seen_ids.add(pid)

                    author_elem = entry.find('atom:author/atom:name', ns)
                    author = (author_elem.text or "unknown").replace("/u/", "") if author_elem is not None else "unknown"
                    if author.lower() == "mgarrettgt4":
                        continue

                    updated_elem = entry.find('atom:updated', ns)
                    age_hours = 12.0
                    if updated_elem is not None and updated_elem.text:
                        try:
                            post_time = datetime.fromisoformat(updated_elem.text)
                            age_hours = (now - post_time).total_seconds() / 3600.0
                        except Exception:
                            pass
                    if age_hours > 72.0:
                        continue

                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text if title_elem is not None else ""
                    link_elem = entry.find('atom:link', ns)
                    link = link_elem.attrib.get('href', '') if link_elem is not None else ""
                    cat_elem = entry.find('atom:category', ns)
                    sub_name = cat_elem.attrib.get('term', 'CarTrackDays') if cat_elem is not None else "CarTrackDays"
                    content_elem = entry.find('atom:content', ns)
                    raw_html = content_elem.text if content_elem is not None else ""
                    selftext = re.sub(r'<[^>]+>', ' ', raw_html)

                    matches = score_and_match(title, selftext)
                    if matches:
                        best_match = matches[0]
                        opportunities.append({
                            "subreddit": sub_name,
                            "title": title,
                            "author": author,
                            "url": link,
                            "score": 1,
                            "num_comments": 0,
                            "age_hours": round(age_hours, 1),
                            "category": best_match["profile"]["category"],
                            "keywords": best_match["matched_keywords"],
                            "draft": best_match["profile"]["draft_template"]
                        })
            else:
                print(f"  [WARN] RSS scout returned HTTP {r.status_code}")
        except Exception as e:
            print(f"  [WARN] RSS scout warning: {e}")

    opportunities.sort(key=lambda x: (len(x["keywords"]), -x["age_hours"]), reverse=True)
    return opportunities

def write_pulse_report(rl_status, rd_status, opps):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(PULSE_REPORT, "w", encoding="utf-8") as f:
        f.write("# ⚡ Daily Community Pulse & Action Brief\n\n")
        f.write(f"*Generated on {now_str} for Matthew Garrett (`/u/mgarrettgt4`)*\n\n")
        f.write("---\n\n")

        # Rennlist Section
        f.write("## 🏁 1. Rennlist Debrief Thread\n\n")
        f.write(f"- **Thread:** [{RENNLIST_THREAD_URL}]({RENNLIST_THREAD_URL})\n")
        f.write(f"- **Total Posts:** {rl_status['total_posts']}\n")
        if rl_status["last_author"]:
            f.write(f"- **Last Post By:** `{rl_status['last_author']}`\n")
            f.write(f"- **Snippet:** *\"{rl_status['last_snippet']}...\"*\n\n")
            if rl_status["needs_reply"]:
                f.write(f"🚨 **ACTION REQUIRED:** New reply from `{rl_status['last_author']}`! [Open Thread]({RENNLIST_THREAD_URL})\n\n")
            else:
                f.write("✅ **Up to date!** You posted the most recent reply in this thread.\n\n")
        else:
            f.write("⚠️ *Could not verify Rennlist status.*\n\n")

        f.write("---\n\n")

        # Reddit Section
        f.write("## 🤖 2. Reddit Account Status (`/u/mgarrettgt4`)\n\n")
        if rd_status["authenticated"]:
            f.write(f"- **Karma:** {rd_status['comment_karma']} Comment | {rd_status['post_karma']} Post\n")
            f.write(f"- **Unread Alerts:** {rd_status['unread_alerts']}\n\n")

            if rd_status["unread_messages"]:
                f.write("### 📥 Unread Notifications:\n\n")
                for msg in rd_status["unread_messages"]:
                    f.write(f"- **From `/u/{msg['author']}` in `r/{msg['subreddit']}`:** {msg['link_title']}\n")
                    f.write(f"  > {msg['body'][:120]}...\n")
                    f.write(f"  [👉 View Context]({msg['context']})\n\n")
            else:
                f.write("✅ **All caught up!** No unread messages in Reddit inbox.\n\n")

            if rd_status["recent_comments"]:
                f.write("### 💬 Recent Comments & Upvotes:\n\n")
                for c in rd_status["recent_comments"]:
                    f.write(f"- **`r/{c['subreddit']}`** (Score: **{c['score']}**): [{c['link_title']}]({c['permalink']})\n")
                    f.write(f"  > *\"{c['body']}...\"*\n\n")
        else:
            f.write("⚠️ *Reddit session cookie expired or not found. Run `python auth_reddit_session.py` to refresh.*\n\n")

        f.write("---\n\n")

        # Opportunities Section
        f.write("## 🎯 3. Today's Top Discussion & Karma Opportunities\n\n")
        if not opps:
            f.write("No fresh high-match threads detected in the last 72 hours. Check back tomorrow!\n")
        else:
            for i, opp in enumerate(opps[:5], 1):
                f.write(f"### {i}. [{opp['title']}]({opp['url']})\n")
                f.write(f"- **Subreddit:** `r/{opp['subreddit']}` | **Author:** `/u/{opp['author']}` | **Age:** {opp['age_hours']}h ago\n")
                f.write(f"- **Engagement:** {opp['score']} upvotes, {opp['num_comments']} comments\n")
                f.write(f"- **Matched Topic:** **{opp['category']}** *(Keywords: `{', '.join(opp['keywords'])}`)*\n\n")
                f.write("**Recommended Technical Reply Draft:**\n")
                f.write(f"> {opp['draft']}\n\n")
                f.write(f"[👉 Click Here to Open Reddit Thread]({opp['url']})\n\n")
                f.write("---\n\n")

    print(f"\n📄 Saved full daily action brief to '{PULSE_REPORT}'.")

def main():
    print("\n" + "=" * 70)
    print("⚡ DAILY COMMUNITY PULSE & ACTION ORCHESTRATOR (Rennlist & Reddit)")
    print("=" * 70 + "\n")

    rl_status = check_rennlist_thread()
    rd_status = check_reddit_status()
    opps = scout_reddit_threads(rd_status["session_client"])

    print("\n" + "-" * 70)
    print("📋 DAILY SUMMARY:")
    print("-" * 70)

    # Rennlist summary
    if rl_status["needs_reply"]:
        print(f"🚨 RENNLIST: New reply from '{rl_status['last_author']}'! Needs response.")
    else:
        print(f"✅ RENNLIST: Up to date ({rl_status['total_posts']} total posts, you have the latest post).")

    # Reddit summary
    if rd_status["authenticated"]:
        print(f"✅ REDDIT:   /u/{rd_status['username']} (Comment Karma: {rd_status['comment_karma']} | Alerts: {rd_status['unread_alerts']})")
    else:
        print(f"⚠️ REDDIT:   Session unauthenticated. Run 'python auth_reddit_session.py'.")

    # Opportunities summary
    print(f"🎯 SCOUT:    {len(opps)} active technical discussions found across r/CarTrackDays & r/Porsche.")

    if opps:
        top = opps[0]
        print(f"\n🔥 Top Recommendation Today:")
        print(f"   [{top['subreddit']}] {top['title'][:65]}...")
        print(f"   Topic: {top['category']} ({top['age_hours']}h ago)")
        print(f"   Link:  {top['url']}")

    write_pulse_report(rl_status, rd_status, opps)
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
