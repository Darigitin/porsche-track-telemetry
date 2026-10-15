#!/usr/bin/env python3
"""
Automated Track Social Media Engine
Extracts highlight moments and hot laps directly from raw track videos using CAN telemetry timestamps.
Supports:
- YouTube 1440p (VP9 quality tier)
- Instagram Reels (9:16 vertical with blurred background + UI safe zones + custom telemetry badges)
"""

import os
import sys
import subprocess
import time

FFMPEG = r"C:\Users\Darig\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
VIDEO_DIR = r"\\THOR\plex\Cayman Videos"
EXPORT_DIR = r"\\THOR\plex\Cayman Videos\Social Exports"

def run_ffmpeg(cmd, desc):
    print(f"\n==========================================")
    print(f"Rendering: {desc}")
    print(f"==========================================")
    t0 = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"ERROR ({res.returncode}):")
        print(res.stderr[-800:])
        return False
    print(f"SUCCESS in {elapsed:.1f}s")
    return True

def clip_highlight_reel(video_file, start_sec, duration_sec, output_name, title_text, stat_badge, subtitle="PORSCHE 718 CAYMAN GT4"):
    """
    Renders a 9:16 vertical Instagram Reel with blurred background and branded telemetry badge.
    """
    out_file = os.path.join(EXPORT_DIR, output_name)
    input_path = os.path.join(VIDEO_DIR, video_file)
    
    if not os.path.exists(input_path):
        print(f"Input video not found: {input_path}")
        return False

    # Formatting time
    m, s = divmod(start_sec, 60)
    start_str = f"00:{int(m):02d}:{s:04.1f}"

    filter_complex = (
        r"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
        r"[0:v]scale=1080:-1[fg];"
        r"[bg][fg]overlay=(W-w)/2:(H-h)/2-60[comp];"
        f"[comp]drawtext=fontfile=C\\\\:/Windows/Fonts/segoeui.ttf:text=\\'{subtitle}\\':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=240,"
        f"drawtext=fontfile=C\\\\:/Windows/Fonts/segoeuib.ttf:text=\\'{title_text}\\':fontcolor=#FFCC00:fontsize=42:x=(w-text_w)/2:y=295,"
        f"drawtext=fontfile=C\\\\:/Windows/Fonts/segoeui.ttf:text=\\'{stat_badge}\\':fontcolor=#AAAAAA:fontsize=28:x=(w-text_w)/2:y=1340[outv]"
    )

    cmd = [
        FFMPEG, "-y",
        "-ss", start_str,
        "-t", str(duration_sec),
        "-i", input_path,
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
    return run_ffmpeg(cmd, f"Instagram Reel: {output_name}")

def clip_hot_lap_youtube(video_file, start_sec, duration_sec, output_name):
    """
    Renders a 1440p landscape YouTube master for an isolated hot lap.
    """
    out_file = os.path.join(EXPORT_DIR, output_name)
    input_path = os.path.join(VIDEO_DIR, video_file)

    if not os.path.exists(input_path):
        print(f"Input video not found: {input_path}")
        return False

    m, s = divmod(start_sec, 60)
    start_str = f"00:{int(m):02d}:{s:04.1f}"

    cmd = [
        FFMPEG, "-y",
        "-ss", start_str,
        "-t", str(duration_sec),
        "-i", input_path,
        "-vf", "scale=2560:1440:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        out_file
    ]
    return run_ffmpeg(cmd, f"YouTube 1440p Master: {output_name}")

if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    print("Automated Social Media Generator Ready.")
    # Example 1: Sunday S2 Best Lap (2:00.12) - The Sunday Follow-up Hot Lap
    print("\nGenerating Sunday S2 2:00.12 Lap...")
    clip_highlight_reel(
        video_file="2026-10-11 HPR-Full Sun-S2 (GT4) - Best 2m00.12s.mp4",
        start_sec=623.0, # 10:23.0
        duration_sec=121.0,
        output_name="2026-10-11_Sun_S2_GT4_2m00s_FollowUp_Reel.mp4",
        title_text="2\\:00.12 CONSISTENCY RUN",
        stat_badge="BACK-TO-BACK SUNDAY PACE"
    )

    # Example 2: Peak Lateral G Moment (1.54G through Turn 13-15 Corkscrew at 81 mph)
    print("\nGenerating Peak Grip Highlight (1.54G)...")
    clip_highlight_reel(
        video_file="2026-10-11 HPR-Full Sun-S2 (GT4) - Best 2m00.12s.mp4",
        start_sec=1091.0, # 18:11.0 (5s before peak 18:21.5)
        duration_sec=20.0,
        output_name="2026-10-11_Sun_S2_1.54G_Peak_Grip_Reel_20s.mp4",
        title_text="1.54G PEAK LATERAL LOAD",
        stat_badge="81 MPH CORKSCREW APEX"
    )

    print(f"\nAll generated files available in: {EXPORT_DIR}")
