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

def upload_photo(image_path, caption):
    """
    Uploads a single photo to Instagram.
    """
    path_obj = Path(image_path)
    if not path_obj.exists():
        print(f"[ERROR] Photo not found: {image_path}")
        return None

    cl = get_instagram_client()
    print(f"\nUploading Instagram Photo: '{path_obj.name}'...")
    print(f"Caption preview:\n{caption[:140]}...\n")

    try:
        media = cl.photo_upload(
            path=path_obj,
            caption=caption
        )
        post_url = f"https://www.instagram.com/p/{media.code}/"
        print(f"\n" + "="*70)
        print("SUCCESS! Instagram Photo published successfully:")
        print(post_url)
        print("="*70 + "\n")
        return post_url
    except Exception as e:
        print(f"[ERROR] Photo upload failed: {e}")
        return None

def upload_carousel(image_paths, caption):
    """
    Uploads a multi-slide image carousel / album to Instagram.
    """
    resolved_paths = []
    for p in image_paths:
        path_obj = Path(p)
        if not path_obj.exists():
            print(f"[ERROR] Carousel image not found: {p}")
            return None
        resolved_paths.append(path_obj)

    cl = get_instagram_client()
    print(f"\nUploading Instagram Carousel ({len(resolved_paths)} slides)...")
    for i, p in enumerate(resolved_paths, 1):
        print(f"  Slide {i}: {p.name}")
    print(f"\nCaption preview:\n{caption[:140]}...\n")

    try:
        media = cl.album_upload(
            paths=resolved_paths,
            caption=caption
        )
        post_url = f"https://www.instagram.com/p/{media.code}/"
        print(f"\n" + "="*70)
        print("SUCCESS! Instagram Carousel published successfully:")
        print(post_url)
        print("="*70 + "\n")
        return post_url
    except Exception as e:
        print(f"[ERROR] Carousel upload failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Instagram Reels, Photos, or Carousels using cached session.")
    parser.add_argument("--file", help="Path to 9:16 MP4 video for Reel upload")
    parser.add_argument("--photo", help="Path to JPEG/PNG image for Photo upload")
    parser.add_argument("--carousel", nargs="+", help="List of image paths for Carousel upload")
    parser.add_argument("--carousel-dir", help="Directory containing carousel slides to upload in alphabetical order")
    parser.add_argument("--caption", help="Post caption text with hashtags")
    parser.add_argument("--caption-file", help="Path to text file containing post caption")
    args = parser.parse_args()

    caption = args.caption
    if args.caption_file:
        with open(args.caption_file, "r", encoding="utf-8") as f:
            caption = f.read()

    if not caption:
        print("[ERROR] Please provide caption via --caption or --caption-file.")
        sys.exit(1)

    if args.file:
        upload_reel(args.file, caption)
    elif args.photo:
        upload_photo(args.photo, caption)
    elif args.carousel:
        upload_carousel(args.carousel, caption)
    elif args.carousel_dir:
        import glob
        slides = sorted(glob.glob(os.path.join(args.carousel_dir, "slide_*.png")))
        if not slides:
            print(f"[ERROR] No slides matching 'slide_*.png' found in: {args.carousel_dir}")
            sys.exit(1)
        upload_carousel(slides, caption)
    else:
        print("[ERROR] Please provide either --file (for Reel), --photo (for Photo), or --carousel / --carousel-dir (for Carousel).")
        sys.exit(1)
