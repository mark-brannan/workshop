# Battery compartment: fit four

The house-battery compartment under a seat aboard: a box whose outboard end
is the hull, rising to port. The goal is four 12 V 280 Ah batteries plus
room for the bus bars, the Orion-Tr DC-DC charger, the MultiPlus
inverter-charger and their cables.

Symphony: none yet

## The tool

[`fit-four.html`](fit-four.html) is an interactive 3D planner. Open it in a
browser; it needs no build.

- A 3D view you can orbit, with top and side views below it.
- Drag a battery in the top or side view. Batteries always sit as low as the
  floor or hull lets them. Only the hull is solid. Batteries pass through
  each other, the lip, the top and the wall units, so all four can always be
  placed. Anything overlapping turns red, and the table says by how much.
- Per battery: level, on the slope (a tilt square to the side walls),
  rotate within the slope, turn 90°, push forward or aft.
- Presets for all four, "Close up the gaps", and where the Orion and the
  MultiPlus go.

## What the numbers are

**None of the shell is confirmed aboard.** The constants at the top of the
script are best guesses from photos and the owner's first readings
(2026-11-20). The top board also sits a little higher than drawn. Read a red
overlap of a fraction of an inch as "close", not as "no".

| Number | Value | Source |
|---|---|---|
| Width between the long walls | 19 1/2 | owner, against a photo |
| Floor to the underside of the forward lip | 19 3/4 | owner, against a photo |
| Floor to the top | 21 3/4 | computed: lip underside plus a 2 in lip |
| Forward lip | stands in 1 1/2, runs 48 | photo; 48 is a guess |
| Level floor ends | 25 along the forward wall | computed |
| Hull rise | 26 1/2°, then 37.1° above 10 1/4 | angle-ruler photos |
| Rise line skew across the width | 20.4° | angle-ruler photo |
| Battery | 17.8 × 9.37 × 8.7 | retailer listing; photos of the one aboard agree |
| MultiPlus 12/500 | 12.24 H × 7.17 W × 3.94 D | Victron datasheet |
| Orion-Tr | about 7 W × 6.5 H × 3.3 D | photo, ±1/2 |
| PR 174 bus-bar board | unknown | not drawn |

Holes (fan, rough hole, floor hole, mousehole, cabin vent) are dashed. Their
places are partly guessed.

## Constraints from the owner

- Every battery as low as possible. Raising one only earns space for the
  ones above, by moving outboard and up the hull.
- A direct two-by-two stack is not wanted.
- Lithium does not need to stand upright, so canted batteries are fair game.
- The top batteries may be pushed aft to clear the lip, and the lower ones
  forward to leave room for bus bars or cables.
