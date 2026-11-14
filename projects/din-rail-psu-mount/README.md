# DIN-rail mount for an 58 x 85 mm AC-DC supply

Purpose: hold the supply (Amazon B0DK3SPYNZ, vented metal case, flat back) on a 35 mm TS35
rail. Two parts: a flat-backed mount, and two stock DIN clips (Maxstupo's heat-insert clip, Printables
420009, CC BY 4.0, `ref_din_clip_heat_insert.stl`) printed apart and screwed on. Each clip takes two M3 heat
inserts; M3 countersunk screws go down through the plate from the PSU side into them, heads below the
pocket floor. Three clip positions along the rail: one clip in the centre, or two at +-20 mm. Each clip's fixed
hook is up (+Y), its spring latch down. The PSU's own two screws are countersunk from the back, heads flush, so
a clip can lie over them: screw the PSU in first, then the clips. The mount prints with one flat face; the clips stay the widely used, refined design. A 2.5 mm solid plate the supply's
85 x 58 footprint, M3 screws to its two base holes, a cut-out for its pill, a loose M3 hole where its U slot mates. An 8 mm lip runs round
all four sides of the supply: 2 mm walls, square-cornered inside (the supply's own corners) and rounded outside. On
the lower side a 33.5 mm stretch, starting 8.5 mm from the left edge (top-down view), is a 15 mm wide, 8 mm tall
shelf with two chamfered zip-tie slot pairs (5.5 x 2.2, long along Y, 8 mm apart) through it, one for the AC cord and one
for the DC, each running straight down the shelf between its pair; the tie loops under the flat back. Each slot has a 2.5 mm roundover on its inner (web-side) bottom edge, so the tie bends round a curve, plus the 1.2 mm chamfer on the outer underside edge. Outside corners
are rounded and the shelf's inside corners filleted. The rail runs along the 58 mm axis, the 85 mm side stands up and down.

## Files (out/)

`din-rail-psu-mount_scad.3mf` / `.stl`: the mount, flat back down (z = 0), lip rising from the PSU face.
`din-rail-psu-mount_din-clip.3mf` / `.stl`: the clip, print one or two. `din-rail-psu-mount_gauge.*`: the fit gauge (fit test 2 passed).

Hardware: per clip, 2 M3 heat inserts and 2 M3 x 6 countersunk (ISO 10642); for the PSU, 2 M3 countersunk.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Footprint (box) | 85 x 58 | owner, caliper (corrects the 110 x 80 in the first brief) |
| Hole spacing, long axis | ~75 | owner, caliper ("approx") |
| Hole spacing, wide axis | ~47 | owner, caliper ("approx") |
| Holes | diagonal pair only; M3 screws | owner |
| Rail | 34.5 caliper, 35 nominal | owner |
| Fit (holes, pill, U slot, pocket) | fit test 2, gauge print: fits | owner, 2026-11-14 |

## Guessed

| Value | Now | Why |
|---|---|---|
| `hole_d` | 3.5 | M3 easy slip fit |
| `clip_xs` | -20, 0, 20 | the widest spread inside the plate that keeps every clip countersink 8 mm or more from the PSU holes and pill |
| Clip screw length | M3 x 6 | 2.5 mm plate + ~3.5 mm into the insert; the clip's insert holes are 7.5 (hook end) and 4.6 deep. Depends on the inserts in hand |
| Rail gap | 34.5 between the hook lips | from the clip's own model; owner's rail reads 34.5 |

Checks: the clip's bounding box (60 x 18 x 7.5) and volume (4488 mm^3) match the Printables STL.
