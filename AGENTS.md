# Porsche Track Telemetry & Operations Context (AGENTS.md)

This file is automatically loaded by Antigravity at the start of every conversation in this workspace. It serves as the single source of truth for driver background, vehicle specifications, channel identity, and operational preferences.

---

## 👤 Driver Profile
* **Driver:** Matthew Garrett
* **Tone & Voice:** First-person singular ("I", "my") — **never "we" or "our"** (Matthew is a solo driver). Humble, authentic, data-driven, engineering-focused. Avoid influencer hype or bragging.
* **Home Track:** High Plains Raceway (Full Course — 2.55 miles, 15 turns)
* **All-Time Personal Best:** **1:56.55** (October 2026)
* **Progression:** Baseline 2:16.78 (June 2024) down to 1:56.55 across 61 sessions and 519 timed CAN telemetry laps.

---

## 🏎️ Vehicle Specifications (2023 718 Cayman GT4)
* **Model:** 2023 Porsche 718 Cayman GT4 (Guards Red, May 2023 build)
* **Transmission:** 6-speed manual with Auto-Blip
* **Wheels:** **Apex VS-5RE Motorsport Forged**
  * Front: `19x9.0"`
  * Rear: `19x11.0"`
* **Tires:** **Vitour Tempesta P1 (P-01R)** (Super-200TW)
  * Front: `265/35R19`
  * Rear: `295/30R19`
  * Cold Pressure Target: `23.5 - 24.0 PSI`
  * Hot Pressure Sweet Spot: `30.5 PSI Front / 31.0 PSI Rear` (achieved 1.35G sustained, 1.54G peak in Corkscrew)
* **Brake System:**
  * Rotors: **GiroDisc 380mm Two-Piece Floating Rotors** (Front & Rear)
  * Lines: **Spiegler Stainless Steel Braided Brake Lines** (Front 4-Line + Rear Kit)
  * Fluid: **Castrol React SRF Racing Brake Fluid**
  * Current Pads: **Pagid 4925-RSL29** (all 4 corners)
  * Caliper Consideration: Factory ceramic pucks crack under track heat. Functional alternatives to €2k Goldleaf:
    - **Demon Speed Motorsports (DSM)**: Proprietary race composite or Ti pucks ($108 - $216) — Cup car proven.
    - **AutoQuest Motorsports**: Grade 5 Titanium replacement pucks ($695 Front / $1,165 Full Car) — Rennlist track standard.
    - **Girodisc Titanium Pad Heat Shields**: 1mm Ti shims ($150 Front / $120 Rear, TS-1741-4) — drops piston heat & protects pucks/boots.
* **Suspension & Geometry (Honest Assembly Garage — Denver, CO):**
  * **Tarett Monoball Camber Plates** (Front)
  * **Tarett Monoball Control Arm Ends** (991 GT3/RSR spec with longer studs)
  * **Tarett Lower Control Arm Shims** (10mm, 2mm, 1mm kit)
  * **Tarett Caster-Adjustable Thrust Arm Bushings** (prevents 265 front tire from rubbing fender liners)
  * **Tarett Rear Toe Control Arms w/ Bump Steer Kit & Locking Plates** (eliminates dynamic rear toe-out under threshold braking)
  * **Tarett Adjustable Drop Links** (Front 991 spec & Rear — zeroed sway bar preload under corner balancing)
  * Full monoball spherical bearing conversion (zero rubber bushing compliance)

---

## 📱 Social Media & Online Identity
* **YouTube:** `Matthew Garrett` (`@mgarrettgt4` / `mgarrettgt4@gmail.com`)
  * Master 1440p PB Video: [https://youtu.be/PRz7gJhED00](https://youtu.be/PRz7gJhED00)
  * Banner & Avatar: Styled and branded in `branding/`
* **Instagram:** `@mgarrettgt4` (Matt Garrett)
  * Avatar: Apex attack shot (`branding/avatars/instagram_profile_avatar.png`)
  * Bio: `718 Cayman GT4 | PCA Rocky Mountain Region\nHigh Plains Raceway (1:56.55 PB)\nCAN telemetry, setup notes & in-car laps 🏁`
  * External Link: `https://youtube.com/@mgarrettgt4`
* **Rennlist Forum:**
  * Account tied to `mgarrettgt4@gmail.com`
  * Thread Draft: [`reports/rennlist_thread_bbcode.txt`](file:///c:/Users/Darig/Projects/Porsche%20Track%20App/reports/rennlist_thread_bbcode.txt)
  * Target subforum: *718 Cayman GTS 4.0 / GT4 / GT4 RS / Spyder*

---

## 📁 Repository Architecture & Rules
1. **Python Scripts Stay in Root**: Do not move `.py` scripts to subdirectories. Subprocesses in `post_event_pipeline.py` and CLI muscle memory depend on root execution.
2. **Assets & Reports**:
   * `branding/`: Contains banners, avatars, previews, and zip archives.
   * `reports/`: Contains debriefs, build sheets, and Rennlist threads.
   * `config/`: Contains credentials (`instagram_session.json`, `youtube_token.json`, `vehicle_spec.json`).
   * `setup/suspension/`: Contains Honest Assembly invoice screenshots.
   * `Track Photos/`: Contains 49 high-res track photos and contact sheet.
3. **Cory / Honest Assembly Next Steps (End-of-Season Maintenance)**:
   * End-of-season fluids: Engine oil change, brake fluid flush (Castrol SRF).
   * Replacing Pagid RSL29 pads on all 4 corners.
   * Inspecting factory Brembo ceramic caliper pucks for chipping/cracking to evaluate Goldleaf titanium caliper pistons.
   * Asking Cory for exact alignment sheet (camber, caster, toe), sway bar hole settings, and corner balance sheet.
