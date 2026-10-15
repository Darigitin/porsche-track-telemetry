#!/usr/bin/env python3
"""
YouTube Analytics & Channel Performance Inspector.
Pulls real-time metrics for track videos, Shorts, and channel growth using YouTube Data & Analytics APIs.
"""

import os
import sys
import datetime
from googleapiclient.discovery import build
import google.oauth2.credentials
from google.auth.transport.requests import Request

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "youtube_token.json")

def get_services():
    if not os.path.exists(TOKEN_FILE):
        print(f"[ERROR] Token file '{TOKEN_FILE}' not found. Please run 'python auth_youtube.py' first.")
        sys.exit(1)
        
    creds = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
            
    yt_data = build("youtube", "v3", credentials=creds)
    yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)
    return yt_data, yt_analytics

def fetch_channel_summary():
    yt_data, yt_analytics = get_services()
    
    # 1. Channel Details
    ch_res = yt_data.channels().list(part="snippet,statistics", mine=True).execute()
    if not ch_res.get("items"):
        print("[ERROR] No channel found for authenticated account.")
        return
        
    ch = ch_res["items"][0]
    title = ch["snippet"]["title"]
    stats = ch["statistics"]
    
    subs = stats.get("subscriberCount", "Hidden")
    views = stats.get("viewCount", "0")
    videos = stats.get("videoCount", "0")
    
    print("\n" + "="*70)
    print(f"🏎️  YOUTUBE CHANNEL: {title.upper()}")
    print("="*70)
    print(f"• Subscribers:    {int(subs):,}" if subs != "Hidden" else f"• Subscribers:    Hidden")
    print(f"• Total Views:    {int(views):,}")
    print(f"• Total Videos:   {int(videos):,}")
    print("-" * 70)
    
    # 2. Recent Videos / Shorts
    print("\n📊 RECENT TRACK VIDEOS & SHORTS:")
    activities = yt_data.search().list(part="snippet", forMine=True, type="video", maxResults=8, order="date").execute()
    video_ids = [item["id"]["videoId"] for item in activities.get("items", [])]
    
    if video_ids:
        v_res = yt_data.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids)).execute()
        for v in v_res.get("items", []):
            v_title = v["snippet"]["title"]
            v_id = v["id"]
            published = v["snippet"]["publishedAt"][:10]
            v_stats = v.get("statistics", {})
            v_views = int(v_stats.get("viewCount", 0))
            v_likes = int(v_stats.get("likeCount", 0))
            v_comments = int(v_stats.get("commentCount", 0))
            duration = v["contentDetails"]["duration"]
            is_short = "#shorts" in v_title.lower() or "PT" in duration and ("M" not in duration or duration == "PT1M")
            tag = "[SHORT]" if is_short else "[MASTER]"
            
            print(f"\n{tag} {v_title[:60]}")
            print(f"   URL: https://youtu.be/{v_id} | Published: {published}")
            print(f"   Views: {v_views:,}  |  Likes: {v_likes:,}  |  Comments: {v_comments:,}")
            
    # 3. Studio Analytics (Last 28 Days)
    try:
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=28)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        analytics_res = yt_analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost",
            dimensions="day"
        ).execute()
        
        rows = analytics_res.get("rows", [])
        if rows:
            tot_views = sum(r[1] for r in rows)
            tot_min = sum(r[2] for r in rows)
            net_subs = sum(r[4] - r[5] for r in rows)
            avg_sec = (tot_min * 60) / tot_views if tot_views > 0 else 0
            
            print("\n" + "="*70)
            print("📈 STUDIO ANALYTICS (LAST 28 DAYS):")
            print("="*70)
            print(f"• Total Period Views:      {int(tot_views):,}")
            print(f"• Total Watch Time:        {tot_min / 60.0:.1f} hours ({int(tot_min):,} mins)")
            print(f"• Avg View Duration (AVD): {avg_sec:.1f} seconds")
            print(f"• Net Subscriber Growth:   +{net_subs}" if net_subs >= 0 else f"• Net Subscriber Growth:   {net_subs}")
            print("="*70 + "\n")
    except Exception as e:
        print(f"\n[NOTE] Studio Analytics API query notice: {e}")
        print("Note: YouTube Analytics API data updates with a 24-48 hour reporting lag.")

if __name__ == "__main__":
    fetch_channel_summary()
