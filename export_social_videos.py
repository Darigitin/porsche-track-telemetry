#!/usr/bin/env python3
"""
Automated Social Media Video Generator for Porsche Track Precision App recordings.
Converts track recordings into:
1. YouTube-optimized 1440p (VP09/AV01 tier) 16:9 video
2. Instagram-optimized 9:16 Vertical Reels with aesthetic blurred background & safe-zone overlays
3. 44s Highlight Reel focused on the finish line PB crossing
"""

import os
import sys
import subprocess
import time

FFMPEG = r"C:\Users\Darig\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"

SOURCE_VIDEO = r"\\THOR\plex\Cayman Videos\2026-10-10 HPR-Full Sat-S2 Lap 8 (GT4) - 1m59.624s [PB Clip].mp4"
EXPORT_DIR = r"\\THOR\plex\Cayman Videos\Social Exports"

def run_cmd(cmd, desc):
    print(f"\n==========================================")
    print(f"Starting: {desc}")
    print(f"==========================================")
    t0 = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"ERROR ({res.returncode}) while processing {desc}:")
        print(res.stderr[-800:])
        return False
    print(f"SUCCESS in {elapsed:.1f}s")
    return True

def create_youtube_1440p():
    out_file = os.path.join(EXPORT_DIR, "2026-10-10_HPR_GT4_1m59s_PB_YouTube_1440p.mp4")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 100 * 1024 * 1024:
        print(f"YouTube 1440p master already exists ({os.path.getsize(out_file)/(1024*1024):.1f} MB). Skipping re-encode.")
        return True, out_file

    cmd = [
        FFMPEG, "-y",
        "-i", SOURCE_VIDEO,
        "-vf", "scale=2560:1440:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        out_file
    ]
    return run_cmd(cmd, "YouTube 1440p Upscale (Forces High-Bitrate VP9 Codec)"), out_file

def create_instagram_full_reel():
    out_file = os.path.join(EXPORT_DIR, "2026-10-10_HPR_GT4_1m59s_PB_Instagram_FullLap_9x16.mp4")
    
    # Complex filter:
    # 1. Background: scale to fill 1080x1920, crop, heavy blur, darken by 22%
    # 2. Foreground: scale to 1080:-1, center vertically (offset -60px for Instagram safe zone)
    # 3. Clean typographic overlays
    filter_complex = (
        r"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
        r"[0:v]scale=1080:-1[fg];"
        r"[bg][fg]overlay=(W-w)/2:(H-h)/2-60[comp];"
        r"[comp]drawtext=fontfile=C\\:/Windows/Fonts/segoeui.ttf:text=\'PORSCHE 718 CAYMAN GT4\':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=240,"
        r"drawtext=fontfile=C\\:/Windows/Fonts/segoeuib.ttf:text=\'1\\:59.62 NEW PB @ HIGH PLAINS\':fontcolor=#FFCC00:fontsize=42:x=(w-text_w)/2:y=295,"
        r"drawtext=fontfile=C\\:/Windows/Fonts/segoeui.ttf:text=\'SUB-2\\:00 LAP RECORD\':fontcolor=#AAAAAA:fontsize=28:x=(w-text_w)/2:y=1340[outv]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-i", SOURCE_VIDEO,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        out_file
    ]
    return run_cmd(cmd, "Instagram 9:16 Full Lap Reel (Blurred Background + UI Safe Zones)"), out_file

def create_instagram_highlight_reel():
    out_file = os.path.join(EXPORT_DIR, "2026-10-10_HPR_GT4_1m59s_PB_Instagram_Highlight_44s.mp4")
    
    # Start at 75s (Turn 9 downhill roller coaster onto main straight across line at 119.5s)
    filter_complex = (
        r"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
        r"[0:v]scale=1080:-1[fg];"
        r"[bg][fg]overlay=(W-w)/2:(H-h)/2-60[comp];"
        r"[comp]drawtext=fontfile=C\\:/Windows/Fonts/segoeui.ttf:text=\'PORSCHE 718 CAYMAN GT4\':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=240,"
        r"drawtext=fontfile=C\\:/Windows/Fonts/segoeuib.ttf:text=\'FINISH LINE SPRINT  |  1\\:59.62 PB\':fontcolor=#FFCC00:fontsize=40:x=(w-text_w)/2:y=295,"
        r"drawtext=fontfile=C\\:/Windows/Fonts/segoeui.ttf:text=\'WATCH THE LAP TIME CLOCK\':fontcolor=#AAAAAA:fontsize=28:x=(w-text_w)/2:y=1340[outv]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-ss", "00:01:15",
        "-to", "00:01:59.5",
        "-i", SOURCE_VIDEO,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        out_file
    ]
    return run_cmd(cmd, "Instagram 9:16 44s Punchy Highlight Reel (Downhill + Finish Line PB)"), out_file

if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    create_youtube_1440p()
    create_instagram_full_reel()
    create_instagram_highlight_reel()
    
    print("\nAll exports complete! Files saved to:")
    print(EXPORT_DIR)
