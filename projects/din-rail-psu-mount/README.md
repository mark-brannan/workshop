# DIN-rail mount for an 80 x 110 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, vented metal case, flat back) on a
35 mm TS35 rail. A flat base plate screws to the supply's two base holes. Four
separate clips press into windows in the plate: two fixed hooks, two flexure
latches. The rail runs along the 110 mm axis.

## Files (out/)

`din-rail-psu-mount_scad.3mf` / `.stl`: base plate plus the four clips laid out on
one bed (clips beside the plate, upright). `part` in `model.scad` selects
`assembled`, `base`, `fixed`, `latch` for single parts (OpenSCAD Customizer).

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Footprint | 110 x 80 | owner, caliper |
| Hole spacing, long axis | ~75 | owner, caliper ("approx") |
| Hole spacing, wide axis | ~47 | owner, caliper ("approx") |
| Holes | diagonal pair only; take 2.5 mm screws, 3.3 mm at the very most | owner |
| Rail | 34.5 caliper, 35 nominal | owner |

## Guessed

| Value | Now | Why |
|---|---|---|
| `hole_d` | 2.8 | M2.5 clearance; thread of the supply's holes unconfirmed |
| `press` | 0.1 per side | clip block oversize against its window; tune per printer |
| TS35 flange 1.0 thick, 35 wide | standard | not measured on the owner's rail |

Latch geometry is the common flexure-beam DIN clip (ramped lip, in-plane beam,
pry slot beside it), not copied from a specific design: the Thingiverse breadboard
mount (thing:2415668) refused automated fetch (HTTP 403), so it was not read.

Release: pry a 2 mm screwdriver blade into the inner slot beside the beam.
