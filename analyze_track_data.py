import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import re

def parse_filename_date(filename):
    basename = os.path.basename(filename)
    match = re.search(r'recording-(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})', basename)
    if match:
        date_str = match.group(1)
        return datetime.datetime.strptime(date_str, '%Y-%m-%d-%H-%M-%S')
    return None

def format_lap_time(seconds):
    if pd.isna(seconds) or seconds is None or seconds <= 0:
        return "N/A"
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:06.3f}"

def analyze_file(filepath, recording_type="User"):
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        if df.empty:
            return None
        
        # Speed normalization: convert to km/h and mph
        max_speed_kmh = None
        max_speed_mph = None
        if 'speed' in df.columns:
            raw_spd = df['speed'].max()
            if raw_spd < 80:
                max_speed_kmh = raw_spd * 3.6
            else:
                max_speed_kmh = raw_spd
            max_speed_mph = max_speed_kmh * 0.621371
        
        # Max Lateral G normalization
        max_lat_g = None
        if 'lateralAcceleration' in df.columns:
            raw_lat = df['lateralAcceleration'].abs()
            lat_g = (raw_lat / 9.81) if raw_lat.quantile(0.999) > 3.0 else raw_lat
            # 99.8th percentile to filter curb vibrations
            valid_lat = lat_g[lat_g < 2.2]
            if not valid_lat.empty:
                computed_lat = valid_lat.quantile(0.998)
                # Sensor sanity filter: High Plains Raceway hot laps always exceed 0.5G; filter CAN dropout
                if computed_lat >= 0.5:
                    max_lat_g = computed_lat
        
        # Max Braking G normalization (negative is braking)
        max_brake_g = None
        if 'longitudinalAcceleration' in df.columns:
            raw_long = df['longitudinalAcceleration']
            long_g = (raw_long / 9.81) if raw_long.abs().quantile(0.999) > 3.0 else raw_long
            valid_brake = long_g[(long_g > -2.5) & (long_g < 0)]
            if not valid_brake.empty:
                computed_brake = valid_brake.quantile(0.005) # Peak negative deceleration
                if computed_brake <= -0.4:
                    max_brake_g = computed_brake
        
        # WOT throttle percentage (None if throttle pedal sensor was disconnected/idle)
        wot_pct = None
        if 'pedalForce' in df.columns and df['pedalForce'].max() > 0.1:
            wot_pct = round((df['pedalForce'] >= 0.95).mean() * 100.0, 1)

        # Best Lap Time
        best_lap_time = None
        if 'laptime' in df.columns:
            lap_ends = df[df['laptime'] > df['laptime'].shift(-1).fillna(0)]
            # Filter valid laps for High Plains Raceway (full course is ~110s - 180s)
            valid_laps = lap_ends[(lap_ends['laptime'] > 100000) & (lap_ends['laptime'] < 240000)]
            if not valid_laps.empty:
                best_lap_time = valid_laps['laptime'].min() / 1000.0
                
        return {
            'File': os.path.basename(filepath),
            'Date': parse_filename_date(filepath),
            'Type': recording_type,
            'Max Speed (km/h)': round(max_speed_kmh, 1) if max_speed_kmh else None,
            'Max Speed (mph)': round(max_speed_mph, 1) if max_speed_mph else None,
            'Max Lateral G': round(max_lat_g, 2) if max_lat_g else None,
            'Max Braking G': round(max_brake_g, 2) if max_brake_g else None,
            'WOT %': wot_pct,
            'Best Lap Time (s)': best_lap_time
        }
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def analyze_laps_detailed(filepath, recording_type="User"):
    """Extracts detailed lap-by-lap data for AI coaching."""
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        
        if 'laptime' not in df.columns:
            return []
            
        lap_ends = df.index[df['laptime'] > df['laptime'].shift(-1).fillna(0)].tolist()
        laps_data = []
        start_idx = 0
        lap_num = 1
        
        for end_idx in lap_ends:
            lap_df = df.iloc[start_idx:end_idx+1]
            lap_time_ms = lap_df['laptime'].max()
            
            # Filter clean flying laps (100s to 240s for HPR Full Course)
            if 100000 <= lap_time_ms <= 240000:
                lap_time_s = lap_time_ms / 1000.0
                
                raw_spd = lap_df['speed'].max() if 'speed' in lap_df.columns else 0.0
                max_spd_kmh = raw_spd * 3.6 if raw_spd < 80 else raw_spd
                max_spd_mph = max_spd_kmh * 0.621371
                
                raw_lat = lap_df['lateralAcceleration'].abs() if 'lateralAcceleration' in lap_df.columns else pd.Series([0.0])
                lat_g = (raw_lat / 9.81) if raw_lat.quantile(0.999) > 3.0 else raw_lat
                computed_lat = lat_g.quantile(0.995)
                max_lat = computed_lat if computed_lat >= 0.5 else None
                
                raw_long = lap_df['longitudinalAcceleration'] if 'longitudinalAcceleration' in lap_df.columns else pd.Series([0.0])
                long_g = (raw_long / 9.81) if raw_long.abs().quantile(0.999) > 3.0 else raw_long
                computed_brake = long_g.quantile(0.005)
                max_brake = computed_brake if computed_brake <= -0.4 else None
                
                max_rpm = lap_df['engineSpeed'].max() if 'engineSpeed' in lap_df.columns and lap_df['engineSpeed'].max() > 1500 else None
                avg_steer_abs = lap_df['steeringWheelAngle'].abs().mean() if 'steeringWheelAngle' in lap_df.columns else None
                
                laps_data.append({
                    'File': os.path.basename(filepath),
                    'Date': parse_filename_date(filepath),
                    'Type': recording_type,
                    'Lap': lap_num,
                    'Lap Time (s)': round(lap_time_s, 3),
                    'Lap Time Formatted': format_lap_time(lap_time_s),
                    'Max Speed (mph)': round(max_spd_mph, 1),
                    'Max Speed (km/h)': round(max_spd_kmh, 1),
                    'Max Lateral G': round(max_lat, 2) if max_lat is not None else None,
                    'Max Braking G': round(max_brake, 2) if max_brake is not None else None,
                    'Max RPM': max_rpm,
                    'Avg Abs Steering Angle': round(avg_steer_abs, 2) if avg_steer_abs else None
                })
                lap_num += 1
            
            start_idx = end_idx + 1
            
        return laps_data
    except Exception as e:
        print(f"Error processing laps for {filepath}: {e}")
        return []

