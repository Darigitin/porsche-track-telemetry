import pandas as pd
import numpy as np

def analyze_sonoma():
    csv_file = 'TrackAddict Data_ 20261016-143634 Sonoma Raceway - 2.01.856.csv'
    df = pd.read_csv(csv_file, comment='#')
    
    # Calculate distance along lap
    laps_summary = []
    
    # Analyze all laps
    for lap_num in range(1, 11):
        lap_df = df[df['Lap'] == lap_num].copy()
        if len(lap_df) < 500:
            continue
            
        t_start = lap_df['Time'].iloc[0]
        lap_df['LapTime'] = lap_df['Time'] - t_start
        lap_duration = lap_df['LapTime'].iloc[-1]
        
        # Calculate distance via speed integration (mph -> ft/s -> miles)
        dt = lap_df['Time'].diff().fillna(0)
        speed_fps = lap_df['Speed (MPH)'] * 1.46667
        lap_df['Dist_ft'] = (speed_fps * dt).cumsum()
        lap_df['Dist_mi'] = lap_df['Dist_ft'] / 5280.0
        
        # Throttle metrics
        thr = lap_df['Throttle Position (%) *OBD']
        wot_mask = thr >= 85
        coast_mask = (thr < 10) & (lap_df['Brake (calculated)'] == 0)
        brake_mask = lap_df['Brake (calculated)'] > 0
        
        wot_pct = wot_mask.mean() * 100
        coast_pct = coast_mask.mean() * 100
        brake_pct = brake_mask.mean() * 100
        
        max_speed = lap_df['Speed (MPH)'].max()
        min_speed = lap_df['Speed (MPH)'].min()
        avg_speed = lap_df['Speed (MPH)'].mean()
        max_rpm = lap_df['Engine Speed (RPM) *OBD'].max()
        
        m, s = divmod(lap_duration, 60)
        laps_summary.append({
            'Lap': lap_num,
            'Duration': lap_duration,
            'TimeStr': f"{int(m)}:{s:06.3f}",
            'MaxSpeed': max_speed,
            'MinSpeed': min_speed,
            'AvgSpeed': avg_speed,
            'WOT_pct': wot_pct,
            'Coast_pct': coast_pct,
            'Brake_pct': brake_pct,
            'MaxRPM': max_rpm,
            'Dist_mi': lap_df['Dist_mi'].iloc[-1]
        })
        
    summary_df = pd.DataFrame(laps_summary)
    print("=== SESSION LAPS SUMMARY ===")
    print(summary_df.to_string(index=False))
    
    # Deep dive on Best Lap (Lap 7) vs Lap 2 / Lap 4
    lap7 = df[df['Lap'] == 7].copy()
    lap7['LapTime'] = lap7['Time'] - lap7['Time'].iloc[0]
    dt7 = lap7['Time'].diff().fillna(0)
    lap7['Dist_ft'] = (lap7['Speed (MPH)'] * 1.46667 * dt7).cumsum()
    
    # Calculate lateral acceleration from curvature & speed
    dh = lap7['Heading'].diff().fillna(0)
    dh = (dh + 180) % 360 - 180
    omega_deg_s = dh / dt7.replace(0, np.nan)
    omega_rad_s = np.radians(omega_deg_s.fillna(0))
    v_fps = lap7['Speed (MPH)'] * 1.46667
    lap7['LatG_calc'] = (v_fps * omega_rad_s) / 32.174
    lap7['LatG_smooth'] = lap7['LatG_calc'].rolling(window=15, center=True).mean()
    
    # Calculate longitudinal acceleration (dv/dt / g)
    dv = v_fps.diff()
    lap7['LongG_calc'] = (dv / (dt7.replace(0, np.nan) * 32.174)).rolling(window=15, center=True).mean()
    
    print("\n=== LAP 7 (2:01.856) DYNAMICS ===")
    print(f"Max Speed: {lap7['Speed (MPH)'].max():.1f} mph")
    print(f"Min Speed: {lap7['Speed (MPH)'].min():.1f} mph")
    print(f"Peak Calc Lat G (Right): {lap7['LatG_smooth'].max():.2f} G")
    print(f"Peak Calc Lat G (Left):  {lap7['LatG_smooth'].min():.2f} G")
    print(f"Peak Calc Braking G:     {lap7['LongG_calc'].min():.2f} G")
    print(f"Peak Calc Accel G:       {lap7['LongG_calc'].max():.2f} G")
    
    tot_mi = lap7['Dist_ft'].iloc[-1] / 5280.0
    print(f"Lap Total Track Distance: {tot_mi:.3f} miles ({lap7['Dist_ft'].iloc[-1]:.0f} ft)")
    
    # Find local speed minima (corners)
    window = 40
    corners = []
    for i in range(window, len(lap7) - window):
        v = lap7['Speed (MPH)'].iloc[i]
        sub = lap7['Speed (MPH)'].iloc[i-window : i+window]
        if v == sub.min() and v < 85:
            dist = lap7['Dist_ft'].iloc[i]
            t = lap7['LapTime'].iloc[i]
            thr = lap7['Throttle Position (%) *OBD'].iloc[i]
            if not corners or (dist - corners[-1]['dist']) > 250:
                corners.append({
                    'index': i,
                    'dist': dist,
                    'dist_pct': dist / lap7['Dist_ft'].iloc[-1] * 100,
                    'time': t,
                    'speed': v,
                    'throttle': thr,
                    'lat_g': lap7['LatG_smooth'].iloc[i]
                })
                
    print("\n=== DETECTED CORNER APEXES (LAP 7) ===")
    for idx, c in enumerate(corners, 1):
        print(f"Apex {idx:02d}: Dist {c['dist']:5.0f} ft ({c['dist_pct']:4.1f}%) | Time {c['time']:5.1f}s | Min Speed: {c['speed']:4.1f} mph | Throttle: {c['throttle']:4.1f}% | Lat G: {c['lat_g']:+4.2f}")

    # Coasting zones in Lap 7
    coast_intervals = []
    in_coast = False
    start_idx = 0
    for i in range(len(lap7)):
        is_coasting = (lap7['Throttle Position (%) *OBD'].iloc[i] < 10) and (lap7['Brake (calculated)'].iloc[i] == 0)
        if is_coasting and not in_coast:
            in_coast = True
            start_idx = i
        elif not is_coasting and in_coast:
            in_coast = False
            duration = lap7['LapTime'].iloc[i] - lap7['LapTime'].iloc[start_idx]
            dist_c = lap7['Dist_ft'].iloc[i] - lap7['Dist_ft'].iloc[start_idx]
            if duration >= 0.5:
                coast_intervals.append({
                    'start_time': lap7['LapTime'].iloc[start_idx],
                    'end_time': lap7['LapTime'].iloc[i],
                    'duration': duration,
                    'start_dist': lap7['Dist_ft'].iloc[start_idx],
                    'end_dist': lap7['Dist_ft'].iloc[i],
                    'dist_ft': dist_c,
                    'avg_speed': lap7['Speed (MPH)'].iloc[start_idx:i].mean()
                })
                
    print("\n=== SIGNIFICANT COASTING ZONES (> 0.5s dead-band) ===")
    tot_coast_time = 0
    for idx, cz in enumerate(coast_intervals, 1):
        print(f"Zone {idx:02d}: T {cz['start_time']:5.1f}s -> {cz['end_time']:5.1f}s ({cz['duration']:4.2f}s) | Dist {cz['start_dist']:5.0f}ft -> {cz['end_dist']:5.0f}ft ({cz['dist_ft']:4.0f}ft) | Speed: {cz['avg_speed']:.1f} mph")
        tot_coast_time += cz['duration']
    print(f"Total time spent coasting in dead-zones: {tot_coast_time:.2f} seconds!")

if __name__ == '__main__':
    analyze_sonoma()
