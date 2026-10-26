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
import argparse

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
        f"[comp]drawtext=fontfile=C\\\\:/Windows/Fonts/segoeui.ttf:text=\\'{subtitle}\\':expansion=none:fontcolor=white:fontsize=36:x=(w-text_w)/2:y=240,"
        f"drawtext=fontfile=C\\\\:/Windows/Fonts/segoeuib.ttf:text=\\'{title_text}\\':expansion=none:fontcolor=#FFCC00:fontsize=42:x=(w-text_w)/2:y=295,"
        f"drawtext=fontfile=C\\\\:/Windows/Fonts/segoeui.ttf:text=\\'{stat_badge}\\':expansion=none:fontcolor=#AAAAAA:fontsize=28:x=(w-text_w)/2:y=1340[outv]"
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
    success = run_ffmpeg(cmd, f"Instagram Reel: {output_name}")
    if success:
        thumb_file = os.path.splitext(out_file)[0] + ".jpg"
        thumb_cmd = [
            FFMPEG, "-y",
            "-ss", "00:00:05",
            "-i", out_file,
            "-vframes", "1",
            "-q:v", "2",
            thumb_file
        ]
        subprocess.run(thumb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return success

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
    
    parser = argparse.ArgumentParser(description="Automated Track Social Media Engine")
    parser.add_argument("--peak-grip", action="store_true", help="Render only the 20s 1.54G Corkscrew Peak Grip Reel")
    parser.add_argument("--followup", action="store_true", help="Render only the Sunday S2 2:00.12 Follow-Up Reel")
    parser.add_argument("--trail-braking", action="store_true", help="Render 20s Turn 4 Trail-Braking Reel")
    parser.add_argument("--wot", action="store_true", help="Render 20s Turn 3 Carousel Exit to Back Straight WOT Reel")
    parser.add_argument("--oversteer", action="store_true", help="Render 20s Chassis Rotation / Oversteer Catch Reel")
    parser.add_argument("--gear-delta", action="store_true", help="Render 20s Turn 4 3rd vs 4th Gear Selection Reel")
    parser.add_argument("--all-next-week", action="store_true", help="Render all Phase 2 reels (Trail-Braking and WOT)")
    parser.add_argument("--phase3", action="store_true", help="Render all Phase 3 reels (Oversteer Rotation and 3rd Gear Delta)")
    args = parser.parse_args()

    render_peak = args.peak_grip
    render_followup = args.followup
    render_trail = args.trail_braking or args.all_next_week
    render_wot = args.wot or args.all_next_week
    render_oversteer = args.oversteer or args.phase3
    render_gear_delta = args.gear_delta or args.phase3

    if not any([args.peak_grip, args.followup, args.trail_braking, args.wot, args.all_next_week, args.oversteer, args.gear_delta, args.phase3]):
        render_peak = True
        render_followup = True

    print("Automated Social Media Generator Ready.")

    # Example 1: Sunday S2 Best Lap (2:00.12) - The Sunday Follow-up Hot Lap
    if render_followup:
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
    if render_peak:
        print("\nGenerating Peak Grip Highlight (1.54G)...")
        clip_highlight_reel(
            video_file="2026-10-11 HPR-Full Sun-S2 (GT4) - Best 2m00.12s.mp4",
            start_sec=1091.0, # 18:11.0 (5s before peak 18:21.5)
            duration_sec=20.0,
            output_name="2026-10-11_Sun_S2_1.54G_Peak_Grip_Reel_20s.mp4",
            title_text="1.54G PEAK LATERAL LOAD",
            stat_badge="81 MPH CORKSCREW APEX"
        )

    # Next Week 1: Turn 4 Trail-Braking CAN Telemetry Breakdown
    if render_trail:
        print("\nGenerating Tuesday Clip: Turn 4 Trail-Braking (-1.25G spike, 15% apex trail)...")
        clip_highlight_reel(
            video_file="2026-10-10 HPR-Full Sat-S2 Lap 8 (GT4) - 1m59.624s [PB Clip].mp4",
            start_sec=52.0,
            duration_sec=20.0,
            output_name="2026-10-10_Sat_S2_GT4_Trail_Braking_Reel_20s.mp4",
            title_text="TRAIL-BRAKING TELEMETRY",
            stat_badge="-1.25G SPIKE | 15% APEX TRAIL"
        )

    # Next Week 2: Turn 3 Carousel Exit to Back Straight (WOT Commitment)
    if render_wot:
        print("\nGenerating Thursday Clip: Turn 3 Carousel Exit to 134.8 MPH Back Straight (WOT Commitment)...")
        clip_highlight_reel(
            video_file="2026-10-10 HPR-Full Sat-S2 Lap 8 (GT4) - 1m59.624s [PB Clip].mp4",
            start_sec=35.0,
            duration_sec=20.0,
            output_name="2026-10-10_Sat_S2_GT4_WOT_Acceleration_Reel_20s.mp4",
            title_text="36.6% WOT COMMITMENT",
            stat_badge="134.8 MPH BACK STRAIGHT EXIT"
        )

    # Phase 3 Clip 1: Chassis Rotation & Oversteer Catch (Sat-S1 @ 15:02.9 -> 893.0s)
    if render_oversteer:
        print("\nGenerating Phase 3 Tuesday Clip: Mid-Engine Chassis Rotation & Oversteer Catch (0.24 Oversteer, 1.08G)...")
        clip_highlight_reel(
            video_file="2026-10-10 HPR-Full Sat-S1 (GT4) - Best 2m00.77s.mp4",
            start_sec=893.0,
            duration_sec=20.0,
            output_name="2026-10-10_Sat_S1_GT4_Oversteer_Rotation_Reel_20s.mp4",
            title_text="MID-ENGINE ROTATION",
            stat_badge="0.24 OVERSTEER | 1.08G APEX SLIP"
        )

    # Phase 3 Clip 2: Turn 4 3rd vs 4th Gear Selection Revelation (+0.300s saved)
    if render_gear_delta:
        print("\nGenerating Phase 3 Thursday Clip: Turn 4 3rd vs 4th Gear Selection (+0.300s, 5411 RPM)...")
        clip_highlight_reel(
            video_file="2026-10-10 HPR-Full Sat-S2 Lap 8 (GT4) - 1m59.624s [PB Clip].mp4",
            start_sec=48.0,
            duration_sec=20.0,
            output_name="2026-10-10_Sat_S2_GT4_3rd_Gear_Revelation_Reel_20s.mp4",
            title_text="3RD vs 4TH GEAR TELEMETRY",
            stat_badge="+0.300s GAINED | 5411 APEX RPM"
        )

    print(f"\nAll generated files available in: {EXPORT_DIR}")
