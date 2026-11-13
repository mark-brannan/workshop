# DIN-rail mount for an 80 x 110 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, vented metal case, flat back) on a
35 mm TS35 rail, as one printed piece. A 2.5 mm frame, cut to the supply's own 110 x 80
footprint and open in the centre, screws to the supply's two base holes with M3 screws. Two
DIN clips are part of the frame: the profile of marauder156's "DIN rail clip basic module"
(Thingiverse thing:3640994, `DINrail_Clip.stl`, section taken at mid-length), a fixed hook on one
side and a spring-arm latch on the other, extruded 15 mm along the rail and standing 16 mm off the
frame. The rail runs along the 80 mm axis, the 110 mm side stands up and down. This replaces the
earlier two-part design (frame plus separate clips on pegs, thing:2415668), which printed too tight
at the pegs and weakened every joint.

## Files (out/)

`din-rail-psu-mount_scad.3mf` / `.stl`: the one piece, PSU face down. No separate clips.

Printing: the barbs over the rail slot overhang as they do in the original, which printed flat;
look at the slicer preview before trusting it.

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
| `clip_len` | 15 | the original is 12.3; longer for a stiffer mount |
| `clip_x` | 25 | clip spacing along the rail |
| Rail gap | 35 between the hooks | from the original profile; owner's rail reads 34.5 |

Checks: the section area times 12.3 matches the STL volume (6026 against 6022 mm^3), and the
bounding box is 60 x 16 across the profile.
