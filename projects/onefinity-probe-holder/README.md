# Onefinity touch-probe holder

Purpose: park the Onefinity touch probe on a vertical surface in front of you (bench or enclosure side), cords still
attached, angled so you can reach in and lift it out. The probe drops in point first, as a diamond, its pocket corner
down. Its two lower edges sit in a 90° V, and its top leans out toward you 30°, so gravity holds it. The large flat
face rests on a support wall on your side; the machined face points up, toward the wall, behind a 15 mm lip. The V
sides reach 40 mm up, about half the probe, and the support wall, a quarter circle about the V point, reaches 65 mm. The top stays open. The cords leave
the two upper edges and nothing gets in their way. The V flares out 4 mm a side toward its top so the probe finds its seat by sliding. The V's side walls carry on toward the wall as fins until they meet the 5 mm plate, so they hold the cradle up. The V's bottom is rounded to R10 outside, with no point, and runs straight down into a rounded U on the plate as a chute. Fins and chute meet the plate through an R6 concave fillet. Outside edges are rounded.

![probe in place](out/concept_with_probe.png)

## Files (out/)

`onefinity-probe-holder_scad.3mf` / `.stl`: the holder, printed as installed: the plate's lower edge on the bed. `concept_with_probe.png`, `concept_side.png`: the probe resting in it (preview, `-D show_probe=true`).

Hardware: 2 × #8 (4 mm) countersunk wood screws, about 25 mm long, through a 5 mm plate. Both sit at the plate's top, above the cradle, where the probe's weight pulls the plate off the wall. A driver reaches them straight on over the support wall.

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
| `fit_t`, `fit_v` | 1.0, 0.8 a side, plus a 4 mm flare at the V's top | loose drop-in that guides itself. It's a holder, not a fixture, so no gauge print |
| `v_depth`, `back_h`, `front_h` | 40, 65, 15 | owner: cover about half the square, a little more on the flat face, top open; cord exits ~67 up stay clear |
| `plate_pt` | 40 | the cradle sits high enough that the chute's underside reaches the plate steeper than 45° |
| Screws | 2 at ±25, z 108, above the cradle; holes 5, countersink 10 | #8 wood screws, loose; printed holes run small. High, because the load pulls the top of the plate off the wall |

## How overhangs are held (print orientation = as installed)

- V arm undersides and the fins: 52° from horizontal, because the 45° V is tilted back 30°.
- The V's R10 rounded bottom would go flat; the chute hides it. The chute is the hull of the V's lower part and a rounded U low on the plate, so its underside runs down to the plate at about 50°.
- The R6 fillet where fins and chute meet the plate runs from vertical at the plate to the face it joins, so it is never flatter than that face.
- The support wall's outer face and the lip's inner face lean out at 60°.
- Screw holes run horizontally with teardrop tops. Countersinks are 90° cones.
- The test allows under 35 mm² of flat overhang: the 3 mm corner rounds of the quarter circle pass through flat for a few mm.

Volume 123.7 cm³ (about 155 g PETG), up from 82.9 for the fins, the fillet and the taller plate.
