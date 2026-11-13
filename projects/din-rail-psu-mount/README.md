# DIN-rail mount for an 58 x 85 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, vented metal case, flat back) on a
35 mm TS35 rail, as one printed piece. A 2.5 mm frame, cut to the supply's own 85 x 58
footprint and open in the centre, screws to the supply's two base holes with M3 screws. Two
low-profile DIN clips are part of the frame: Maxstupo's "DIN Rail Clip (Heat Insert Version)"
(Printables 420009, CC BY 4.0; `ref_din_clip_heat_insert.stl`), a fixed hook on one end and a
spring latch on the other, 18 mm along the rail. Its two heat-insert holes are filled, since no
screw joins it to anything. The rail flange sits 4.1 mm off the PSU face; the whole mount is 7.5 mm
deep. The rail runs along the 58 mm axis, the 85 mm side stands up and down. The plate runs 15 mm past the
supply's lower end with three chamfered zip-tie slot pairs (5.5 x 2.2 slots, 5 mm apart, chamfered on the
underside outer edges) for strain relief; the tie loops under the plate where no supply sits.
This is the preferred clip style for DIN mounts here, over a clip lifted higher off the rail.

## Files (out/)

`din-rail-psu-mount_scad.3mf` / `.stl`: the one piece, PSU face down. No separate clips.

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
