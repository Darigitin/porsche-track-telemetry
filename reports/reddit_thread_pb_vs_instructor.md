# Overlaying my 1:59.67 PB against my instructor's 1:56.55 reference lap in a 718 GT4: where the last 3 seconds actually hide

Hey everyone,

When I finally broke the 2-minute barrier at High Plains Raceway this October with a 1:59.67 in my 2023 718 Cayman GT4 (6MT), the first thing I did when I got home was overlay my 10Hz CAN telemetry against a 1:56.55 reference lap logged in the Porsche Track Precision App by one of my instructors in a GT4.

Working down from my original 2:16 baseline to a 1:59 was mostly about fixing big novice habits and getting the chassis sorted (Tarett monoballs, camber plates, rear toe locking plates, GiroDisc rotors, and 265/295 Vitour P1s at 30.5/31.0 PSI hot). Chasing the next 3 seconds from 1:59.67 down to 1:56.55 is a totally different game, and looking at the CAN traces side by side was pretty eye-opening.

What surprised me most was where I wasn't losing time. Our average lateral G across all corners (>0.5G) was basically identical at 0.97G on my lap vs 0.96G on the reference lap. Even cooler, through the technical back-half S-curves (Turns 8 through 10), my car actually pulled 0.26 seconds back on the reference trace thanks to the front-end bite from the monoball alignment setup and the 265 front Vitour P1s. So the car itself clearly has the mechanical grip for a 1:56.

Where the 3.1 seconds actually went came down to four specific habits in my driving:

First is initial brake attack (81.9 bar vs 111.6 bar). Even though both laps hit almost the exact same peak deceleration (-1.24G vs -1.27G), how we got there looked completely different on the graph. My instructor hits 111.6 bar of brake pressure right at initial pedal application while aero drag and speed are highest, then bleeds off smoothly into the corner. I ramp up more gradually to 81.9 bar, which forces me to get off the gas and onto the brakes 15 to 20 feet earlier in the two big brake zones (Turn 1 and Turn 4).

Second is Turn 3 Carousel exit speed onto the back straight (50.6 MPH vs 56.5 MPH, worth 0.60s). High Plains has a 2,838-foot straight right after a long double-apex right-hander. I pinched my exit slightly and rolled 50.6 MPH at the slowest point, whereas the reference lap rolled 56.5 MPH and got to full throttle earlier. That 5.9 MPH gap at the apex compounded down the entire half-mile straight and cost me 0.60 seconds before we even touched the brakes for Turn 4.

Third is commitment into the blind downhill Corkscrew at Turns 13-15 (59.6 MPH vs 66.1 MPH, worth 0.56s). My brain still tells me to over-slow the blind entry to 59.6 MPH before leaning on the compression at the bottom (where it hits 1.54G). The instructor trusts the compression from turn-in, rolls 66.1 MPH through the dip, and pulls 0.56 seconds on the run to the start/finish line.

Fourth is coasting dead-time during pedal transitions (7.7% vs 4.1% of the lap). Across the whole lap, I spent 7.7% of the time with both pedals at 0% between releasing the brake and picking up maintenance throttle, compared to just 4.1% on the reference lap. Shrinking that hesitation window is worth over a second by itself.

That gives me a super clear list to work on next spring once the car is back from its winter fluid and pad service. For those of you who overlay your data against faster drivers or coaches, what was the biggest eye-opener you found in a telemetry comparison?
