# 2-Year Progression: 2:16 down to 1:56.55 at High Plains Raceway in a 718 Cayman GT4 (Chassis Setup & CAN Telemetry Debrief)

Hey everyone,

I wanted to share a data-driven debrief of my 2-year progression tracking my 2023 718 Cayman GT4 (6MT) at High Plains Raceway (Full Course — 2.55 miles, 15 turns) here in Colorado.

When I started in June 2024, my baseline was **2:16.78**. Over the past two seasons across **61 sessions and 519 timed CAN telemetry laps**, I chipped away at line, brake modulation, and chassis setup to cross the line at **1:56.55** this October.

Here is an honest breakdown of the chassis changes, brake thermal management, tire pressures, and telemetry findings that actually moved the needle.

---

### 1. Curing the 718 Front-End Understeer (Chassis & Geometry)
From the factory, the 718 Cayman GT4 has noticeable mid-corner understeer designed into the rubber bushings and conservative front camber. To fix this without compromising mid-engine stability, I had Honest Assembly in Denver do a complete spherical bearing conversion:
* **Tarett Monoball Camber Plates & Control Arm Ends:** Unlocked proper track camber while eliminating squishy rubber compliance.
* **Tarett Caster-Adjustable Thrust Arm Bushings:** Crucial when running wider rubber—pulls the front wheel forward in the wheel well to prevent a 265 tire from chewing through the fender liners under steering lock.
* **Tarett Rear Toe Links w/ Bump Steer Kit & Locking Plates:** The factory eccentric rear toe bolts are notorious for slipping under track curb impacts. More importantly, this eliminated the nervous dynamic rear toe-out that mid-engine cars suffer under threshold braking.
* **Tarett Adjustable Drop Links:** Allowed us to zero out sway bar preload when corner balanced with driver weight in the cockpit.

The car now points cleanly into corners and transitions onto the nose predictably under trail-braking.

---

### 2. Brake Setup & Caliper Puck Thermal Management
High Plains Raceway features three heavy deceleration zones from 120–135 mph. At 5,000+ ft altitude, brake heat builds up quickly:
* **Rotors:** GiroDisc 380mm 2-piece floating rotors (front & rear). Sheds unsprung rotational mass and the curved internal vanes pump significantly more cooling air.
* **Pads & Fluid:** Pagid 4925-RSL29 endurance pads on all 4 corners + Castrol React SRF fluid. Spiegler stainless braided lines give rock-hard pedal modulation.
* **Tarett Caliper Stud Conversion:** Protects the factory aluminum wheel upright threads from stripping during pad swaps.
* **The Factory Brembo Ceramic Puck Issue:** If you track a 718 GT4 or 991, check your caliper piston pucks regularly. The factory ceramic pucks chip and crack under track heat. Instead of dropping €2k on boutique titanium pistons, running **Girodisc 1mm titanium pad heat shields (TS-1741)** or Demon Speed / AutoQuest replacement pucks drops heat transfer to the fluid and keeps dust boots intact.

---

### 3. Tire Pressures: Vitour Tempesta P1 (Super-200TW)
I run **Apex VS-5RE motorsport forged wheels** (19x9.0 front / 19x11.0 rear) wrapped in **Vitour Tempesta P1s** (265/35R19 front, 295/30R19 rear).
* **Cold Starting Pressure:** 23.5 – 24.0 PSI
* **Hot Target Sweet Spot:** **30.5 PSI Front / 31.0 PSI Rear**
* **The Data:** At 30.5/31.0 PSI, the car pulled **1.35G sustained lateral load** and **1.54G peak** through the HPR Corkscrew. If the rear tires creep above 32.5 PSI hot, the telemetry shows a distinct spike in slip angle and the rear gets greasy on corner exits.

---

### 4. Telemetry Findings: Where the 20 Seconds Came From
Looking at the 10Hz CAN-bus delta overlays comparing my 2:16 baseline to the 1:56.55:
1. **Turn 4 Trail-Braking:** In 2024, I was overslowing in a straight line and fighting understeer at turn-in. Telemetry showed that carrying 15–20% trail-brake pressure deep toward the apex kept the front tires loaded, rotated the chassis, and carried 6+ mph higher minimum apex velocity.
2. **Turn 3 Carousel Exit onto Back Straight:** Maximizing late throttle pickup onto the 2,838-foot straight drove peak terminal velocity from 125 mph up to 134.8 mph at the brake marker.
3. **Wide Open Throttle (WOT) %:** Increased from just 2.2% WOT in early 2024 to **36.6% WOT** on the 1:56.55 lap.

---

Happy to answer any questions on 718 GT4 setup, Tarett alignment specs, Girodisc rotor wear, or tire pressure management!

*(I uploaded the full 1440p lap with complete CAN-bus telemetry gauges—throttle, brake pressure, lateral Gs, and delta timer—in the first comment below for anyone studying HPR lines or setting up a 718).*
