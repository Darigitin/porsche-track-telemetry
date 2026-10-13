import os
import shutil
import zipfile
import json
import pandas as pd
from convert_csv_to_vbo import convert_csv_to_vbo

def ingest_best_in_class(tparecord_path):
    print(f"Ingesting Best-in-Class recording: {tparecord_path}")
    basename = os.path.basename(tparecord_path)
    base_name_no_ext = os.path.splitext(basename)[0]
    
    # 1. Ensure raw record is archived in tpa_records/
    dest_tparecord = os.path.join("tpa_records", basename)
    if not os.path.exists(dest_tparecord) and os.path.abspath(tparecord_path) != os.path.abspath(dest_tparecord):
        shutil.copy2(tparecord_path, dest_tparecord)
        print(f"Archived raw file to: {dest_tparecord}")
        
    # 2. Extract JSON from .tparecord
    with zipfile.ZipFile(tparecord_path, 'r') as z:
        json_filename = f"{base_name_no_ext}.json"
        if json_filename not in z.namelist():
            # Search for any json inside
            json_files = [n for n in z.namelist() if n.endswith('.json')]
            if not json_files:
                raise ValueError("No JSON file found in .tparecord")
            json_filename = json_files[0]
            
        with z.open(json_filename) as f:
            data = json.load(f)
            
    car_info = data.get('recording', {}).get('car', {})
    track_info = data.get('track', {})
    print(f"Vehicle: {car_info.get('modelKey', 'Unknown')} | Track: {track_info.get('name', 'Unknown')}")
    
    samples = data.get('recording', {}).get('data', [])
    laps = data.get('recording', {}).get('laps', [])
    print(f"Extracted {len(samples)} telemetry points and {len(laps)} laps.")
    
    for i, l in enumerate(laps):
        duration = l['timestampEnd'] - l['timestampStart']
        m, s = divmod(duration, 60)
        print(f"  Lap {i+1}: {int(m)}:{s:06.3f} ({duration:.3f}s)")
        
    # 3. Construct CSV
    rows = []
    for s in samples:
        ts_sec = s.get('timestamp', 0.0)
        ts_ms = int(round(ts_sec * 1000))
        gps = s.get('GPS') or {}
        coord = gps.get('GPSCoordinate') or {}
        
        lap_time = 0
        for l in laps:
            l_start = l['timestampStart']
            l_end = l['timestampEnd']
            if l_start <= ts_sec <= l_end:
                lap_time = int(round((ts_sec - l_start) * 1000))
                break
                
        lat_acc = s.get('lateralAcceleration', 0.0)
        long_acc = s.get('longitudinalAcceleration', 0.0)
        # In PTPA JSON, accelerometer data is in SI units (m/s^2); convert uniformly to G
        lat_g = lat_acc / 9.80665
        long_g = long_acc / 9.80665
        
        rows.append({
            'brakingPressure': s.get('brakingPressure', 0.0),
            'currentGear': s.get('currentGear', 0),
            'distanceCounter': s.get('distanceCounter', 0.0),
            'electronicStabilityProgram': s.get('electronicStabilityProgram', ''),
            'engineSpeed': s.get('engineSpeed', 0),
            'fuelConsumption': s.get('fuelConsumption', 0.0),
            'gearSelection': s.get('gearSelection', ''),
            'lapDistance': 0.0,
            'laptime': lap_time,
            'lateralAcceleration': round(lat_g, 3),
            'longitudinalAcceleration': round(long_g, 3),
            'longitudinalSlipRR': s.get('longitudinalSlipRR', 0.0),
            'longitudinalSlipRL': s.get('longitudinalSlipRL', 0.0),
            'longitudinalSlipFR': s.get('longitudinalSlipFR', 0.0),
            'longitudinalSlipFL': s.get('longitudinalSlipFL', 0.0),
            'pedalForce': round(s.get('pedalForce', 0.0), 2),
            'sectorDistance': 0.0,
            'sectorTime': 0,
            'speed': round(s.get('speed', 0.0), 5),
            'steeringWheelAngle': round(s.get('steeringWheelAngle', 0.0), 2),
            'timestamp': ts_ms,
            'tirePressureFR': s.get('tirePressureFR', 0.0),
            'tirePressureFL': s.get('tirePressureFL', 0.0),
            'tirePressureRR': s.get('tirePressureRR', 0.0),
            'tirePressureRL': s.get('tirePressureRL', 0.0),
            'tripDistance': s.get('tripDistance', 0.0),
            'wpoCharismaDamper': '',
            'wpoCharismaMotor': '',
            'wpoCharismaTransmission': '',
            'wpoOversteer': round(s.get('wpoOversteer', 0.0), 2),
            'wpoUndersteer': round(s.get('wpoUndersteer', 0.0), 2),
            'latitude': coord.get('latitude', 0.0),
            'longitude': coord.get('longitude', 0.0),
            'yawVelocity': round(s.get('yawVelocity', 0.0), 2)
        })
        
    df = pd.DataFrame(rows)
    os.makedirs("Best in Class Recording", exist_ok=True)
    out_csv = os.path.join("Best in Class Recording", f"{base_name_no_ext}.csv")
    df.to_csv(out_csv, index=False)
    print(f"Generated Best-in-Class CSV: {out_csv} ({len(df)} rows)")
    
    # 4. Generate VBO
    out_vbo = os.path.join("Best in Class Recording", f"{base_name_no_ext}.vbo")
    convert_csv_to_vbo(out_csv, out_vbo)
    print(f"Generated Best-in-Class VBO: {out_vbo}")
    
    return out_csv

if __name__ == '__main__':
    ingest_best_in_class('recording-2026-09-20-08-36-34.tparecord')
