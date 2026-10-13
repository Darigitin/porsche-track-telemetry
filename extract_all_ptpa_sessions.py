#!/usr/bin/env python3
"""
Direct Extractor for Porsche Track Precision App (PTPA) ObjectBox Database.
Extracts all raw CAN and GPS telemetry from 'backup_data_20260924_122822.mdb'
and exports every track session into standard PTPA CSV and Racelogic .VBO files.
"""

import os
import sys
import glob
import struct
import lmdb
import datetime
import pandas as pd
import numpy as np

# High Plains Raceway start/finish gate coordinates in Racelogic minutes
HPR_GATE_START = "6233.6713436133905 2384.10624946811 6233.66568038661 2384.09892253189"

def read_str(data, str_offset):
    slen = struct.unpack('<I', data[str_offset:str_offset+4])[0]
    return data[str_offset+4:str_offset+4+slen].decode('utf-8', errors='ignore')

def get_fb_table(data, root_offset):
    vtable_rel = struct.unpack('<i', data[root_offset:root_offset+4])[0]
    vtable_off = root_offset - vtable_rel
    vtable_len = struct.unpack('<H', data[vtable_off:vtable_off+2])[0]
    num_fields = (vtable_len - 4) // 2
    offsets = struct.unpack(f'<{num_fields}H', data[vtable_off+4:vtable_off+vtable_len])
    return offsets

def write_vbo(df, output_vbo_path, dt, gate_coords=HPR_GATE_START):
    created_str = dt.strftime("%Y-%m-%d %H:%M:%S -0600")
    
    # Filter valid coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    df = df[(df['latitude'] != 0) & (df['longitude'] != 0)].copy()
    if df.empty:
        return False

    timestamps_s = df['timestamp'] / 1000.0
    t0 = timestamps_s.iloc[0]
    times_str = []
    for t in timestamps_s:
        row_dt = dt + datetime.timedelta(seconds=(t - t0))
        times_str.append(row_dt.strftime("%H%M%S") + f".{int(row_dt.microsecond / 10000):02d}")
    df['vbo_time'] = times_str

    df['vbo_lat'] = df['latitude'] * 60.0
    df['vbo_long'] = df['longitude'].abs() * 60.0

    sats = 10
    height = 1532.0
    heading = 102.0
    temp = 0

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

    slip_f = ((col('longitudinalSlipFR') + col('longitudinalSlipFL')) / 2.0).round(2)
    slip_r = ((col('longitudinalSlipRR') + col('longitudinalSlipRL')) / 2.0).round(2)

    tp_fl = col('tirePressureFL', 3276.8)
    tp_fr = col('tirePressureFR', 3276.8)
    tp_rl = col('tirePressureRL', 3276.8)
    tp_rr = col('tirePressureRR', 3276.8)

    overunder = (col('wpoOversteer', 0.0) - col('wpoUndersteer', 0.0)).round(2)
    esc = (col('electronicStabilityProgram', 'idle') == 'active').astype(int)

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
    return True

def get_latest_db():
    candidates = glob.glob(r'D:\My Drive\Database Backups\*.mdb') + glob.glob(r'D:\My Drive\*.mdb') + glob.glob('*.mdb')
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)

