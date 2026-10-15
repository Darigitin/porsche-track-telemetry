import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load elevation data
df_elev = pd.read_csv('charts/hpr_elevation_profile.csv')

# Load PB lap speed & distance data
filepath = 'Recording CSVs/recording-2026-10-10-10-57-43.csv'
df = pd.read_csv(filepath)
df.columns = df.columns.str.strip()
lap_ends = df.index[df['laptime'] > df['laptime'].shift(-1).fillna(0)].tolist()
start = 0
for end in lap_ends:
    sub = df.iloc[start:end+1]
    t = sub['laptime'].max()
    if 115000 <= t <= 120000:
        lap = sub.copy().reset_index(drop=True)
        break
    start = end + 1

lap['dist'] = lap['distanceCounter'] - lap['distanceCounter'].iloc[0]
if lap['speed'].max() < 80:
    lap['spd'] = lap['speed'] * 2.23694
else:
    lap['spd'] = lap['speed'] * 0.621371

# Interpolate elevation across full distance grid
grid_dist = np.linspace(0, lap['dist'].max(), 500)
elev_interp = np.interp(grid_dist, df_elev['dist_m'], df_elev['elev_ft'])
spd_interp = np.interp(grid_dist, lap['dist'], lap['spd'])

# Color Palette
COLOR_BG = '#090a0d'
COLOR_PANEL = '#131419'
COLOR_BORDER = '#252733'
COLOR_WHITE = '#ffffff'
COLOR_SILVER = '#9ca3af'
COLOR_MUTED = '#6b7280'
COLOR_RED = '#e4002b'
COLOR_CYAN = '#00e5ff'

plt.style.use('dark_background')
fig, (ax_elev, ax_spd) = plt.subplots(2, 1, figsize=(15, 9), dpi=150, sharex=True, gridspec_kw={'height_ratios': [1.3, 1.0]})
fig.patch.set_facecolor(COLOR_BG)
ax_elev.set_facecolor(COLOR_PANEL)
ax_spd.set_facecolor(COLOR_PANEL)

# 1. Elevation Plot
ax_elev.fill_between(grid_dist, 4950, elev_interp, color='#3b82f6', alpha=0.25)
ax_elev.plot(grid_dist, elev_interp, color='#60a5fa', linewidth=2.8, label='USGS 1m Topographic Elevation (ft)')
ax_elev.set_ylim(4960, 5065)
ax_elev.set_ylabel('Elevation (Feet MSL)', fontsize=11, fontweight='bold', color=COLOR_WHITE)
ax_elev.set_title('HIGH PLAINS RACEWAY - 3D TOPOGRAPHIC ELEVATION PROFILE & CORNER CORRELATION\nAltitude Range: 4,968 ft to 5,053 ft (84.6 ft Vertical Relief / 300+ ft Cumulative Grade)', fontsize=13, fontweight='bold', color=COLOR_WHITE, pad=12)
ax_elev.grid(True, alpha=0.15, linestyle=':', color=COLOR_BORDER)
ax_elev.tick_params(colors=COLOR_SILVER)

# Critical Elevation Landmarks
corners = [
    ("T1", 200, 5037, "T1 Turn-in"),
    ("T3 (Carousel)", 650, 5028, "Carousel Apex"),
    ("Main Straight", 1150, 5003, "Downhill Run"),
    ("T4 (Bikers Berm)", 1450, 5012, "Uphill Brake"),
    ("T5 (Niagara)", 1630, 5022, "Steep Crest"),
    ("T6 (Danny's Lesson)", 1920, 4968, "Lowest Point (4,968')"),
    ("T7 (HP Drifter)", 2270, 5015, "Blind Climb"),
    ("T8 (80' Hook)", 2575, 4995, "Infield Dip"),
    ("T9 (Bobsled)", 2850, 5018, "Climbing"),
    ("T11 (Hilltop)", 3300, 5053, "Highest Point (5,053')"),
    ("T12 (Ladder)", 3460, 5040, "Descent"),
    ("T13-15 (Corkscrew)", 3700, 5010, "Laguna Plunge"),
    ("S/F", 3995, 5036, "Pit Straight")
]

for name, d, h, desc in corners:
    is_extreme = "Lowest" in desc or "Highest" in desc or "Niagara" in desc
    c = COLOR_RED if is_extreme else COLOR_SILVER
    ax_elev.axvline(d, color=c, alpha=0.35, linestyle='--')
    ax_elev.scatter(d, h, color=c, s=35, zorder=5)
    ax_elev.annotate(name, (d, h), textcoords="offset points", xytext=(0, 10),
                    fontsize=8.5, fontweight='bold' if is_extreme else 'normal',
                    color=COLOR_WHITE if is_extreme else COLOR_SILVER, ha='center',
                    bbox=dict(boxstyle="square,pad=0.2", facecolor=COLOR_BG, edgecolor=c, alpha=0.85, lw=0.8),
                    zorder=6)

# 2. Speed Plot (GT4 PB Lap)
ax_spd.plot(grid_dist, spd_interp, color=COLOR_CYAN, linewidth=2.2, label='Porsche 718 GT4 Speed (MPH)')
ax_spd.fill_between(grid_dist, 0, spd_interp, color=COLOR_CYAN, alpha=0.10)
ax_spd.set_ylim(30, 145)
ax_spd.set_ylabel('Speed (MPH)', fontsize=11, fontweight='bold', color=COLOR_CYAN)
ax_spd.set_xlabel('Lap Distance (Meters)', fontsize=11, fontweight='bold', color=COLOR_WHITE)
ax_spd.grid(True, alpha=0.15, linestyle=':', color=COLOR_BORDER)
ax_spd.tick_params(colors=COLOR_SILVER)

# Highlight Niagara / Danny's Lesson
ax_spd.axvspan(1450, 1950, color=COLOR_RED, alpha=0.15, label='Turn 5-6 Plunge & Compression (Highest Time Loss: +0.60s)')

ax_elev.legend(loc='lower left', facecolor=COLOR_PANEL, edgecolor=COLOR_BORDER)
ax_spd.legend(loc='upper right', facecolor=COLOR_PANEL, edgecolor=COLOR_BORDER)

plt.tight_layout()
out_fig = 'charts/hpr_elevation_profile.png'
plt.savefig(out_fig, facecolor=COLOR_BG, edgecolor='none')
plt.close()
print("Generated elevation profile chart:", out_fig)
