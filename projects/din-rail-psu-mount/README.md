# DIN-rail mount for an 58 x 85 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, vented metal case, flat back) on a 35 mm TS35
rail. **Prototype stage: flat back, no DIN clips yet** (the Printables 420009 clips were removed
from the model; `ref_din_clip_heat_insert.stl` and git history keep them). A 2.5 mm solid plate the supply's
85 x 58 footprint, M3 screws to its two base holes, cut-outs for its U slot and pill. An 8 mm lip runs round
all four sides of the supply: 2 mm walls, square-cornered inside (the supply's own corners) and rounded outside. On
the lower side a 33.5 mm stretch, starting 8.5 mm from the left edge (top-down view), is a 15 mm wide, 8 mm tall
shelf with two chamfered zip-tie slot pairs (5.5 x 2.2, long along Y, 8 mm apart) through it, one for the AC cord and one
for the DC, each running straight down the shelf between its pair; the tie loops under the flat back. Outside corners
are rounded and the shelf's inside corners filleted. The rail runs along the 58 mm axis, the 85 mm side stands up and down.

## Files (out/)

`din-rail-psu-mount_scad.3mf` / `.stl`: the one piece, flat back down (z = 0), lip rising from the PSU face.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Footprint (box) | 85 x 58 | owner, caliper (corrects the 110 x 80 in the first brief) |
| Hole spacing, long axis | ~75 | owner, caliper ("approx") |
| Hole spacing, wide axis | ~47 | owner, caliper ("approx") |
| Holes | diagonal pair only; M3 screws | owner |
| Rail | 34.5 caliper, 35 nominal | owner |

## Guessed

| Value | Now | Why |
|---|---|---|
| `hole_d` | 3.5 | M3 easy slip fit |
| `clip_x` | 13.5 | clip spacing along the rail |
| Rail gap | 34.5 between the hook lips | from the clip's own model; owner's rail reads 34.5 |

Checks: the clip's bounding box (60 x 18 x 7.5) and volume (4488 mm^3) match the Printables STL.
