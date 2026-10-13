#!/usr/bin/env python3
"""
Convert Porsche Track Precision App (PTPA) raw CSV recordings into 
Track Evolution compatible Racelogic .VBO files.
"""

import os
import glob
import re
import datetime
import pandas as pd
import numpy as np

# High Plains Raceway start/finish gate coordinates in Racelogic minutes
# Derived from successful PTPA VBO export for HPR
HPR_GATE_START = "6233.6713436133905 2384.10624946811 6233.66568038661 2384.09892253189"

def parse_filename_datetime(filename):
    basename = os.path.basename(filename)
    match = re.search(r'recording-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})', basename)
    if match:
        year, month, day, hour, minute, second = map(int, match.groups())
        return datetime.datetime(year, month, day, hour, minute, second)
    return None

def convert_csv_to_vbo(csv_path, output_vbo_path, gate_coords=HPR_GATE_START):
    dt = parse_filename_datetime(csv_path)
    created_str = dt.strftime("%Y-%m-%d %H:%M:%S -0600") if dt else "2026-06-07 12:00:00 -0600"
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    # Filter out rows with invalid GPS coordinates
    if 'latitude' in df.columns and 'longitude' in df.columns:
        df = df.dropna(subset=['latitude', 'longitude'])
        df = df[(df['latitude'] != 0) & (df['longitude'] != 0)]
    
    if df.empty:
        print(f"Skipping {csv_path}: No valid GPS data.")
        return False

    # Calculate time of day (HHMMSS.SS)
    # If timestamp column exists (Unix ms), convert to time of day
    if 'timestamp' in df.columns:
        # Timestamps are epoch ms
        timestamps_s = df['timestamp'] / 1000.0
        # Compute time of day in local / session time
        # Use starting dt + relative seconds
        t0 = timestamps_s.iloc[0]
        base_time = dt if dt else datetime.datetime.fromtimestamp(t0)
        
        times_str = []
        for t in timestamps_s:
            row_dt = base_time + datetime.timedelta(seconds=(t - t0))
            times_str.append(row_dt.strftime("%H%M%S") + f".{int(row_dt.microsecond / 10000):02d}")
        df['vbo_time'] = times_str
    else:
        # Synthesize 10Hz clock
        times_str = []
        cur_dt = dt if dt else datetime.datetime(2026, 6, 7, 10, 0, 0)
        for i in range(len(df)):
            row_dt = cur_dt + datetime.timedelta(seconds=i * 0.1)
            times_str.append(row_dt.strftime("%H%M%S") + f".{int(row_dt.microsecond / 10000):02d}")
        df['vbo_time'] = times_str

    # Convert coordinates to minutes (degrees * 60)
    # In Racelogic format, longitude is west-positive (abs(longitude) for US coordinates)
    df['vbo_lat'] = df['latitude'] * 60.0
    df['vbo_long'] = df['longitude'].abs() * 60.0

    # Fill defaults for standard columns
    sats = 10
    height = 1532.0 # HPR altitude ~5026 ft = 1532 m
    heading = 102.0
    temp = 0
    
    # Helpers for channel mapping
    def col(name, default=0.0):
        if name in df.columns:
            return df[name].fillna(default)
        return pd.Series(default, index=df.index)

    speed = col('speed', 0.0)
    current_gear = col('currentGear', 0).astype(int)
    engine_rpm = col('engineSpeed', 0).astype(int)
    pedal = col('pedalForce', 0.0).round(2)
    braking = col('brakingPressure', 0.0).round(1)
    steering = col('steeringWheelAngle', 0.0).round(2)
    lat_g = col('lateralAcceleration', 0.0).round(3)
    long_g = col('longitudinalAcceleration', 0.0).round(3)
    yaw = col('yawVelocity', 0.0).round(2)
    lap_dist = col('lapDistance', -1.0).round(1)
    lap_time = col('laptime', 0).astype(int)
    
    # Derived slip
    slip_f = ((col('longitudinalSlipFL') + col('longitudinalSlipFR')) / 2.0).round(2)
    slip_r = ((col('longitudinalSlipRL') + col('longitudinalSlipRR')) / 2.0).round(2)

    # TPMS
    tp_fl = col('tirePressureFL', 3276.8)
    tp_fr = col('tirePressureFR', 3276.8)
    tp_rl = col('tirePressureRL', 3276.8)
    tp_rr = col('tirePressureRR', 3276.8)

    # Chassis / OverUndersteer
    overunder = (col('wpoOversteer', 0.0) - col('wpoUndersteer', 0.0)).round(2)

    # ESC flag
    esc = (col('electronicStabilityProgram', 'idle') == 'active').astype(int)

    # Open VBO for writing
    with open(output_vbo_path, 'w', encoding='ascii', newline='') as f:
        f.write(f"File created at {created_str}\r\n\r\n")
        
        f.write("[header]\r\n")
        f.write("satellites\r\ntime\r\nlatitude\r\nlongitude\r\nvelocity kmh\r\nheading\r\nheight\r\n")
        f.write("longAccel g\r\nlatAccel g\r\ntemperature\r\nbraking pressure\r\ncurrent gear\r\nESC\r\n")
        f.write("engine speed\r\nfuel consumption\r\nlap distance\r\nlap time\r\nlongitudinal slip front\r\n")
        f.write("longitudinal slip rear\r\npedal force\r\nsteering wheel angle\r\ntire pressure front left\r\n")
        f.write("tire pressure front right\r\ntire pressure rear left\r\ntire pressure rear right\r\n")
        f.write("trip distance\r\ncharisma damper\r\ncharisma motor\r\ncharisma transmission\r\n")
        f.write("OverUndersteer\r\nyaw velocity\r\nLatAcc_PTPA\r\nLongAcc_PTPA\r\n\r\n")
        
        f.write("[comments]\r\n(c) Porsche _Track Precision AppCamera\r\n\r\n")
        f.write("[units]\r\ndegC\r\nv\r\n\r\nmA\r\n%\r\n\r\n")
        
        f.write("[laptiming]\r\n")
        f.write(f"Start\t{gate_coords}\r\n\r\n")
        
        f.write("[column names]\r\n")
        f.write("sats\r\ntime\r\nlat\r\nlong\r\nvelocity\r\nheading\r\nheight\r\nlongacc\r\nlatacc\r\ntemp\r\n")
        f.write("braking\r\ncurrent gear\r\nESC\r\nengine\r\nfuel\r\nlap distance\r\nlap time\r\n")
        f.write("longitudinal slip front\r\nlongitudinal slip rear\r\npedal\r\nsteering wheel angle\r\n")
        f.write("tire pressure front left\r\ntire pressure front right\r\ntire pressure rear left\r\ntire pressure rear right\r\n")
        f.write("trip\r\ndamper\r\nmotor\r\ntransmission\r\nOverUndersteer\r\nyaw\r\nLatAcc_PTPA\r\nLongAcc_PTPA\r\n\r\n")
        
        f.write("[data]\r\n")
        for i in range(len(df)):
            row = (
                f"{sats} "
                f"{df['vbo_time'].iloc[i]} "
                f"{df['vbo_lat'].iloc[i]:.8f} "
                f"{df['vbo_long'].iloc[i]:.8f} "
                f"{speed.iloc[i]:.5f} "
                f"{heading:.1f} "
                f"{height:.1f} "
                f"{(long_g.iloc[i] / 9.81):.8f} "
                f"{(lat_g.iloc[i] / 9.81):.8f} "
                f"{temp} "
                f"{braking.iloc[i]:.1f} "
                f"{current_gear.iloc[i]} "
                f"{esc.iloc[i]} "
                f"{engine_rpm.iloc[i]} "
                f"0.0 "
                f"{lap_dist.iloc[i]} "
                f"{lap_time.iloc[i]} "
                f"{slip_f.iloc[i]} "
                f"{slip_r.iloc[i]} "
                f"{pedal.iloc[i]} "
                f"{steering.iloc[i]} "
                f"{tp_fl.iloc[i]} "
                f"{tp_fr.iloc[i]} "
                f"{tp_rl.iloc[i]} "
                f"{tp_rr.iloc[i]} "
                f"0 0 0 0 "
                f"{overunder.iloc[i]} "
                f"{yaw.iloc[i]} "
                f"{lat_g.iloc[i]} "
                f"{long_g.iloc[i]}"
            )
            f.write(row + "\r\n")
            
    print(f"Successfully converted {os.path.basename(csv_path)} -> {os.path.basename(output_vbo_path)} ({len(df)} samples)")
    return True

def convert_all_missing(csv_dir="Recording CSVs", vbo_dir="Recording VBOs"):
    os.makedirs(vbo_dir, exist_ok=True)
    csv_files = sorted(glob.glob(os.path.join(csv_dir, "*.csv")))
    converted_count = 0
    
    for csv_file in csv_files:
        base = os.path.splitext(os.path.basename(csv_file))[0]
        vbo_file = os.path.join(vbo_dir, f"{base}.vbo")
        
        if os.path.exists(vbo_file):
            print(f"Skipping {base}.vbo: already exists in {vbo_dir}")
            continue
            
        success = convert_csv_to_vbo(csv_file, vbo_file)
        if success:
            converted_count += 1
            
    print(f"\nDone! Converted {converted_count} new VBO sessions into {vbo_dir}")

if __name__ == "__main__":
    convert_all_missing()