def extract_all():
    db_path = get_latest_db()
    if not db_path or not os.path.exists(db_path):
        print(f"Error: Database not found (scanned Google Drive and local folder)")
        return
    print(f"Using latest database: {db_path}")

    csv_dir = "Recording CSVs"
    vbo_dir = "Recording VBOs"
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(vbo_dir, exist_ok=True)

    print("Opening LMDB database...")
    env = lmdb.open(db_path, subdir=False, readonly=True, lock=False)

    with env.begin() as txn:
        c = txn.cursor()

        # 1. Load Tracks
        tracks = {}
        p_track = struct.pack('>I', 0x18000038)
        if c.set_range(p_track):
            for k, v in c:
                if not k.startswith(p_track): break
                obj_id = struct.unpack('>I', k[4:])[0]
                root = struct.unpack('<I', v[:4])[0]
                offs = get_fb_table(v, root)
                name = ''
                if len(offs) >= 6 and offs[5]:
                    rel = struct.unpack('<I', v[root+offs[5]:root+offs[5]+4])[0]
                    name = read_str(v, root+offs[5]+rel)
                tracks[obj_id] = name

        # 2. Load Laps (0x18000004)
        laps_by_rec = {}
        p_lap = struct.pack('>I', 0x18000004)
        if c.set_range(p_lap):
            for k, v in c:
                if not k.startswith(p_lap): break
                root = struct.unpack('<I', v[:4])[0]
                offs = get_fb_table(v, root)
                if len(offs) >= 4 and offs[3]:
                    rec_id = struct.unpack('<q', v[root+offs[3]:root+offs[3]+8])[0]
                    lap_num = struct.unpack('<i', v[root+offs[2]:root+offs[2]+4])[0] if len(offs)>=3 and offs[2] else 0
                    ts_start = struct.unpack('<q', v[root+offs[4]:root+offs[4]+8])[0] if len(offs)>=5 and offs[4] else 0
                    ts_end = struct.unpack('<q', v[root+offs[5]:root+offs[5]+8])[0] if len(offs)>=6 and offs[5] else 0
                    invalid = struct.unpack('<?', v[root+offs[1]:root+offs[1]+1])[0] if len(offs)>=2 and offs[1] else False
                    if rec_id not in laps_by_rec:
                        laps_by_rec[rec_id] = []
                    laps_by_rec[rec_id].append({
                        'lapNumber': lap_num,
                        'tsStart': ts_start,
                        'tsEnd': ts_end,
                        'invalid': invalid
                    })

        # 3. Load RecordingLaptimer (0x1800002c)
        sessions_map = {}
        p_rec = struct.pack('>I', 0x1800002c)
        if c.set_range(p_rec):
            for k, v in c:
                if not k.startswith(p_rec): break
                obj_id = struct.unpack('>I', k[4:])[0]
                root = struct.unpack('<I', v[:4])[0]
                offs = get_fb_table(v, root)
                if len(offs) >= 9 and offs[7] and offs[8]:
                    ts_start = struct.unpack('<q', v[root+offs[7]:root+offs[7]+8])[0]
                    ts_end = struct.unpack('<q', v[root+offs[8]:root+offs[8]+8])[0]
                    track_id = struct.unpack('<q', v[root+offs[12]:root+offs[12]+8])[0] if len(offs)>=13 and offs[12] else 0
                    track_name = tracks.get(track_id, '')
                    
                    # Filter: Only real track sessions (after 2023, High Plains Raceway)
                    if ts_start > 1700000000000:
                        dt = datetime.datetime.fromtimestamp(ts_start / 1000.0)
                        session_key = (ts_start, ts_end)
                        if session_key not in sessions_map:
                            sessions_map[session_key] = {
                                'db_ids': [obj_id],
                                'ts_start': ts_start,
                                'ts_end': ts_end,
                                'datetime': dt,
                                'filename_base': f"recording-{dt.strftime('%Y-%m-%d-%H-%M-%S')}",
                                'track': track_name,
                                'laps': laps_by_rec.get(obj_id, [])
                            }
                        else:
                            sessions_map[session_key]['db_ids'].append(obj_id)
                            if not sessions_map[session_key]['laps'] and obj_id in laps_by_rec:
                                sessions_map[session_key]['laps'] = laps_by_rec[obj_id]

    sorted_sessions = sorted(sessions_map.values(), key=lambda s: s['ts_start'])
    print(f"Loaded {len(sorted_sessions)} unique track driving sessions from database.")

    # 4. Stream VehicleData (0x18000048) in a single pass
    print("Streaming 10Hz CAN telemetry records from database...")
    session_data = {s['filename_base']: [] for s in sorted_sessions}
    seen_timestamps = {s['filename_base']: set() for s in sorted_sessions}

    # Prepare quick interval lookup
    session_intervals = [
        (s['ts_start'], s['ts_end'], s['filename_base']) for s in sorted_sessions
    ]

    with env.begin() as txn:
        c = txn.cursor()
        p = struct.pack('>I', 0x18000048)
        c.set_range(p)
        record_count = 0

        while True:
            k, v = c.item()
            if not k.startswith(p): break
            root = struct.unpack('<I', v[:4])[0]
            offs = get_fb_table(v, root)
            
            ts = struct.unpack('<q', v[root+offs[23]:root+offs[23]+8])[0] if len(offs)>23 and offs[23] else 0
            
            # Check which session ts falls into
            for ts_s, ts_e, sname in session_intervals:
                if ts_s <= ts <= ts_e:
                    if ts not in seen_timestamps[sname]:
                        seen_timestamps[sname].add(ts)
                        
                        def g_f32(idx): return struct.unpack('<f', v[root+offs[idx]:root+offs[idx]+4])[0] if len(offs)>idx and offs[idx] else 0.0
                        def g_f64(idx): return struct.unpack('<d', v[root+offs[idx]:root+offs[idx]+8])[0] if len(offs)>idx and offs[idx] else 0.0
                        def g_i16(idx): return struct.unpack('<h', v[root+offs[idx]:root+offs[idx]+2])[0] if len(offs)>idx and offs[idx] else 0

                        # Match PTPA CSV schema
                        rec = {
                            'brakingPressure': round(g_f32(1), 1),
                            'currentGear': g_i16(2),
                            'distanceCounter': round(g_f32(5), 3),
                            'electronicStabilityProgram': '',
                            'engineSpeed': g_i16(7),
                            'fuelConsumption': 0.0,
                            'gearSelection': '',
                            'lapDistance': 0.0,
                            'laptime': 0,
                            'lateralAcceleration': round(g_f32(13), 3),
                            'longitudinalAcceleration': round(g_f32(14), 3),
                            'longitudinalSlipRR': round(g_f32(18), 3),
                            'longitudinalSlipRL': round(g_f32(17), 3),
                            'longitudinalSlipFR': round(g_f32(16), 3),
                            'longitudinalSlipFL': round(g_f32(15), 3),
                            'pedalForce': round(g_f32(47), 2),
                            'sectorDistance': '',
                            'sectorTime': '',
                            'speed': round(g_f32(20), 5),
                            'steeringWheelAngle': round(g_f32(22), 2),
                            'timestamp': ts,
                            'tirePressureFR': round(g_f32(25), 1),
                            'tirePressureFL': round(g_f32(24), 1),
                            'tirePressureRR': round(g_f32(27), 1),
                            'tirePressureRL': round(g_f32(26), 1),
                            'tripDistance': 0,
                            'wpoCharismaDamper': '',
                            'wpoCharismaMotor': '',
                            'wpoCharismaTransmission': '',
                            'wpoOversteer': round(g_f32(38), 2),
                            'wpoUndersteer': round(g_f32(39), 2),
                            'latitude': g_f64(36),
                            'longitude': g_f64(40),
                            'yawVelocity': 0.0
                        }
                        session_data[sname].append(rec)
                    break

            record_count += 1
            if record_count % 150000 == 0:
                print(f"  Processed {record_count} / 947,578 records...")
            if not c.next(): break

    print(f"Data streaming complete! Processed {record_count} database records.\n")

    # 5. Export CSV & VBO for each session
    total_csv_written = 0
    total_vbo_written = 0

    for s in sorted_sessions:
        sname = s['filename_base']
        records = session_data[sname]
        if not records:
            print(f"Skipping {sname}: No records found in timestamp range.")
            continue

        df_session = pd.DataFrame(records)
        df_session = df_session.sort_values('timestamp').reset_index(drop=True)

        # Compute lap times and lap distances using lap boundaries
        laps = s['laps']
        if laps:
            laps = sorted(laps, key=lambda l: l['tsStart'])
            for lap in laps:
                mask = (df_session['timestamp'] >= lap['tsStart']) & (df_session['timestamp'] <= lap['tsEnd'])
                if mask.any():
                    start_dist = df_session.loc[mask, 'distanceCounter'].iloc[0]
                    df_session.loc[mask, 'laptime'] = df_session.loc[mask, 'timestamp'] - lap['tsStart']
                    df_session.loc[mask, 'lapDistance'] = (df_session.loc[mask, 'distanceCounter'] - start_dist).round(1)

        csv_file = os.path.join(csv_dir, f"{sname}.csv")
        vbo_file = os.path.join(vbo_dir, f"{sname}.vbo")

        # Write CSV if missing
        if not os.path.exists(csv_file):
            df_session.to_csv(csv_file, index=False)
            total_csv_written += 1
            csv_status = "EXTRACTED (NEW)"
        else:
            csv_status = "EXISTS"

        # Write VBO if missing
        if not os.path.exists(vbo_file):
            success = write_vbo(df_session, vbo_file, s['datetime'])
            if success:
                total_vbo_written += 1
                vbo_status = "GENERATED (NEW)"
            else:
                vbo_status = "ERROR"
        else:
            vbo_status = "EXISTS"

        print(f"[{s['datetime'].strftime('%Y-%m-%d %H:%M')}] {sname}: {len(df_session):<6} rows | CSV: {csv_status:<15} | VBO: {vbo_status}")

    print("\n" + "=" * 60)
    print(f"EXTRACTION COMPLETE!")
    print(f"  New CSV files written: {total_csv_written}")
    print(f"  New VBO files written: {total_vbo_written}")
    print(f"  Total CSVs in folder:  {len(os.listdir(csv_dir))}")
    print(f"  Total VBOs in folder:  {len(os.listdir(vbo_dir))}")
    print("=" * 60)

if __name__ == '__main__':
    extract_all()
