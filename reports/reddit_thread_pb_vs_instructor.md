# Overlaying my 1:59.67 PB against my instructor's 1:56.55 reference lap in a 718 GT4: where the last 3 seconds actually hide

Hey everyone,

When I finally broke the 2-minute barrier at High Plains Raceway this October with a 1:59.67 in my 2023 718 Cayman GT4 (6MT), the very first thing I did when I got home was overlay my CAN telemetry against a 1:56.55 reference lap logged in the Porsche Track Precision App by one of my instructors in a GT4.

Going from my original 2:16 baseline down to a 1:59 was mostly about fixing big, obvious novice mistakes and getting the chassis sorted (Tarett monoballs, camber plates, rear toe locking plates, GiroDisc rotors, and 265/295 Vitour P1s at 30.5/31.0 PSI hot). 

Finding the next 3 seconds from 1:59.67 down to a 1:56.55 is a completely different game. Looking at the 10Hz CAN traces side by side was super humbling and honestly pretty eye-opening:

**What surprised me (where I wasn't losing time):**
Our average lateral G across all corners (>0.5G) was basically identical (0.97G on my lap vs 0.96G on the reference lap). Even crazier, through the technical back-half S-curves (Turns 8 through 10), my car actually pulled 0.26 seconds back on the reference trace thanks to the front-end bite from the monoball/alignment setup and Vitour P1s. So the car itself easily has the grip for a 1:56.

**Where the 3.1 seconds actually went:**

**1. Initial Brake Attack (81.9 bar vs 111.6 bar)**
Even though both laps hit almost the exact same peak deceleration (-1.24G vs -1.27G), how we got there was totally different. The instructor hits 111.6 bar of brake pressure right at initial pedal application while aero drag is highest, then bleeds off smoothly into the corner. I ramp up more gradually to 81.9 bar, which forces me to get off the gas and onto the brakes 15-20 feet earlier in the two big brake zones (Turn 1 and Turn 4).

**2. Turn 3 Carousel Exit Minimum Speed (50.6 MPH vs 56.5 MPH -> 0.60s lost)**
High Plains has a 2,838-foot back straight right after a long double-apex right-hander (Turns 2-3). I pinched my exit slightly and rolled 50.6 MPH at the slowest point, whereas the reference lap rolled 56.5 MPH and got to full throttle earlier. That 5.9 MPH difference at the apex compounded down the entire half-mile straight and cost me a full 0.60 seconds before we even touched the brakes for Turn 4.

**3. Downhill Corkscrew Commitment (59.6 MPH vs 66.1 MPH -> 0.56s lost)**
Turns 13-15 is a blind downhill compression corkscrew leading onto the front straight. My brain still tells me to over-slow the entry to 59.6 MPH before leaning on the compression at the bottom (where it hits 1.54G). The instructor trusts the compression from turn-in, rolls 66.1 MPH through the dip, and pulls 0.56 seconds on the run to the checkered flag.

**4. Coasting Dead-Time (7.7% vs 4.1% of the lap)**
Across the whole lap, I spent 7.7% of the time coasting (0% throttle and 0% brake) during pedal transitions, compared to just 4.1% on the reference lap. Shrinking that hesitation window between brake release and maintenance throttle is worth over a second by itself.

That gives me three super clear homework items to chase next spring once the car is back from its winter fluid/pad service. For those of you who analyze your own data against faster drivers or coaches, what was the biggest "aha" moment you found in a telemetry overlay?
