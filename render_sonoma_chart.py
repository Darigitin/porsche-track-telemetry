import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def render_sonoma_debrief_chart():
    csv_file = 'TrackAddict Data_ 20261016-143634 Sonoma Raceway - 2.01.856.csv'
    df = pd.read_csv(csv_file, comment='#')
    
    lap7 = df[df['Lap'] == 7].copy()
    lap2 = df[df['Lap'] == 2].copy()
    
    # Distance calculation
    for lap in [lap7, lap2]:
        dt = lap['Time'].diff().fillna(0)
        v_fps = lap['Speed (MPH)'] * 1.46667
        lap['Dist_ft'] = (v_fps * dt).cumsum()
        
    # Coasting zones on Lap 7
    thr = lap7['Throttle Position (%) *OBD']
    brk = lap7['Brake (calculated)']
    lap7['is_coast'] = (thr < 10) & (brk == 0)
    
    # Dark modern motorsport theme
    COLOR_BG = '#090a0d'
    COLOR_CARD = '#131419'
    COLOR_BORDER = '#252733'
    COLOR_GOLD = '#e5a93c'
    COLOR_WHITE = '#ffffff'
    COLOR_RED = '#e4002b'
    COLOR_CYAN = '#00d2be'
    COLOR_SILVER = '#9ca3af'
    
    fig = plt.figure(figsize=(14, 10), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    
    # Grid layout: 3 rows of subplots
    gs = fig.add_gridspec(3, 1, height_ratios=[1.2, 0.9, 0.9], hspace=0.25, left=0.08, right=0.95, top=0.90, bottom=0.08)
    
    ax_speed = fig.add_subplot(gs[0])
    ax_throttle = fig.add_subplot(gs[1], sharex=ax_speed)
    ax_map = fig.add_subplot(gs[2])
    
    for ax in [ax_speed, ax_throttle]:
        ax.set_facecolor(COLOR_CARD)
        ax.tick_params(colors=COLOR_SILVER, labelsize=10)
        for spine in ax.spines.values():
            spine.set_color(COLOR_BORDER)
        ax.grid(True, color=COLOR_BORDER, linestyle='--', alpha=0.6)
        
    # Top plot: Speed Trace
    ax_speed.plot(lap7['Dist_ft'], lap7['Speed (MPH)'], color=COLOR_CYAN, linewidth=2.0, label='Lap 7 (2:01.856 PB)')
    ax_speed.plot(lap2['Dist_ft'], lap2['Speed (MPH)'], color=COLOR_SILVER, linewidth=1.2, linestyle=':', alpha=0.7, label='Lap 2 (2:02.970)')
    ax_speed.set_ylabel('Speed (MPH)', color=COLOR_WHITE, fontsize=11, fontweight='bold')
    ax_speed.legend(loc='lower left', facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, labelcolor=COLOR_WHITE)
    ax_speed.set_title('SONOMA RACEWAY TELEMETRY DEBRIEF — 996 CAB (3.2 SWAP) — 2:01.856 PB', 
                       color=COLOR_WHITE, fontsize=14, fontweight='bold', pad=12, loc='left')
    
    # Annotate key Sonoma corners
    corner_labels = [
        (1460, 'T2 Crest\n45.6 mph'),
        (2670, 'T4\n56.0 mph'),
        (5160, 'T6 Carousel\n63.4 mph'),
        (7200, 'T7 Hairpin\n39.9 mph'),
        (8460, 'T8/8A Esses\n70.2 mph'),
        (10420, 'T10\n71.3 mph'),
        (11850, 'T11 Hairpin\n32.5 mph'),
    ]
    for dist, text in corner_labels:
        ax_speed.axvline(x=dist, color=COLOR_BORDER, linestyle='--', alpha=0.8)
        ax_speed.text(dist, 106, text, color=COLOR_GOLD, fontsize=8.5, ha='center', va='bottom', fontweight='bold')
    ax_speed.set_ylim(25, 120)
    
    # Highlight coasting zones on speed trace
    coast_starts = lap7.index[lap7['is_coast'] & ~lap7['is_coast'].shift(1, fill_value=False)].tolist()
    coast_ends = lap7.index[~lap7['is_coast'] & lap7['is_coast'].shift(1, fill_value=False)].tolist()
    
    for s_idx in coast_starts:
        matching_ends = [e for e in coast_ends if e > s_idx]
        if matching_ends:
            e_idx = matching_ends[0]
            d_start = lap7.loc[s_idx, 'Dist_ft']
            d_end = lap7.loc[e_idx, 'Dist_ft']
            if (d_end - d_start) > 60:
                ax_speed.axvspan(d_start, d_end, color=COLOR_RED, alpha=0.18)
                ax_throttle.axvspan(d_start, d_end, color=COLOR_RED, alpha=0.18)

    # Middle plot: Throttle & Calculated Brake
    ax_throttle.plot(lap7['Dist_ft'], lap7['Throttle Position (%) *OBD'], color=COLOR_GOLD, linewidth=1.8, label='Throttle Position (%)')
    ax_throttle.plot(lap7['Dist_ft'], lap7['Brake (calculated)'] * 100, color=COLOR_RED, linewidth=1.5, label='Brake (Calc %)')
    ax_throttle.set_ylabel('Pedal Input (%)', color=COLOR_WHITE, fontsize=11, fontweight='bold')
    ax_throttle.set_xlabel('Lap Distance (Feet)', color=COLOR_WHITE, fontsize=11, fontweight='bold')
    ax_throttle.set_ylim(-5, 110)
    ax_throttle.legend(loc='upper right', facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, labelcolor=COLOR_WHITE)
    
    # Callout boxes on Throttle
    ax_throttle.text(10550, 40, '2.2s Coasting Dead-Zone\n(T10 into straight)', color='#ff6b6b', fontsize=8.5, fontweight='bold', bbox=dict(facecolor=COLOR_CARD, edgecolor=COLOR_RED, pad=3))
    ax_throttle.text(12000, 40, '2.2s Coasting Dead-Zone\n(T11 exit onto main)', color='#ff6b6b', fontsize=8.5, fontweight='bold', bbox=dict(facecolor=COLOR_CARD, edgecolor=COLOR_RED, pad=3))

    # Bottom plot: Track Map colored by Speed
    ax_map.set_facecolor(COLOR_CARD)
    ax_map.tick_params(colors=COLOR_SILVER, labelsize=9)
    for spine in ax_map.spines.values():
        spine.set_color(COLOR_BORDER)
    
    sc = ax_map.scatter(lap7['Longitude'], lap7['Latitude'], c=lap7['Speed (MPH)'], cmap='plasma', s=8)
    ax_map.set_title('GPS TRACK TRACE COLORED BY VELOCITY (RED/PURPLE = APEX BRAKING | YELLOW = TOP SPEED)', 
                     color=COLOR_WHITE, fontsize=11, fontweight='bold', pad=8, loc='left')
    ax_map.set_xlabel('Longitude', color=COLOR_SILVER, fontsize=9)
    ax_map.set_ylabel('Latitude', color=COLOR_SILVER, fontsize=9)
    ax_map.set_aspect('equal', adjustable='datalim')
    cbar = fig.colorbar(sc, ax=ax_map, orientation='horizontal', pad=0.25, shrink=0.6)
    cbar.set_label('Speed (MPH)', color=COLOR_WHITE, fontsize=9, fontweight='bold')
    cbar.ax.tick_params(colors=COLOR_SILVER, labelsize=8)

    outpath = os.path.join('charts', 'sonoma_996_telemetry_debrief.png')
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    print(f"Saved visual debrief chart to: {outpath}")
    return outpath

if __name__ == '__main__':
    render_sonoma_debrief_chart()
