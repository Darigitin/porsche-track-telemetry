#!/usr/bin/env python3
"""
Instagram Carousel Slide Generator for Porsche Track Telemetry.
Official Porsche Motorsport Palette: Deep Carbon Black, Guards Red, and Pure White.
Renders high-impact 1080x1350 (4:5 vertical) carousel slides optimized for Instagram mobile feed.

Slides:
1. Cover: 2-Year Progression Hero Card (2:16.78 -> 1:59.62 PB)
2. Lap Time Evolution: Chronological drop across 61 sessions & 519 laps
3. Racing Line Comparison: 1:59.62 PB (Guards Red) vs 1:56.86 Benchmark (White) at HPR
4. Chassis Dynamics: Peak Lateral Grip (White) & Threshold Braking G (Guards Red)
5. Throttle Commitment: Wide Open Throttle (WOT %) Progression (Guards Red)
6. Engineering Debrief: Setup takeaways, tire pressures & driver insights
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as patches
from datetime import datetime

# Configure directories
CHART_DIR = os.path.join("charts", "carousel")
THOR_DIR = r"\\THOR\plex\Cayman Videos\Social Exports\Carousel"
os.makedirs(CHART_DIR, exist_ok=True)

# Official Porsche Motorsport Livery Palette
COLOR_BG = '#090a0d'               # Deep Carbon Asphalt Black
COLOR_CARD = '#131419'             # Technical Graphite Panel
COLOR_BORDER = '#252733'           # Platinum Silver Divider
COLOR_RED = '#e4002b'              # Porsche Motorsport Guards Red
COLOR_WHITE = '#ffffff'            # Pure Racing White
COLOR_SILVER = '#9ca3af'           # Platinum Metallic Grey
COLOR_MUTED = '#6b7280'            # Technical Dark Grey
COLOR_RED_TINT = '#240d12'         # Subtle Red Card Accent

def style_legend(leg):
    if leg is not None:
        leg.get_frame().set_facecolor(COLOR_CARD)
        leg.get_frame().set_edgecolor(COLOR_BORDER)
        leg.get_frame().set_linewidth(1.2)
        for text in leg.get_texts():
            text.set_color(COLOR_WHITE)
            text.set_fontweight('bold')
    return leg

def format_lap_time(seconds):
    if pd.isna(seconds) or seconds is None or seconds <= 0:
        return "N/A"
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:06.3f}"

def create_slide_canvas():
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    overlay_ax = fig.add_axes([0, 0, 1, 1])
    overlay_ax.set_facecolor(COLOR_BG)
    overlay_ax.axis('off')
    return fig, overlay_ax

def add_header(overlay_ax, slide_num, total_slides, category, title, subtitle):
    # Slide Indicator & Category Tag
    overlay_ax.text(0.07, 0.960, f"SLIDE {slide_num:02d} / {total_slides:02d}",
                    transform=overlay_ax.transAxes, fontsize=11.0, fontweight='bold', color=COLOR_RED)
    overlay_ax.text(0.93, 0.960, category.upper(),
                    transform=overlay_ax.transAxes, fontsize=11.0, fontweight='bold', color=COLOR_SILVER, ha='right')
    
    # Title & Subtitle
    overlay_ax.text(0.07, 0.918, title,
                    transform=overlay_ax.transAxes, fontsize=19, fontweight='bold', color=COLOR_WHITE)
    overlay_ax.text(0.07, 0.884, subtitle,
                    transform=overlay_ax.transAxes, fontsize=11.5, color=COLOR_SILVER)

def add_footer_box(overlay_ax, insight_title, insight_text, swipe_label="SWIPE FOR NEXT METRIC ➔"):
    # Dark card at the bottom with ample height
    rect = patches.FancyBboxPatch((0.06, 0.020), 0.88, 0.150,
                                  boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.5,
                                  transform=overlay_ax.transAxes, zorder=10)
    overlay_ax.add_patch(rect)
    
    # Red accent stripe on the left edge of footer card
    stripe = patches.Rectangle((0.06, 0.035), 0.008, 0.120,
                               facecolor=COLOR_RED, edgecolor='none',
                               transform=overlay_ax.transAxes, zorder=12)
    overlay_ax.add_patch(stripe)
    
    # Insight Title (Porsche Guards Red)
    overlay_ax.text(0.088, 0.140, f">>> {insight_title.upper()}",
                    transform=overlay_ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_RED, zorder=11)
    
    # Insight Text (multi-line, strictly contained above y=0.055)
    overlay_ax.text(0.088, 0.114, insight_text,
                    transform=overlay_ax.transAxes, fontsize=9.4, color='#e5e7eb', va='top', zorder=11, linespacing=1.30)
    
    # Swipe CTA on its own dedicated bottom margin, separated vertically
    if swipe_label:
        overlay_ax.text(0.915, 0.036, swipe_label,
                        transform=overlay_ax.transAxes, fontsize=9.0, fontweight='bold', color=COLOR_RED, ha='right', zorder=11)

def load_data():
    from analyze_track_data import analyze_file
    user_files = glob.glob(os.path.join("Recording CSVs", "*.csv"))
    results = []
    for f in user_files:
        res = analyze_file(f, "User")
        if res and res['Date'] is not None:
            results.append(res)
    df = pd.DataFrame(results).sort_values('Date').reset_index(drop=True)
    return df

# -------------------------------------------------------------
# SLIDE 1: HERO COVER CARD (Porsche Motorsport Livery)
# -------------------------------------------------------------
def generate_slide_1(df):
    fig, overlay_ax = create_slide_canvas()

    # Prominent pill badge container in Porsche Racing Colors
    pill_w = 0.54
    pill_h = 0.036
    pill_x = (1.0 - pill_w) / 2.0
    pill_y = 0.940
    badge = patches.FancyBboxPatch((pill_x, pill_y), pill_w, pill_h,
                                   boxstyle="round,pad=0.008,rounding_size=0.015",
                                   facecolor=COLOR_RED_TINT, edgecolor=COLOR_RED, linewidth=1.5,
                                   transform=overlay_ax.transAxes, zorder=5)
    overlay_ax.add_patch(badge)
    overlay_ax.text(0.50, pill_y + (pill_h / 2.0), "718 GT4 | TRACK TELEMETRY LAB",
                    transform=overlay_ax.transAxes, fontsize=11.0, fontweight='bold', color=COLOR_WHITE, ha='center', va='center', zorder=6)
    
    # Main Headline
    overlay_ax.text(0.50, 0.860, "CRACKING THE\n2-MINUTE BARRIER", transform=overlay_ax.transAxes,
                    fontsize=28, fontweight='bold', color=COLOR_WHITE, ha='center', va='center', linespacing=1.15)
    
    overlay_ax.text(0.50, 0.775, "2 Years of CAN-Bus Telemetry & Chassis Tuning\nHigh Plains Raceway (Full Course) • Porsche 718 Cayman GT4",
                    transform=overlay_ax.transAxes, fontsize=11.5, color=COLOR_SILVER, ha='center', va='center', linespacing=1.25)

    # Center Hero Stat Card (Red accent border)
    hero_card = patches.FancyBboxPatch((0.08, 0.44), 0.84, 0.28, boxstyle="round,pad=0.02,rounding_size=0.03",
                                       facecolor=COLOR_CARD, edgecolor=COLOR_RED, linewidth=2.0,
                                       transform=overlay_ax.transAxes)
    overlay_ax.add_patch(hero_card)

    overlay_ax.text(0.50, 0.665, "OFFICIAL ALL-TIME PERSONAL BEST", transform=overlay_ax.transAxes,
                    fontsize=12, fontweight='bold', color=COLOR_SILVER, ha='center')
    
    overlay_ax.text(0.50, 0.560, "1:59.62", transform=overlay_ax.transAxes,
                    fontsize=50, fontweight='bold', color=COLOR_WHITE, ha='center')
    
    overlay_ax.text(0.50, 0.475, "DROPPED -17.16s FROM 2:16.78 BASELINE", transform=overlay_ax.transAxes,
                    fontsize=12.5, fontweight='bold', color=COLOR_RED, ha='center')

    # 4 Quick Stat Metric Tiles (Porsche Tri-Color balance)
    tiles = [
        ("519", "TIMED LAPS", "61 Sessions Analyzed", COLOR_WHITE),
        ("+20.5 MPH", "TOP SPEED GAIN", "114.3 -> 134.8 mph", COLOR_RED),
        ("1.35G / 1.54G", "LATERAL GRIP", "Sustained / Peak Spike", COLOR_WHITE),
        ("36.6%", "WOT COMMITMENT", "Up from 2.2% baseline", COLOR_RED),
    ]
    
    positions = [(0.08, 0.275), (0.52, 0.275), (0.08, 0.135), (0.52, 0.135)]
    
    for (val, title, sub, color), (x, y) in zip(tiles, positions):
        box = patches.FancyBboxPatch((x, y), 0.40, 0.115, boxstyle="round,pad=0.015,rounding_size=0.02",
                                     facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2,
                                     transform=overlay_ax.transAxes)
        overlay_ax.add_patch(box)
        overlay_ax.text(x + 0.20, y + 0.080, val, transform=overlay_ax.transAxes,
                        fontsize=17, fontweight='bold', color=color, ha='center')
        overlay_ax.text(x + 0.20, y + 0.048, title, transform=overlay_ax.transAxes,
                        fontsize=9.5, fontweight='bold', color=COLOR_SILVER, ha='center')
        overlay_ax.text(x + 0.20, y + 0.020, sub, transform=overlay_ax.transAxes,
                        fontsize=8.5, color=COLOR_MUTED, ha='center')

    # Bottom Swipe CTA in Guards Red
    overlay_ax.text(0.50, 0.055, "SWIPE TO EXPLORE COMPLETE TELEMETRY PROGRESSION ➔",
                    transform=overlay_ax.transAxes, fontsize=11.0, fontweight='bold', color=COLOR_RED, ha='center')

    outpath = os.path.join(CHART_DIR, "slide_01_cover.png")
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    return outpath

# -------------------------------------------------------------
# SLIDE 2: LAP TIME PROGRESSION (White session laps + Red PB frontier)
# -------------------------------------------------------------
def generate_slide_2(df):
    fig, overlay_ax = create_slide_canvas()
    
    chart_ax = fig.add_axes([0.12, 0.245, 0.80, 0.57])
    chart_ax.set_facecolor(COLOR_CARD)
    
    df_laps = df.dropna(subset=['Best Lap Time (s)']).copy()
    df_laps['Running_Best'] = df_laps['Best Lap Time (s)'].cummin()
    
    # White Session Best Line with white markers
    chart_ax.plot(df_laps['Date'], df_laps['Best Lap Time (s)'], marker='o', markersize=4.5,
                  linestyle='-', color=COLOR_WHITE, linewidth=1.8, label='Session Best Lap', alpha=0.90)
    # Porsche Guards Red Step Line for Personal Records
    chart_ax.step(df_laps['Date'], df_laps['Running_Best'], where='post',
                  color=COLOR_RED, linestyle='--', linewidth=2.5, label='Personal Record Frontier')

    min_row = df_laps.loc[df_laps['Best Lap Time (s)'].idxmin()]
    chart_ax.annotate(f"PB: {format_lap_time(min_row['Best Lap Time (s)'])}",
                      xy=(min_row['Date'], min_row['Best Lap Time (s)']),
                      xytext=(-45, 28), textcoords='offset points',
                      ha='center', fontsize=10.5, fontweight='bold', color=COLOR_WHITE,
                      bbox=dict(boxstyle="round,pad=0.3", facecolor=COLOR_RED, edgecolor='none'),
                      arrowprops=dict(arrowstyle='->', color=COLOR_RED, lw=2))

    chart_ax.set_ylabel('Lap Time (M:SS)', fontsize=10.5, color=COLOR_WHITE, fontweight='bold')
    
    def time_formatter(x, pos):
        return f"{int(x//60)}:{int(x%60):02d}"
    chart_ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
    chart_ax.tick_params(colors=COLOR_SILVER, labelsize=8.5)
    chart_ax.grid(True, alpha=0.15, linestyle=':', color=COLOR_BORDER)
    leg = chart_ax.legend(frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER,
                          fontsize=9.0, loc='upper right')
    style_legend(leg)
    plt.setp(chart_ax.get_xticklabels(), rotation=25, ha='right')
    
    add_header(overlay_ax, 2, 6, "LAP TIME EVOLUTION", "2-YEAR PACE PROGRESSION",
               "Tracking every personal record from June 2024 to October 2026")
    
    add_footer_box(overlay_ax, "Key Takeaway: The Step-Function Drops",
                   "Lap times dropped in distinct plateaus: 2:16 baseline -> 2:09 braking\n-> 2:04 corner speed -> 1:59.62 PB with setup discipline.")

    outpath = os.path.join(CHART_DIR, "slide_02_lap_time_trend.png")
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    return outpath

# -------------------------------------------------------------
# SLIDE 3: RACING LINE COMPARISON (Red GT4 vs White Benchmark)
# -------------------------------------------------------------
def generate_slide_3():
    detailed = pd.read_csv('detailed_lap_analysis.csv')
    
    user_laps = detailed[detailed['Type'] == 'User'].dropna(subset=['Lap Time (s)'])
    best_user = user_laps.loc[user_laps['Lap Time (s)'].idxmin()]
    bic_laps = detailed[detailed['Type'] == 'Best_In_Class'].dropna(subset=['Lap Time (s)'])
    best_bic = bic_laps.loc[bic_laps['Lap Time (s)'].idxmin()]

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
    bic_df = extract_lap_data(best_bic['File'], 'Best in Class Recording', best_bic['Lap'])

    fig, overlay_ax = create_slide_canvas()
    
    map_ax = fig.add_axes([0.10, 0.245, 0.82, 0.57])
    map_ax.set_facecolor(COLOR_CARD)
    
    # Benchmark in clean White dashed
    if bic_df is not None and 'longitude' in bic_df.columns:
        map_ax.plot(bic_df['longitude'], bic_df['latitude'],
                    label=f"Benchmark: 1:56.86 (Reference)", color=COLOR_WHITE, linewidth=1.8,
                    linestyle='--', alpha=0.80, zorder=2)
    # GT4 Personal Best in Porsche Guards Red
    if user_df is not None and 'longitude' in user_df.columns:
        map_ax.plot(user_df['longitude'], user_df['latitude'],
                    label=f"Personal Best: 1:59.60 (GT4)", color=COLOR_RED, linewidth=2.8, zorder=3)
        
    map_ax.set_title("High Plains Raceway (Full Course: 2.55 Miles, 15 Turns)",
                     fontsize=10.5, color=COLOR_WHITE, pad=10, fontweight='bold')
    leg = map_ax.legend(frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER,
                        fontsize=9.0, loc='upper right')
    style_legend(leg)
    map_ax.grid(True, alpha=0.15, linestyle=':', color=COLOR_BORDER)
    map_ax.axis('equal')
    map_ax.tick_params(colors=COLOR_SILVER, labelsize=8)

    add_header(overlay_ax, 3, 6, "RACING LINE COMPARISON", "GEOMETRY & TRACK POSITION",
               "Comparing 1:59.62 PB against the 1:56.86 track benchmark")

    add_footer_box(overlay_ax, "Key Geometry Finding: Turn 3 Carousel",
                   "Wider entry into Turn 3 Carousel carried +4.8 mph apex speed.\nExit line now matches the benchmark trajectory onto the back straight.")

    outpath = os.path.join(CHART_DIR, "slide_03_racing_line.png")
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    return outpath

# -------------------------------------------------------------
# SLIDE 4: CHASSIS DYNAMICS (White Lateral Grip + Red Braking G)
# -------------------------------------------------------------
def generate_slide_4(df):
    fig, overlay_ax = create_slide_canvas()
    
    chart_ax = fig.add_axes([0.12, 0.245, 0.80, 0.57])
    chart_ax.set_facecolor(COLOR_CARD)
    
    df_lat = df.dropna(subset=['Max Lateral G']).copy()
    df_brake = df.dropna(subset=['Max Braking G']).copy()
    
    # Lateral Grip in Racing White
    chart_ax.plot(df_lat['Date'], df_lat['Max Lateral G'], marker='o', markersize=5,
                  linestyle='-', color=COLOR_WHITE, linewidth=2.0, label='Peak Lateral Grip (Cornering G)')
    
    # Braking Deceleration in Guards Red
    if not df_brake.empty:
        chart_ax.plot(df_brake['Date'], df_brake['Max Braking G'].abs(), marker='s', markersize=5,
                      linestyle='--', color=COLOR_RED, linewidth=1.8, label='Threshold Braking Deceleration (|G|)')

    chart_ax.set_ylabel('Acceleration Magnitude (G)', fontsize=10.5, color=COLOR_WHITE, fontweight='bold')
    chart_ax.tick_params(colors=COLOR_SILVER, labelsize=8.5)
    chart_ax.grid(True, alpha=0.15, linestyle=':', color=COLOR_BORDER)
    leg = chart_ax.legend(frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER,
                          fontsize=9.0, loc='upper left')
    style_legend(leg)
    plt.setp(chart_ax.get_xticklabels(), rotation=25, ha='right')

    add_header(overlay_ax, 4, 6, "CHASSIS DYNAMICS", "LATERAL GRIP & BRAKING G",
               "Evolution of cornering grip and threshold braking deceleration")

    add_footer_box(overlay_ax, "Setup Insight: Target 30.5 PSI Hot",
                   "Grip climbed from 1.10G to 1.35G sustained (1.54G peak in Turn 3).\nBleeding pressures between sessions prevented mid-corner push.")

    outpath = os.path.join(CHART_DIR, "slide_04_chassis_dynamics.png")
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    return outpath

# -------------------------------------------------------------
# SLIDE 5: THROTTLE COMMITMENT (Guards Red WOT Curve)
# -------------------------------------------------------------
def generate_slide_5(df):
    fig, overlay_ax = create_slide_canvas()
    
    chart_ax = fig.add_axes([0.12, 0.245, 0.80, 0.57])
    chart_ax.set_facecolor(COLOR_CARD)
    
    df_wot = df.dropna(subset=['WOT %']).copy()
    
    # Throttle Aggression in Porsche Guards Red
    chart_ax.plot(df_wot['Date'], df_wot['WOT %'], marker='o', markersize=5,
                  linestyle='-', color=COLOR_RED, linewidth=2.0, label='Wide Open Throttle (% of Lap)')

    chart_ax.set_ylabel('Wide Open Throttle Time (%)', fontsize=10.5, color=COLOR_WHITE, fontweight='bold')
    chart_ax.tick_params(colors=COLOR_SILVER, labelsize=8.5)
    chart_ax.grid(True, alpha=0.15, linestyle=':', color=COLOR_BORDER)
    leg = chart_ax.legend(frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER,
                          fontsize=9.0, loc='upper left')
    style_legend(leg)
    plt.setp(chart_ax.get_xticklabels(), rotation=25, ha='right')

    add_header(overlay_ax, 5, 6, "DRIVER COMMITMENT", "THROTTLE AGGRESSION & WOT %",
               "Percentage of lap spent at 100% wide open throttle")

    add_footer_box(overlay_ax, "Coaching Takeaway: Earlier Throttle Pickup",
                   "WOT commitment surged from 2.2% in rookie sessions to 36.6% in 2026.\nEarlier throttle pickup off apex was the single biggest time saver.")

    outpath = os.path.join(CHART_DIR, "slide_05_wot_progression.png")
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    return outpath

# -------------------------------------------------------------
# SLIDE 6: ENGINEERING DEBRIEF & SETUP SUMMARY CARD
# -------------------------------------------------------------
def generate_slide_6(df):
    fig, overlay_ax = create_slide_canvas()

    add_header(overlay_ax, 6, 6, "SUMMARY & SETUP", "THE 3 KEY LESSONS",
               "What actually dropped 17.2 seconds at High Plains Raceway")

    # 3 Engineering Takeaway Cards with Porsche Motorsport Red/White accents
    cards = [
        ("1. TIRE PRESSURE DISCIPLINE (HOT: 30.5 PSI)",
         "Starting cold at 24 PSI and bleeding immediately after Session 1\n"
         "kept tires in the optimal grip window across all 20-minute sessions,\n"
         "completely eliminating greasy mid-corner push.",
         COLOR_RED),
        ("2. TRAIL BRAKING ROTATES THE PLATFORM",
         "Rather than releasing the brake before turn-in, trailing off to 15%\n"
         "pressure down to apex loaded the front tires and cured the 718 GT4's\n"
         "natural high-speed entry understeer.",
         COLOR_WHITE),
        ("3. EXIT VELOCITY DWARFS TOP-END HORSEPOWER",
         "Top speed on the back straight climbed from 114 to 134.8 mph purely\n"
         "from carrying speed through Turn 3 and committing to flat throttle\n"
         "40 feet earlier.",
         COLOR_RED),
    ]
    
    y_starts = [0.66, 0.45, 0.24]
    for (title, text, accent), y in zip(cards, y_starts):
        box = patches.FancyBboxPatch((0.06, y), 0.88, 0.175, boxstyle="round,pad=0.015,rounding_size=0.02",
                                     facecolor=COLOR_CARD, edgecolor=accent, linewidth=1.5,
                                     transform=overlay_ax.transAxes)
        overlay_ax.add_patch(box)
        overlay_ax.text(0.09, y + 0.130, title, transform=overlay_ax.transAxes,
                        fontsize=11.5, fontweight='bold', color=accent)
        overlay_ax.text(0.09, y + 0.090, text, transform=overlay_ax.transAxes,
                        fontsize=10.0, color='#e5e7eb', va='top', linespacing=1.35)

    # Final Engagement Prompt in Footer
    rect = patches.FancyBboxPatch((0.06, 0.05), 0.88, 0.135, boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor='#16171d', edgecolor=COLOR_BORDER, linewidth=1.2,
                                  transform=overlay_ax.transAxes)
    overlay_ax.add_patch(rect)
    
    overlay_ax.text(0.50, 0.125, "[ DISCUSSION QUESTION ]", transform=overlay_ax.transAxes,
                    fontsize=11.5, fontweight='bold', color=COLOR_RED, ha='center')
    overlay_ax.text(0.50, 0.080, "What data metric unlocked the biggest chunk of time at your home track?\nDrop your thoughts and setup notes below!",
                    transform=overlay_ax.transAxes, fontsize=10.5, color=COLOR_WHITE, ha='center', linespacing=1.25)

    outpath = os.path.join(CHART_DIR, "slide_06_setup_takeaways.png")
    plt.savefig(outpath, facecolor=COLOR_BG)
    plt.close()
    return outpath

def main():
    print("[CAROUSEL] Loading multi-year telemetry data...")
    df = load_data()
    print(f"[CAROUSEL] Found {len(df)} sessions.")
    
    slides = []
    print("[CAROUSEL] Generating Slide 1: Hero Cover Card (Porsche Motorsport Livery)...")
    slides.append(generate_slide_1(df))
    
    print("[CAROUSEL] Generating Slide 2: Lap Time Progression...")
    slides.append(generate_slide_2(df))
    
    print("[CAROUSEL] Generating Slide 3: Racing Line Comparison...")
    slides.append(generate_slide_3())
    
    print("[CAROUSEL] Generating Slide 4: Chassis Dynamics...")
    slides.append(generate_slide_4(df))
    
    print("[CAROUSEL] Generating Slide 5: WOT Throttle Commitment...")
    slides.append(generate_slide_5(df))
    
    print("[CAROUSEL] Generating Slide 6: Engineering Summary & Setup...")
    slides.append(generate_slide_6(df))
    
    print("\n[SUCCESS] Generated all 6 Porsche Motorsport carousel slides:")
    for s in slides:
        print(f"  - {s}")
        
    # Copy to THOR if accessible
    try:
        import shutil
        if os.path.exists(r"\\THOR\plex\Cayman Videos\Social Exports"):
            os.makedirs(THOR_DIR, exist_ok=True)
            for s in slides:
                dest = os.path.join(THOR_DIR, os.path.basename(s))
                shutil.copy2(s, dest)
            print(f"[SUCCESS] Mirrored all carousel slides to THOR: {THOR_DIR}")
    except Exception as e:
        print(f"[WARNING] Could not mirror to THOR: {e}")

if __name__ == '__main__':
    main()