def plot_track_map(df_detailed):
    user_laps = df_detailed[df_detailed['Type'] == 'User'].dropna(subset=['Lap Time (s)'])
    if user_laps.empty:
        return
    best_user = user_laps.loc[user_laps['Lap Time (s)'].idxmin()]
    
    bic_laps = df_detailed[df_detailed['Type'] == 'Best_In_Class'].dropna(subset=['Lap Time (s)'])
    best_bic = bic_laps.loc[bic_laps['Lap Time (s)'].idxmin()] if not bic_laps.empty else None
    
    def extract_lap_data(file_name, folder, target_lap):
        filepath = os.path.join(folder, file_name)
        if not os.path.exists(filepath):
            return None
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        lap_ends = df.index[df['laptime'] > df['laptime'].shift(-1).fillna(0)].tolist()
        
        start_idx = 0
        lap_num = 1
        for end_idx in lap_ends:
            lap_df = df.iloc[start_idx:end_idx+1]
            lap_time_ms = lap_df['laptime'].max()
            if 100000 <= lap_time_ms <= 240000:
                if lap_num == target_lap:
                    return lap_df
                lap_num += 1
            start_idx = end_idx + 1
        return None

    user_df = extract_lap_data(best_user['File'], 'Recording CSVs', best_user['Lap'])
    bic_df = extract_lap_data(best_bic['File'], 'Best in Class Recording', best_bic['Lap']) if best_bic is not None else None
    
    if user_df is not None and 'longitude' in user_df.columns and 'latitude' in user_df.columns:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(13, 8), dpi=150)
        
        # Plot User Line colored by speed
        ax.plot(user_df['longitude'], user_df['latitude'], label=f"Personal Best Lap ({format_lap_time(best_user['Lap Time (s)'])})", color='#00e5ff', linewidth=2.5, zorder=3)
        
        if bic_df is not None:
            ax.plot(bic_df['longitude'], bic_df['latitude'], label=f"Best In Class Benchmark ({format_lap_time(best_bic['Lap Time (s)'])})", color='#76ff03', linewidth=1.8, linestyle='--', alpha=0.85, zorder=2)
            
        ax.set_title(f"High Plains Raceway - Racing Line Comparison\nPersonal Best: {format_lap_time(best_user['Lap Time (s)'])} vs Benchmark", fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Longitude', fontsize=11)
        ax.set_ylabel('Latitude', fontsize=11)
        ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333333', fontsize=11, loc='upper right')
        ax.grid(True, alpha=0.25, linestyle=':')
        ax.axis('equal')
        plt.tight_layout()
        plt.savefig('charts/track_map_comparison.png')
        plt.close()
        print("Generated track map comparison chart: charts/track_map_comparison.png")

def main():
    print("Starting comprehensive multi-year telemetry analysis...")
    
    user_files = glob.glob(os.path.join("Recording CSVs", "*.csv"))
    best_in_class_files = glob.glob(os.path.join("Best in Class Recording", "*.csv"))
    
    all_files = [(f, "User") for f in user_files] + [(f, "Best_In_Class") for f in best_in_class_files]
    print(f"Processing {len(all_files)} total CSV files ({len(user_files)} User sessions)...")
    
    results = []
    detailed_laps_results = []
    
    for f, rec_type in all_files:
        res = analyze_file(f, rec_type)
        if res and res['Date'] is not None:
            results.append(res)
            
        lap_data = analyze_laps_detailed(f, rec_type)
        if lap_data:
            detailed_laps_results.extend(lap_data)
            
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(['Type', 'Date']).reset_index(drop=True)
    
    # Save detailed laps to CSV
    if detailed_laps_results:
        df_detailed = pd.DataFrame(detailed_laps_results)
        df_detailed = df_detailed.sort_values(['Type', 'Date', 'Lap']).reset_index(drop=True)
        df_detailed['Date_str'] = df_detailed['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_detailed.to_csv('detailed_lap_analysis.csv', index=False)
        print(f"Generated detailed lap analysis CSV: detailed_lap_analysis.csv ({len(df_detailed)} laps)")
        plot_track_map(pd.DataFrame(detailed_laps_results))
    
    # Format for markdown summary
    df_markdown = df_results[df_results['Type'] == 'User'].copy()
    df_markdown['Date_Formatted'] = df_markdown['Date'].dt.strftime('%Y-%m-%d %H:%M')
    df_markdown['Best Lap'] = df_markdown['Best Lap Time (s)'].apply(format_lap_time)
    
    summary_cols = ['Date_Formatted', 'File', 'Best Lap', 'Max Speed (mph)', 'Max Lateral G', 'Max Braking G', 'WOT %']
    df_display = df_markdown[summary_cols].rename(columns={'Date_Formatted': 'Date'})
    markdown_table = df_display.to_markdown(index=False)
    
    os.makedirs('reports', exist_ok=True)
    summary_path = os.path.join('reports', 'analysis_summary.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Porsche Track Precision Analysis (2-Year Progression)\n\n")
        f.write(f"**Vehicle:** Porsche 718 Cayman GT4 | **Track:** High Plains Raceway (Full Course)\n\n")
        f.write(f"**Total Sessions:** {len(df_markdown)} | **Total Timed Laps:** {len(detailed_laps_results)}\n\n")
        f.write("## Session Breakdown\n\n")
        f.write(markdown_table)
        f.write("\n")
        
    print(f"Generated updated {summary_path}")
    
    # Set dark motorsport style for all plots
    os.makedirs('charts', exist_ok=True)
    plt.style.use('dark_background')
    
    user_results = df_results[df_results['Type'] == 'User'].copy()
    
    # 1. Best Lap Time Trend Chart
    df_laps = user_results.dropna(subset=['Best Lap Time (s)']).copy()
    if not df_laps.empty:
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        ax.plot(df_laps['Date'], df_laps['Best Lap Time (s)'], marker='o', markersize=6, linestyle='-', color='#00e5ff', linewidth=2, label='Session Best Lap')
        
        # Calculate running best
        df_laps['Running_Best'] = df_laps['Best Lap Time (s)'].cummin()
        ax.step(df_laps['Date'], df_laps['Running_Best'], where='post', color='#ff1744', linestyle='--', linewidth=2, label='Progression Frontier (PB)')
        
        # Annotate personal record
        min_row = df_laps.loc[df_laps['Best Lap Time (s)'].idxmin()]
        ax.annotate(f"PB: {format_lap_time(min_row['Best Lap Time (s)'])}",
                    xy=(min_row['Date'], min_row['Best Lap Time (s)']),
                    xytext=(-45, 25), textcoords='offset points',
                    ha='center', fontsize=11, fontweight='bold', color='#ffea00',
                    arrowprops=dict(arrowstyle='->', color='#ffea00', lw=1.5))
        
        ax.set_title('High Plains Raceway - Lap Time Progression (2024 - 2026)', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Lap Time (M:SS)', fontsize=11)
        
        # Y-axis formatted as M:SS
        def time_formatter(x, pos):
            return f"{int(x//60)}:{int(x%60):02d}"
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
        
        ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333333', fontsize=10)
        ax.grid(True, alpha=0.25, linestyle=':')
        plt.xticks(rotation=35)
        plt.tight_layout()
        plt.savefig('charts/best_lap_time_trend.png')
        plt.close()
        print("Generated: charts/best_lap_time_trend.png")

    # 2. Max Speed Trend Chart
    df_speed = user_results.dropna(subset=['Max Speed (mph)']).copy()
    if not df_speed.empty:
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        ax.plot(df_speed['Date'], df_speed['Max Speed (mph)'], marker='o', markersize=5, linestyle='-', color='#00e676', linewidth=2, label='Top Speed (mph)')
        ax.set_title('Top Speed Evolution - Back Straight (2024 - 2026)', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Speed (mph)', fontsize=11)
        ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333333', fontsize=10)
        ax.grid(True, alpha=0.25, linestyle=':')
        plt.xticks(rotation=35)
        plt.tight_layout()
        plt.savefig('charts/max_speed_trend.png')
        plt.close()
        print("Generated: charts/max_speed_trend.png")

    # 3. G-Forces Trend Chart
    df_lat = user_results.dropna(subset=['Max Lateral G']).copy()
    df_brake = user_results.dropna(subset=['Max Braking G']).copy()
    if not df_lat.empty:
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        ax.plot(df_lat['Date'], df_lat['Max Lateral G'], marker='o', markersize=5, linestyle='-', color='#76ff03', linewidth=2, label='Peak Lateral Grip (Cornering G)')
        if not df_brake.empty:
            ax.plot(df_brake['Date'], df_brake['Max Braking G'].abs(), marker='s', markersize=5, linestyle='--', color='#ff3d00', linewidth=1.8, label='Peak Braking Deceleration (Brake G)')
        ax.set_title('Chassis Dynamics Evolution - Lateral Grip & Braking G (2024 - 2026)', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('G-Force (g)', fontsize=11)
        ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333333', fontsize=10)
        ax.grid(True, alpha=0.25, linestyle=':')
        plt.xticks(rotation=35)
        plt.tight_layout()
        plt.savefig('charts/max_gforce_trend.png')
        plt.close()
        print("Generated: charts/max_gforce_trend.png")

    # 4. WOT Throttle Commitment Trend Chart
    df_wot = user_results.dropna(subset=['WOT %']).copy()
    if not df_wot.empty:
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        ax.plot(df_wot['Date'], df_wot['WOT %'], marker='o', markersize=5, linestyle='-', color='#ff9100', linewidth=2, label='Wide Open Throttle Commitment (% of lap)')
        ax.set_title('Driver Commitment - Wide Open Throttle % (2024 - 2026)', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('WOT Time (%)', fontsize=11)
        ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333333', fontsize=10)
        ax.grid(True, alpha=0.25, linestyle=':')
        plt.xticks(rotation=35)
        plt.tight_layout()
        plt.savefig('charts/wot_throttle_progression.png')
        plt.close()
        print("Generated: charts/wot_throttle_progression.png")

    print("\nAll progression charts successfully regenerated with complete 2-year data!")

if __name__ == '__main__':
    main()
