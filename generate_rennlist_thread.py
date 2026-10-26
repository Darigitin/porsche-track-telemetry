#!/usr/bin/env python3
"""
Rennlist Thread Generator for Porsche Track Telemetry.
Generates comprehensive, publication-ready BBCode forum threads for:
1. '718 Cayman GTS 4.0 / GT4 / GT4 RS / Spyder' Forum
2. 'Racing & Track Day Drivers, DE / Time Trial' Forum
3. 'Porsche Data Acquisition & Video' Forum

Formats CAN-bus telemetry, PB benchmarks, tire pressures, and YouTube embeds into clean BBCode.
"""

import os
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def generate_rennlist_bbcode(
    vehicle_name="2023 Porsche 718 Cayman GT4",
    track_name="High Plains Raceway (Full Course - 2.55 Miles)",
    all_time_pb="1:59.67",
    baseline_time="2:16.78",
    total_laps=519,
    total_sessions=61,
    youtube_pb_id="PRz7gJhED00",
    instagram_handle="mgarrettgt4"
):
    bb = []
    bb.append(f"[B][SIZE=5]718 Cayman GT4 Telemetry Debrief: {all_time_pb} PB at High Plains Raceway[/SIZE][/B]")
    bb.append("")
    bb.append("Hey everyone,")
    bb.append("")
    bb.append(f"I wrapped up my 2026 track season this past weekend at [B]{track_name}[/B] and wanted to share a comprehensive telemetry and setup debrief.")
    bb.append("")
    bb.append(f"My car is a [B]2023 718 Cayman GT4[/B] in Guards Red running [B]Apex VS-5RE forged wheels[/B] (19x9 front / 19x11 rear) wrapped in [B]Vitour Tempesta P1 (P-01R)[/B] tires (265/35R19 front / 295/30R19 rear).")
    bb.append("")
    bb.append(f"When I first brought the car out in June 2024, my baseline was a humble [B]{baseline_time}[/B]. Over the course of [B]{total_sessions} sessions[/B] and [B]{total_laps} timed CAN telemetry laps[/B], I systematically chipped away at my inputs, tire pressures, and braking technique down to an official [B]{all_time_pb}[/B].")
    bb.append("")
    bb.append("[B]Full Onboard Lap (1440p 60fps Master with CAN Telemetry):[/B]")
    bb.append(f"https://youtu.be/{youtube_pb_id}")
    bb.append("")
    bb.append("____________________________________________________")
    bb.append("")
    bb.append("[B][SIZE=4]📊 The 2-Year Progression & Telemetry Breakdown[/SIZE][/B]")
    bb.append("")
    bb.append(f"• [B]Official Best Lap:[/B] 2:16.78  -->  [B]{all_time_pb}[/B]  [COLOR=Green][B](-17.11 seconds)[/B][/COLOR]")
    bb.append("• [B]Back Straight Top Speed:[/B] 114.2 MPH  -->  [B]134.8 MPH[/B]  [COLOR=Green][B](+20.6 MPH)[/B][/COLOR]")
    bb.append("• [B]Wide Open Throttle (WOT %):[/B] 2.2% of lap  -->  [B]36.6% of lap[/B]  [COLOR=Green][B](+34.4% WOT)[/B][/COLOR]")
    bb.append("• [B]Peak Lateral Grip:[/B] 1.12 G  -->  [B]1.54 G[/B] (Turn 13-15 Prairie Corkscrew)")
    bb.append("• [B]Sustained Cornering:[/B] ~1.05 G  -->  [B]1.32 - 1.35 G[/B]")
    bb.append("")
    bb.append("____________________________________________________")
    bb.append("")
    bb.append("[B][SIZE=4]⚙️ Key Chassis & Driving Takeaways[/SIZE][/B]")
    bb.append("")
    bb.append("[B]1. The Tire Pressure Sweet Spot on Vitour Tempesta P1 (~30.5 PSI Hot Target)[/B]")
    bb.append("• [B]Cold Start:[/B] 23.5 - 24.0 PSI cold.")
    bb.append("• [B]The Trap:[/B] Starting above 28-30 PSI cold pushed the P1s past 36-38 PSI hot within a few laps, causing the compound to overheat and introducing sharp mid-corner understeer.")
    bb.append("• [B]The Discipline:[/B] Coming in immediately after Session 1 and bleeding down to [B]30.5 PSI hot front / 31.0 PSI hot rear[/B] kept the tire right in its prime grip window—delivering [B]1.35G sustained[/B] and peaking at [B]1.54G[/B] through the Prairie Corkscrew (Turns 13-15).")
    bb.append("")
    bb.append("[B]2. The Turn 4 Revelation (Braking in 3rd vs 4th Gear: Gaining 0.300s)[/B]")
    bb.append("• I compared my July telemetry against my October telemetry through Turn 4 (Biker's Berm) and Turn 5 (Niagara Plunge).")
    bb.append("• In July, I held 4th gear through the T4 braking zone. In October, I executed an immediate downshift to 3rd gear during threshold braking at 1,364m.")
    bb.append("• [B]Data Result:[/B]")
    bb.append("   - Apex RPM jumped from 4,477 RPM (4th gear) to [B]5,411 RPM (3rd gear)[/B].")
    bb.append("   - Corner exit acceleration climbed from +0.20G to [B]+0.31G[/B].")
    bb.append("   - Uphill entry speed into T5 climbed from 79.1 MPH to [B]84.7 MPH[/B].")
    bb.append("   - [B]Total time saved across T4-T5: Exactly 0.300 seconds[/B] purely from gear selection and engine braking stability.")
    bb.append("")
    bb.append("[B]3. Trail-Braking Front Axle Loading[/B]")
    bb.append("• The 718 GT4 mid-engine chassis rotates beautifully if I keep 10-15% trail-braking pressure on the nose all the way down to the apex curb.")
    bb.append("• Bleeding off the brake pedal smoothly rather than snapping off eliminated my mid-corner push in Turns 8 and 10 completely.")
    bb.append("")
    bb.append("____________________________________________________")
    bb.append("")
    bb.append("[B][SIZE=4]💬 Questions for fellow 718 GT4 track drivers:[/SIZE][/B]")
    bb.append("1. For those running the Vitour Tempesta P1 or similar super-200s (CR-S, RE-71RS): what hot pressures are you finding optimal on the 19\" 265/295 staggered setup?")
    bb.append("2. For those running Tarett adjustable drop links: what sway bar hole settings (soft/med/stiff) are you running to balance turn-in rotation vs high-speed stability?")
    bb.append("3. What alignment specs (camber/toe) have given you the best tire life without killing high-speed braking stability?")
    bb.append("")
    bb.append("Happy to share raw CAN telemetry CSVs or compare sector deltas with anyone running High Plains Raceway or similar technical tracks!")
    bb.append("")
    bb.append("Best,")
    bb.append("[B]Matthew Garrett[/B]")
    bb.append(f"[I]Instagram: @{instagram_handle} | YouTube: @mgarrettgt4[/I]")
    return "\n".join(bb)

def main():
    bbcode = generate_rennlist_bbcode()
    bbcode_file = REPORTS_DIR / "rennlist_thread_bbcode.txt"
    with open(bbcode_file, "w", encoding="utf-8") as f:
        f.write(bbcode)
    
    md_file = REPORTS_DIR / "rennlist_thread_preview.md"
    clean_md = bbcode.replace("[B]", "**").replace("[/B]", "**").replace("[I]", "*").replace("[/I]", "*").replace("[HR][/HR]", "\n---\n")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(clean_md)
        
    print(f"Generated: {bbcode_file}")
    print(f"Generated: {md_file}")

if __name__ == "__main__":
    main()
