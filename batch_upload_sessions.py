#!/usr/bin/env python3
"""
Batch Uploader for Full Track Sessions to YouTube (Unlisted).
Prepares full sessions for the weekend playlist archive.
"""

import os
import sys
import json
from youtube_uploader import upload_video

VIDEO_DIR = r"\\THOR\plex\Cayman Videos"
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "session_uploads.json")

SESSIONS = [
    {
        "file": "2026-10-10 HPR-Full Sat-S1 (GT4) - Best 2m00.77s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sat S1 (2:00.77)",
        "desc": "Saturday Session 1 morning baseline at High Plains Raceway (Full Course).\nBest Lap: 2:00.77\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-10 HPR-Full Sat-S2 (GT4) - Best 1m59.62s [NEW PB].mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sat S2 Full Session [1:59.62 PB]",
        "desc": "Saturday Session 2 full session containing the all-time 1:59.62 Personal Best on Lap 8 at High Plains Raceway (Full Course).\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-10 HPR-Full Sat-S3 (GT4) - Best 2m01.91s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sat S3 (2:01.91)",
        "desc": "Saturday Session 3 midday run at High Plains Raceway.\nBest Lap: 2:01.91\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-10 HPR-Full Sat-S4 (GT4) - Best 2m00.19s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sat S4 (2:00.19)",
        "desc": "Saturday Session 4 afternoon heat run at High Plains Raceway.\nBest Lap: 2:00.19\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-11 HPR-Full Sun-S1 (GT4) - Best 2m00.32s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sun S1 (2:00.32)",
        "desc": "Sunday Session 1 morning session at High Plains Raceway.\nBest Lap: 2:00.32\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-11 HPR-Full Sun-S2 (GT4) - Best 2m00.12s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sun S2 Consistency Run (2:00.12)",
        "desc": "Sunday Session 2 consistency session at High Plains Raceway.\nBest Lap: 2:00.12 on heat-cycled tires.\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-11 HPR-Full Sun-S3 (GT4) - Best 2m01.90s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sun S3 (2:01.90)",
        "desc": "Sunday Session 3 midday heat run at High Plains Raceway.\nBest Lap: 2:01.90\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    },
    {
        "file": "2026-10-11 HPR-Full Sun-S4 (GT4) - Best 2m00.97s.mp4",
        "title": "Porsche 718 Cayman GT4 | High Plains Raceway - Sun S4 Season Closer (2:00.97)",
        "desc": "Sunday Session 4 final weekend session at High Plains Raceway.\nBest Lap: 2:00.97\nCar: 2023 Porsche 718 Cayman GT4\nTelemetry: Porsche Track Precision App (PTPA)"
    }
]

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def main():
    progress = load_progress()
    print("=== BATCH SESSION UPLOADER (UNLISTED) ===")
    print(f"Total sessions configured: {len(SESSIONS)}")
    
    for item in SESSIONS:
        fname = item["file"]
        fpath = os.path.join(VIDEO_DIR, fname)
        
        if fname in progress:
            print(f"\n[SKIPPED] Already uploaded: {fname} -> {progress[fname]}")
            continue
            
        if not os.path.exists(fpath):
            print(f"\n[WARNING] File not found on THOR: {fpath}")
            continue
            
        print(f"\nUploading: {fname}...")
        url = upload_video(
            file_path=fpath,
            title=item["title"],
            description=item["desc"],
            tags=["Porsche", "718 Cayman GT4", "High Plains Raceway", "Track Day", "Full Session", "PTPA"],
            category="2",
            privacy="unlisted"
        )
        
        if url:
            progress[fname] = url
            save_progress(progress)
            print(f"Saved progress: {fname} -> {url}")
        else:
            print(f"[ERROR] Failed uploading {fname}. Stopping batch to preserve quota.")
            break

    print("\n=== UPLOAD SUMMARY ===")
    for k, v in progress.items():
        print(f"{k} -> {v}")

if __name__ == "__main__":
    main()
