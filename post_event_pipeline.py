#!/usr/bin/env python3
"""
MASTER POST-EVENT TRACKSIDE PIPELINE
Automates all post-event activities after returning from a track weekend:
1. Ingests latest database backup from Google Drive & extracts raw telemetry (CSV & VBO)
2. Runs multi-year progression analysis & regenerates all high-res motorsport charts
3. Generates the comprehensive Driver Debrief & Consumables Report (POST_EVENT_DEBRIEF.md)
4. Scouts telemetry for milestone clips and renders YouTube 1440p & Instagram 9:16 reels
5. Generates the social media upload manifest (with ready-to-copy metadata)
6. Optional automated publishing to YouTube and Instagram
"""

import os
import sys
import glob
import time
import argparse
import subprocess
import pandas as pd
import numpy as np

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(PROJECT_DIR, "Recording CSVs")
VBO_DIR = os.path.join(PROJECT_DIR, "Recording VBOs")
CHARTS_DIR = os.path.join(PROJECT_DIR, "charts")
VIDEO_DIR = r"\\THOR\plex\Cayman Videos"
EXPORT_DIR = r"\\THOR\plex\Cayman Videos\Social Exports"

def banner(title):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def step_1_extract_sessions():
    banner("Stage 1: Ingesting Latest Database & Telemetry Extraction")
    extract_script = os.path.join(PROJECT_DIR, "extract_all_ptpa_sessions.py")
    res = subprocess.run([sys.executable, extract_script], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Extraction failed:\n{res.stderr[-600:]}")
        return False
    print(res.stdout[-600:])
    return True

def step_2_analyze_telemetry_and_charts():
    banner("Stage 2: Multi-Year Analysis & High-Res Chart Generation")
    analyze_script = os.path.join(PROJECT_DIR, "analyze_track_data.py")
    res = subprocess.run([sys.executable, analyze_script], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Telemetry analysis failed:\n{res.stderr[-600:]}")
        return False
    print(res.stdout)
    return True

def step_3_generate_driver_debrief():
    banner("Stage 3: Generating Driver Debrief & Consumables Inspection")
    csv_files = sorted(glob.glob(os.path.join(CSV_DIR, "recording-*.csv")))
    if not csv_files:
        print("[WARN] No session CSVs found for debrief.")
        return

    # Identify the most recent event dates
    latest_date_str = os.path.basename(csv_files[-1])[10:20]
    month_prefix = latest_date_str[:7]
    weekend_files = [f for f in csv_files if month_prefix in os.path.basename(f)]

    all_laps = []
    max_oil_temp = 0
    max_coolant_temp = 0
    pressures_fl = []
    pressures_fr = []
    pressures_rl = []
    pressures_rr = []

    for f in weekend_files:
        df = pd.read_csv(f)
        df.columns = df.columns.str.strip()
        
        # Consumables
        for col, target in [('tirePressureFL', pressures_fl), ('tirePressureFR', pressures_fr),
                             ('tirePressureRL', pressures_rl), ('tirePressureRR', pressures_rr)]:
            if col in df.columns:
                valid = df[col][(df[col] > 20) & (df[col] < 45)]
                if not valid.empty:
                    target.extend(valid.tail(200).tolist())

        # Laps
        if 'laptime' in df.columns:
            lap_ends = df[df['laptime'] > df['laptime'].shift(-1).fillna(0)]
            valid = lap_ends[(lap_ends['laptime'] > 100000) & (lap_ends['laptime'] < 200000)]
            for _, row in valid.iterrows():
                all_laps.append(row['laptime'] / 1000.0)

    all_laps = sorted(all_laps)
    best_lap = all_laps[0] if all_laps else 0.0
    top_5_avg = np.mean(all_laps[:5]) if len(all_laps) >= 5 else best_lap

    debrief_path = os.path.join(PROJECT_DIR, "POST_EVENT_DEBRIEF.md")
    content = f"""# Post-Event Trackside Debrief & Consumables Inspection

**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Vehicle:** Porsche 718 Cayman GT4 | **Track:** High Plains Raceway (Full Course)

---

## ⏱️ Weekend Pace & Consistency
* **Total Timed Laps This Event:** {len(all_laps)} laps
* **Weekend Best Lap:** **{int(best_lap//60)}:{best_lap%60:06.3f}**
* **Top 5 Average Pace:** **{int(top_5_avg//60)}:{top_5_avg%60:06.3f}**
* **Consistency Window:** {len([l for l in all_laps if l <= best_lap + 1.5])} laps within 1.5s of PB pace

---

## 🛞 Chassis Dynamics & Tire Thermal Status
* **Target Hot Pressure Benchmark:** `30.5 PSI`
* **Recorded Hot Pressures (End of Stint Averages):**
  * Front Left (FL): `{np.mean(pressures_fl):.1f} PSI` if available else `N/A`
  * Front Right (FR): `{np.mean(pressures_fr):.1f} PSI` if available else `N/A`
  * Rear Left (RL): `{np.mean(pressures_rl):.1f} PSI` if available else `N/A`
  * Rear Right (RR): `{np.mean(pressures_rr):.1f} PSI` if available else `N/A`

---

## 📈 Multi-Year Progression Frontier
* **Historical Baseline (June 2024):** `2:16.78`
* **Current Personal Record:** **`{int(best_lap//60)}:{best_lap%60:06.3f}`**
* **Total Progression Drop:** **`{(136.78 - best_lap):.2f} seconds`**
* **Updated Charts Generated:**
  * [`charts/best_lap_time_trend.png`](charts/best_lap_time_trend.png)
  * [`charts/wot_throttle_progression.png`](charts/wot_throttle_progression.png)
  * [`charts/max_gforce_trend.png`](charts/max_gforce_trend.png)
  * [`charts/max_speed_trend.png`](charts/max_speed_trend.png)
  * [`charts/track_map_comparison.png`](charts/track_map_comparison.png)
"""
    with open(debrief_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated Driver Debrief: {debrief_path}")
    return debrief_path

def step_4_scout_and_render_social():
    banner("Stage 4: Scouting Highlights & Social Video Rendering")
    social_script = os.path.join(PROJECT_DIR, "process_weekend_for_social.py")
    res = subprocess.run([sys.executable, social_script], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Social media render failed:\n{res.stderr[-600:]}")
        return False
    print(res.stdout)
    return True

def main():
    parser = argparse.ArgumentParser(description="Master Post-Event Track Pipeline.")
    parser.add_argument("--skip-extract", action="store_true", help="Skip database extraction")
    parser.add_argument("--upload-youtube", action="store_true", help="Auto-upload YouTube 1440p master")
    parser.add_argument("--upload-instagram", action="store_true", help="Auto-upload Instagram highlight reel")
    args = parser.parse_args()

    banner("PORSCHE TRACKSIDE POST-EVENT MASTER PIPELINE")
    t0 = time.time()

    # Stage 1: Extraction
    if not args.skip_extract:
        step_1_extract_sessions()

    # Stage 2: Telemetry Analysis & Charts
    step_2_analyze_telemetry_and_charts()

    # Stage 3: Driver Debrief
    step_3_generate_driver_debrief()

    # Stage 4: Social Video Render & Manifest
    step_4_scout_and_render_social()

    # Stage 5: Optional Uploads
    if args.upload_youtube:
        banner("Stage 5A: Automated YouTube Upload")
        yt_script = os.path.join(PROJECT_DIR, "youtube_uploader.py")
        pb_video = os.path.join(EXPORT_DIR, "2026-10-10_HPR_GT4_1m59s_PB_YouTube_1440p.mp4")
        subprocess.run([sys.executable, yt_script, "--file", pb_video, "--title", "Porsche 718 Cayman GT4 | Sub-2:00 at High Plains Raceway (1:59.62 PB) [Telemetry]", "--privacy", "public"])

    if args.upload_instagram:
        banner("Stage 5B: Automated Instagram Upload")
        ig_script = os.path.join(PROJECT_DIR, "instagram_uploader.py")
        ig_video = os.path.join(EXPORT_DIR, "2026-10-10_HPR_GT4_1m59s_PB_Instagram_Highlight_44s.mp4")
        caption = "Finally cracked into the 1:50s at High Plains Raceway 🏁 1:59.624 across the line in the 718 Cayman GT4. Full lap with telemetry on YouTube! #Porsche #718GT4 #HighPlainsRaceway #TrackDay"
        subprocess.run([sys.executable, ig_script, "--file", ig_video, "--caption", caption])

    banner(f"ALL POST-EVENT ACTIVITIES COMPLETED IN {time.time()-t0:.1f}s")
    print(f"Summary Document: {os.path.join(PROJECT_DIR, 'POST_EVENT_DEBRIEF.md')}")
    print(f"Full Session Log: {os.path.join(PROJECT_DIR, 'analysis_summary.md')}")
    print(f"Updated Charts:   {CHARTS_DIR}")
    print(f"Social Media:     {EXPORT_DIR}")

if __name__ == "__main__":
    main()
