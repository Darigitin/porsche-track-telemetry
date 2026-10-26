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

if __name__ == "__main__":
    os.makedirs("charts", exist_ok=True)
    render_maintenance_card()
    render_diy_garage_card()
    render_hpr_guide_carousel()
