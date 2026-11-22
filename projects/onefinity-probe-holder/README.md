# Onefinity touch-probe holder

Purpose: park the Onefinity touch probe on a vertical surface in front of you (bench or enclosure side), cords still
attached, angled so you can reach in and lift it out. The probe drops in point first, as a diamond, its pocket corner
down. Its two lower edges sit in a 90° V, and its top leans out toward you 30°, so gravity holds it. The large flat
face rests on a support wall on your side; the machined face points up, toward the wall, behind a 15 mm lip. The V
sides reach 40 mm up, about half the probe, and the support wall, a quarter circle about the V point, reaches 65 mm. The top stays open. The cords leave
the two upper edges and nothing gets in their way. The point blends into a narrow 5 mm screw plate through a solid gusset; outside edges are rounded.

![probe in place](out/concept_with_probe.png)

## Files (out/)

`onefinity-probe-holder_scad.3mf` / `.stl`: the holder, printed as installed: the plate's lower edge on the bed. `concept_with_probe.png`, `concept_side.png`: the probe resting in it (preview, `-D show_probe=true`).

Hardware: 2 × #8 (4 mm) countersunk wood screws, about 25 mm long, through a 5 mm plate. Fit the screws with the probe out.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Probe block | 63.5 × 63.5 × 18.8 | owner, caliper |
| Pocket | 54 × 54, square to the block, in one corner, open on two edges; leaves 15 thick | owner, caliper; photos |
| Lip | 9.5 wide along the two upper edges (63.5 − 54) | derived |
| Cord exits | roughly centred on the two lipped edges | owner |

## Guessed

| Value | Now | Why |
|---|---|---|
| `tilt` | 30° from vertical, top out toward the user | owner: 15 to 20, top out, bottom near the wall |
| `fit_t`, `fit_v` | 0.6 a side | loose drop-in. It's a holder, not a fixture, so no gauge print |
| `v_depth`, `back_h`, `front_h` | 40, 65, 15 | owner: cover about half the square, a little more on the flat face, top open; cord exits ~67 up stay clear |
| Screws | 2 at ±20, z 10, below the cradle point; holes 5, countersink 10 | #8 wood screws, loose; printed holes run small |

## How overhangs are held (print orientation = as installed)

- V arm undersides: 52° from horizontal, because the 45° V is tilted back 30°. The V's lower flanks stay sharp: a rounded downward edge goes flat.
- The support wall's outer face and the lip's inner face lean out at 60°.
- The gusset under the point narrows toward the plate and drops 8 mm there, so its flanks and underside stay steeper than 45°.
- Screw holes run horizontally with teardrop tops. Countersinks are 90° cones.
- The test allows under 25 mm² of flat overhang: the 3 mm corner rounds of the quarter circle pass through flat for a few mm.

Volume 57.5 cm³ (about 73 g PETG).
