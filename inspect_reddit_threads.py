import json
import sys
from pathlib import Path
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

session_data = json.load(open('config/reddit_session.json', encoding='utf-8'))
s = requests.Session()
s.cookies.set('reddit_session', session_data['reddit_session'], domain='.reddit.com')
s.headers.update({'User-Agent': session_data['user_agent']})

threads = [
    ("1. Sonoma Data (googoo-gajoob)", "https://www.reddit.com/r/CarTrackDays/comments/1xa0psf/.json"),
    ("2. VIR PB (bynummustang)", "https://www.reddit.com/r/CarTrackDays/comments/1xaxogc/.json"),
    ("3. C8 Z51 Summit Point (Stoneware_Maker)", "https://www.reddit.com/r/CarTrackDays/comments/1x92hyq/.json"),
    ("4. PalmSizedTriceratops in your HPR Thread", "https://www.reddit.com/r/CarTrackDays/comments/1x8syr3/comment/phq1meo/.json")
]

for title, url in threads:
    print("\n" + "="*70)
    print(title)
    print("="*70)
    r = s.get(url, timeout=10)
    if r.status_code == 200:
        data = r.json()
        post = data[0]['data']['children'][0]['data']
        print(f"Title: {post.get('title')}")
        print(f"Author: /u/{post.get('author')} | Subreddit: r/{post.get('subreddit')}")
        body = post.get('selftext', '')
        print(f"Body:\n{body[:500]}\n")
        
        if len(data) > 1:
            comments = data[1]['data']['children']
            print(f"--- Top Comments ({len(comments)} total) ---")
            for c in comments[:3]:
                cdata = c.get('data', {})
                c_author = cdata.get('author')
                c_body = cdata.get('body', '')
                print(f"[/u/{c_author}]: {c_body[:200]}")
    else:
        print(f"Error fetching: HTTP {r.status_code}")
