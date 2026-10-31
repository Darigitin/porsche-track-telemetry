#!/usr/bin/env python3
"""
Telemetry Scout: Scans Porsche Track Precision App (.tparecord) files for:
1. Peak Lateral G apexes
2. Brutal braking spikes
3. Oversteer slides & countersteer corrections
4. Session best laps with video timestamp offsets
"""

import glob
import zipfile
import json
import os

SESSION_MAP = {
    "recording-2026-10-10-08-59-55.tparecord": "2026-10-10 HPR-Full Sat-S1 (GT4) - Best 2m00.77s.mp4",
    "recording-2026-10-10-10-57-43.tparecord": "2026-10-10 HPR-Full Sat-S2 (GT4) - Best 1m59.62s [NEW PB].mp4",
    "recording-2026-10-10-14-07-51.tparecord": "2026-10-10 HPR-Full Sat-S3 (GT4) - Best 2m01.91s.mp4",
    "recording-2026-10-10-15-55-51.tparecord": "2026-10-10 HPR-Full Sat-S4 (GT4) - Best 2m00.19s.mp4",
    "recording-2026-10-11-08-59-54.tparecord": "2026-10-11 HPR-Full Sun-S1 (GT4) - Best 2m00.32s.mp4",
    "recording-2026-10-11-10-58-49.tparecord": "2026-10-11 HPR-Full Sun-S2 (GT4) - Best 2m00.12s.mp4",
    "recording-2026-10-11-14-08-52.tparecord": "2026-10-11 HPR-Full Sun-S3 (GT4) - Best 2m01.90s.mp4",
    "recording-2026-10-11-15-34-02.tparecord": "2026-10-11 HPR-Full Sun-S4 (GT4) - Best 2m00.97s.mp4"
}

def scan():
    files = sorted(glob.glob("tpa_records/*.tparecord") + glob.glob("*.tparecord"))
    # Filter for the most recent weekend (e.g. October 2026 or latest dates found)
    if files:
        latest_date_prefix = sorted([os.path.basename(f)[10:20] for f in files])[-1][:7]
        files = [f for f in files if latest_date_prefix in f]
    all_events = []
    best_laps = []

    for f in files:
        base = os.path.basename(f)
        video_name = SESSION_MAP.get(base, "")
        with zipfile.ZipFile(f) as z:
            name = z.namelist()[0]
            data = json.loads(z.read(name))
            rec = data["recording"]
            vid = rec.get("videos", [{}])[0]
            vid_start = vid.get("timestampStart", 0)

            # Laps
            session_best = None
            for lap in rec.get("laps", []):
                dur = lap["timestampEnd"] - lap["timestampStart"]
                if 60 < dur < 180:
                    if session_best is None or dur < session_best["dur"]:
                        session_best = {
                            "session": base,
                            "video_name": video_name,
                            "lap_num": lap["number"],
                            "dur": dur,
                            "start": lap["timestampStart"],
                            "end": lap["timestampEnd"],
                            "v_start": (lap["timestampStart"] - vid_start) if vid_start else 0,
                            "v_end": (lap["timestampEnd"] - vid_start) if vid_start else 0
                        }
            if session_best:
                best_laps.append(session_best)

            # Telemetry samples
            samples = rec.get("data", [])
            max_raw_spd = max((s.get("speed", 0) for s in samples), default=0)
            spd_scale = 2.23694 if max_raw_spd < 80 else 0.621371
            for sample in samples:
                spd_raw = sample.get("speed", 0)
                spd_mph = spd_raw * spd_scale
                if spd_mph < 35.0: # Ignore pit lane / stopped
                    continue

                ts = sample.get("timestamp", 0)
                ts_s = ts / 1000.0 if ts > 1e11 else ts
                lat_g = abs(sample.get("lateralAcceleration", 0)) / 9.80665
                long_g = sample.get("longitudinalAcceleration", 0) / 9.80665
                over = abs(sample.get("wpoOversteer", 0))
                esc = sample.get("electronicStabilityProgram", "")
                steering = sample.get("steeringWheelAngle", 0)
                v_offset = (ts_s - vid_start) if vid_start else 0

                all_events.append({
                    "session": base,
                    "video_name": video_name,
                    "v_offset": v_offset,
                    "lat_g": lat_g,
                    "long_g": long_g,
                    "oversteer": over,
                    "esc": esc,
                    "steering": steering,
                    "speed_mph": spd_mph
                })

    print(f"Scanned {len(files)} sessions ({len(all_events):,} active track telemetry frames).")
    
    print("\n" + "="*80)
    print("SESSION BEST LAPS & EXACT VIDEO TIMESTAMPS")
    print("="*80)
    for b in best_laps:
        m, s = divmod(b["dur"], 60)
        vm_s, vs_s = divmod(b["v_start"], 60)
        vm_e, vs_e = divmod(b["v_end"], 60)
        print(f"{b['video_name'][:38]:<38} | Lap {b['lap_num']:<2} | {int(m)}:{s:06.3f} | Video {int(vm_s):02d}:{vs_s:04.1f} -> {int(vm_e):02d}:{vs_e:04.1f}")

    print("\n" + "="*80)
    print("TOP 5 HIGHEST LATERAL G CORNERING MOMENTS")
    print("="*80)
    dedup_lat = []
    for e in sorted(all_events, key=lambda x: x["lat_g"], reverse=True):
        if not any(e["session"] == d["session"] and abs(e["v_offset"] - d["v_offset"]) < 6.0 for d in dedup_lat):
            dedup_lat.append(e)
            if len(dedup_lat) == 5: break
    for e in dedup_lat:
        vm, vs = divmod(e["v_offset"], 60)
        print(f"{e['video_name'][:38]:<38} | {e['lat_g']:.2f}G Lateral | Video {int(vm):02d}:{vs:04.1f} | Speed: {e['speed_mph']:.1f} mph | Steer: {e['steering']:.1f}°")

    print("\n" + "="*80)
    print("TOP 5 HARD BRAKING THRESHOLD ENTRIES")
    print("="*80)
    dedup_brake = []
    for e in sorted(all_events, key=lambda x: x["long_g"]):
        if not any(e["session"] == d["session"] and abs(e["v_offset"] - d["v_offset"]) < 6.0 for d in dedup_brake):
            dedup_brake.append(e)
            if len(dedup_brake) == 5: break
    for e in dedup_brake:
        vm, vs = divmod(e["v_offset"], 60)
        print(f"{e['video_name'][:38]:<38} | {e['long_g']:.2f}G Braking | Video {int(vm):02d}:{vs:04.1f} | Speed: {e['speed_mph']:.1f} mph")

    print("\n" + "="*80)
    print("TOP 5 CHASSIS ROTATION / OVERSTEER MOMENTS")
    print("="*80)
    dedup_over = []
    for e in sorted([x for x in all_events if x["oversteer"] > 0], key=lambda x: x["oversteer"], reverse=True):
        if not any(e["session"] == d["session"] and abs(e["v_offset"] - d["v_offset"]) < 6.0 for d in dedup_over):
            dedup_over.append(e)
            if len(dedup_over) == 5: break
    for e in dedup_over:
        vm, vs = divmod(e["v_offset"], 60)
        print(f"{e['video_name'][:38]:<38} | Oversteer: {e['oversteer']:.2f} | LatG: {e['lat_g']:.2f}G | Video {int(vm):02d}:{vs:04.1f} | Speed: {e['speed_mph']:.1f} mph")

    return best_laps, dedup_lat, dedup_brake, dedup_over

if __name__ == "__main__":
    scan()
