# DIN-rail mount for an 80 x 110 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, vented metal case, flat back) on a
35 mm TS35 rail. A 2.5 mm frame, cut to the supply's own 110 x 80 footprint and
open in the centre, screws to the supply's two base holes with M3 screws. Two DIN
clips press into peg holes in 1 mm seats on the frame; plate plus seat (3.5) is
deeper than the pegs (3.25), so the holes go through and a clip can be pushed out
from behind. The clip is the owner's
design (Thingiverse thing:2415668, DIN_Clip.stl), outline copied point for point:
a fixed lip on one end, a flexing hooked arm on the other, so two clips give two
fixed and two flex latches. The rail runs along the 80 mm axis, the 110 mm side
stands up and down.

## Files (out/)

`din-rail-psu-mount_scad.3mf` / `.stl`: base plate plus two clips laid out on one
bed, clips flat as in the original STL. `part` in `model.scad` selects
`assembled`, `base`, `clip`. Release a clip hook by pushing the arm's hook tip outward.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Footprint | 110 x 80 | owner, caliper |
| Hole spacing, long axis | ~75 | owner, caliper ("approx") |
| Hole spacing, wide axis | ~47 | owner, caliper ("approx") |
| Holes | diagonal pair only; M3 screws | owner |
| Rail | 34.5 caliper, 35 nominal | owner |

## Guessed

| Value | Now | Why |
|---|---|---|
| `hole_d` | 3.5 | M3 easy slip fit |
| `peg_hole_d` | 4.2 | the original frame's holes are 4.03 on 4.0 pegs, which printed too tight; tune here |
| `clip_w` | 6 | the original width; widen for a stiffer mount |
| `clip_x` | 25 | clip spacing along the rail |
| Rail | 35.25 between clip walls | from the original clip; owner's rail reads 34.5 |

Checks: the clip volume (1884.3) and bounding box match the original STL. The
original frame (`Breadboard_Frame.stl` in the thing's zip) has 4.03-4.04 peg
holes for the 3.99 pegs: a press fit with no allowance for print artefacts.
