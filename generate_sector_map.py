#!/usr/bin/env python3
"""
High Plains Raceway (Full Course) - Telemetry Sector Map Generator.
Visualizes the 8 telemetry micro-sectors used by the pit-lane crew chief,
showing how Sectors 6 & 7 map to HPR's 15 corners and where lap time is won or lost.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Color Palette (Porsche Motorsport Livery)
COLOR_BG = '#090a0d'
COLOR_PANEL = '#131419'
COLOR_BORDER = '#252733'
COLOR_WHITE = '#ffffff'
COLOR_SILVER = '#9ca3af'
COLOR_MUTED = '#6b7280'
COLOR_RED = '#e4002b'

# 8 Sector Palette
SECTOR_COLORS = [
    '#3b82f6',  # S1: Blue (T1-T2)
    '#06b6d4',  # S2: Cyan (T3 Carousel)
    '#10b981',  # S3: Green (Back Straight & T4 Brake)
    '#ef4444',  # S4: Bright Red (T5-T6 Roller Coaster - High Loss)
    '#f59e0b',  # S5: Amber (T7 Crest)
    '#8b5cf6',  # S6: Purple (T8-T9 Downhill Infield) - MATCHING PACE
    '#ec4899',  # S7: Magenta (T10-T12 Hairpins) - MATCHING PACE
    '#6366f1',  # S8: Indigo (T13-T15 Front Straight)
]

SECTOR_DATA = [
    {"sec": "S1", "dist": "0 - 500m", "turns": "Paddock Straight & T1", "delta": "+0.494s", "note": "Pit wall, timing tower & T1 turn-in"},
    {"sec": "S2", "dist": "500 - 1000m", "turns": "T2 & T3 (The Carousel)", "delta": "+0.241s", "note": "180° carousel sweep launch to 2,838' straight"},
    {"sec": "S3", "dist": "1000 - 1500m", "turns": "2,838' Straight & T4 (Bikers Berm)", "delta": "+0.334s", "note": "133+ mph top speed & heavy threshold brake"},
    {"sec": "S4", "dist": "1500 - 2000m", "turns": "T5 (Niagara) & T6 (Danny's Lesson)", "delta": "+0.602s", "note": "Steep downhill plunge & southwest hairpin"},
    {"sec": "S5", "dist": "2000 - 2500m", "turns": "T7 (High Plains Drifter)", "delta": "+0.229s", "note": "Fast blind uphill right-hand crest"},
    {"sec": "S6", "dist": "2500 - 3000m", "turns": "T8 & T9 (To Hell on a Bobsled)", "delta": "+0.058s", "note": "80' R hook into technical climbing esses"},
    {"sec": "S7", "dist": "3000 - 3500m", "turns": "T10, T11 & T12 (Ladder to Heaven)", "delta": "+0.013s", "note": "Peak elevation hairpin & downhill sweep"},
    {"sec": "S8", "dist": "3500 - 3995m", "turns": "T13 - T15 (Prairie Corkscrew)", "delta": "+0.277s", "note": "Laguna-style blind downhill drop to pit straight"},
]

def load_pb_lap():
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
    return lap

def main():
    lap = load_pb_lap()
    total_dist = lap['dist'].max()
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9.5), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    
    # Left: Track Map (GPS)
    ax_map = fig.add_axes([0.05, 0.08, 0.58, 0.82])
    ax_map.set_facecolor(COLOR_PANEL)
    ax_map.grid(True, alpha=0.12, linestyle=':', color=COLOR_BORDER)
    
    # 8 distance bins
    edges = np.linspace(0, total_dist, 9)
    
    for i in range(8):
        d0, d1 = edges[i], edges[i+1]
        mask = (lap['dist'] >= d0) & (lap['dist'] <= d1)
        sub = lap[mask]
        
        # Thicker line for S6 & S7
        lw = 4.8 if i in [5, 6] else 3.2
        alpha = 1.0 if i in [5, 6] else 0.85
        
        ax_map.plot(sub['longitude'], sub['latitude'], 
                    color=SECTOR_COLORS[i], linewidth=lw, alpha=alpha, 
                    solid_capstyle='round', zorder=4)
        
        # Sector label on map at midpoint
        mid_pt = sub.iloc[len(sub)//2]
        ax_map.annotate(f"S{i+1}", 
                        (mid_pt['longitude'], mid_pt['latitude']),
                        textcoords="offset points", xytext=(0, 6),
                        fontsize=9.5, fontweight='bold', color=SECTOR_COLORS[i],
                        ha='center', va='bottom',
                        bbox=dict(boxstyle="round,pad=0.2", facecolor=COLOR_BG, edgecolor=SECTOR_COLORS[i], alpha=0.85, lw=1.2),
                        zorder=6)

    # Official HPR Turn Annotations
    turn_approx_dists = [
        ("T1", 200, (8, 8)),
        ("T2", 400, (-15, 8)),
        ("T3 (Carousel)", 650, (12, -10)),
        ("2,838' Straight", 1150, (0, -14)),
        ("T4 (Bikers Berm)", 1450, (10, 8)),
        ("T5 (Niagara)", 1630, (-18, 6)),
        ("T6 (Danny's Lesson)", 1920, (10, -10)),
        ("T7 (HP Drifter)", 2270, (10, 8)),
        ("T8 (80' R)", 2575, (-14, 8)),
        ("T9 (Bobsled)", 2850, (10, -10)),
        ("T10", 3100, (-14, 8)),
        ("T11 (Hilltop)", 3300, (10, 8)),
        ("T12 (Ladder to Heaven)", 3460, (-18, -10)),
        ("T13-15 (Corkscrew)", 3700, (10, 8)),
        ("Paddock Straight (1,397')", 3920, (-25, -12)),
    ]
    
    for name, d, offset in turn_approx_dists:
        pt = lap.iloc[(lap['dist'] - d).abs().argmin()]
        is_highlight = any(k in name for k in ["T8", "T9", "T10", "T11", "T12"])
        is_loss = any(k in name for k in ["T1", "T4", "T5", "T6"])
        badge_color = '#ec4899' if is_highlight else (COLOR_RED if is_loss else COLOR_SILVER)
        
        ax_map.scatter(pt['longitude'], pt['latitude'], color=COLOR_WHITE, s=25, zorder=5)
        ax_map.annotate(name, 
                        (pt['longitude'], pt['latitude']),
                        textcoords="offset points", xytext=offset,
                        fontsize=8.5, fontweight='bold' if is_highlight else 'normal',
                        color=COLOR_WHITE if is_highlight else COLOR_SILVER,
                        bbox=dict(boxstyle="square,pad=0.15", facecolor='#1e2029', edgecolor=badge_color, alpha=0.9, lw=0.8),
                        zorder=7)
        
    # Start / Finish Line marker
    sf_pt = lap.iloc[0]
    ax_map.scatter(sf_pt['longitude'], sf_pt['latitude'], color='#22c55e', s=80, marker='s', zorder=8)
    ax_map.annotate("START / FINISH", 
                    (sf_pt['longitude'], sf_pt['latitude']),
                    textcoords="offset points", xytext=(-25, -20),
                    fontsize=9, fontweight='bold', color='#22c55e',
                    bbox=dict(boxstyle="round,pad=0.25", facecolor=COLOR_BG, edgecolor='#22c55e', lw=1.2),
                    zorder=9)

    ax_map.set_title("HIGH PLAINS RACEWAY (FULL COURSE: 2.55 MILES / 15 TURNS)\nCAN-Bus Telemetry Micro-Sectors (8 × 500m Gates)",
                     fontsize=12, fontweight='bold', color=COLOR_WHITE, pad=12)
    ax_map.axis('equal')
    ax_map.tick_params(colors=COLOR_MUTED, labelsize=8)
    ax_map.set_xlabel("Longitude", color=COLOR_MUTED, fontsize=9)
    ax_map.set_ylabel("Latitude", color=COLOR_MUTED, fontsize=9)
    
    # Border styling
    for spine in ax_map.spines.values():
        spine.set_edgecolor(COLOR_BORDER)
        spine.set_linewidth(1.2)

    # Right: Telemetry Sector Breakdown Panel
    ax_info = fig.add_axes([0.65, 0.08, 0.31, 0.82])
    ax_info.set_facecolor(COLOR_PANEL)
    ax_info.axis('off')
    
    # Border for panel
    rect = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                  facecolor=COLOR_PANEL, edgecolor=COLOR_BORDER, linewidth=1.5,
                                  transform=ax_info.transAxes)
    ax_info.add_patch(rect)
    
    # Title
    ax_info.text(0.06, 0.95, "TELEMETRY SECTORS & DELTA", fontsize=13, fontweight='bold', color=COLOR_WHITE, transform=ax_info.transAxes)
    ax_info.text(0.06, 0.915, "1:59.67 PB vs. 1:56.55 Instructor Benchmark", fontsize=10, color=COLOR_SILVER, transform=ax_info.transAxes)
    
    y = 0.850
    y_step = 0.090
    card_h = 0.078
    for item in SECTOR_DATA:
        i = int(item['sec'][1]) - 1
        is_highlight = item['sec'] in ['S6', 'S7']
        is_loss = item['sec'] in ['S1', 'S4']
        
        # Sector badge card
        bg_card = '#201625' if is_highlight else ('#261214' if is_loss else '#16171d')
        b_edge = SECTOR_COLORS[i] if is_highlight else (COLOR_RED if is_loss else COLOR_BORDER)
        
        card = patches.FancyBboxPatch((0.05, y - card_h), 0.90, card_h,
                                      boxstyle="round,pad=0.008,rounding_size=0.015",
                                      facecolor=bg_card, edgecolor=b_edge, linewidth=1.5 if (is_highlight or is_loss) else 1.0,
                                      transform=ax_info.transAxes)
        ax_info.add_patch(card)
        
        # Sector Color square
        sq = patches.Rectangle((0.07, y - 0.052), 0.038, 0.038, facecolor=SECTOR_COLORS[i], transform=ax_info.transAxes)
        ax_info.add_patch(sq)
        
        # Sector Name & Range
        ax_info.text(0.125, y - 0.024, f"{item['sec']} • {item['turns']}", fontsize=9.5, fontweight='bold', color=COLOR_WHITE, transform=ax_info.transAxes)
        ax_info.text(0.125, y - 0.052, f"{item['dist']} | {item['note']}", fontsize=7.8, color=COLOR_SILVER, transform=ax_info.transAxes)
        
        # Delta Badge
        delta_color = '#22c55e' if item['delta'] in ['+0.013s', '+0.058s'] else (COLOR_RED if is_loss else '#f59e0b')
        status_text = "PACE MATCH" if is_highlight else ("KEY LOSS" if is_loss else "")
        ax_info.text(0.92, y - 0.024, item['delta'], fontsize=10.0, fontweight='bold', color=delta_color, ha='right', transform=ax_info.transAxes)
        if status_text:
            ax_info.text(0.92, y - 0.052, status_text, fontsize=7.0, fontweight='bold', color=delta_color, ha='right', transform=ax_info.transAxes)
            
        y -= y_step

    # Bottom summary callout
    y_callout = 0.018
    callout_card = patches.FancyBboxPatch((0.05, y_callout), 0.90, 0.088,
                                          boxstyle="round,pad=0.01",
                                          facecolor='#111827', edgecolor='#374151', linewidth=1.2,
                                          transform=ax_info.transAxes)
    ax_info.add_patch(callout_card)
    ax_info.text(0.08, y_callout + 0.056, "CREW CHIEF TAKEAWAY:", fontsize=8.5, fontweight='bold', color=COLOR_WHITE, transform=ax_info.transAxes)
    ax_info.text(0.08, y_callout + 0.020, "S6 & S7 (Turns 8-12) delta is +0.071s combined. You are already at\nbenchmark pace in the technical infield! Time is lost in S1 & S4.",
                 fontsize=8.0, color='#9ca3af', transform=ax_info.transAxes)

    os.makedirs('charts', exist_ok=True)
    outpath = 'charts/hpr_sector_map.png'
    plt.savefig(outpath, facecolor=COLOR_BG, edgecolor='none')
    plt.close()
    print(f"Generated High Plains Raceway Sector Map: {outpath}")

if __name__ == '__main__':
    main()
