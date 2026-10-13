import lmdb, struct
from datetime import datetime

db_path = r'D:\My Drive\Database Backups\backup_data_20261011_210739.mdb'
env = lmdb.open(db_path, subdir=False, readonly=True, lock=False)

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

with env.begin() as txn:
    # 1. Load Tracks (0x18000038)
    tracks = {}
    c = txn.cursor()
    p_track = struct.pack('>I', 0x18000038)
    if c.set_range(p_track):
        for k, v in c:
            if not k.startswith(p_track): break
            obj_id = struct.unpack('>I', k[4:])[0]
            root = struct.unpack('<I', v[:4])[0]
            offs = get_fb_table(v, root)
            name = ''
            if len(offs) >= 6 and offs[5] != 0:
                rel = struct.unpack('<I', v[root+offs[5]:root+offs[5]+4])[0]
                name = read_str(v, root+offs[5]+rel)
            tracks[obj_id] = name

    # 2. Count laps per recording (0x18000004)
    laps_by_rec = {}
    p_lap = struct.pack('>I', 0x18000004)
    if c.set_range(p_lap):
        for k, v in c:
            if not k.startswith(p_lap): break
            root = struct.unpack('<I', v[:4])[0]
            offs = get_fb_table(v, root)
            # Prop 4 is recordingLaptimerId (int64)
            if len(offs) >= 4 and offs[3] != 0:
                rec_id = struct.unpack('<q', v[root+offs[3]:root+offs[3]+8])[0]
                ts_start = struct.unpack('<q', v[root+offs[4]:root+offs[4]+8])[0] if len(offs)>=5 and offs[4] else 0
                ts_end = struct.unpack('<q', v[root+offs[5]:root+offs[5]+8])[0] if len(offs)>=6 and offs[5] else 0
                dur = (ts_end - ts_start)/1000.0 if (ts_end > ts_start) else 0
                if rec_id not in laps_by_rec:
                    laps_by_rec[rec_id] = []
                laps_by_rec[rec_id].append(dur)

    # 3. Load RecordingLaptimer (0x1800002c)
    recordings = []
    p_rec = struct.pack('>I', 0x1800002c)
    if c.set_range(p_rec):
        for k, v in c:
            if not k.startswith(p_rec): break
            obj_id = struct.unpack('>I', k[4:])[0]
            root = struct.unpack('<I', v[:4])[0]
            offs = get_fb_table(v, root)
            
            def get_s(prop_idx):
                if prop_idx < len(offs) and offs[prop_idx] != 0:
                    rel = struct.unpack('<I', v[root+offs[prop_idx]:root+offs[prop_idx]+4])[0]
                    return read_str(v, root+offs[prop_idx]+rel)
                return ''

            def get_i64(prop_idx):
                if prop_idx < len(offs) and offs[prop_idx] != 0:
                    return struct.unpack('<q', v[root+offs[prop_idx]:root+offs[prop_idx]+8])[0]
                return 0

            name = get_s(2) # Prop 3
            car = get_s(27) # Prop 28
            ts_start = get_i64(7) # Prop 8
            track_id = get_i64(12) # Prop 13
            track_name = tracks.get(track_id, name)
            dt_str = datetime.fromtimestamp(ts_start/1000.0).strftime('%Y-%m-%d %H:%M:%S') if ts_start else 'N/A'
            laps = laps_by_rec.get(obj_id, [])
            best_lap = min([l for l in laps if l > 30], default=0.0)
            
            recordings.append({
                'id': obj_id,
                'name': name,
                'track': track_name,
                'car': car,
                'datetime': dt_str,
                'laps_count': len(laps),
                'best_lap': best_lap
            })

print(f"{'ID':<4} | {'Date/Time':<19} | {'Track':<12} | {'Car':<18} | {'Laps':<5} | {'Best Lap':<8}")
print("-" * 75)
for r in sorted(recordings, key=lambda x: x['datetime']):
    best_str = f"{r['best_lap']:.2f}s" if r['best_lap'] > 0 else "N/A"
    print(f"{r['id']:<4} | {r['datetime']:<19} | {r['track']:<12} | {r['car']:<18} | {r['laps_count']:<5} | {best_str:<8}")
