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

## Notes for the next session (2026-11-13)

- **The supply's box is 58 x 85 mm** (owner, caliper). The first brief said 8 x 11 cm; the earlier plates were built
  to 80 x 110 and were wrong. The 47 x 75 hole spacing fits the 58 x 85 box (about 5 mm in from each edge).
- **Holes:** `hole_d` 3.5 for M3, an easy slip fit, unprinted as of this note. The earlier plates had 2.8 (M2.5) and were
  too small for M3. The supply's own holes take 2.5 mm, 3.3 mm at the very most.
- **Zip-tie extension:** the plate runs 15 mm past the supply's lower end (`ext`), with three slot pairs
  (`tie_xs`, 5.5 x 2.2 slots, 5 mm apart, 1.2 mm underside chamfer on each outer edge), after the halmet fixture.
- **Slicing:** the owner's draft settings are "My 0.24mm Lightening Draft @Creality K2 Plus 0.4 nozzle", SUNLU PETG,
  10% lightning infill, 2 walls, plus `brim_ears`. The full resolved settings are in the tail of any g-code OrcaSlicer made
  with them (the halmet gauge job on the printer was one). The owner slices by hand in OrcaSlicer.
- **Printer:** `shop printer` is read-only. Moonraker file upload works with the key `shop printer` already reads, but
  accepts g-code only, not 3mf. `orca-slicer.exe --slice` on this WSL box exits 5 with no message even given the
  full settings; unexplained, not worth chasing before the owner asks.
