# calibration

First real project. Measures the fit numbers in `AGENTS.md` so nothing ships on
a guess. Two halves: a printer tolerance test and a laser kerf test.

## Part 1: K2 Plus tolerance print (ASA)

One plate, printed in ASA in the default orientation.

| Feature | Range | Purpose |
|---|---|---|
| Holes | 3.0 to 6.0 mm in 0.1 steps | Which modelled diameter yields which real bore |
| Pegs | Same nominal range, printed standing | Press fit against the holes above |
| Slot | One, with a known-width gauge | Horizontal expansion along a straight edge |

| Measured | How | Fills AGENTS.md row |
|---|---|---|
| Real bore of every hole | Caliper or pin gauge; smallest hole a nominal M3/M4/M5 shank passes freely | K2 Plus hole clearance (ASA) |
| Which peg holds in which hole by hand pressure | Trial | K2 Plus press fit |
| Slot width and plate outer dimensions against model | Caliper | K2 Plus horizontal expansion |

## Part 2: K40 kerf cut, per material

A comb of slots and a measured square per material.

| Material | Measured | Fills AGENTS.md row |
|---|---|---|
| 3 mm ply | Square outer size minus model, and slot width minus model, both halved | K40 kerf, 3 mm ply |
| 3 mm acrylic | Same | K40 kerf, 3 mm acrylic |

The K40 half is a live session: the user runs it from the workshop Mac in
LightBurn, reads back caliper numbers, and the agent fills the table.
Card 1793768721f8cb0073.

## Not in this project

Router end-mill runout waits for a dial indicator and a known-good collet.
