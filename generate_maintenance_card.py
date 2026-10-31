#!/usr/bin/env python3
"""
End-of-Season Maintenance & Chassis Checklist Card Generator.
Renders a 4:5 vertical (1080x1350) graphic in Porsche Motorsport livery.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Official Porsche Motorsport Livery Palette
COLOR_BG = '#090a0d'               # Deep Carbon Asphalt Black
COLOR_CARD = '#131419'             # Technical Graphite Panel
COLOR_BORDER = '#252733'           # Platinum Silver Divider
COLOR_RED = '#e4002b'              # Porsche Motorsport Guards Red
COLOR_WHITE = '#ffffff'            # Pure Racing White
COLOR_SILVER = '#9ca3af'           # Platinum Metallic Grey
COLOR_MUTED = '#6b7280'            # Technical Dark Grey
COLOR_RED_TINT = '#240d12'         # Subtle Red Card Accent
COLOR_GOLD = '#f59e0b'             # Technical Amber

def render_maintenance_card():
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis('off')

    # Top Header
    ax.text(0.07, 0.960, "WINTER SERVICE // BUILD LOG",
            transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_RED)
    ax.text(0.93, 0.960, "GARAGE LOG // GT4",
            transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_SILVER, ha='right')

    ax.text(0.07, 0.905, "END-OF-SEASON CHASSIS DEBRIEF",
            transform=ax.transAxes, fontsize=16.5, fontweight='bold', color=COLOR_WHITE)
    ax.text(0.07, 0.875, "2023 Porsche 718 Cayman GT4 | Post-PB Inspection & Winter Refresh",
            transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)

    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    # 4 Service Sections
    sections = [
        {
            "num": "01",
            "title": "BRAKE SYSTEM OVERHAUL",
            "items": [
                "• Fluid Flush: Castrol React SRF Racing Brake Fluid (wet boil 518°F)",
                "• Friction Replacement: Pagid 4925-RSL29 pads across all 4 corners",
                "• Hardware Check: GiroDisc 380mm floating rotors & Spiegler lines",
                "• Caliper Inspection: Inspect OEM ceramic pucks for thermal chipping"
            ],
            "accent": COLOR_RED
        },
        {
            "num": "02",
            "title": "THERMAL UPGRADE EVALUATION",
            "items": [
                "• Heat Mitigation: Girodisc 1mm Titanium Pad Heat Shields (TS-1741-4)",
                "• Piston Protection: Grade 5 Titanium replacement pucks (AutoQuest / DSM)",
                "• Prevents thermal transfer into calipers & fluid boil during 10-lap runs"
            ],
            "accent": COLOR_GOLD
        },
        {
            "num": "03",
            "title": "POWERTRAIN & DRIVELINE FLUIDS",
            "items": [
                "• Engine Service: Full synthetic Porsche A40 engine oil & OEM filter",
                "• Transaxle Check: 6-speed manual gearbox fluid inspection",
                "• Cooling: Front radiator & center heat exchanger debris cleaning"
            ],
            "accent": COLOR_SILVER
        },
        {
            "num": "04",
            "title": "SUSPENSION & MONOBALL GEOMETRY",
            "items": [
                "• Spherical Spheres: Inspect Tarett monoballs & drop links for zero play",
                "• Alignment Benchmark: Verify front/rear camber, caster & rear toe locking plates",
                "• Corner Balance: Confirm cross-weight balance with zero sway bar preload"
            ],
            "accent": COLOR_WHITE
        }
    ]

    y_pos = 0.825
    box_height = 0.170
    gap = 0.022

    for s in sections:
        rect = patches.FancyBboxPatch(
            (0.07, y_pos - box_height), 0.86, box_height,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor=COLOR_CARD, edgecolor=COLOR_BORDER,
            linewidth=1.2, transform=ax.transAxes
        )
        ax.add_patch(rect)

        # Left accent stripe
        ax.plot([0.07, 0.07], [y_pos - box_height, y_pos], color=s["accent"], linewidth=4.0, transform=ax.transAxes)

        # Section Header
        ax.text(0.10, y_pos - 0.032, f"[{s['num']}]  {s['title']}",
                transform=ax.transAxes, fontsize=11.5, fontweight='bold', color=s["accent"])

        # Items
        item_y = y_pos - 0.062
        for it in s["items"]:
            ax.text(0.10, item_y, it, transform=ax.transAxes, fontsize=9.2, color=COLOR_WHITE)
            item_y -= 0.026

        y_pos -= (box_height + gap)

    # Footer
    ax.plot([0.07, 0.93], [0.055, 0.055], color=COLOR_BORDER, linewidth=1.0, transform=ax.transAxes)
    ax.text(0.07, 0.030, "ENGINEERING SPEC // 718 GT4 TRACK TELEMETRY",
            transform=ax.transAxes, fontsize=9.0, fontweight='bold', color=COLOR_MUTED)
    ax.text(0.93, 0.030, "DENVER, CO",
            transform=ax.transAxes, fontsize=9.0, fontweight='bold', color=COLOR_MUTED, ha='right')

    out_local = "charts/end_of_season_maintenance_card.png"
    plt.savefig(out_local, dpi=150, facecolor=COLOR_BG)
    plt.close()
    print(f"Generated maintenance card: {out_local}")

    # Also copy to THOR
    thor_dir = r"\\THOR\plex\Cayman Videos\Social Exports"
    if os.path.exists(thor_dir):
        import shutil
        shutil.copy(out_local, os.path.join(thor_dir, "end_of_season_maintenance_card.png"))
        print(f"Copied to THOR: {os.path.join(thor_dir, 'end_of_season_maintenance_card.png')}")

def render_diy_garage_card():
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis('off')

    ax.text(0.07, 0.960, "IN-HOUSE TRACK PREP // TOOLING SPEC",
            transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_RED)
    ax.text(0.93, 0.960, "GARAGE OPS // GT4",
            transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_SILVER, ha='right')

    ax.text(0.07, 0.905, "DIY TRACK GARAGE & PUCK CHECKLIST",
            transform=ax.transAxes, fontsize=16.5, fontweight='bold', color=COLOR_WHITE)
    ax.text(0.07, 0.875, "2023 Porsche 718 Cayman GT4 | Sub-$215 Specialty Track Tooling Kit",
            transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)

    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    sections = [
        {
            "num": "01",
            "title": "LIFTING & WHEEL SWAP PROTECTION",
            "items": [
                "• Porsche Twist-Lock Jacking Pucks (Set of 4): Protects oval side skirt slots",
                "• M14 x 1.5 Stainless Wheel Hanger Pins (Pair): Shields 380mm GiroDisc rotors",
                "• 19mm Thin-Wall Non-Marring Socket: Polymer sleeve for Apex VS-5RE barrels",
                "• Existing Base: Daytona 3-Ton Low-Profile Jack, Stands & 1/2\" Torque Wrench"
            ],
            "accent": COLOR_RED
        },
        {
            "num": "02",
            "title": "CALIPER PUCK & PAD SERVICE TOOLING",
            "items": [
                "• 360° Ratcheting Quad/6-Piston Spreader: Retracts pistons evenly without prying",
                "• Critical: Prevents chipping fragile OEM Brembo ceramic piston pucks",
                "• Vinyl-Coated Caliper S-Hooks: Supports calipers on Tarett upright studs",
                "• Protects Spiegler braided stainless lines during Pagid RSL29 swaps"
            ],
            "accent": COLOR_GOLD
        },
        {
            "num": "03",
            "title": "1-PERSON CASTROL SRF PRESSURE BLEEDING",
            "items": [
                "• Motive 0100 European Power Bleeder: 45mm threaded master cylinder cap",
                "• Silicone Catch Bottle & 11mm Flare Nut Wrench for inner/outer bleed nipples",
                "• Maintains rock-hard pedal modulation across 5,000+ ft altitude track days"
            ],
            "accent": COLOR_SILVER
        },
        {
            "num": "04",
            "title": "THERMAL BARRIER & PUCK UPGRADE PATH",
            "items": [
                "• Girodisc 1mm Titanium Pad Heat Shields (TS-1741-4 Front / TS-1740-4 Rear)",
                "• AutoQuest / Demon Speed Grade 5 Titanium Replacement Piston Pucks",
                "• Eliminates $2k+ boutique caliper rebuilds while protecting dust boots & fluid"
            ],
            "accent": COLOR_WHITE
        }
    ]

    y_pos = 0.825
    box_height = 0.170
    gap = 0.022

    for s in sections:
        rect = patches.FancyBboxPatch(
            (0.07, y_pos - box_height), 0.86, box_height,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor=COLOR_CARD, edgecolor=COLOR_BORDER,
            linewidth=1.2, transform=ax.transAxes
        )
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_pos - box_height, y_pos], color=s["accent"], linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_pos - 0.032, f"[{s['num']}]  {s['title']}",
                transform=ax.transAxes, fontsize=11.5, fontweight='bold', color=s["accent"])
        item_y = y_pos - 0.062
        for it in s["items"]:
            ax.text(0.10, item_y, it, transform=ax.transAxes, fontsize=9.0, color=COLOR_WHITE)
            item_y -= 0.026
        y_pos -= (box_height + gap)

    ax.plot([0.07, 0.93], [0.055, 0.055], color=COLOR_BORDER, linewidth=1.0, transform=ax.transAxes)
    ax.text(0.07, 0.030, "DIY TRACK OPERATIONS // 718 CAYMAN GT4",
            transform=ax.transAxes, fontsize=9.0, fontweight='bold', color=COLOR_MUTED)
    ax.text(0.93, 0.030, "HIGH PLAINS RACEWAY",
            transform=ax.transAxes, fontsize=9.0, fontweight='bold', color=COLOR_MUTED, ha='right')

    out_local = "charts/diy_track_garage_card.png"
    plt.savefig(out_local, dpi=150, facecolor=COLOR_BG)
    plt.close()
    print(f"Generated DIY garage card: {out_local}")

    thor_dir = r"\\THOR\plex\Cayman Videos\Social Exports"
    if os.path.exists(thor_dir):
        import shutil
        shutil.copy(out_local, os.path.join(thor_dir, "diy_track_garage_card.png"))

def render_hpr_guide_carousel():
    import matplotlib.image as mpimg
    out_dir = os.path.join("charts", "carousel_hpr_guide")
    os.makedirs(out_dir, exist_ok=True)

    # Slide 1: Cover Card
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis('off')

    ax.text(0.07, 0.955, "SLIDE 01 / 04", transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_RED)
    ax.text(0.93, 0.955, "TRACK ENGINEERING GUIDE", transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_SILVER, ha='right')
    ax.text(0.07, 0.895, "HIGH PLAINS RACEWAY", transform=ax.transAxes, fontsize=22, fontweight='bold', color=COLOR_WHITE)
    ax.text(0.07, 0.858, "2.55 Miles | 15 Turns | 300+ Ft Elevation & Blind Compression Guide", transform=ax.transAxes, fontsize=10.8, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.835, 0.835], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    metrics = [
        ("1:59.67", "ALL-TIME PERSONAL BEST", "2023 Porsche 718 Cayman GT4 (6MT) | -17.11s 2-Year Drop", COLOR_RED),
        ("134.8 MPH", "BACK STRAIGHT TERMINAL VELOCITY", "2,838-Foot Straight | 36.6% Lap-Wide WOT Commitment", COLOR_GOLD),
        ("1.54G PEAK", "PRAIRIE CORKSCREW LATERAL LOAD", "Turns 13–15 Downhill Compression | 30.5/31.0 PSI Hot Vitour P1", COLOR_WHITE),
        ("-1.27G", "PEAK THRESHOLD DECELERATION", "GiroDisc 380mm Rotors + Pagid RSL29 + Tarett Rear Toe Locking Kit", COLOR_SILVER),
    ]
    y_p = 0.795
    for val, lbl, sub, col in metrics:
        rect = patches.FancyBboxPatch((0.07, y_p - 0.135), 0.86, 0.135, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_p - 0.135, y_p], color=col, linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_p - 0.048, val, transform=ax.transAxes, fontsize=20, fontweight='bold', color=col)
        ax.text(0.10, y_p - 0.082, lbl, transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_WHITE)
        ax.text(0.10, y_p - 0.112, sub, transform=ax.transAxes, fontsize=9.0, color=COLOR_SILVER)
        y_p -= 0.160

    ax.text(0.50, 0.065, "SWIPE FOR SECTOR MAP & ELEVATION PROFILE ➔", transform=ax.transAxes,
            fontsize=10.5, fontweight='bold', color=COLOR_RED, ha='center')
    plt.savefig(os.path.join(out_dir, "slide_01_hpr_cover.png"), dpi=150, facecolor=COLOR_BG)
    plt.close()

    # Slide 2 & 3: Embed existing Sector Map & Elevation Profile into 4:5 Livery Frames
    embedded_slides = [
        ("slide_02_sector_map.png", "SLIDE 02 / 04", "SECTOR & CORNER SPEED BREAKDOWN",
         "15 Turns | Color-Coded Braking, Apex & WOT Zones", "charts/hpr_sector_map.png",
         "KEY TAKEAWAY: Turn 3 Carousel exit dictates terminal velocity all the way to Turn 4 (134.8 MPH)."),
        ("slide_03_elevation_profile.png", "SLIDE 03 / 04", "300+ FT ELEVATION & COMPRESSION PROFILE",
         "Managing Vertical Load Across Blind Crests & Compressions", "charts/hpr_elevation_profile.png",
         "KEY TAKEAWAY: Turn 5 (Niagara), Turn 7 Crest & Turn 13 Corkscrew require trail-braking before the crest unloads the nose.")
    ]
    for fname, s_tag, title, sub, img_path, footer_note in embedded_slides:
        fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
        fig.patch.set_facecolor(COLOR_BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(COLOR_BG)
        ax.axis('off')

        ax.text(0.07, 0.955, s_tag, transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_RED)
        ax.text(0.93, 0.955, "HPR TELEMETRY GUIDE", transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_SILVER, ha='right')
        ax.text(0.07, 0.905, title, transform=ax.transAxes, fontsize=16.5, fontweight='bold', color=COLOR_WHITE)
        ax.text(0.07, 0.875, sub, transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)
        ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

        if os.path.exists(img_path):
            img = mpimg.imread(img_path)
            img_ax = fig.add_axes([0.05, 0.20, 0.90, 0.62])
            img_ax.imshow(img)
            img_ax.axis('off')

        rect = patches.FancyBboxPatch((0.07, 0.055), 0.86, 0.110, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [0.055, 0.165], color=COLOR_RED, linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, 0.110, footer_note, transform=ax.transAxes, fontsize=9.2, fontweight='bold', color=COLOR_WHITE, wrap=True)
        plt.savefig(os.path.join(out_dir, fname), dpi=150, facecolor=COLOR_BG)
        plt.close()

    # Slide 4: 3 Signature Complexes Breakdown
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis('off')

    ax.text(0.07, 0.955, "SLIDE 04 / 04", transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_RED)
    ax.text(0.93, 0.955, "CORNER COMPLEX DEBRIEF", transform=ax.transAxes, fontsize=10.5, fontweight='bold', color=COLOR_SILVER, ha='right')
    ax.text(0.07, 0.905, "3 SIGNATURE HPR CORNER COMPLEXES", transform=ax.transAxes, fontsize=16.5, fontweight='bold', color=COLOR_WHITE)
    ax.text(0.07, 0.875, "Where Lap Time Is Won or Lost in a Mid-Engine Platform", transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    complexes = [
        ("T4–T5", "BIKER'S BERM TO NIAGARA PLUNGE", [
            "• Threshold Spike: -1.25G braking from 134.8 MPH with immediate downshift to 3rd gear",
            "• Apex RPM: 5,411 RPM in 3rd (vs 4,477 RPM in 4th) unlocks +0.31G uphill pull",
            "• Trail-Braking: Hold 15% brake pressure to apex curb to cure front push (+0.300s saved)"
        ], COLOR_RED),
        ("T6–T7", "DANNY'S LESSON TO HIGH PLAINS DRIFTER CREST", [
            "• Compression Bottom: Late apex at bottom of bowl (T6) to square up the uphill climb",
            "• Blind Crest (T7): Unwind steering lock BEFORE cresting as vertical load drops to 0.4G",
            "• Tarett Rear Toe Locking Kit keeps rear track dead-straight over the crest transition"
        ], COLOR_GOLD),
        ("T13–T15", "THE PRAIRIE CORKSCREW", [
            "• Entry Commitment: Turn in off the hilltop (T11/12) into the downhill compression",
            "• Peak Load: Sustained 1.35G / 1.54G peak lateral grip at 81 MPH through the dip",
            "• Tire Window: 30.5F / 31.0R PSI hot keeps the 265/295 Vitour P1 contact patch flat"
        ], COLOR_WHITE)
    ]
    y_c = 0.820
    for code, cname, bullets, col in complexes:
        rect = patches.FancyBboxPatch((0.07, y_c - 0.215), 0.86, 0.215, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_c - 0.215, y_c], color=col, linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_c - 0.038, f"[{code}]  {cname}", transform=ax.transAxes, fontsize=11.5, fontweight='bold', color=col)
        by = y_c - 0.078
        for b in bullets:
            ax.text(0.10, by, b, transform=ax.transAxes, fontsize=9.0, color=COLOR_WHITE)
            by -= 0.042
        y_c -= 0.245

    ax.text(0.50, 0.045, "SAVE THIS GUIDE FOR YOUR NEXT HPR TRACK DAY ★", transform=ax.transAxes,
            fontsize=10.5, fontweight='bold', color=COLOR_RED, ha='center')
    plt.savefig(os.path.join(out_dir, "slide_04_complex_breakdown.png"), dpi=150, facecolor=COLOR_BG)
    plt.close()

    caption_text = (
        "Engineering & elevation guide to High Plains Raceway (Full Course — 2.55 miles, 15 turns) in the 718 Cayman GT4 🏁📐\n\n"
        "What makes HPR such a technical driver's track is the 300+ feet of elevation change—nearly every major braking and turn-in zone happens over a blind crest or into a heavy compression bowl.\n\n"
        "Swipe through for the sector speed map, vertical elevation profile, and the 3 complexes where lap time is won or lost:\n\n"
        "1️⃣ Turns 4–5 (Biker's Berm to Niagara Plunge): Braking at -1.25G from 134.8 MPH, downshifting immediately to 3rd gear (5,411 apex RPM), and trailing 15% brake pressure to the curb saves 0.300s pulling up the hill.\n"
        "2️⃣ Turns 6–7 (Danny's Lesson to High Plains Drifter): Using the compression at the bottom of the bowl to rotate, then unwinding the wheel *before* cresting T7 as the chassis goes light.\n"
        "3️⃣ Turns 13–15 (The Prairie Corkscrew): Leaning on the downhill compression at 81 MPH to pull 1.54G peak lateral load on 30.5/31.0 PSI hot Vitour Tempesta P1s.\n\n"
        "Save this for your next HPR weekend 📌 What's your favorite corner complex at High Plains?\n\n"
        "#Porsche #718GT4 #CaymanGT4 #HighPlainsRaceway #TrackGuide #TrackTelemetry #MotorsportEngineering #DataDriven #HPDE #TrackDay #PCA"
    )
    with open(os.path.join(out_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption_text)
    print(f"Generated 4-slide HPR Engineering Guide Carousel in: {out_dir}")

def render_phase4_assets():
    import numpy as np
    import pandas as pd
    import matplotlib.image as mpimg

    # 1. Load real CAN telemetry traces for PB vs Instructor Reference
    def get_fastest_lap(csv_path):
        df = pd.read_csv(csv_path, low_memory=False)
        lt = pd.to_numeric(df["laptime"], errors="coerce").fillna(0).values
        resets = np.where(np.diff(lt) < -5000)[0] + 1
        lap_ids = np.zeros(len(df), dtype=int)
        for i, r in enumerate(resets):
            lap_ids[r:] = i + 1
        df["lap_id"] = lap_ids
        best_dur, best_g = 999.0, None
        for lid, grp in df.groupby("lap_id"):
            dur_s = grp["laptime"].max() / 1000.0
            if 110.0 < dur_s < 130.0 and len(grp) > 1000 and dur_s < best_dur:
                g = grp.copy()
                g["dist_m"] = g["distanceCounter"] - g["distanceCounter"].iloc[0]
                g["time_s"] = (g["laptime"] - g["laptime"].iloc[0]) / 1000.0
                g["speed_mph"] = g["speed"] * 2.236936 if g["speed"].max() < 100 else g["speed"] * 0.621371
                best_dur, best_g = dur_s, g
        return best_g

    ref_df = get_fastest_lap("Best in Class Recording/recording-2026-09-20-08-36-34.csv")
    pb_df = get_fastest_lap("Recording CSVs/recording-2026-10-10-10-57-43.csv")

    grid_d = np.linspace(0, 4050, 800)
    ref_spd = np.interp(grid_d, ref_df["dist_m"], ref_df["speed_mph"])
    pb_spd = np.interp(grid_d, pb_df["dist_m"], pb_df["speed_mph"])
    ref_brk = np.interp(grid_d, ref_df["dist_m"], ref_df["brakingPressure"])
    pb_brk = np.interp(grid_d, pb_df["dist_m"], pb_df["brakingPressure"])
    ref_t = np.interp(grid_d, ref_df["dist_m"], ref_df["time_s"])
    pb_t = np.interp(grid_d, pb_df["dist_m"], pb_df["time_s"])
    delta_t = pb_t - ref_t

    # Render 3-Panel Telemetry Overlay Chart (for Reddit & Carousel Slide 2)
    fig, axes = plt.subplots(3, 1, figsize=(11.0, 7.5), dpi=150, sharex=True)
    fig.patch.set_facecolor(COLOR_BG)
    for ax in axes:
        ax.set_facecolor(COLOR_CARD)
        for sp in ax.spines.values():
            sp.set_color(COLOR_BORDER)
        ax.tick_params(colors=COLOR_SILVER, labelsize=8.5)
        ax.grid(True, color=COLOR_BORDER, linestyle="--", alpha=0.5)

    fig.suptitle("CAN TELEMETRY OVERLAY: 1:59.67 DRIVER PB vs 1:56.55 INSTRUCTOR BENCHMARK (718 GT4)",
                 color=COLOR_WHITE, fontsize=12.5, fontweight="bold", y=0.96)

    axes[0].plot(grid_d, ref_spd, color=COLOR_GOLD, linewidth=1.8, label="Instructor Benchmark (1:56.55)")
    axes[0].plot(grid_d, pb_spd, color=COLOR_RED, linewidth=1.8, label="Matthew PB (1:59.67)")
    axes[0].set_ylabel("Speed (MPH)", color=COLOR_WHITE, fontsize=9.5, fontweight="bold")
    axes[0].legend(loc="lower right", facecolor=COLOR_BG, edgecolor=COLOR_BORDER, labelcolor=COLOR_WHITE, fontsize=8.5)

    axes[1].plot(grid_d, ref_brk, color=COLOR_GOLD, linewidth=1.6, label="Instructor Brake (111.6 bar peak)")
    axes[1].plot(grid_d, pb_brk, color=COLOR_RED, linewidth=1.6, label="Matthew Brake (81.9 bar peak)")
    axes[1].set_ylabel("Brake (bar)", color=COLOR_WHITE, fontsize=9.5, fontweight="bold")
    axes[1].legend(loc="upper right", facecolor=COLOR_BG, edgecolor=COLOR_BORDER, labelcolor=COLOR_WHITE, fontsize=8.5)

    axes[2].plot(grid_d, delta_t, color=COLOR_WHITE, linewidth=2.0)
    axes[2].axhline(0, color=COLOR_SILVER, linestyle=":", linewidth=1.0)
    axes[2].axvspan(2650, 3350, color=COLOR_RED, alpha=0.18, label="Turns 8–10 S-Curves: PB Gained -0.26s")
    axes[2].set_ylabel("Delta-T (s)", color=COLOR_WHITE, fontsize=9.5, fontweight="bold")
    axes[2].set_xlabel("Track Distance (Meters) — High Plains Raceway (Full Course)", color=COLOR_SILVER, fontsize=9.5)
    axes[2].legend(loc="upper left", facecolor=COLOR_BG, edgecolor=COLOR_BORDER, labelcolor=COLOR_WHITE, fontsize=8.5)

    plt.tight_layout(rect=[0.01, 0.01, 0.99, 0.93])
    delta_chart_path = "charts/pb_vs_instructor_telemetry_delta.png"
    plt.savefig(delta_chart_path, dpi=150, facecolor=COLOR_BG)
    plt.close()
    print(f"Generated PB vs Instructor telemetry chart: {delta_chart_path}")

    # 2. Render Wednesday 4-Slide 4:5 Carousel: PB vs Instructor Delta Deck
    c_dir = os.path.join("charts", "carousel_pb_vs_instructor")
    os.makedirs(c_dir, exist_ok=True)

    # Slide 1: Cover
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis("off")

    ax.text(0.07, 0.955, "SLIDE 01 / 04", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_RED)
    ax.text(0.93, 0.955, "CAN TELEMETRY BENCHMARK", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_SILVER, ha="right")
    ax.text(0.07, 0.895, "1:59.67 PB vs 1:56.55 PRO", transform=ax.transAxes, fontsize=20.5, fontweight="bold", color=COLOR_WHITE)
    ax.text(0.07, 0.858, "Where the Final 3.12 Seconds Hide in 10Hz Porsche GT4 Telemetry", transform=ax.transAxes, fontsize=10.2, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.835, 0.835], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    s1_cards = [
        ("0.97G vs 0.96G", "IDENTICAL AVERAGE CORNERING GRIP", "Tarett Monoballs + 265/295 Vitour P1s Match Pro Mechanical Grip", COLOR_WHITE),
        ("-0.26s GAINED", "TURNS 8–10 TECHNICAL S-CURVES", "22.10s (PB) vs 22.36s (Pro) — Zero Bushing Deflection on Transitions", COLOR_RED),
        ("81.9 vs 111.6 BAR", "INITIAL THRESHOLD BRAKE ATTACK", "Pro Hits +36% Higher Initial Pedal Pressure at High Aero Drag", COLOR_GOLD),
        ("7.7% vs 4.1%", "PEDAL TRANSITION COASTING TIME", "Cutting 0% Throttle / 0% Brake Hesitation Saves 1.0+ Second", COLOR_SILVER),
    ]
    y_p = 0.795
    for val, lbl, sub, col in s1_cards:
        rect = patches.FancyBboxPatch((0.07, y_p - 0.135), 0.86, 0.135, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_p - 0.135, y_p], color=col, linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_p - 0.048, val, transform=ax.transAxes, fontsize=18.5, fontweight="bold", color=col)
        ax.text(0.10, y_p - 0.082, lbl, transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_WHITE)
        ax.text(0.10, y_p - 0.112, sub, transform=ax.transAxes, fontsize=8.8, color=COLOR_SILVER)
        y_p -= 0.160

    ax.text(0.50, 0.065, "SWIPE FOR SPEED, BRAKE & DELTA-T TRACES ➔", transform=ax.transAxes,
            fontsize=10.5, fontweight="bold", color=COLOR_RED, ha="center")
    plt.savefig(os.path.join(c_dir, "slide_01_benchmark_cover.png"), dpi=150, facecolor=COLOR_BG)
    plt.close()

    # Slide 2: Embedded Telemetry Chart
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis("off")

    ax.text(0.07, 0.955, "SLIDE 02 / 04", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_RED)
    ax.text(0.93, 0.955, "10HZ TRACE OVERLAY", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_SILVER, ha="right")
    ax.text(0.07, 0.905, "SPEED, BRAKE PRESSURE & DELTA-T", transform=ax.transAxes, fontsize=16.5, fontweight="bold", color=COLOR_WHITE)
    ax.text(0.07, 0.875, "4,050m Lap Overlay | Red: 1:59.67 PB | Gold: 1:56.55 Reference", transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    img = mpimg.imread(delta_chart_path)
    img_ax = fig.add_axes([0.04, 0.20, 0.92, 0.62])
    img_ax.imshow(img)
    img_ax.axis("off")

    rect = patches.FancyBboxPatch((0.07, 0.055), 0.86, 0.110, boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
    ax.add_patch(rect)
    ax.plot([0.07, 0.07], [0.055, 0.165], color=COLOR_RED, linewidth=4.0, transform=ax.transAxes)
    ax.text(0.10, 0.110, "KEY INSIGHT: Notice the Delta-T slope flatten and dip downward in Turns 8–10 (-0.26s)!",
            transform=ax.transAxes, fontsize=9.2, fontweight="bold", color=COLOR_WHITE)
    plt.savefig(os.path.join(c_dir, "slide_02_telemetry_overlay.png"), dpi=150, facecolor=COLOR_BG)
    plt.close()

    # Slide 3: Corner-by-Corner Speed & Time Loss Breakdown
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis("off")

    ax.text(0.07, 0.955, "SLIDE 03 / 04", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_RED)
    ax.text(0.93, 0.955, "SECTOR BREAKDOWN", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_SILVER, ha="right")
    ax.text(0.07, 0.905, "WHERE THE 3.1 SECONDS ACTUALLY GO", transform=ax.transAxes, fontsize=16.5, fontweight="bold", color=COLOR_WHITE)
    ax.text(0.07, 0.875, "Corner-by-Corner Minimum Apex Speeds & Sector Time Deltas", transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    sectors = [
        ("T3 EXIT TO T4", "CAROUSEL EXIT ONTO BACK STRAIGHT (+0.60s LOST)", [
            "• Minimum Apex Speed: 50.6 MPH (PB) vs 56.5 MPH (Reference) -> -5.9 MPH at apex",
            "• Back Straight Terminal Speed: Carrying +5.9 MPH exit speed compounds across 2,838 ft",
            "• Fix: Open hands 15 ft earlier at T3B curb to get to 100% throttle sooner"
        ], COLOR_GOLD),
        ("T13 TO FINISH", "DOWNHILL PRAIRIE CORKSCREW (+0.56s LOST)", [
            "• Minimum Compression Speed: 59.6 MPH (PB) vs 66.1 MPH (Reference) -> -6.5 MPH",
            "• Over-slowing turn-in before the downhill dip leaves 0.56s on the run to the line",
            "• Fix: Trust the 1.54G compression bowl at turn-in and roll +6 MPH entry speed"
        ], COLOR_RED),
        ("TURNS 8 TO 10", "TECHNICAL BACK S-CURVES (-0.26s GAINED!)", [
            "• Sector Time: 22.10s (PB) vs 22.36s (Reference) | Peak Speed: 99.2 MPH",
            "• Full Tarett spherical bearings + 30.5/31.0 PSI hot Vitour P1s shine in transitions",
            "• Proves the chassis setup has 1:56 mechanical grip right now"
        ], COLOR_WHITE)
    ]
    y_c = 0.820
    for code, cname, bullets, col in sectors:
        rect = patches.FancyBboxPatch((0.07, y_c - 0.215), 0.86, 0.215, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_c - 0.215, y_c], color=col, linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_c - 0.038, f"[{code}]  {cname}", transform=ax.transAxes, fontsize=11.0, fontweight="bold", color=col)
        by = y_c - 0.078
        for b in bullets:
            ax.text(0.10, by, b, transform=ax.transAxes, fontsize=9.0, color=COLOR_WHITE)
            by -= 0.042
        y_c -= 0.245

    plt.savefig(os.path.join(c_dir, "slide_03_corner_deltas.png"), dpi=150, facecolor=COLOR_BG)
    plt.close()

    # Slide 4: 2027 Driver Homework
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis("off")

    ax.text(0.07, 0.955, "SLIDE 04 / 04", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_RED)
    ax.text(0.93, 0.955, "2027 DRIVER TARGETS", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_SILVER, ha="right")
    ax.text(0.07, 0.905, "THE 3-STEP PLAN TO CHASE 1:56", transform=ax.transAxes, fontsize=16.5, fontweight="bold", color=COLOR_WHITE)
    ax.text(0.07, 0.875, "Turning Telemetry Findings Into Actionable Track Adjustments", transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    hw = [
        ("01", "100+ BAR INITIAL THRESHOLD BRAKE ATTACK", [
            "• Hit peak pedal pressure immediately at the brake marker while aero drag is highest",
            "• Bleed brake pressure off linearly as downforce drops and steering angle increases",
            "• Moves Turn 1 and Turn 4 brake markers 15–20 feet deeper"
        ], COLOR_RED),
        ("02", "ELIMINATE THE 7.7% COASTING WINDOW", [
            "• Shrink 0%-throttle / 0%-brake dead time from 7.7% down toward the 4.1% pro benchmark",
            "• Transition directly from 10–15% trail-brake release into maintenance throttle at apex",
            "• Keeps chassis pitch stable and eliminates mid-corner front-end unload"
        ], COLOR_GOLD),
        ("03", "PRIORITIZE T3 & T15 EXIT VELOCITY", [
            "• Sacrifice 1–2 MPH on T3A entry to square up T3B and carry 56+ MPH onto the straight",
            "• Commit to a 65+ MPH minimum roll speed through the Turn 13–15 Corkscrew compression",
            "• Combined potential gain: -1.16s in just two corners"
        ], COLOR_WHITE)
    ]
    y_c = 0.820
    for code, cname, bullets, col in hw:
        rect = patches.FancyBboxPatch((0.07, y_c - 0.215), 0.86, 0.215, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_c - 0.215, y_c], color=col, linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_c - 0.038, f"[{code}]  {cname}", transform=ax.transAxes, fontsize=11.0, fontweight="bold", color=col)
        by = y_c - 0.078
        for b in bullets:
            ax.text(0.10, by, b, transform=ax.transAxes, fontsize=9.0, color=COLOR_WHITE)
            by -= 0.042
        y_c -= 0.245

    ax.text(0.50, 0.045, "SAVE THIS TELEMETRY BREAKDOWN ★", transform=ax.transAxes,
            fontsize=10.5, fontweight="bold", color=COLOR_RED, ha="center")
    plt.savefig(os.path.join(c_dir, "slide_04_driver_targets.png"), dpi=150, facecolor=COLOR_BG)
    plt.close()

    c_caption = (
        "Overlaying my 1:59.67 PB against my instructor's 1:56.55 reference lap in a 718 Cayman GT4: where the final 3.1 seconds actually hide 🏁📊\n\n"
        "Dropping 17 seconds from my 2:16 baseline down to a 1:59.67 was about fixing big technique habits and dialing in the chassis. Finding the next 3 seconds from 1:59 down to a 1:56 is a game of inches and pedal discipline.\n\n"
        "Swipe through the 10Hz CAN telemetry comparison for what surprised me most:\n\n"
        "1️⃣ Mechanical Grip Is Already There: Average cornering load (>0.5G) was nearly identical (0.97G vs 0.96G), and through the technical Turns 8–10 S-curves my GT4 actually pulled 0.26s back on the benchmark thanks to the Tarett monoball setup and 265/295 Vitour P1s.\n"
        "2️⃣ Initial Brake Attack (81.9 bar vs 111.6 bar): Hitting harder initial pedal pressure right at the brake zone while aero drag is highest lets the reference lap brake 15–20 ft deeper into T1 and T4.\n"
        "3️⃣ Two Key Corner Exits (+1.16s combined): Carrying +5.9 MPH out of Turn 3 onto the 2,838 ft back straight (+0.60s) and rolling +6.5 MPH through the downhill Corkscrew compression (+0.56s).\n"
        "4️⃣ Pedal Transition Coasting (7.7% vs 4.1%): Cutting out hesitation between brake release and throttle pickup.\n\n"
        "When you overlay your data against a faster driver or coach, where do you usually find the biggest time delta? 👇\n\n"
        "#Porsche #718GT4 #CaymanGT4 #HighPlainsRaceway #TrackTelemetry #DataAnalysis #MotorsportEngineering #TarettEngineering #VitourP1 #HPDE #TrackDay #PCA"
    )
    with open(os.path.join(c_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(c_caption)
    print(f"Generated 4-slide PB vs Instructor Carousel in: {c_dir}")

    # 3. Render Friday 4:5 Card: 2026 Season by the Numbers & 2027 Track Roadmap
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150)
    fig.patch.set_facecolor(COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLOR_BG)
    ax.axis("off")

    ax.text(0.07, 0.960, "SEASON FINALE // TELEMETRY LOGBOOK", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_RED)
    ax.text(0.93, 0.960, "2026 -> 2027 // GT4", transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=COLOR_SILVER, ha="right")
    ax.text(0.07, 0.905, "2026 SEASON WRAP & 2027 ROADMAP", transform=ax.transAxes, fontsize=16.5, fontweight="bold", color=COLOR_WHITE)
    ax.text(0.07, 0.875, "2023 Porsche 718 Cayman GT4 | 61 Sessions & 519 Timed CAN Telemetry Laps", transform=ax.transAxes, fontsize=10.0, color=COLOR_SILVER)
    ax.plot([0.07, 0.93], [0.855, 0.855], color=COLOR_RED, linewidth=2.5, transform=ax.transAxes)

    wrap_sections = [
        {
            "num": "01",
            "title": "PROGRESSION & TELEMETRY MILESTONES",
            "items": [
                "• Lap Time Drop: 2:16.78 Baseline (June 2024) -> 1:59.67 Official PB (-17.11s)",
                "• Volume Logged: 61 Track Sessions | 519 Timed Laps | 1,320+ Track Miles at HPR",
                "• Dynamic Envelope: 1.54G Peak Lateral Grip | -1.27G Braking | 134.8 MPH Top Speed",
                "• Tire Window: 30.5F / 31.0R PSI Hot on 19\" Apex VS-5RE + 265/295 Vitour P1s"
            ],
            "accent": COLOR_RED
        },
        {
            "num": "02",
            "title": "CHASSIS & BRAKE PACKAGE VALIDATION",
            "items": [
                "• Full Tarett Monoball Conversion: Zero bushing compliance & zero 265 liner rub",
                "• Tarett Rear Toe Links + Locking Plates: Cured high-speed braking toe deflection",
                "• GiroDisc 380mm 2-Piece Rotors + Pagid RSL29 + Castrol SRF: Zero fade at 5,000 ft",
                "• Matched 1:56.55 instructor mechanical grip (0.97G avg) & gained -0.26s in T8–T10"
            ],
            "accent": COLOR_GOLD
        },
        {
            "num": "03",
            "title": "WINTER OFF-SEASON SERVICE & DIY PREP",
            "items": [
                "• Honest Assembly Service: Fresh Pagid RSL29s, SRF flush & alignment sheet log",
                "• Caliper Thermal Check: Inspect OEM ceramic pucks & add Girodisc Ti heat shields",
                "• In-House Garage Kit: Motive 0100 bleeder, 360° pad spreader & wheel hanger pins"
            ],
            "accent": COLOR_SILVER
        },
        {
            "num": "04",
            "title": "2027 TRACK SEASON GOALS & ROADMAP",
            "items": [
                "• Dedicated Track Rig: Acquiring a trailer to retire I-70 highway commuter miles",
                "• New Circuits: Expanding beyond High Plains Raceway to out-of-state tracks",
                "• Data Target: 110+ bar initial brake attack & chasing the 1:56.55 HPR benchmark"
            ],
            "accent": COLOR_WHITE
        }
    ]

    y_pos = 0.825
    box_height = 0.170
    gap = 0.022
    for s in wrap_sections:
        rect = patches.FancyBboxPatch((0.07, y_pos - box_height), 0.86, box_height,
                                      boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, linewidth=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.plot([0.07, 0.07], [y_pos - box_height, y_pos], color=s["accent"], linewidth=4.0, transform=ax.transAxes)
        ax.text(0.10, y_pos - 0.032, f"[{s['num']}]  {s['title']}", transform=ax.transAxes, fontsize=11.5, fontweight="bold", color=s["accent"])
        item_y = y_pos - 0.062
        for it in s["items"]:
            ax.text(0.10, item_y, it, transform=ax.transAxes, fontsize=9.0, color=COLOR_WHITE)
            item_y -= 0.026
        y_pos -= (box_height + gap)

    ax.plot([0.07, 0.93], [0.055, 0.055], color=COLOR_BORDER, linewidth=1.0, transform=ax.transAxes)
    ax.text(0.07, 0.030, "MATTHEW GARRETT // @MGARRETTGT4", transform=ax.transAxes, fontsize=9.0, fontweight="bold", color=COLOR_MUTED)
    ax.text(0.93, 0.030, "HIGH PLAINS RACEWAY", transform=ax.transAxes, fontsize=9.0, fontweight="bold", color=COLOR_MUTED, ha="right")

    out_wrap = "charts/season_2026_wrapup_card.png"
    plt.savefig(out_wrap, dpi=150, facecolor=COLOR_BG)
    plt.close()
    print(f"Generated 2026 Season Wrap-Up Card: {out_wrap}")

if __name__ == "__main__":
    os.makedirs("charts", exist_ok=True)
    render_maintenance_card()
    render_diy_garage_card()
    render_hpr_guide_carousel()
    render_phase4_assets()
