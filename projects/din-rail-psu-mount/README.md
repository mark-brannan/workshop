# DIN-rail mount for an 80 x 110 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, enclosed case) on a 35 mm TS35 rail.
Plate bolts to the supply's two base holes; two fixed hooks and two flexure
latches clip onto the rail. Rail runs along the 110 mm axis.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Footprint | 110 x 80 | owner, caliper |
| Hole spacing, long axis | ~75 | owner, caliper ("approx") |
| Hole spacing, wide axis | ~47 | owner, caliper ("approx") |
| Holes | diagonal pair only | owner |

## Guessed, change before printing

| Value | Now | Why it is a guess |
|---|---|---|
| `hole_d` | 4.5 (M4 clearance) | thread size of the supply's base holes unknown |
| `clr` | 0.4 | K2 Plus tolerance row in AGENTS.md is unmeasured |
| `side_clr` | 0.5 | same |
| TS35 flange 1.0 thick, 35 wide, crown 27 wide | standard | not measured on the owner's rail |

Screw length: plate is 4 mm; add the supply's thread depth limit.

## Print

PSU face down (z = 0), no supports, ASA or PETG. The beams flex in-plane (about
1.4 % strain at 2.3 mm travel): print with 4+ perimeters. Release: pry a 2 mm
screwdriver blade into the inner slot beside the beam, outside the hook.
