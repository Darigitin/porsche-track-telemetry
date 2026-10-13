#!/usr/bin/env python3
"""
Personal Instagram Reel Uploader using instagrapi.
Uploads 9:16 vertical videos directly as Instagram Reels using cached session.
"""

import os
import sys
import argparse
from pathlib import Path
from instagrapi import Client

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SESSION_FILE = Path(__file__).parent / "instagram_session.json"

def get_instagram_client():
    cl = Client()
    cl.delay_range = [2, 5]

    if not SESSION_FILE.exists():
        print(f"\n[ERROR] Instagram session file not found: {SESSION_FILE}")
        print("Please run the one-time authentication script in your terminal first:")
        print("    python auth_instagram.py\n")
        sys.exit(1)

    print(f"Loading cached Instagram session from '{SESSION_FILE}'...")
    try:
        cl.load_settings(SESSION_FILE)
        # Test session validity
        cl.get_timeline_feed()
        print("Session authenticated successfully!")
        return cl
    except Exception as e:
        print(f"\n[ERROR] Cached session expired or invalid: {e}")
        print("Please refresh your session by running:")
        print("    python auth_instagram.py\n")
        sys.exit(1)

def upload_reel(video_path, caption):
    """
    Uploads a 9:16 vertical MP4 video as an Instagram Reel.
    """
    path_obj = Path(video_path)
    if not path_obj.exists():
        print(f"[ERROR] Video file not found: {video_path}")
        return None

    cl = get_instagram_client()
    print(f"\nUploading Reel: '{path_obj.name}'...")
    print(f"Caption preview:\n{caption[:120]}...\n")

    # Auto-generate video thumbnail using FFmpeg if not present
    thumb_path = path_obj.with_suffix('.jpg')
    ffmpeg_bin = r"C:\Users\Darig\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    if not thumb_path.exists():
        print(f"Generating video thumbnail with FFmpeg...")
        import subprocess
        subprocess.run(
            [ffmpeg_bin, "-y", "-ss", "00:00:05", "-i", str(path_obj), "-vframes", "1", "-q:v", "2", str(thumb_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    try:
        media = cl.clip_upload(
            path=path_obj,
            caption=caption,
            thumbnail=thumb_path if thumb_path.exists() else None
        )
        reel_url = f"https://www.instagram.com/reel/{media.code}/"
        print(f"\n" + "="*70)
        print("SUCCESS! Instagram Reel published successfully:")
        print(reel_url)
        print("="*70 + "\n")
        return reel_url
    except Exception as e:
        print(f"[ERROR] Reel upload failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a 9:16 video as an Instagram Reel.")
    parser.add_argument("--file", required=True, help="Path to 9:16 MP4 video")
    parser.add_argument("--caption", required=True, help="Reel caption text with hashtags")
    args = parser.parse_args()

    upload_reel(args.file, args.caption)
